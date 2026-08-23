use crate::models::{MatchGroup, MatchItem, MatchRequest, MatchResult};
use redis::{AsyncCommands, Client};
use std::collections::{HashMap, VecDeque};
use std::env;
use std::sync::{Arc, Mutex};
use std::time::Duration;
use tokio::time::timeout;

struct BoundedRegexCache<T: Clone> {
    map: HashMap<String, T>,
    order: VecDeque<String>,
    capacity: usize,
}

impl<T: Clone> BoundedRegexCache<T> {
    fn new(capacity: usize) -> Self {
        Self {
            map: HashMap::with_capacity(capacity),
            order: VecDeque::with_capacity(capacity),
            capacity,
        }
    }

    fn get(&mut self, key: &str) -> Option<T> {
        self.map.get(key).cloned()
    }

    fn insert(&mut self, key: String, re: T) {
        if !self.map.contains_key(&key) {
            if self.order.len() >= self.capacity {
                if let Some(old_key) = self.order.pop_front() {
                    self.map.remove(&old_key);
                }
            }
            self.order.push_back(key.clone());
        }
        self.map.insert(key, re);
    }
}

type StandardCache = Arc<Mutex<BoundedRegexCache<regex::Regex>>>;
type FancyCache = Arc<Mutex<BoundedRegexCache<fancy_regex::Regex>>>;

// The fancy-regex backtracking VM has no wall clock of its own; this caps how
// many steps a catastrophic pattern may burn before it gives up.
const FANCY_BACKTRACK_LIMIT: usize = 1_000_000;

fn failure(req: &MatchRequest, error: String) -> MatchResult {
    MatchResult {
        task_id: req.task_id.clone(),
        engine_id: req.engine_id.clone(),
        success: false,
        matches: vec![],
        execution_time_ms: 0.0,
        error: Some(error),
    }
}

// The regex crates report byte offsets; the platform contract requires Unicode
// code point indices. For ASCII text both are identical.
fn build_byte_to_char(text: &str) -> Option<Vec<u32>> {
    if text.is_ascii() {
        return None;
    }
    let mut map = vec![0u32; text.len() + 1];
    let mut count: u32 = 0;
    for (i, ch) in text.char_indices() {
        for b in i..i + ch.len_utf8() {
            map[b] = count;
        }
        count += 1;
    }
    map[text.len()] = count;
    Some(map)
}

pub async fn listen_and_process(client: Client) {
    println!("[Worker] Rust worker listening on 'queue:rust'...");

    let mut con = client.get_async_connection().await.expect("Failed to connect to Redis");

    let timeout_ms: u64 = env::var("WORKER_EXECUTION_TIMEOUT_MS").unwrap_or_else(|_| "1000".to_string()).parse().unwrap_or(1000);
    let max_input_size: usize = env::var("WORKER_MAX_INPUT_SIZE").unwrap_or_else(|_| "10485760".to_string()).parse().unwrap_or(10485760);
    let max_matches: usize = env::var("WORKER_MAX_MATCHES").unwrap_or_else(|_| "10000".to_string()).parse().unwrap_or(10000);
    let max_groups: usize = env::var("WORKER_MAX_GROUPS").unwrap_or_else(|_| "1000".to_string()).parse().unwrap_or(1000);
    let max_json_size: usize = env::var("WORKER_MAX_JSON_SIZE").unwrap_or_else(|_| "10485760".to_string()).parse().unwrap_or(10485760);

    let standard_cache: StandardCache = Arc::new(Mutex::new(BoundedRegexCache::new(1000)));
    let fancy_cache: FancyCache = Arc::new(Mutex::new(BoundedRegexCache::new(1000)));

    loop {
        let result: redis::RedisResult<(String, String)> = con.brpop("queue:rust", 0.0).await;

        match result {
            Ok((_, task_json)) => {
                let mut req: MatchRequest = match serde_json::from_str(&task_json) {
                    Ok(r) => r,
                    Err(e) => {
                        handle_dlq(&client, &task_json, &format!("JSON parse error: {}", e)).await;
                        continue;
                    }
                };

                let mut con_clone = client.get_async_connection().await.unwrap();
                let mut pub_con_clone = client.get_async_connection().await.unwrap();
                let client_clone = client.clone();
                let standard_clone = Arc::clone(&standard_cache);
                let fancy_clone = Arc::clone(&fancy_cache);
                let original_json = task_json.clone();

                tokio::spawn(async move {
                    if let Some(payload_id) = &req.text_payload_id {
                        let payload_res: redis::RedisResult<String> = con_clone.get(payload_id).await;
                        match payload_res {
                            Ok(payload) => req.text = payload,
                            Err(_) => {
                                handle_dlq(&client_clone, &original_json, "Payload expired or missing from Redis").await;
                                let err_res = MatchResult {
                                    task_id: req.task_id.clone(),
                                    engine_id: req.engine_id.clone(),
                                    success: false,
                                    matches: vec![],
                                    execution_time_ms: 0.0,
                                    error: Some("Payload expired or missing from Redis".to_string()),
                                };
                                publish_result(&mut pub_con_clone, &req.task_id, err_res, max_json_size).await;
                                return;
                            }
                        }
                    }

                    let start = std::time::Instant::now();

                    let exec_future = execute_regex(&req, standard_clone, fancy_clone, max_input_size, max_matches, max_groups);
                    let final_result = match timeout(Duration::from_millis(timeout_ms), exec_future).await {
                        Ok(res) => {
                            let mut r = res;
                            r.execution_time_ms = start.elapsed().as_micros() as f64 / 1000.0;
                            r
                        },
                        Err(_) => {
                            handle_dlq(&client_clone, &original_json, "TIMEOUT: Rust execution exceeded SLA.").await;
                            MatchResult {
                                task_id: req.task_id.clone(),
                                engine_id: req.engine_id.clone(),
                                success: false,
                                matches: vec![],
                                execution_time_ms: timeout_ms as f64,
                                error: Some(format!("TIMEOUT: Rust execution exceeded {}ms SLA.", timeout_ms)),
                            }
                        }
                    };

                    publish_result(&mut pub_con_clone, &req.task_id, final_result, max_json_size).await;
                });
            }
            Err(_) => {
                tokio::time::sleep(Duration::from_millis(100)).await;
            }
        }
    }
}

