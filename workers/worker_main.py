"""Worker entry point.

Connects to Redis, runs a placeholder loop, and shuts down cleanly on
SIGINT/SIGTERM. Does not consume real jobs yet — that's T060/T061.
"""

import logging
import signal
import socket
import threading
import uuid
from types import FrameType

from workers.config import WorkerSettings, get_worker_settings
from workers.observability.logging import configure_logging
from workers.queue import get_redis_client, ping_redis

logger = logging.getLogger(__name__)

LOOP_POLL_INTERVAL_SECONDS = 5.0


def resolve_worker_id(settings: WorkerSettings) -> str:
    if settings.worker_id:
        return settings.worker_id
    return f"{socket.gethostname()}-{uuid.uuid4().hex[:8]}"


def install_signal_handlers(stop_event: threading.Event) -> None:
    def _handle(signum: int, _frame: FrameType | None) -> None:
        logger.info("received shutdown signal", extra={"signal": signum})
        stop_event.set()

    # SIGTERM is only fully meaningful on POSIX; registering it on
    # Windows is harmless (it can still be raised in-process) but
    # Ctrl+C (SIGINT) is the primary local shutdown path there.
    signal.signal(signal.SIGINT, _handle)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handle)


def run(stop_event: threading.Event, settings: WorkerSettings, worker_id: str) -> None:
    logger.info("worker starting", extra={"worker_id": worker_id})

    client = get_redis_client(settings)
    if ping_redis(client):
        logger.info("redis connection healthy", extra={"worker_id": worker_id})
    else:
        logger.warning(
            "redis unavailable at startup; worker will keep idling and retry "
            "connectivity once real queue consumption is implemented (T060)",
            extra={"worker_id": worker_id},
        )

    while not stop_event.is_set():
        # Placeholder: real job consumption lands in T060/T061.
        stop_event.wait(timeout=LOOP_POLL_INTERVAL_SECONDS)

    logger.info("worker shutting down", extra={"worker_id": worker_id})


def main() -> None:
    settings = get_worker_settings()
    configure_logging(settings.log_level)
    worker_id = resolve_worker_id(settings)

    stop_event = threading.Event()
    install_signal_handlers(stop_event)

    run(stop_event, settings, worker_id)


if __name__ == "__main__":
    main()
