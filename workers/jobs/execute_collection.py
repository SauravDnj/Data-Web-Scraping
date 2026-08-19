"""T061 — Worker job execution, "the first major vertical slice."
`process_next_job()` composes every piece built T038-T060 into the
full dequeue-to-acknowledge workflow for exactly one job. Uses only
the generic `ProviderAdapter` interface (T040) — no Google-specific
import anywhere in this module, so this exact function works against
the fake provider (this task's own acceptance test,
`tests/unit/fakes.FakeProviderAdapter`) or a real Google-backed
adapter (`app.providers.google_maps.provider.GoogleMapsProvider`,
T041-T045) interchangeably. `field_rules`/`provider_operation` are
supplied by the caller for exactly this reason — the Google-specific
values (`GOOGLE_FIELD_RULES`, `GOOGLE_MAPS_TEXT_SEARCH_OPERATION`) live
in `app.providers.google_maps.mapper`, not here.

Updated at T062 to wire in `workers.jobs.heartbeat.HeartbeatUpdater`
(item 5, "start heartbeat" — was previously just the `JobRun.
heartbeat_at` column default with no periodic refresh during
execution).

Maps directly onto T061's 17 IMPLEMENT items, in the order they run:

1.  Dequeue job ID — `queue.dequeue()` (T060).
2.  Atomically claim the queued job —
    `JobRepository.claim_queued_job()` (new here — a real conditional
    `UPDATE`, not the ORM get-then-mutate race `update_status()` has).
3.  Create a `JobRun` — `JobRepository.create_run()` (T024/T032).
4.  Update status to running — part of `claim_queued_job()`'s single
    atomic `UPDATE` (not a separate step).
5.  Start heartbeat — `JobRun.heartbeat_at`'s own column default
    (T024), refreshed periodically during the loop below via
    `workers.jobs.heartbeat.HeartbeatUpdater` (T062).
6.  Load the exact configuration version pinned to this job —
    `CollectionConfigRepository.get(job.config_id)` (T024 already
    pins a specific version, not "whatever's active now").
7.  Validate that configuration — `ProviderAdapter.validate_config()`.
8.  Call the provider adapter — `ProviderAdapter.collect()`.
9.  Normalize items — `ProviderAdapter.normalize()`, then this module
    attaches job/project context itself (`RecordDraft` has no
    provider-specific "map to draft" convenience at the generic
    Protocol level — only Google's mapper has one, T043).
10. Validate items — `app.pipeline.validate.validate_record_draft()`
    (T051); a `REJECTED` record never proceeds to persistence.
11-12. Deduplicate + persist transactionally —
    `app.pipeline.persist.persist_batch()` (T054), which already
    composes T053's dedup logic internally.
13. Update metrics — `app.pipeline.metrics.compute_job_counters()` +
    `JobRepository.update_counters()` (T055).
14-15. Finalize status + record errors —
    `JobRepository.finalize_job()` (new here — combines both in one
    write, so a status can never show FAILED with no error detail
    yet, or vice versa).
16. Stop heartbeat — `JobRepository.finish_run()` (new here — a
    bookend, not continuous polling).
17. Acknowledge the queue message — `queue.acknowledge()` (T060),
    always, in a `finally` block — a job the worker marked FAILED in
    MySQL is still "acknowledged" in Redis; Redis's job is delivery,
    not outcome tracking (`workers/queue.py`'s own docstring).

**Job-level status decision, a design decision this task had to
make**: `total_units == 0` or `failed_units == 0` → `COMPLETED`;
`failed_units > 0` and `successful_units == 0` → `FAILED` (nothing
survived); otherwise → `PARTIALLY_COMPLETED` — matching
docs/08_DATA_PIPELINE_DEEP.md's own worked example exactly ("300
successful, 150 skipped, 50 failed → partially_completed"). Per-record
failure reasons live on the individual `ValidationResult`/
`PersistOutcome` objects, not condensed into `Job.error_code` — that
field is reserved for a *whole-job* failure reason (config missing,
config invalid, `collect()` itself raised), where a single
`ProviderError` genuinely describes the entire failure."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from app.domain.jobs import Job, JobRun, JobRunStatus, JobStatus
from app.domain.provider_contracts import ProviderError, ProviderErrorCategory
from app.domain.records import RecordDraft
from app.pipeline.metrics import compute_job_counters
from app.pipeline.persist import persist_batch
from app.pipeline.validate import FieldRule, RecordQuality, ValidationResult
from app.pipeline.validate import validate_record_draft as validate_draft
from app.providers.base import ProviderAdapter
from app.repositories.configs import CollectionConfigRepository
from app.repositories.jobs import JobRepository
from app.repositories.records import RecordRepository
from sqlalchemy.orm import Session

from workers.jobs.heartbeat import HeartbeatUpdater
from workers.queue import JobQueue


@dataclass(frozen=True)
class JobExecutionOutcome:
    job_id: int
    claimed: bool
    status: JobStatus | None = None  # None when claimed=False


def process_next_job(
    session: Session,
    queue: JobQueue,
    provider: ProviderAdapter,
    job_repository: JobRepository,
    config_repository: CollectionConfigRepository,
    record_repository: RecordRepository,
    *,
    field_rules: Mapping[str, FieldRule],
    provider_operation: str,
    worker_id: str,
    now: datetime,
    dequeue_timeout_seconds: float = 5.0,
) -> JobExecutionOutcome | None:
    """`now` is caller-supplied (a real caller passes
    `datetime.now(UTC)`) rather than read internally — same
    deterministic-injected-time principle as every `RecordDraft.
    collected_at` in this pipeline; nothing in `app.pipeline`/this
    module ever calls `datetime.now()` itself. Returns `None` only
    when the queue had nothing to dequeue within the timeout — every
    other outcome (including "claimed by another worker") returns a
    real `JobExecutionOutcome`."""
    job_id = queue.dequeue(timeout_seconds=dequeue_timeout_seconds)
    if job_id is None:
        return None

    try:
        job = job_repository.claim_queued_job(job_id, started_at=now)
        if job is None:
            return JobExecutionOutcome(job_id=job_id, claimed=False)

        run = job_repository.create_run(
            JobRun(
                id=None,
                job_id=job_id,
                worker_id=worker_id,
                status=JobRunStatus.RUNNING,
                attempt=len(job_repository.list_runs_for_job(job_id)) + 1,
            )
        )
        assert run.id is not None
        heartbeat = HeartbeatUpdater(job_repository, run.id, started_at=now)

        status, error = _execute(
            job,
            session,
            provider,
            job_repository,
            config_repository,
            record_repository,
            heartbeat=heartbeat,
            field_rules=field_rules,
            provider_operation=provider_operation,
            now=now,
        )

        job_repository.finalize_job(
            job_id,
            status=status,
            finished_at=now,
            error_code=error.category.value if error is not None else None,
            error_message=error.message if error is not None else None,
        )
        job_repository.finish_run(
            run.id,
            status=(
                JobRunStatus.FAILED
                if status == JobStatus.FAILED
                else JobRunStatus.COMPLETED
            ),
            finished_at=now,
        )

        return JobExecutionOutcome(job_id=job_id, claimed=True, status=status)
    finally:
        queue.acknowledge(job_id)


def _execute(
    job: Job,
    session: Session,
    provider: ProviderAdapter,
    job_repository: JobRepository,
    config_repository: CollectionConfigRepository,
    record_repository: RecordRepository,
    *,
    heartbeat: HeartbeatUpdater,
    field_rules: Mapping[str, FieldRule],
    provider_operation: str,
    now: datetime,
) -> tuple[JobStatus, ProviderError | None]:
    config = config_repository.get(job.config_id)
    if config is None:
        return JobStatus.FAILED, ProviderError(
            category=ProviderErrorCategory.PERMANENT,
            message=f"CollectionConfig {job.config_id} no longer exists.",
            retryable=False,
        )

    validation = provider.validate_config(config.config)
    if not validation.is_valid:
        return JobStatus.FAILED, ProviderError(
            category=ProviderErrorCategory.INVALID_REQUEST,
            message="; ".join(validation.errors) or "Configuration is invalid.",
            retryable=False,
        )

    try:
        raw_items = list(provider.collect(config.config))
    except Exception as exc:  # noqa: BLE001 - deliberately broad: any
        # collection failure must be classified, never leaked as a
        # raw traceback out of the worker loop.
        return JobStatus.FAILED, provider.classify_error(exc)

    assert job.id is not None
    drafts: list[RecordDraft] = []
    validation_results: list[ValidationResult] = []
    for raw_item in raw_items:
        heartbeat.maybe_beat(now)  # item 1 — interval-gated, cheap to call per item
        normalized = provider.normalize(raw_item)
        draft = RecordDraft(
            project_id=job.project_id,
            job_id=job.id,
            provider=config.provider,
            data=normalized.data,
            collected_at=now,
            provider_record_id=normalized.provider_record_id,
        )
        result = validate_draft(draft, field_rules)
        validation_results.append(result)
        if result.quality != RecordQuality.REJECTED:
            drafts.append(draft)

    persist_outcomes, _summary = persist_batch(
        session, drafts, record_repository, provider_operation=provider_operation
    )

    counters = compute_job_counters(validation_results, persist_outcomes)
    job_repository.update_counters(job.id, counters)

    if counters.total_units == 0 or counters.failed_units == 0:
        return JobStatus.COMPLETED, None
    if counters.successful_units == 0:
        return JobStatus.FAILED, None
    return JobStatus.PARTIALLY_COMPLETED, None
