import logging

from fastapi import APIRouter, HTTPException
from backend.core.redis import redis_client
from backend.core.config import API_REGEX_ENDPOINT_ENABLE
from openregex_libs.models import WorkerInfo, EngineInfo, WORKER_SCHEMA_VERSION
from openregex_libs.lifecycle import WORKERS_HASH_KEY, HEARTBEAT_KEY_PREFIX

router = APIRouter(tags=["Discovery"], include_in_schema=API_REGEX_ENDPOINT_ENABLE)

logger = logging.getLogger("backend.discovery")

# Mismatches already reported, so each worker/version pair is logged once.
_reported_schema_mismatches: set[tuple[str, str]] = set()


def _check_schema_version(worker: WorkerInfo) -> None:
    if worker.worker_schema_version == WORKER_SCHEMA_VERSION:
        return
    key = (worker.worker_name, worker.worker_schema_version)
    if key not in _reported_schema_mismatches:
        _reported_schema_mismatches.add(key)
        logger.warning(
            "Worker '%s' registered with communication schema %s, backend expects %s. "
            "Match offsets from this worker may be inconsistent - update the worker image.",
            worker.worker_name, worker.worker_schema_version, WORKER_SCHEMA_VERSION,
        )


async def _load_live_workers() -> list[WorkerInfo]:
    workers_data = await redis_client.hgetall(WORKERS_HASH_KEY)
    workers = []
    for name, worker_json in workers_data.items():
        worker = WorkerInfo.model_validate_json(worker_json)
        _check_schema_version(worker)

        # Workers on schema >= 1.1 maintain a TTL heartbeat; a registration
        # without one belongs to a dead worker, so drop it (self-healing).
        # Legacy 1.0 workers never set heartbeats and keep the old behavior.
        if worker.worker_schema_version != "1.0":
            alive = await redis_client.exists(HEARTBEAT_KEY_PREFIX + worker.worker_name)
            if not alive:
                await redis_client.hdel(WORKERS_HASH_KEY, name)
                logger.info("Removed stale registration for worker '%s' (no heartbeat).",
                            worker.worker_name)
                continue

        workers.append(worker)
    return workers


@router.get("/engines", response_model=list[WorkerInfo])
async def get_engines():
    return await _load_live_workers()

@router.get("/engines/{engine_id}", response_model=EngineInfo)
async def get_single_engine(engine_id: str):
    for worker in await _load_live_workers():
        for engine in worker.engines:
            if engine.engine_id == engine_id:
                return engine
    raise HTTPException(status_code=404, detail=f"Engine '{engine_id}' not found.")