"""Redis connection helper. This is NOT the job queue abstraction
(that's T060) — just enough to let the worker skeleton connect and
report whether Redis is reachable."""

import logging

import redis

from workers.config import WorkerSettings

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT_SECONDS = 2


def get_redis_client(settings: WorkerSettings) -> redis.Redis:
    return redis.Redis.from_url(
        settings.redis_url, socket_connect_timeout=CONNECT_TIMEOUT_SECONDS
    )


def ping_redis(client: redis.Redis) -> bool:
    try:
        return bool(client.ping())
    except redis.exceptions.RedisError as exc:
        logger.warning("redis connection check failed", extra={"detail": str(exc)})
        return False
