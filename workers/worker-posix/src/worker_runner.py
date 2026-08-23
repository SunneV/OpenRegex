import os

import redis
from openregex_libs.lifecycle import install_shutdown_unregister, start_heartbeat
from openregex_libs.runtime import WorkerRuntime

from worker_posix.engine import execute
from worker_posix.registry import WORKER_NAME, build_worker_info, register_engines


def main() -> None:
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379")
    redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

    # Heartbeat must be live before registration so discovery never sees
    # a registered worker without one.
    start_heartbeat(redis_client, WORKER_NAME)
    register_engines(redis_client, build_worker_info())
    install_shutdown_unregister(redis_client, WORKER_NAME)

    WorkerRuntime(redis_client, WORKER_NAME, execute).run()


if __name__ == "__main__":
    main()
