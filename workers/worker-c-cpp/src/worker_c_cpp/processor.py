import os
import json
import subprocess
import time
import queue
import redis
import threading
import multiprocessing
from array import array
from itertools import accumulate
from concurrent.futures import ThreadPoolExecutor

from openregex_libs.models import MatchRequest, MatchResult

# Maps each byte to 1 when it starts a UTF-8 sequence, 0 for continuation bytes.
_UTF8_START_TABLE = bytes(0 if 0x80 <= b < 0xC0 else 1 for b in range(256))


def _byte_to_char_map(text: str):
    """Prefix map converting UTF-8 byte offsets to code point indices.

    Returns None for pure-ASCII text, where byte offsets already equal
    code point indices. The C engine binaries operate on UTF-8 bytes and
    report byte offsets; the platform contract requires code points.
    """
    if text.isascii():
        return None
    starts = text.encode("utf-8").translate(_UTF8_START_TABLE)
    return array("I", accumulate(starts, initial=0))


def _normalize_match_offsets(matches: list, text: str) -> None:
    b2c = _byte_to_char_map(text)
    if b2c is None:
        return
    last = len(b2c) - 1
    for match in matches:
        byte_end = match.get("end", 0)
        match["start"] = b2c[min(match.get("start", 0), last)]
        match["end"] = b2c[min(byte_end, last)]
        # Hyperscan runs without start-of-match tracking and encodes the byte
        # end offset in its synthetic full_match text; keep it consistent with
        # the converted code point offsets.
        if match.get("full_match") == f"Match ends at {byte_end}":
            match["full_match"] = f"Match ends at {match['end']}"
        for group in match.get("groups", []):
            group["start"] = b2c[min(group.get("start", 0), last)]
            group["end"] = b2c[min(group.get("end", 0), last)]

ENGINE_BINARIES = {
    "cpp_re2": "/usr/local/bin/re2_engine",
    "cpp_std": "/usr/local/bin/std_engine",
    "cpp_boost": "/usr/local/bin/boost_engine",
    "c_posix": "/usr/local/bin/posix_engine",
    "c_pcre2": "/usr/local/bin/pcre2_engine",
    "c_onig": "/usr/local/bin/onig_engine",
    "cpp_hyperscan": "/usr/local/bin/hyperscan_engine"
}

TIMEOUT_MS = int(os.environ.get("WORKER_EXECUTION_TIMEOUT_MS", 1000))
MAX_INPUT_SIZE = int(os.environ.get("WORKER_MAX_INPUT_SIZE", 10485760))
MAX_MATCHES = int(os.environ.get("WORKER_MAX_MATCHES", 10000))
MAX_GROUPS = int(os.environ.get("WORKER_MAX_GROUPS", 1000))
MAX_JSON_SIZE = int(os.environ.get("WORKER_MAX_JSON_SIZE", 10485760))


