import os
import redis
from openregex_libs.lifecycle import start_heartbeat, install_shutdown_unregister
from worker_c_cpp.engines import WORKER_INFO
from worker_c_cpp.registry import register_engines
from worker_c_cpp.processor import listen_and_process


def main():
    redis_url = os.environ.get("REDIS_URL", "redis://redis:6379")
    redis_client = redis.Redis.from_url(redis_url, decode_responses=True)

    # Heartbeat must be live before registration so discovery never sees
    # a registered worker without one.
    start_heartbeat(redis_client, WORKER_INFO.worker_name)
    register_engines(redis_client)
    install_shutdown_unregister(redis_client, WORKER_INFO.worker_name)
    listen_and_process(redis_client)


if __name__ == "__main__":
    main()