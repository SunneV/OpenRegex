import json
import uuid
import asyncio
from fastapi import APIRouter, HTTPException, Request
from openregex_libs.models import MatchRequest, MatchResult, WorkerInfo
from backend.core.redis import redis_client, check_rate_limit
from backend.core.config import API_REGEX_ENDPOINT_ENABLE, PAYLOAD_THRESHOLD, RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW

router = APIRouter(tags=["Execution"], include_in_schema=API_REGEX_ENDPOINT_ENABLE)

@router.post("/match", response_model=MatchResult)
async def match_regex(request: MatchRequest, fastapi_req: Request):
    client_ip = fastapi_req.client.host or "unknown"

    if not await check_rate_limit(client_ip, request.engine_id):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {request.engine_id}. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_WINDOW}s."
        )

    if not request.task_id:
        request.task_id = str(uuid.uuid4())

    workers_data = await redis_client.hgetall("openregex:workers")
    target_worker_name = None
    for worker_json in workers_data.values():
        worker = WorkerInfo.model_validate_json(worker_json)
        for engine in worker.engines:
            if engine.engine_id == request.engine_id:
                target_worker_name = worker.worker_name
                break
        if target_worker_name:
            break

    if not target_worker_name:
        raise HTTPException(status_code=404, detail=f"Engine '{request.engine_id}' not found or no worker available.")

    queue_name = f"queue:{target_worker_name.replace('worker-', '')}"

    request_dict = request.model_dump()
    if len(request.text) > PAYLOAD_THRESHOLD:
        payload_id = f"payload:{uuid.uuid4()}"
        await redis_client.setex(payload_id, 60, request.text)
        request_dict["text"] = ""
        request_dict["text_payload_id"] = payload_id

    task_json = json.dumps(request_dict)

    pubsub = redis_client.pubsub()
    channel_name = f"result:{request.task_id}"

    try:
        await pubsub.subscribe(channel_name)
        await redis_client.lpush(queue_name, task_json)

        async with asyncio.timeout(5.0):
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"]
                    if data == "ready":
                        result_data = await redis_client.get(f"result:{request.task_id}")
                        if result_data:
                            return MatchResult.model_validate_json(result_data)
                    else:
                        # Fallback for workers not yet using the SETEX pattern
                        return MatchResult.model_validate_json(data)
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Backend Timeout: Worker failed to respond within 5000ms.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # A pubsub object holds a connection checked out of the pool for the
        # whole request. Unsubscribing does not give it back - only closing
        # does - so without this the pool ran dry after a few hundred matches
        # and every further request failed with "Too many connections".
        await pubsub.aclose()