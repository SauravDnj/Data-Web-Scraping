"""Redis connection helper (T015) + job queue abstraction (T060).

**Redis is coordination-only** (docs/16_MEMORY.md's queue decision,
docs/09_JOB_QUEUE_WORKER_DEEP.md): the ONLY payload this queue ever
carries is a job ID (item 8, "keep queue payload minimal"). Every
durable fact about a job — status, config, counters, error detail —
lives in MySQL (`app.repositories.jobs`, T032/T035/T055), never in
Redis. If Redis is lost or flushed entirely, no `Job` row is affected
(item 9); only in-flight *delivery* is lost, which is exactly the
failure mode the reliable-queue pattern below (and the heartbeat/
recovery sweep, T062/T065, not this task) exists to detect and correct
— a job stuck mid-delivery is still fully described in MySQL and can
always be re-enqueued from there.

**Reliable-queue pattern (items 5-6, acknowledgement + worker
failure)**: `dequeue()` atomically moves a job ID from the main queue
list into a separate "in-flight" list (`BLMOVE`, Redis's non-
deprecated successor to `BRPOPLPUSH`) rather than just popping it —
so if the worker that dequeued it crashes before calling
`acknowledge()`, the job ID is not silently lost; it sits visibly in
the in-flight list (`list_in_flight()`) until something calls
`requeue()` on it. This task provides the primitives; deciding *when*
to sweep stale in-flight entries automatically is T062/T065's
heartbeat/recovery job, not built here."""

import logging
from typing import Protocol, cast

import redis

from workers.config import WorkerSettings

logger = logging.getLogger(__name__)

CONNECT_TIMEOUT_SECONDS = 2

DEFAULT_QUEUE_KEY = "queue:jobs"
DEFAULT_IN_FLIGHT_KEY = "queue:jobs:in_flight"


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


class JobQueue(Protocol):
    """Item 1 — the generic interface, matching every repository
    Protocol this project has built (`app.repositories.*`). Any future
    caller (the worker's main loop, T061+) depends on this, never on
    `redis.Redis` directly."""

    def enqueue(self, job_id: int) -> None: ...

    def dequeue(self, *, timeout_seconds: float) -> int | None: ...

    def acknowledge(self, job_id: int) -> None: ...

    def requeue(self, job_id: int) -> None: ...

    def list_in_flight(self) -> list[int]: ...


class RedisJobQueue:
    """Item 2 — the real implementation. `client` is injectable
    (`redis.Redis` or `fakeredis.FakeRedis`, which is API-compatible —
    used in tests since no live Redis is available to verify against
    locally yet, T013) — same dependency-injection pattern as
    `GoogleMapsClient(http_client=...)`, T042."""

    def __init__(
        self,
        client: redis.Redis,
        *,
        queue_key: str = DEFAULT_QUEUE_KEY,
        in_flight_key: str = DEFAULT_IN_FLIGHT_KEY,
    ) -> None:
        self._client = client
        self._queue_key = queue_key
        self._in_flight_key = in_flight_key

    def enqueue(self, job_id: int) -> None:
        """Item 3. FIFO: `LPUSH` here pairs with `dequeue()`'s
        right-hand pop, so the first job enqueued is the first
        dequeued."""
        self._client.lpush(self._queue_key, str(job_id))

    def dequeue(self, *, timeout_seconds: float) -> int | None:
        """Item 4. Blocks up to `timeout_seconds` waiting for a job;
        `None` means the queue was empty for the whole wait, not an
        error. Atomically moves the job ID into the in-flight list
        rather than discarding it — see this module's docstring.

        redis-py's type stub declares `blmove`'s `timeout` as `int`,
        but the real Redis `BLMOVE` command accepts a fractional-
        second timeout — the stub is just overly strict here, not a
        real runtime constraint (verified directly against
        `fakeredis`, which implements the same command)."""
        result = self._client.blmove(
            self._queue_key,
            self._in_flight_key,
            timeout_seconds,  # type: ignore[arg-type]
            src="RIGHT",
            dest="LEFT",
        )
        if result is None:
            return None
        return int(cast(bytes | str, result))

    def acknowledge(self, job_id: int) -> None:
        """Item 5. Removes `job_id` from the in-flight list — the
        worker is done with it (successfully or not; a job the worker
        marked FAILED in MySQL is still "acknowledged" here, since
        Redis's job is delivery, not outcome tracking)."""
        self._client.lrem(self._in_flight_key, 0, str(job_id))

    def requeue(self, job_id: int) -> None:
        """Item 6. Moves `job_id` back from in-flight to the main
        queue for redelivery — the explicit primitive a recovery
        process (T062/T065) calls once it decides an in-flight job has
        been abandoned (e.g. a stale heartbeat)."""
        removed = cast(int, self._client.lrem(self._in_flight_key, 0, str(job_id)))
        if removed:
            self._client.lpush(self._queue_key, str(job_id))

    def list_in_flight(self) -> list[int]:
        """Diagnostic/testable surface for item 6 — what a recovery
        sweep would scan to find abandoned jobs."""
        raw_values = cast(
            list[bytes | str], self._client.lrange(self._in_flight_key, 0, -1)
        )
        return [int(value) for value in raw_values]
