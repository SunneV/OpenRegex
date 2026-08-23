use redis::AsyncCommands;
use serde_json::{json, Value};
use std::env;

fn engine_flag(name: &str) -> Value {
    let (description, group): (String, String) = match name {
        "i" => ("Case-insensitive matching.".to_string(), "Basic".to_string()),
        "m" => ("Multiline mode. Makes ^ and $ work per line.".to_string(), "Basic".to_string()),
        "s" => ("DotAll mode. Makes . match newline.".to_string(), "Basic".to_string()),
        "R" => ("CRLF-aware mode for anchors and dot behavior.".to_string(), "Unique".to_string()),
        "U" => ("Swap greedy and lazy quantifier behavior.".to_string(), "Advance".to_string()),
        "u" => ("Unicode mode (enabled by default).".to_string(), "Basic".to_string()),
        "-u" => ("Disable Unicode mode (ASCII-only).".to_string(), "Basic".to_string()),
        "x" => ("Ignore insignificant whitespace and allow comments.".to_string(), "Basic".to_string()),
        _ => (format!("Flag ({name})"), "Basic".to_string()),
    };

    json!({
        "name": name,
        "description": description,
        "group": group
    })
}

fn build_engine_flags(names: &[&str]) -> Vec<Value> {
    names.iter().map(|name| engine_flag(name)).collect()
}

