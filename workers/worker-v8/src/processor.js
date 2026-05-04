import { Worker } from 'worker_threads';
import os from 'os';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const TIMEOUT_MS = parseInt(process.env.WORKER_EXECUTION_TIMEOUT_MS || "1000", 10);
const MAX_INPUT_SIZE = parseInt(process.env.WORKER_MAX_INPUT_SIZE || "10485760", 10);
const MAX_MATCHES = parseInt(process.env.WORKER_MAX_MATCHES || "10000", 10);
const MAX_GROUPS = parseInt(process.env.WORKER_MAX_GROUPS || "1000", 10);
const MAX_JSON_SIZE = parseInt(process.env.WORKER_MAX_JSON_SIZE || "10485760", 10);

function executeRegexIsolated(req) {
  return new Promise((resolve) => {
    const workerCode = `
      const { parentPort, workerData } = require('worker_threads');
      const { req, limits } = workerData;
      const { regex, text, flags, engine_id } = req;
      
      try {
        if (text.length > limits.MAX_INPUT_SIZE) {
          throw new Error("Input text exceeds maximum allowed size of " + limits.MAX_INPUT_SIZE + " bytes.");
        }

        let RegExpClass = RegExp;
        if (engine_id === 'v8_re2') {
          RegExpClass = require('re2');
        }

        let flagStr = flags.includes('g') ? flags.join('') : flags.join('') + 'g';
        
        // Inject 'd' flag to extract precise capture group boundaries via match.indices
        if (!flagStr.includes('d')) {
          flagStr += 'd';
        }
        
        // Cache object attached to global for subsequent potential re-use in a long-lived isolate
        global.__regexCache = global.__regexCache || new Map();
        const cacheKey = engine_id + "|" + regex + "|" + flagStr;
        let re;
        
        if (global.__regexCache.has(cacheKey)) {
          re = global.__regexCache.get(cacheKey);
          re.lastIndex = 0;
        } else {
          re = new RegExpClass(regex, flagStr);
          if (global.__regexCache.size > 1000) {
            global.__regexCache.clear();
          }
          global.__regexCache.set(cacheKey, re);
        }

        let match;
        const matches = [];
        let matchId = 0;
        
        while ((match = re.exec(text)) !== null) {
          if (matchId >= limits.MAX_MATCHES) {
            throw new Error("Exceeded maximum allowed matches (" + limits.MAX_MATCHES + ").");
          }

          const groups = [];
          for (let i = 1; i < match.length; i++) {
            if (groups.length >= limits.MAX_GROUPS) {
              throw new Error("Exceeded maximum allowed groups per match (" + limits.MAX_GROUPS + ").");
            }

            if (match[i] !== undefined) {
              let start = 0;
              let end = 0;
              
              if (match.indices && match.indices[i]) {
                // Exact boundaries via match.indices
                start = match.indices[i][0];
                end = match.indices[i][1];
              } else {
                // Fallback
                start = text.indexOf(match[i], match.index);
                end = start + match[i].length;
              }

              groups.push({
                group_id: i,
                name: null, 
                content: match[i],
                start: start,
                end: end
              });
            }
          }
          
          matches.push({
            match_id: matchId++,
            full_match: match[0],
            start: match.index,
            end: match.index + match[0].length,
            groups: groups
          });

          if (re.lastIndex === match.index) {
            re.lastIndex++; // Prevent infinite loop on zero-length matches
          }
        }
        parentPort.postMessage({ success: true, matches });
      } catch (err) {
        parentPort.postMessage({ success: false, error: err.message });
      }
    `;

    const limits = { MAX_INPUT_SIZE, MAX_MATCHES, MAX_GROUPS };
    const worker = new Worker(workerCode, { eval: true, workerData: { req, limits } });
    let isFinished = false;

    const timeout = setTimeout(() => {
      if (!isFinished) {
        worker.terminate();
        resolve({ success: false, error: `TIMEOUT: V8 execution exceeded ${TIMEOUT_MS}ms SLA.` });
      }
    }, TIMEOUT_MS);

    worker.on('message', (msg) => {
      isFinished = true;
      clearTimeout(timeout);
      resolve(msg);
    });

    worker.on('error', (err) => {
      isFinished = true;
      clearTimeout(timeout);
      resolve({ success: false, error: err.message });
    });
  });
}

async function resolvePayload(redisClient, taskDict) {
  if (taskDict.text_payload_id) {
    const payload = await redisClient.get(taskDict.text_payload_id);
    if (!payload) {
      throw new Error("Payload expired or missing from Redis");
    }
    taskDict.text = payload;
  }
  return taskDict;
}

async function handleDlq(redisClient, taskDict, errorMsg) {
  try {
    taskDict.attempt_count = (taskDict.attempt_count || 0) + 1;
    taskDict.error_reason = errorMsg;
    await redisClient.lpush("queue:v8:dead", JSON.stringify(taskDict));
  } catch (err) {
    // Failsafe
  }
}

export async function listenAndProcess(redisClient, pubClient) {
  console.log("[Worker] V8 worker listening on 'queue:v8'...");

  const MAX_WORKERS = Math.max(1, os.cpus().length);
  let activeWorkers = 0;

  while (true) {
    try {
      if (activeWorkers >= MAX_WORKERS) {
        await new Promise(r => setTimeout(r, 10));
        continue;
      }

      // Use a 1-second timeout so the loop yields and re-evaluates activeWorkers safely
      const result = await redisClient.brpop("queue:v8", 1);
      if (!result) continue;

      activeWorkers++;

      (async () => {
        let taskDict = {};
        let req = null;
        let taskId = "unknown";

        try {
          taskDict = JSON.parse(result[1]);
          taskId = taskDict.task_id || "unknown";
          req = await resolvePayload(redisClient, taskDict);

          const startTime = performance.now();
          const execResult = await executeRegexIsolated(req);
          const execTime = performance.now() - startTime;

          let payloadObj = {
            task_id: req.task_id,
            engine_id: req.engine_id,
            success: execResult.success,
            matches: execResult.matches || [],
            execution_time_ms: execTime,
            error: execResult.error || null
          };

          let payloadStr = JSON.stringify(payloadObj);
          if (Buffer.byteLength(payloadStr, 'utf8') > MAX_JSON_SIZE) {
            payloadObj = {
              task_id: req.task_id,
              engine_id: req.engine_id,
              success: false,
              matches: [],
              execution_time_ms: execTime,
              error: `Output JSON exceeds maximum allowed size of ${MAX_JSON_SIZE} bytes.`
            };
            payloadStr = JSON.stringify(payloadObj);
          }

          await redisClient.setex(`result:${req.task_id}`, 60, payloadStr);
          await pubClient.publish(`result:${req.task_id}`, "ready");

        } catch (err) {
          console.error("[Error] Task processing failure:", err.message);
          await handleDlq(redisClient, taskDict, err.message);

          if (taskId !== "unknown") {
            const errorPayload = {
              task_id: taskId,
              engine_id: taskDict.engine_id || "unknown",
              success: false,
              matches: [],
              execution_time_ms: 0.0,
              error: err.message
            };
            const payloadStr = JSON.stringify(errorPayload);
            await redisClient.setex(`result:${taskId}`, 60, payloadStr);
            await pubClient.publish(`result:${taskId}`, "ready");
          }
        } finally {
          activeWorkers--;
        }
      })();

    } catch (err) {
      console.error("[Error] V8 Worker loop failure:", err);
      await new Promise(res => setTimeout(res, 1000));
    }
  }
}