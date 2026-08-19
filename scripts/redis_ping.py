"""T013: minimal Redis connectivity check.

Confirms Redis is reachable and responds to PING before any queue code
is built on top of it. Redis is treated purely as transient
coordination (the job queue), never the system of record — MySQL is.

Usage (from apps/api's virtual environment, or any Python environment
with the `redis` package installed):

    python scripts/redis_ping.py

Reads REDIS_URL from the environment, falling back to the local
default from .env.example. No credentials are hardcoded here.
"""

import os
import sys

import redis

DEFAULT_REDIS_URL = "redis://localhost:6379/0"


def main() -> int:
    redis_url = os.environ.get("REDIS_URL", DEFAULT_REDIS_URL)
    client = redis.Redis.from_url(redis_url, socket_connect_timeout=3)

    try:
        if client.ping():
            print(f"OK: Redis responded to PING at {redis_url}")
            return 0
        print(f"FAIL: Redis did not respond to PING at {redis_url}")
        return 1
    except redis.exceptions.RedisError as exc:
        print(f"FAIL: could not connect to Redis at {redis_url}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