class PersistentEngine:
    def __init__(self, engine_id: str, binary_path: str):
        self.engine_id = engine_id
        self.binary_path = binary_path
        self.process = None
        self.restart()

    def restart(self):
        if self.process:
            try:
                self.process.kill()
                self.process.wait(timeout=1.0)
            except Exception:
                pass
        try:
            self.process = subprocess.Popen(
                [self.binary_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except Exception as e:
            print(f"[Engine] Warning: Could not start {self.binary_path} - {e}", flush=True)
            self.process = None

    def execute(self, regex: str, text: str, flags: list):
        if not self.process:
            self.restart()
            if not self.process:
                return {"success": False, "error": f"Engine binary missing or failed to start: {self.binary_path}"}

        req_data = {"regex": regex, "text": text, "flags": flags}
        try:
            self.process.stdin.write(json.dumps(req_data) + "\n")
            self.process.stdin.flush()
        except Exception:
            self.restart()
            return {"success": False, "error": "Failed to write to engine process IPC stream."}

        result_container = []

        def read_stdout():
            try:
                line = self.process.stdout.readline()
                result_container.append(line)
            except Exception:
                pass

        reader_thread = threading.Thread(target=read_stdout)
        reader_thread.daemon = True
        reader_thread.start()
        reader_thread.join(TIMEOUT_MS / 1000.0)

        if reader_thread.is_alive():
            self.restart()
            return {"success": False, "error": f"TIMEOUT: {self.engine_id} execution exceeded {TIMEOUT_MS}ms SLA."}

        if not result_container or not result_container[0].strip():
            self.restart()
            return {"success": False, "error": "Engine process crashed or closed stdout unexpectedly."}

        try:
            parsed = json.loads(result_container[0])

            # Post-execution limits check for C/C++ engine outputs
            if parsed.get("success"):
                matches = parsed.get("matches", [])
                if len(matches) > MAX_MATCHES:
                    return {"success": False, "error": f"Exceeded maximum allowed matches ({MAX_MATCHES})."}
                for match in matches:
                    if len(match.get("groups", [])) > MAX_GROUPS:
                        return {"success": False, "error": f"Exceeded maximum allowed groups per match ({MAX_GROUPS})."}

            return parsed
        except Exception as e:
            return {"success": False, "error": f"Invalid JSON from engine: {str(e)}"}


class EngineGroup:
    def __init__(self):
        self.engines = {
            eid: PersistentEngine(eid, path) for eid, path in ENGINE_BINARIES.items()
        }

    def get_engine(self, engine_id: str) -> PersistentEngine:
        for key, engine in self.engines.items():
            if engine_id.endswith(key):
                return engine
        return None


class WorkerPool:
    def __init__(self, size: int):
        self.workers = [EngineGroup() for _ in range(size)]
        self.available = queue.Queue()
        for w in self.workers:
            self.available.put(w)

    def acquire(self) -> EngineGroup:
        return self.available.get()

    def release(self, worker: EngineGroup):
        self.available.put(worker)


def handle_dlq(redis_client: redis.Redis, task_dict: dict, error_msg: str):
    task_dict["attempt_count"] = task_dict.get("attempt_count", 0) + 1
    task_dict["error_reason"] = error_msg
    try:
        redis_client.lpush("queue:c-cpp:dead", json.dumps(task_dict))
    except Exception:
        pass


def publish_result(redis_client: redis.Redis, task_id: str, out: MatchResult):
    try:
        res_json = out.model_dump_json()
        if len(res_json.encode('utf-8')) > MAX_JSON_SIZE:
            out.success = False
            out.matches = []
            out.error = f"Output JSON exceeds maximum allowed size of {MAX_JSON_SIZE} bytes."
            res_json = out.model_dump_json()

        key = f"result:{task_id}"
        redis_client.setex(key, 60, res_json)
        redis_client.publish(key, "ready")
    except Exception as e:
        print(f"[Error] Failed to publish result: {e}", flush=True)


def process_task(redis_client: redis.Redis, raw_json_bytes: bytes, pool: WorkerPool):
    task_id = "unknown"
    task_dict = {}
    try:
        task_dict = json.loads(raw_json_bytes)
        task_id = task_dict.get("task_id", "unknown")

        payload_id = task_dict.get("text_payload_id")
        if payload_id:
            raw_text = redis_client.get(payload_id)
            if not raw_text:
                error_msg = "Payload expired or missing from Redis"
                handle_dlq(redis_client, task_dict, error_msg)

                error_res = MatchResult(
                    task_id=task_id,
                    engine_id=task_dict.get("engine_id", "unknown"),
                    success=False,
                    matches=[],
                    execution_time_ms=0.0,
                    error=error_msg
                )
                publish_result(redis_client, task_id, error_res)
                return

            task_dict["text"] = raw_text.decode('utf-8') if isinstance(raw_text, bytes) else raw_text

        req = MatchRequest.model_validate(task_dict)
        start_time = time.time()

        if len(req.text) > MAX_INPUT_SIZE:
            error_res = MatchResult(
                task_id=req.task_id,
                engine_id=req.engine_id,
                success=False,
                matches=[],
                execution_time_ms=0.0,
                error=f"Input text exceeds maximum allowed size of {MAX_INPUT_SIZE} bytes."
            )
            publish_result(redis_client, req.task_id, error_res)
            return

        engine_group = pool.acquire()
        try:
            engine = engine_group.get_engine(req.engine_id)

            if not engine:
                out = MatchResult(
                    task_id=req.task_id,
                    engine_id=req.engine_id,
                    success=False,
                    matches=[],
                    execution_time_ms=0.0,
                    error=f"Unknown engine target routed to C/C++ worker: {req.engine_id}"
                )
            else:
                parsed = engine.execute(req.regex, req.text, req.flags)
                exec_time = (time.time() - start_time) * 1000

                if parsed.get("success"):
                    matches = parsed.get("matches", [])
                    _normalize_match_offsets(matches, req.text)
                    out = MatchResult(
                        task_id=req.task_id,
                        engine_id=req.engine_id,
                        success=True,
                        matches=matches,
                        execution_time_ms=exec_time
                    )
                else:
                    out = MatchResult(
                        task_id=req.task_id,
                        engine_id=req.engine_id,
                        success=False,
                        matches=[],
                        execution_time_ms=exec_time,
                        error=parsed.get("error", "Unknown compilation error")
                    )

            publish_result(redis_client, req.task_id, out)
        finally:
            pool.release(engine_group)

    except Exception as e:
        error_msg = str(e)
        print(f"[Error] Task processing failure: {error_msg}", flush=True)
        handle_dlq(redis_client, task_dict, error_msg)

        if task_id != "unknown":
            err_out = MatchResult(
                task_id=task_id,
                engine_id=task_dict.get("engine_id", "unknown"),
                success=False,
                matches=[],
                execution_time_ms=0.0,
                error=f"Worker node internal error: {error_msg}"
            )
            publish_result(redis_client, task_id, err_out)


def listen_and_process(redis_client: redis.Redis):
    target_queues = ["queue:c-cpp", "queue:c_cpp", "queue:cpp", "queue:c"]
    print(f"[Worker] C/C++ worker listening on {target_queues}...", flush=True)

    num_cores = multiprocessing.cpu_count()
    pool_size = min(4, max(1, num_cores))
    pool = WorkerPool(size=pool_size)

    dispatch_threads = ThreadPoolExecutor(max_workers=pool_size * 2)

    while True:
        try:
            result = redis_client.brpop(target_queues, timeout=0)
            if not result:
                continue
            _, task_json_bytes = result
            dispatch_threads.submit(process_task, redis_client, task_json_bytes, pool)
        except Exception as e:
            print(f"[Error] Global loop failure: {e}", flush=True)
            time.sleep(1)