async fn handle_dlq(client: &Client, task_json: &str, error_msg: &str) {
    if let Ok(mut con) = client.get_async_connection().await {
        if let Ok(mut v) = serde_json::from_str::<serde_json::Value>(task_json) {
            if let Some(obj) = v.as_object_mut() {
                let current_attempts = obj.get("attempt_count").and_then(|a| a.as_u64()).unwrap_or(0);
                obj.insert("attempt_count".to_string(), serde_json::json!(current_attempts + 1));
                obj.insert("error_reason".to_string(), serde_json::json!(error_msg));
            }
            let _ : redis::RedisResult<()> = con.lpush("queue:rust:dead", v.to_string()).await;
        }
    }
}

async fn publish_result(con: &mut redis::aio::Connection, task_id: &str, mut result: MatchResult, max_json_size: usize) {
    let mut res_json = serde_json::to_string(&result).unwrap_or_default();

    if res_json.len() > max_json_size {
        result.success = false;
        result.matches = vec![];
        result.error = Some(format!("Output JSON exceeds maximum allowed size of {} bytes.", max_json_size));
        res_json = serde_json::to_string(&result).unwrap_or_default();
    }

    let key = format!("result:{}", task_id);
    let _ : redis::RedisResult<()> = con.set_ex(&key, res_json, 60).await;
    let _ : redis::RedisResult<()> = con.publish(&key, "ready").await;
}

async fn execute_regex(
    req: &MatchRequest,
    standard_cache: StandardCache,
    fancy_cache: FancyCache,
    max_input_size: usize,
    max_matches: usize,
    max_groups: usize
) -> MatchResult {

    if req.text.len() > max_input_size {
        return failure(req, format!("Input text exceeds maximum allowed size of {} bytes.", max_input_size));
    }

    match req.engine_id.as_str() {
        "rust_fancy" => execute_fancy(req, fancy_cache, max_matches, max_groups),
        _ => execute_standard(req, standard_cache, max_matches, max_groups),
    }
}

