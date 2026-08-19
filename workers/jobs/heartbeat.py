"""T062 — Worker heartbeat: keeping `JobRun.heartbeat_at` fresh during
a potentially long-running `collect()` call (items 1-2), and detecting
runs whose heartbeat fell silent (items 3-5) — the signal a future
recovery process (T065) uses to decide a run's worker has crashed and
the job needs requeuing (`workers.queue.RedisJobQueue.requeue()`,
T060, already has the primitive for that; deciding *when* to call it
automatically is T065's job, not built here — this module only
detects, it never acts)."""

import logging
from datetime import datetime, timedelta

from app.domain.jobs import JobRun
from app.repositories.jobs import JobRepository

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = timedelta(seconds=30)
# Several missed intervals' worth of tolerance before a run counts as
# stale — a single slow or delayed heartbeat write must never falsely
# trigger recovery of a genuinely healthy job (item 5).
STALE_THRESHOLD = timedelta(minutes=5)


class HeartbeatUpdater:
    """Item 1. `maybe_beat(current_time)` is interval-gated — cheap to
    call on every loop iteration of a long collection; it only
    actually writes to the database once `interval` has elapsed since
    the last real write. `current_time` is supplied by the caller at
    each call, never read internally (T062 item 6's own "tests with
    controlled time" instruction, same discipline as every other
    timestamp in this codebase) — a real caller would pass a genuinely
    advancing clock reading. `workers.jobs.execute_collection`'s
    current fake-provider-driven loop finishes fast enough that
    wiring a truly ticking clock into it isn't needed yet; that's
    deferred until a real, slow, multi-page provider call actually
    needs it — not invented speculatively here."""

    def __init__(
        self,
        job_repository: JobRepository,
        run_id: int,
        *,
        started_at: datetime,
        interval: timedelta = HEARTBEAT_INTERVAL,
    ) -> None:
        self._job_repository = job_repository
        self._run_id = run_id
        self._interval = interval
        self._last_beat = started_at

    def maybe_beat(self, current_time: datetime) -> bool:
        if current_time - self._last_beat < self._interval:
            return False
        try:
            self._job_repository.touch_heartbeat(
                self._run_id, heartbeat_at=current_time
            )
        except Exception:
            # Item 7: a heartbeat write failure must never crash the
            # job it's monitoring. The worst case of a missed beat is
            # this run looking stale a little early — safe, because
            # requeuing an already-finished job is harmless as long as
            # claiming stays idempotent (JobRepository.
            # claim_queued_job() only ever succeeds against a row
            # that's still QUEUED, T061).
            logger.warning(
                "heartbeat_update_failed",
                extra={"run_id": self._run_id},
                exc_info=True,
            )
            return False
        self._last_beat = current_time
        return True


def find_stale_job_runs(
    job_repository: JobRepository,
    *,
    now: datetime,
    stale_threshold: timedelta = STALE_THRESHOLD,
) -> list[JobRun]:
    """Items 3-5. A thin, named entry point — the actual query lives
    on `JobRepository.list_stale_running_runs()` (matching every other
    query in this codebase); this function is what a future recovery
    process (T065) imports and calls."""
    return job_repository.list_stale_running_runs(
        now=now, stale_threshold=stale_threshold
    )
