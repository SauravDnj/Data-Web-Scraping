"""T065 — Worker recovery: closing out job runs a crashed worker
abandoned, without corrupting or duplicating anything.

**Builds directly on T062 (detection) and T063 (bounded retry) rather
than inventing parallel machinery**: `workers.jobs.heartbeat.
find_stale_job_runs()` is the detector (already existed, unused by any
caller until now); `workers.jobs.retry.retry_failed_job()` is the
requeue/exhaust decision (already existed, already enforces
`max_attempts` via `count_retry_chain_length()`). This module's only
new work is (1) safely reclaiming a stale `JobRun` and (2) closing its
`Job` out as a genuine `FAILED` outcome so `retry_failed_job()` has
something legal to act on — `retry_job()` (T035) only accepts a
`FAILED` job, and a crashed worker's job is still sitting at `RUNNING`
until something says otherwise.

**Item 6, "ensure only one active execution owner exists" — the real
distributed-systems question this task poses**: heartbeat-based
liveness (T062) has an inherent, well-known false-positive risk — a
worker that is merely slow (GC pause, thread contention, a genuinely
slow provider page) rather than actually dead can still be judged
stale. This codebase has no distributed lock manager or fencing-token
protocol (out of scope for every task through T065; Redis is
coordination-only, per docs/16_MEMORY.md's "Queue decision"), so this
module cannot make that false-positive structurally impossible. What
it does instead, deliberately:

1.  `JobRepository.close_stale_run()` re-verifies staleness with the
    exact same atomic conditional `UPDATE ... WHERE status='running'
    AND heartbeat_at < stale_before` shape as `claim_queued_job()`
    (T061) and `request_cancellation()` (T064) — a run whose worker
    wrote a fresh heartbeat between listing and reclaiming is left
    alone, and two concurrent recovery passes can never both "win" the
    same run.
2.  `JobRepository.finalize_job()`'s own `transition()` call
    (`app.domain.job_state_machine`) is the second, independent guard:
    if the "dead" worker was actually still alive and finished
    normally microseconds after its run was reclaimed, its own
    `finalize_job()` call already landed a real terminal status first
    or will hit `InvalidJobTransition` — either way this module treats
    that as "someone else already decided this job's outcome," logs
    it, and does not override it.
3.  A retry always creates a **new** `Job` row (T035's unchanged
    design) rather than reusing the crashed job's id, so even in the
    worst case — a zombie worker's writes landing after recovery has
    already retried the job — there is no shared mutable counter for
    the two executions to corrupt together; they'd be writing to two
    different `Job.counters`. Any duplicate *record* that scenario
    could still produce collapses back into one row anyway, because
    persistence (T053/T054) already dedupes by `canonical_key` within
    a project — a place collected twice under two different job ids
    updates the same record, it does not create a second one.

This is a bounded, honest "good enough with the tools this codebase
actually has" answer, not a claim of perfect exactly-once execution —
recorded here explicitly, the same way T063 documented its
un-enforced backoff delay as a deliberate scope boundary rather than
silently pretending the gap doesn't exist.

**Still not wired into a real, continuously-running loop** — same as
`process_next_job()` itself (T061): `workers/worker_main.py`'s main
loop is still T015's placeholder and has never called either function
from any task T061-T065. No task prompt through T065 asks for that
wiring explicitly; docs/00_TASK_INDEX.md's T091 ("Reliability
review... test worker crash") is the first task that reads as
depending on a real running loop existing. Flagged here rather than
built speculatively, matching T042/T041's own "no route/caller wires
this up yet" precedent."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.domain.audit_actions import AuditAction
from app.domain.job_errors import WORKER_CRASHED_ERROR_CODE
from app.domain.job_state_machine import InvalidJobTransition
from app.domain.jobs import JobStatus
from app.repositories.audit import AuditLogRepository
from app.repositories.jobs import JobRepository
from app.repositories.projects import ProjectRepository
from app.services.audit import AuditService
from app.services.jobs import JobService

from workers.jobs.heartbeat import STALE_THRESHOLD, find_stale_job_runs
from workers.jobs.retry import DEFAULT_RETRY_POLICY, RetryPolicy, retry_failed_job
from workers.queue import JobQueue

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RecoveryOutcome:
    job_id: int
    run_id: int
    requeued_job_id: int | None  # None: not retryable, exhausted, or job
    # already finalized by something else before recovery reached it.


def recover_stale_job_runs(
    *,
    job_repository: JobRepository,
    project_repository: ProjectRepository,
    audit_repository: AuditLogRepository,
    audit_service: AuditService,
    job_service: JobService,
    queue: JobQueue,
    now: datetime,
    stale_threshold: timedelta = STALE_THRESHOLD,
    retry_policy: RetryPolicy = DEFAULT_RETRY_POLICY,
) -> list[RecoveryOutcome]:
    """Items 1-5, one full sweep. `now`/`stale_threshold` are supplied
    by the caller, never read internally — same injected-time
    discipline as every other timestamp in this codebase (T038's
    `as_naive_utc` lesson, T062's own controlled-time tests). A real
    caller runs this periodically (see the module docstring's "not yet
    wired into a loop" note); tests call it once with a fixed `now`."""
    stale_before = now - stale_threshold
    stale_runs = find_stale_job_runs(
        job_repository, now=now, stale_threshold=stale_threshold
    )

    outcomes: list[RecoveryOutcome] = []
    for run in stale_runs:
        assert run.id is not None  # always set for a persisted JobRun
        outcome = _recover_one_run(
            run.id,
            run.job_id,
            job_repository=job_repository,
            project_repository=project_repository,
            audit_repository=audit_repository,
            audit_service=audit_service,
            job_service=job_service,
            queue=queue,
            now=now,
            stale_before=stale_before,
            retry_policy=retry_policy,
        )
        if outcome is not None:
            outcomes.append(outcome)
    return outcomes


def _recover_one_run(
    run_id: int,
    job_id: int,
    *,
    job_repository: JobRepository,
    project_repository: ProjectRepository,
    audit_repository: AuditLogRepository,
    audit_service: AuditService,
    job_service: JobService,
    queue: JobQueue,
    now: datetime,
    stale_before: datetime,
    retry_policy: RetryPolicy,
) -> RecoveryOutcome | None:
    # Item 6 — re-verified staleness, single winner. See module
    # docstring point 1.
    closed_run = job_repository.close_stale_run(
        run_id, stale_before=stale_before, finished_at=now
    )
    if closed_run is None:
        logger.info(
            "job_recovery_run_no_longer_stale_or_already_claimed",
            extra={"run_id": run_id, "job_id": job_id},
        )
        return None

    try:
        job = job_repository.finalize_job(
            job_id,
            status=JobStatus.FAILED,
            finished_at=now,
            error_code=WORKER_CRASHED_ERROR_CODE,
            error_message=(
                f"Worker heartbeat lost for job run {run_id}; "
                "reclaimed by the recovery process."
            ),
        )
    except InvalidJobTransition:
        # Module docstring point 2 — something else already decided
        # this job's real outcome; the orphaned run is closed either
        # way, nothing more to do here.
        logger.info(
            "job_recovery_run_closed_job_already_finalized",
            extra={"run_id": run_id, "job_id": job_id},
        )
        return RecoveryOutcome(job_id=job_id, run_id=run_id, requeued_job_id=None)

    audit_service.record_event(
        actor_user_id=None,  # a system process, not a human actor
        action=AuditAction.JOB_RECOVERED,
        entity_type="job",
        entity_id=job_id,
        details={"run_id": run_id, "error_code": WORKER_CRASHED_ERROR_CODE},
    )

    # Items 2-5: retryability, bounded attempt count, requeue-or-stay-
    # failed — all already built at T063, reused rather than
    # reimplemented.
    new_job = retry_failed_job(
        job_id,
        job_repository=job_repository,
        project_repository=project_repository,
        audit_repository=audit_repository,
        job_service=job_service,
        queue=queue,
        policy=retry_policy,
    )
    logger.info(
        "job_recovery_completed",
        extra={
            "job_id": job.id,
            "run_id": run_id,
            "requeued_job_id": new_job.id if new_job is not None else None,
        },
    )
    return RecoveryOutcome(
        job_id=job_id,
        run_id=run_id,
        requeued_job_id=new_job.id if new_job is not None else None,
    )