fn execute_standard(
    req: &MatchRequest,
    cache: StandardCache,
    max_matches: usize,
    max_groups: usize
) -> MatchResult {

    let mut case_insensitive = false;
    let mut multi_line = false;
    let mut dot_matches_new_line = false;
    let mut crlf = false;
    let mut swap_greed = false;
    let mut unicode = true;
    let mut ignore_whitespace = false;

    let mut flag_str = String::new();

    for flag in &req.flags {
        flag_str.push_str(flag);
        match flag.as_str() {
            "i" => case_insensitive = true,
            "m" => multi_line = true,
            "s" => dot_matches_new_line = true,
            "R" => crlf = true,
            "U" => swap_greed = true,
            "u" => unicode = true,
            "-u" => unicode = false,
            "x" => ignore_whitespace = true,
            _ => {}
        }
    }

    let cache_key = format!("{}|{}", flag_str, req.regex);

    let re_opt = {
        let mut c = cache.lock().unwrap();
        c.get(&cache_key)
    };

    let re = match re_opt {
        Some(r) => r,
        None => {
            let builder = regex::RegexBuilder::new(&req.regex)
                .case_insensitive(case_insensitive)
                .multi_line(multi_line)
                .dot_matches_new_line(dot_matches_new_line)
                .crlf(crlf)
                .swap_greed(swap_greed)
                .unicode(unicode)
                .ignore_whitespace(ignore_whitespace)
                .size_limit(10 * (1 << 20))
                .build();

            match builder {
                Ok(r) => {
                    cache.lock().unwrap().insert(cache_key, r.clone());
                    r
                }
                Err(e) => return failure(req, format!("Compilation failed: {}", e))
            }
        }
    };

    let byte_to_char = build_byte_to_char(&req.text);
    let to_char = |byte_idx: usize| -> usize {
        match &byte_to_char {
            Some(map) => map[byte_idx.min(map.len() - 1)] as usize,
            None => byte_idx,
        }
    };

    let mut match_items = Vec::new();
    let mut match_id = 0;

    for caps in re.captures_iter(&req.text) {
        if match_id >= max_matches {
            return failure(req, format!("Exceeded maximum allowed matches ({}).", max_matches));
        }

        if let Some(full_match) = caps.get(0) {
            let mut groups = Vec::new();

            for (i, name_opt) in re.capture_names().enumerate().skip(1) {
                if groups.len() >= max_groups {
                    return failure(req, format!("Exceeded maximum allowed groups per match ({}).", max_groups));
                }

                if let Some(m) = caps.get(i) {
                    groups.push(MatchGroup {
                        group_id: i,
                        name: name_opt.map(|s| s.to_string()),
                        content: m.as_str().to_string(),
                        start: to_char(m.start()),
                        end: to_char(m.end()),
                    });
                }
            }

            match_items.push(MatchItem {
                match_id,
                full_match: full_match.as_str().to_string(),
                start: to_char(full_match.start()),
                end: to_char(full_match.end()),
                groups,
            });
            match_id += 1;
        }
    }

    MatchResult {
        task_id: req.task_id.clone(),
        engine_id: req.engine_id.clone(),
        success: true,
        matches: match_items,
        execution_time_ms: 0.0,
        error: None,
    }
}

// fancy-regex has no RegexBuilder switches for the mode flags, so they are
// applied as an inline group prefix, exactly as a user would write them.
fn execute_fancy(
    req: &MatchRequest,
    cache: FancyCache,
    max_matches: usize,
    max_groups: usize
) -> MatchResult {

    let mut inline = String::new();
    for flag in &req.flags {
        match flag.as_str() {
            "i" | "m" | "s" | "x" | "U" => inline.push_str(flag),
            other => return failure(req, format!("Unsupported flag '{}' for the Rust fancy-regex engine", other)),
        }
    }

    let source = if inline.is_empty() {
        req.regex.clone()
    } else {
        format!("(?{}){}", inline, req.regex)
    };

    let cache_key = format!("{}|{}", inline, req.regex);

    let re_opt = {
        let mut c = cache.lock().unwrap();
        c.get(&cache_key)
    };

    let re = match re_opt {
        Some(r) => r,
        None => {
            let built = fancy_regex::RegexBuilder::new(&source)
                .backtrack_limit(FANCY_BACKTRACK_LIMIT)
                .build();

            match built {
                Ok(r) => {
                    cache.lock().unwrap().insert(cache_key, r.clone());
                    r
                }
                Err(e) => return failure(req, format!("Compilation failed: {}", e))
            }
        }
    };

    let byte_to_char = build_byte_to_char(&req.text);
    let to_char = |byte_idx: usize| -> usize {
        match &byte_to_char {
            Some(map) => map[byte_idx.min(map.len() - 1)] as usize,
            None => byte_idx,
        }
    };

    let names: Vec<Option<String>> = re.capture_names().map(|n| n.map(|s| s.to_string())).collect();

    let mut match_items = Vec::new();
    let mut match_id = 0;

    for caps_result in re.captures_iter(&req.text) {
        if match_id >= max_matches {
            return failure(req, format!("Exceeded maximum allowed matches ({}).", max_matches));
        }

        let caps = match caps_result {
            Ok(c) => c,
            Err(e) => return failure(req, format!("Match failed: {}", e)),
        };

        if let Some(full_match) = caps.get(0) {
            let mut groups = Vec::new();

            for i in 1..caps.len() {
                if groups.len() >= max_groups {
                    return failure(req, format!("Exceeded maximum allowed groups per match ({}).", max_groups));
                }

                if let Some(m) = caps.get(i) {
                    groups.push(MatchGroup {
                        group_id: i,
                        name: names.get(i).cloned().flatten(),
                        content: m.as_str().to_string(),
                        start: to_char(m.start()),
                        end: to_char(m.end()),
                    });
                }
            }

            match_items.push(MatchItem {
                match_id,
                full_match: full_match.as_str().to_string(),
                start: to_char(full_match.start()),
                end: to_char(full_match.end()),
                groups,
            });
            match_id += 1;
        }
    }

    MatchResult {
        task_id: req.task_id.clone(),
        engine_id: req.engine_id.clone(),
        success: true,
        matches: match_items,
        execution_time_ms: 0.0,
        error: None,
    }
}
