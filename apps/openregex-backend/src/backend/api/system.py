from fastapi import APIRouter, Request
from backend.core.redis import redis_client
from backend.core.config import APP_RELEASE_DATE
from openregex_libs.models import WORKER_SCHEMA_VERSION

router = APIRouter(tags=["System"])

@router.get("/info")
async def get_info(request: Request):
    client_frontend_version = request.headers.get("X-Frontend-Version")
    if client_frontend_version:
        await redis_client.set("system:frontend_version", client_frontend_version)

    saved_frontend_version = await redis_client.get("system:frontend_version")

    return {
        "title": request.app.title,
        "version": request.app.version,
        "backend_version": request.app.version,
        "frontend_version": saved_frontend_version or "Unknown",
        "release_date": APP_RELEASE_DATE,
        "worker_schema_version": WORKER_SCHEMA_VERSION
    }

@router.get("/health")
async def get_health():
    try:
        await redis_client.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"

    return {
        "status": "healthy" if redis_status == "connected" else "degraded",
        "redis": redis_status
    }