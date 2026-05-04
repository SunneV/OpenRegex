import json
import time
import uuid
import threading
import redis
from typing import List
from openregex_libs.models import MatchRequest, MatchResult, WorkerInfo


class RedisBroker:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self._workers_cache = {}
        self._workers_cache_time = 0

    def _get_workers(self) -> dict:
        now = time.time()
        if now - self._workers_cache_time > 15:
            self._workers_cache = self.redis.hgetall("openregex:workers")
            self._workers_cache_time = now
        return self._workers_cache

    def start_heartbeat(self, version: str, release_date: str) -> None:
        def heartbeat():
            payload = json.dumps({"version": version, "release_date": release_date})
            while True:
                self.redis.setex("openregex:llm_active", 15, payload)
                time.sleep(5)

        threading.Thread(target=heartbeat, daemon=True).start()

    def is_client_connected(self, task_id: str) -> bool:
        channel_name = f"result:llm:{task_id}"
        subs = self.redis.pubsub_numsub(channel_name)
        return bool(subs and subs[0][1] > 0)

    def emit(self, task_id: str, msg_type: str, data: dict) -> None:
        payload = json.dumps({"type": msg_type, **data})
        if msg_type in ("result", "error"):
            self.redis.setex(f"result:llm:{task_id}", 60, payload)
            self.redis.publish(f"result:llm:{task_id}", "ready")
        else:
            self.redis.publish(f"result:llm:{task_id}", payload)

    def resolve_text_payload(self, task_dict: dict) -> str:
        text = task_dict.get("text", "")
        payload_id = task_dict.get("text_payload_id")
        if not text and payload_id:
            cached_text = self.redis.get(payload_id)
            if cached_text:
                return cached_text
        return text

    def get_engine_context(self, engine_id: str) -> str:
        try:
            workers_data = self._get_workers()
            target_engine = None
            for worker_json in workers_data.values():
                worker = WorkerInfo.model_validate_json(worker_json)
                for engine in worker.engines:
                    if engine.engine_id == engine_id:
                        target_engine = engine
                        break
                if target_engine:
                    break

            if not target_engine:
                return f"Technical Engine ID: {engine_id}"

            context_parts = [
                f"Engine: {target_engine.engine_label} (Library Version: {target_engine.engine_regex_lib_version})"
            ]

            capabilities = target_engine.engine_capabilities
            if capabilities:
                flags = [flag.name for flag in capabilities.flags]
                supports_lookaround = capabilities.supports_lookaround
                supports_backrefs = capabilities.supports_backrefs
                context_parts.append(
                    f"Capabilities - Flags: {', '.join(flags) if flags else 'None'}, "
                    f"Supports Lookaround: {supports_lookaround}, "
                    f"Supports Backreferences: {supports_backrefs}"
                )

            docs = target_engine.engine_docs
            if docs and docs.trivia:
                context_parts.append("Engine Specifics & Limitations:")
                for t in docs.trivia:
                    context_parts.append(f"- {t}")

            if target_engine.engine_cheat_sheet:
                context_parts.append("\nEngine Cheat Sheet (Supported Syntax):")
                for category in target_engine.engine_cheat_sheet:
                    context_parts.append(f"[{category.category}]")
                    for item in category.items:
                        context_parts.append(f"  - {item.character} : {item.description}")

            return "\n".join(context_parts)
        except Exception:
            return f"Technical Engine ID: {engine_id}"

    def test_regex_against_engine(self, engine_id: str, regex: str, text: str, flags: List[str] = None) -> MatchResult:
        task_id = str(uuid.uuid4())
        req = MatchRequest(task_id=task_id, engine_id=engine_id, regex=regex, text=text, flags=flags or [])

        workers_data = self._get_workers()
        target_worker_name = None
        for worker_json in workers_data.values():
            worker = WorkerInfo.model_validate_json(worker_json)
            for engine in worker.engines:
                if engine.engine_id == engine_id:
                    target_worker_name = worker.worker_name
                    break
            if target_worker_name:
                break

        if not target_worker_name:
            return MatchResult(task_id=task_id, engine_id=engine_id, success=False, execution_time_ms=0,
                               error=f"No worker available for engine '{engine_id}'")

        queue_name = f"queue:{target_worker_name.replace('worker-', '')}"

        request_dict = req.model_dump()
        if len(req.text) > 1024:
            payload_id = f"payload:{uuid.uuid4()}"
            self.redis.setex(payload_id, 60, req.text)
            request_dict["text"] = ""
            request_dict["text_payload_id"] = payload_id

        pubsub = self.redis.pubsub()
        channel_name = f"result:{task_id}"
        pubsub.subscribe(channel_name)

        self.redis.lpush(queue_name, json.dumps(request_dict))

        start_time = time.time()
        while time.time() - start_time < 5.0:
            message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                data = message["data"]
                if data == "ready":
                    result_data = self.redis.get(f"result:{task_id}")
                    if result_data:
                        pubsub.unsubscribe(channel_name)
                        return MatchResult.model_validate_json(result_data)
                else:
                    pubsub.unsubscribe(channel_name)
                    return MatchResult.model_validate_json(data)

        pubsub.unsubscribe(channel_name)
        return MatchResult(task_id=task_id, engine_id=engine_id, success=False, execution_time_ms=5000,
                           error="Timeout testing regex")
