"""Shared Redis queue runtime for Python-hosted workers.

Workers that drive an external runtime (a database server, a CLI tool) do not
need the multiprocessing pool that the in-process engines use - the guardrail
lives in the runtime itself (statement timeouts, subprocess kill). What they do
share is the queue contract: brpop, claim-check payload resolution, dead-letter
handling and the result envelope. That part lives here so every such worker
speaks it identically.

The engine callback receives a validated MatchRequest and returns a list of
MatchItem with offsets already expressed in Unicode code points
(worker schema 1.1). Raising an exception turns into a failed MatchResult.
"""

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, List

from .models import MatchItem, MatchRequest, MatchResult

TIMEOUT_MS = int(os.environ.get("WORKER_EXECUTION_TIMEOUT_MS", 1000))
MAX_INPUT_SIZE = int(os.environ.get("WORKER_MAX_INPUT_SIZE", 10485760))
MAX_MATCHES = int(os.environ.get("WORKER_MAX_MATCHES", 10000))
MAX_GROUPS = int(os.environ.get("WORKER_MAX_GROUPS", 1000))
MAX_JSON_SIZE = int(os.environ.get("WORKER_MAX_JSON_SIZE", 10485760))

# How long a single blocking poll waits. redis-py applies its own socket read
# timeout (5s by default in 8.x) to blocking commands, so this has to stay
# comfortably below it or every idle poll raises instead of returning nil.
QUEUE_POLL_TIMEOUT_S = int(os.environ.get("WORKER_QUEUE_POLL_TIMEOUT_S", 2))

EngineCallback = Callable[[MatchRequest], List[MatchItem]]


def queue_name(worker_name: str) -> str:
    """Backend routing derives the queue from the worker name; mirror it here."""
    return f"queue:{worker_name.removeprefix('worker-')}"


class WorkerRuntime:
    def __init__(self, redis_client: Any, worker_name: str, engine: EngineCallback,
                 concurrency: int = 4):
        self.redis = redis_client
        self.worker_name = worker_name
        self.engine = engine
        self.queue = queue_name(worker_name)
        self.dead_queue = f"{self.queue}:dead"
        self.concurrency = max(1, concurrency)

    # --- Redis plumbing -------------------------------------------------

    def _resolve_payload(self, task: dict) -> MatchRequest:
        payload_id = task.get("text_payload_id")
        if payload_id:
            raw = self.redis.get(payload_id)
            if not raw:
                raise ValueError("Payload expired or missing from Redis")
            task["text"] = raw.decode("utf-8") if isinstance(raw, bytes) else raw
        return MatchRequest.model_validate(task)

    def _handle_dlq(self, task: dict, error: str) -> None:
        try:
            task = dict(task)
            task["attempt_count"] = task.get("attempt_count", 0) + 1
            task["error_reason"] = error
            self.redis.lpush(self.dead_queue, json.dumps(task))
        except Exception:
            pass

    def _publish(self, task_id: str, result: MatchResult) -> None:
        result_json = result.model_dump_json()
        if len(result_json.encode("utf-8")) > MAX_JSON_SIZE:
            result = MatchResult(
                task_id=result.task_id,
                engine_id=result.engine_id,
                success=False,
                matches=[],
                execution_time_ms=result.execution_time_ms,
                error=f"Output JSON exceeds maximum allowed size of {MAX_JSON_SIZE} bytes.",
            )
            result_json = result.model_dump_json()
        try:
            with self.redis.pipeline() as pipe:
                pipe.setex(f"result:{task_id}", 60, result_json)
                pipe.publish(f"result:{task_id}", "ready")
                pipe.execute()
        except Exception as e:
            print(f"[Error] Failed to publish result to Redis pipeline: {e}", flush=True)

    # --- Task execution -------------------------------------------------

    def _process(self, raw_json: str) -> None:
        task: dict = {}
        try:
            task = json.loads(raw_json)
            req = self._resolve_payload(task)
        except Exception as e:
            error = str(e)
            print(f"[Error] Task processing failure: {error}", flush=True)
            self._handle_dlq(task, error)
            task_id = task.get("task_id")
            if task_id:
                self._publish(task_id, MatchResult(
                    task_id=task_id,
                    engine_id=task.get("engine_id", "unknown"),
                    success=False,
                    matches=[],
                    execution_time_ms=0.0,
                    error=error,
                ))
            return

        started = time.time()
        matches: List[MatchItem] = []
        error = None

        try:
            if len(req.text) > MAX_INPUT_SIZE:
                raise ValueError(f"Input text exceeds maximum allowed size of {MAX_INPUT_SIZE} bytes.")
            matches = self.engine(req)
        except Exception as e:
            error = str(e) or e.__class__.__name__
            self._handle_dlq(task, error)

        self._publish(req.task_id, MatchResult(
            task_id=req.task_id,
            engine_id=req.engine_id,
            success=error is None,
            matches=matches if error is None else [],
            execution_time_ms=(time.time() - started) * 1000,
            error=error,
        ))

    def run(self) -> None:
        print(f"[Worker] {self.worker_name} listening on '{self.queue}'...", flush=True)
        pool = ThreadPoolExecutor(max_workers=self.concurrency)

        while True:
            try:
                entry = self.redis.brpop(self.queue, timeout=QUEUE_POLL_TIMEOUT_S)
                if not entry:
                    continue
                pool.submit(self._process, entry[1])
            except Exception as e:
                # A socket read timeout on an idle poll is not a failure.
                if type(e).__name__ == "TimeoutError":
                    continue
                print(f"[Error] Global loop failure: {e}", flush=True)
                time.sleep(1)