pub async fn register_engines(con: &mut redis::aio::MultiplexedConnection) -> redis::RedisResult<()> {
    let worker_version = env::var("WORKER_VERSION").unwrap_or_else(|_| "1.0.0".to_string());
    let release_date = env::var("WORKER_RELEASE_DATE").unwrap_or_else(|_| "Unreleased".to_string());
    let library_version = "1.12.3";
    let fancy_version = "0.14";

    // Contract version: "1.1" = match offsets normalized to Unicode code points.
    let schema_version = "1.1";

    let worker_info = json!({
        "worker_name": "worker-rust",
        "worker_version": worker_version,
        "worker_release_date": release_date,
        "worker_schema_version": schema_version,
        "engines": [
            {
                "engine_id": "rust_standard",
                "engine_language_type": "Rust",
                "engine_language_version": "1.75+",
                "engine_regex_lib": "regex",
                "engine_regex_lib_version": library_version,
                "engine_label": "Rust (regex crate)",
                "engine_capabilities": {
                    "flags": build_engine_flags(&["i", "m", "s", "R", "U", "u", "-u", "x"]),
                    "supports_lookaround": false,
                    "supports_backrefs": false
                },
                "engine_docs": {
                    "trivia": [
                        "Guarantees worst-case O(m * n) search time, where m is proportional to the regex size and n is proportional to the haystack size.",
                        "The Rust regex crate is dual-licensed under MIT OR Apache-2.0.",
                        "Avoids features such as lookaround and backreferences to maintain predictable performance.",
                        "Unicode mode is enabled by default for &str regexes and can be disabled with the 'u' flag only where valid.",
                        "Supports lazy quantifiers, named capture groups, Unicode properties, and character-class set operations."
                    ],
                    "cheat_sheet_url": "https://docs.rs/regex/latest/regex/"
                },
                "engine_cheat_sheet": [
                    {
                        "category": "Matching One Character & Classes",
                        "items": [
                            { "character": ".", "description": "Any character except newline unless 's' flag is set" },
                            { "character": "\\w", "description": "Unicode word character by default; ASCII-only when Unicode mode is disabled" },
                            { "character": "\\W", "description": "Non-word character" },
                            { "character": "\\d", "description": "Unicode decimal digit by default; ASCII-only when Unicode mode is disabled" },
                            { "character": "\\D", "description": "Non-digit" },
                            { "character": "\\s", "description": "Unicode whitespace character by default; ASCII-only when Unicode mode is disabled" },
                            { "character": "\\S", "description": "Non-whitespace character" },
                            { "character": "\\pX", "description": "Unicode character class identified by a one-letter name" },
                            { "character": "\\p{Greek}", "description": "Unicode character class (general category or script)" },
                            { "character": "\\PX", "description": "Negated Unicode character class identified by a one-letter name" },
                            { "character": "\\P{Greek}", "description": "Negated Unicode character class (general category or script)" },
                            { "character": "[xyz]", "description": "Character class matching either x, y or z (union)" },
                            { "character": "[^xyz]", "description": "Negated character class matching any character except x, y and z" },
                            { "character": "[a-z]", "description": "Character class matching any character in range a-z" },
                            { "character": "[x[^xyz]]", "description": "Nested/grouping character class" },
                            { "character": "[a-y&&xyz]", "description": "Intersection (matching x or y)" },
                            { "character": "[0-9&&[^4]]", "description": "Subtraction using intersection and negation" },
                            { "character": "[0-9--4]", "description": "Direct subtraction (matching 0-9 except 4)" },
                            { "character": "[a-g~~b-h]", "description": "Symmetric difference (matching 'a' and 'h' only)" },
                            { "character": "[\\[\\]]", "description": "Escaping in character classes (matching [ or ])" },
                            { "character": "[a&&b]", "description": "An empty character class matching nothing" }
                        ]
                    },
                    {
                        "category": "ASCII Character Classes",
                        "items": [
                            { "character": "[[:alnum:]]", "description": "Alphanumeric ([0-9A-Za-z])" },
                            { "character": "[[:alpha:]]", "description": "Alphabetic ([A-Za-z])" },
                            { "character": "[[:ascii:]]", "description": "ASCII ([\\x00-\\x7F])" },
                            { "character": "[[:blank:]]", "description": "Blank ([\\t ])" },
                            { "character": "[[:cntrl:]]", "description": "Control ([\\x00-\\x1F\\x7F])" },
                            { "character": "[[:digit:]]", "description": "Digits ([0-9])" },
                            { "character": "[[:graph:]]", "description": "Graphical ([!-~])" },
                            { "character": "[[:lower:]]", "description": "Lower case ([a-z])" },
                            { "character": "[[:print:]]", "description": "Printable ([ -~])" },
                            { "character": "[[:punct:]]", "description": "Punctuation ([!-/:-@\\[-`{-~])" },
                            { "character": "[[:space:]]", "description": "Whitespace ([\\t\\n\\v\\f\\r ])" },
                            { "character": "[[:upper:]]", "description": "Upper case ([A-Z])" },
                            { "character": "[[:word:]]", "description": "Word characters ([0-9A-Za-z_])" },
                            { "character": "[[:xdigit:]]", "description": "Hex digit ([0-9A-Fa-f])" }
                        ]
                    },
                    {
                        "category": "Composites",
                        "items": [
                            { "character": "xy", "description": "Concatenation (x followed by y)" },
                            { "character": "x|y", "description": "Alternation (x or y, prefer x)" }
                        ]
                    },
                    {
                        "category": "Anchors & Boundaries",
                        "items": [
                            { "character": "^", "description": "Start of haystack, or start of line if 'm' flag is set" },
                            { "character": "$", "description": "End of haystack, or end of line if 'm' flag is set" },
                            { "character": "\\A", "description": "Only the beginning of a haystack" },
                            { "character": "\\z", "description": "Only the end of a haystack" },
                            { "character": "\\b", "description": "Unicode word boundary by default" },
                            { "character": "\\B", "description": "Not a Unicode word boundary by default" },
                            { "character": "\\b{start}, \\<", "description": "Start-of-word boundary" },
                            { "character": "\\b{end}, \\>", "description": "End-of-word boundary" },
                            { "character": "\\b{start-half}", "description": "Half of a start-of-word boundary" },
                            { "character": "\\b{end-half}", "description": "Half of an end-of-word boundary" }
                        ]
                    },
                    {
                        "category": "Escape Sequences",
                        "items": [
                            { "character": "\\*", "description": "Literal *, applies to all ASCII except [0-9A-Za-z<>]" },
                            { "character": "\\a", "description": "Bell (\\x07)" },
                            { "character": "\\f", "description": "Form feed (\\x0C)" },
                            { "character": "\\t", "description": "Horizontal tab" },
                            { "character": "\\n", "description": "New line" },
                            { "character": "\\r", "description": "Carriage return" },
                            { "character": "\\v", "description": "Vertical tab (\\x0B)" },
                            { "character": "\\123", "description": "Octal character code, up to three digits" },
                            { "character": "\\x7F", "description": "Hex character code (exactly two digits)" },
                            { "character": "\\x{10FFFF}", "description": "Hex character code corresponding to a Unicode code point" },
                            { "character": "\\u007F", "description": "Hex character code (exactly four digits)" },
                            { "character": "\\u{7F}", "description": "Hex character code corresponding to a Unicode code point" },
                            { "character": "\\U0000007F", "description": "Hex character code (exactly eight digits)" },
                            { "character": "\\U{7F}", "description": "Hex character code corresponding to a Unicode code point" }
                        ]
                    },
                    {
                        "category": "Quantifiers",
                        "items": [
                            { "character": "*", "description": "0 or more times, greedy" },
                            { "character": "+", "description": "1 or more times, greedy" },
                            { "character": "?", "description": "0 or 1 time, greedy" },
                            { "character": "{n,m}", "description": "At least n and at most m times, greedy" },
                            { "character": "{n,}", "description": "At least n times, greedy" },
                            { "character": "{n}", "description": "Exactly n times" },
                            { "character": "*?", "description": "0 or more times, ungreedy/lazy" },
                            { "character": "+?", "description": "1 or more times, ungreedy/lazy" },
                            { "character": "??", "description": "0 or 1 time, ungreedy/lazy" },
                            { "character": "{n,m}?", "description": "At least n and at most m times, ungreedy/lazy" },
                            { "character": "{n,}?", "description": "At least n times, ungreedy/lazy" },
                            { "character": "{n}?", "description": "Exactly n times, ungreedy/lazy" }
                        ]
                    },
                    {
                        "category": "Grouping & Captures",
                        "items": [
                            { "character": "(exp)", "description": "Numbered capture group" },
                            { "character": "(?:exp)", "description": "Non-capturing group" },
                            { "character": "(?P<name>exp)", "description": "Named capture group" },
                            { "character": "(?<name>exp)", "description": "Named capture group" },
                            { "character": "(?flags)", "description": "Set flags within current group" },
                            { "character": "(?flags:exp)", "description": "Set flags for exp (non-capturing)" }
                        ]
                    },
                    {
                        "category": "Inline Flags & Advanced",
                        "items": [
                            { "character": "(?i)", "description": "Case-insensitive: letters match both upper and lower case" },
                            { "character": "(?m)", "description": "Multi-line mode: ^ and $ match begin/end of line" },
                            { "character": "(?s)", "description": "Allow . to match \\n" },
                            { "character": "(?R)", "description": "Enables CRLF mode: \\r\\n is used for line terminators" },
                            { "character": "(?U)", "description": "Swap the meaning of x* and x*?" },
                            { "character": "(?u)", "description": "Unicode support (enabled by default)" },
                            { "character": "(?-u)", "description": "Disable Unicode mode where valid" },
                            { "character": "(?x)", "description": "Verbose mode, ignores whitespace and allow line comments" },
                            { "character": "(?i:...)", "description": "Scoped inline flag" },
                            { "character": "(?-i:...)", "description": "Scoped inline flag disable" }
                        ]
                    }
                ],
                "engine_examples": [
                    {
                        "regex": "(?P<IP>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d))(/(\\d{1,2}))?(?:-(?P<IP2>(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)))?(?::(?P<port>\\d{1,5}))?",
                        "text": "This is an example to get IP:\n\n192.168.1.100\n192.168.1.100:8080\n127.0.0.1\n192.168.1.0/24\n192.168.1.1-192.168.1.255\n192.168.1.1-192.168.1.255:80\n192.168.1.0/24:80"
                    }
                ]
            },
            {
                "engine_id": "rust_fancy",
                "engine_language_type": "Rust",
                "engine_language_version": "1.75+",
                "engine_regex_lib": "fancy-regex",
                "engine_regex_lib_version": fancy_version,
                "engine_label": "Rust (fancy-regex crate)",
                "engine_capabilities": {
                    "flags": build_engine_flags(&["i", "m", "s", "U", "x"]),
                    "supports_lookaround": true,
                    "supports_backrefs": true
                },
                "engine_docs": {
                    "trivia": [
                        "fancy-regex wraps the regex crate: everything the linear-time engine can handle is delegated to it, and only lookaround and backreferences run on its own backtracking VM.",
                        "The fancy-regex crate is distributed under the MIT license.",
                        "This is the direct answer to the deliberate omissions of the regex crate - the same Rust ecosystem, but with (?=...), (?<=...), \\1 and atomic groups.",
                        "Because part of the work is delegated, a pattern without fancy constructs runs at exactly the speed of the regex crate.",
                        "The backtracking half is bounded by an explicit backtrack limit rather than a wall clock, so a catastrophic pattern fails fast with an error instead of hanging.",
                        "Lookbehind must be fixed width, the same restriction the Python re module has.",
                        "Put this engine side by side with the regex crate one: identical results for everything both support, and a hard error there for every construct only fancy-regex accepts."
                    ],
                    "cheat_sheet_url": "https://docs.rs/fancy-regex/latest/fancy_regex/"
                },
                "engine_cheat_sheet": [
                    {
                        "category": "Matching One Character & Classes",
                        "items": [
                            { "character": ".", "description": "Any character except newline unless 's' flag is set" },
                            { "character": "\\w", "description": "Unicode word character" },
                            { "character": "\\W", "description": "Non-word character" },
                            { "character": "\\d", "description": "Unicode decimal digit" },
                            { "character": "\\D", "description": "Non-digit" },
                            { "character": "\\s", "description": "Unicode whitespace character" },
                            { "character": "\\S", "description": "Non-whitespace character" },
                            { "character": "\\p{Greek}", "description": "Unicode character class (general category or script)" },
                            { "character": "[xyz]", "description": "Character class matching either x, y or z" },
                            { "character": "[^xyz]", "description": "Negated character class" },
                            { "character": "[[:alpha:]]", "description": "POSIX character class inside a class" }
                        ]
                    },
                    {
                        "category": "Anchors & Boundaries",
                        "items": [
                            { "character": "^", "description": "Start of haystack, or start of line if 'm' flag is set" },
                            { "character": "$", "description": "End of haystack, or end of line if 'm' flag is set" },
                            { "character": "\\A", "description": "Absolute start of haystack" },
                            { "character": "\\z", "description": "Absolute end of haystack" },
                            { "character": "\\b", "description": "Word boundary" },
                            { "character": "\\B", "description": "Non-word boundary" },
                            { "character": "\\G", "description": "Where the previous match ended" },
                            { "character": "\\K", "description": "Keep-out: drop everything to the left from the reported match" }
                        ]
                    },
                    {
                        "category": "Quantifiers",
                        "items": [
                            { "character": "*", "description": "0 or more times, greedy" },
                            { "character": "+", "description": "1 or more times, greedy" },
                            { "character": "?", "description": "0 or 1 time, greedy" },
                            { "character": "{m,n}", "description": "Between m and n times, greedy" },
                            { "character": "*?", "description": "0 or more times, lazy" },
                            { "character": "+?", "description": "1 or more times, lazy" },
                            { "character": "??", "description": "0 or 1 time, lazy" },
                            { "character": "*+", "description": "0 or more times, possessive" },
                            { "character": "++", "description": "1 or more times, possessive" },
                            { "character": "?+", "description": "0 or 1 time, possessive" }
                        ]
                    },
                    {
                        "category": "Grouping & Backreferences",
                        "items": [
                            { "character": "(...)", "description": "Capturing group" },
                            { "character": "(?:...)", "description": "Non-capturing group" },
                            { "character": "x|y", "description": "Alternation (x or y, prefer x)" },
                            { "character": "(?<name>...)", "description": "Named capturing group" },
                            { "character": "(?P<name>...)", "description": "Named capturing group, Python-compatible syntax" },
                            { "character": "\\1", "description": "Backreference to capture group 1 - not available in the regex crate" },
                            { "character": "\\k<name>", "description": "Backreference to a named group" }
                        ]
                    },
                    {
                        "category": "Lookarounds & Advanced",
                        "items": [
                            { "character": "(?=...)", "description": "Positive lookahead - not available in the regex crate" },
                            { "character": "(?!...)", "description": "Negative lookahead" },
                            { "character": "(?<=...)", "description": "Positive lookbehind; must be fixed width" },
                            { "character": "(?<!...)", "description": "Negative lookbehind; must be fixed width" },
                            { "character": "(?>...)", "description": "Atomic group; prevents backtracking" },
                            { "character": "(?i)", "description": "Inline flag: case-insensitive" },
                            { "character": "(?m)", "description": "Inline flag: multi-line anchors" },
                            { "character": "(?s)", "description": "Inline flag: dot matches newline" },
                            { "character": "(?x)", "description": "Inline flag: verbose / free-spacing" },
                            { "character": "(?U)", "description": "Inline flag: swap greedy and lazy" },
                            { "character": "(?i:...)", "description": "Scoped inline flag" }
                        ]
                    }
                ],
                "engine_examples": [
                    {
                        "regex": "(?<word>\\w+)\\s+\\k<word>",
                        "text": "A backreference finds doubled words:\n\nthe the quick brown fox\nnot not only here\nbut but also there\nand a clean line without repeats"
                    }
                ]
            }
        ]
    });

    let json_str = serde_json::to_string(&worker_info).unwrap();
    let _: () = con.hset("openregex:workers", "worker-rust", json_str).await?;
    println!("[Worker] Registered 'worker-rust' with 2 engines.");

    Ok(())
}
