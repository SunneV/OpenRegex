import os
import time

import redis
from openregex_libs.lifecycle import install_shutdown_unregister, start_heartbeat
from openregex_libs.runtime import WorkerRuntime

from worker_postgres.engine import execute, server_version
from worker_postgres.registry import WORKER_NAME, build_worker_info, register_engines

DB_STARTUP_TIMEOUT_S = int(os.environ.get("POSTGRES_STARTUP_TIMEOUT_S", 120))


def wait_for_server() -> str:
    """The database container may still be initialising when the worker starts."""
    deadline = time.time() + DB_STARTUP_TIMEOUT_S
    last_error = ""
    while time.time() < deadline:
        try:
            return server_version()
        except Exception as exc:
            last_error = str(exc).strip()
            time.sleep(2)
    raise RuntimeError(f"PostgreSQL did not become available in {DB_STARTUP_TIMEOUT_S}s: {last_error}")


def main() -> None:
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379")
    redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

    version = wait_for_server()
    print(f"[Worker] Connected to PostgreSQL {version}.", flush=True)

    # Heartbeat must be live before registration so discovery never sees
    # a registered worker without one.
    start_heartbeat(redis_client, WORKER_NAME)
    register_engines(redis_client, build_worker_info(version))
    install_shutdown_unregister(redis_client, WORKER_NAME)

    WorkerRuntime(redis_client, WORKER_NAME, execute).run()


if __name__ == "__main__":
    main()
