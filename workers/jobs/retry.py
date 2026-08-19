"""T063 — Retry system: bounded, classified retry for a job whose
worker execution (T061) ended in a retryable failure.

**Builds on already-established architecture rather than inventing a
parallel one**: `FAILED` is a terminal `Job` status (T031's state
machine has no outgoing transition from it) — "a job that needs to
run again is a NEW `Job` row, not a resurrection of the old one"
(`app/services/jobs.py`'s `retry_job()`, T035, already builds exactly
this and already gates on `is_retryable(original.error_code)`,
reconciled with `ProviderErrorCategory` at T044). T063 does not
reinvent that decision — it adds the missing pieces around it: a
bounded attempt count (T035's `retry_job()` had none — an unbounded
"retry indefinitely" gap this closes) and the worker-side wiring to
actually enqueue the new job.

**Max attempts, without a schema change**: there is no
`original_job_id` column on `Job` — retry lineage is only recorded in
the audit trail (`retry_job()`'s `JOB_RETRIED` event, T037, which
already stores `original_job_id` in its `details`).
`count_retry_chain_length()` walks that trail backward to count how
many times this lineage has already been retried, reusing existing
audit infrastructure rather than adding a migration for one counter.

**Backoff is defined and tested, not yet enforced as real delayed
delivery** — `RedisJobQueue` (T060) is a plain FIFO list with no
delayed-delivery primitive, and no task before this one built one.
`compute_backoff_delay()` is a correct, pure, tested function a future
scheduler (a natural fit alongside T083) can use once real delayed
delivery exists; today, an eligible retry is enqueued immediately.
This is a deliberate, documented scope boundary, not an oversight —
the literal acceptance criterion ("retryable failures recover within
configured limits; permanent failures stop") holds either way, since
it concerns *whether* a bounded retry happens, not its exact timing.
Combined with the hard `max_attempts` ceiling, this is what "prevent
retry storms" means within what this codebase's current queue
infrastructure can actually enforce — an unbounded instant-retry loop
is impossible because attempts are capped, even without delay."""

import logging
import random
from dataclasses import dataclass
from datetime import timedelta

from app.domain.audit_actions import AuditAction
from app.domain.job_errors import is_retryable
from app.domain.jobs import Job
from app.repositories.audit import AuditLogRepository
from app.repositories.jobs import JobRepository
from app.repositories.projects import ProjectRepository
from app.services.jobs import JobService

from workers.queue import JobQueue

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 3  # item 1
    base_delay: timedelta = timedelta(seconds=5)  # item 2
    backoff_multiplier: float = 4.0  # item 2 — ~5s, 20s, 80s across 3 attempts
    jitter_fraction: float = 0.2  # item 3 — +/-20%, spreads simultaneous retries out


DEFAULT_RETRY_POLICY = RetryPolicy()


def should_retry(
    *, retryable: bool, attempt: int, policy: RetryPolicy = DEFAULT_RETRY_POLICY
) -> bool:
    """Item 4 (classification, via the caller-supplied `retryable`
    flag) combined with item 1 (the attempt ceiling) — DO NOT list:
    never retry a non-retryable error, never exceed `max_attempts`.
    Both enforced here, in one place, so neither can be forgotten at a
    call site."""
    if not retryable:
        return False
    return attempt < policy.max_attempts


def compute_backoff_delay(
    attempt: int,
    policy: RetryPolicy = DEFAULT_RETRY_POLICY,
    *,
    random_fraction: float | None = None,
) -> timedelta:
    """Items 2-3. Exponential: `base_delay * multiplier^(attempt-1)`,
    jittered by up to `jitter_fraction` in either direction.
    `random_fraction` (expected in `[-1.0, 1.0]`) is caller-injectable
    for deterministic tests; a real caller omits it and a fresh
    `random.uniform()` draw is used."""
    base_seconds = policy.base_delay.total_seconds() * (
        policy.backoff_multiplier ** max(0, attempt - 1)
    )
    fraction = random.uniform(-1.0, 1.0) if random_fraction is None else random_fraction
    jittered_seconds = base_seconds + base_seconds * policy.jitter_fraction * fraction
    return timedelta(seconds=max(0.0, jittered_seconds))


def count_retry_chain_length(audit_repository: AuditLogRepository, job_id: int) -> int:
    """How many times this job's lineage has already been retried —
    `job_id` itself is the current end of the chain; walking backward
    through `JOB_RETRIED` events counts how many hops lead to it. `0`
    for a job that has never been retried (the original)."""
    count = 0
    current_id = job_id
    while True:
        events = audit_repository.list_for_entity("job", current_id)
        retried_event = next(
            (
                event
                for event in events.items
                if event.action == AuditAction.JOB_RETRIED
            ),
            None,
        )
        if retried_event is None:
            return count
        count += 1
        current_id = retried_event.details["original_job_id"]


def retry_failed_job(
    job_id: int,
    *,
    job_repository: JobRepository,
    project_repository: ProjectRepository,
    audit_repository: AuditLogRepository,
    job_service: JobService,
    queue: JobQueue,
    policy: RetryPolicy = DEFAULT_RETRY_POLICY,
) -> Job | None:
    """Items 5-7. Returns the newly created, already-queued `Job` if a
    retry was started, or `None` if this is a permanent failure —
    nothing more to do; the original `Job`'s `FAILED` status (set by
    T061's `finalize_job()`) stands as final."""
    job = job_repository.get(job_id)
    if job is None:
        raise LookupError(f"Job {job_id} does not exist.")

    attempt = count_retry_chain_length(audit_repository, job_id)
    retryable = is_retryable(job.error_code)

    if not should_retry(retryable=retryable, attempt=attempt, policy=policy):
        logger.info(
            "job_retry_not_eligible",
            extra={
                "job_id": job_id,
                "attempt": attempt,
                "retryable": retryable,
                "error_code": job.error_code,
            },
        )
        return None

    project = project_repository.get(job.project_id)
    if project is None:
        raise LookupError(f"Project {job.project_id} does not exist.")

    new_job = job_service.retry_job(job_id, requesting_user_id=project.user_id)
    assert new_job.id is not None  # always set for a freshly persisted Job
    queue.enqueue(new_job.id)
    logger.info(
        "job_retry_started",
        extra={
            "original_job_id": job_id,
            "new_job_id": new_job.id,
            "attempt": attempt + 1,
        },
    )
    return new_job
