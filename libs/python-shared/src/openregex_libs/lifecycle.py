"""Worker registration lifecycle: TTL heartbeat and graceful unregister.

Reliability contract (schema >= 1.1 workers):
- the worker sets a TTL-guarded heartbeat key BEFORE registering, then
  refreshes it in the background for as long as it lives;
- on SIGTERM/SIGINT it removes its registration and heartbeat key;
- the backend treats a registered worker without a live heartbeat as dead
  and removes the stale registration (self-healing discovery).
"""

import signal
import sys
import threading
import time

WORKERS_HASH_KEY = "openregex:workers"
HEARTBEAT_KEY_PREFIX = "openregex:workers:heartbeat:"
HEARTBEAT_TTL_S = 15
HEARTBEAT_INTERVAL_S = 5


def start_heartbeat(redis_client, worker_name: str) -> threading.Thread:
    """Set the heartbeat immediately, then keep refreshing it in a daemon thread.

    Call this BEFORE registering the worker so discovery never observes a
    registration without a live heartbeat.
    """
    key = HEARTBEAT_KEY_PREFIX + worker_name
    redis_client.setex(key, HEARTBEAT_TTL_S, str(int(time.time())))

    def _beat():
        while True:
            time.sleep(HEARTBEAT_INTERVAL_S)
            try:
                redis_client.setex(key, HEARTBEAT_TTL_S, str(int(time.time())))
            except Exception:
                pass  # transient Redis outage; the TTL just expires until it recovers

    thread = threading.Thread(target=_beat, name=f"heartbeat-{worker_name}", daemon=True)
    thread.start()
    return thread


def unregister_worker(redis_client, worker_name: str) -> None:
    try:
        redis_client.hdel(WORKERS_HASH_KEY, worker_name)
        redis_client.delete(HEARTBEAT_KEY_PREFIX + worker_name)
    except Exception:
        pass


def install_shutdown_unregister(redis_client, worker_name: str) -> None:
    """Unregister on SIGTERM/SIGINT (docker stop, Ctrl+C)."""

    def _handler(_signum, _frame):
        unregister_worker(redis_client, worker_name)
        sys.exit(0)

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            signal.signal(sig, _handler)
        except (ValueError, OSError):
            pass  # not the main thread or unsupported platform
