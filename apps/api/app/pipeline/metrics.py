"""Stage 8 ("Metrics") of docs/08_DATA_PIPELINE_DEEP.md (T055) —
aggregates T051's validation results and T054's persistence outcomes
for a batch into `app.domain.jobs.JobCounters`, and applies them to a
`Job` row (`JobRepository.update_counters()`, new here) within the
same transaction as the batch's own record writes.

**This module is deliberately NOT the worker orchestrator** (T060+) —
it doesn't call `collect()`/`validate_record_draft()`/`persist_batch()`
itself, only aggregates their already-computed results. That keeps it
testable without a real provider or a real worker loop, same as every
other `app.pipeline` module this session.

**Bucket mapping, a design decision this task had to make (docs/08
names the seven counters but not how every outcome type maps onto
them)**:

-   Every item in `validation_results` counts toward `total_units`
    exactly once — this is *every* collected item, before persistence
    is even attempted.
-   `RecordQuality.REJECTED` → `failed_units` **and**
    `records_rejected`. A rejected record never reaches
    `persist_batch()` at all, so it can never also appear in
    `persist_outcomes`.
-   `RecordQuality.VALID`/`WARNING` records proceed to persistence;
    their fate is decided entirely by `persist_outcomes`, not
    re-derived from validation quality (a WARNING is informational —
    docs/08 lists it as a distinct third state, not "half rejected" —
    it still gets created/updated normally).
-   `PersistAction.CREATED`/`UPDATED` → `successful_units` +
    `records_created`/`records_updated` respectively.
-   `PersistAction.FAILED` (a database constraint conflict, T054) →
    `failed_units` — **not** `records_rejected`, which is reserved for
    *quality* rejections (Stage 4); a DB-level write failure is a
    different kind of problem from a data-quality one, and conflating
    them would make `records_rejected` an inaccurate quality signal.
-   `PersistAction.SKIPPED_EXISTING`/`SKIPPED_DUPLICATE_IN_BATCH` →
    `skipped_units`.

By construction, `total_units == successful_units + failed_units +
skipped_units` always holds — every collected item lands in exactly
one of those three buckets. `records_created`/`records_updated`/
`records_rejected` are a separate, cross-cutting breakdown that does
NOT need to sum to `total_units` (skipped items appear in neither).

**Retries** are not a `JobCounters` field — this codebase already has
two distinct, already-tracked "retry" concepts, and T055 doesn't
invent a third: `JobRun.attempt` (T024) counts a *worker*-level
re-attempt of the same job (e.g. after a crash/heartbeat timeout,
T062/T065); `JobService.retry_job()` (T035) creates an entirely new
`Job` row after a terminal `FAILED` job, tracked via the audit log
(`AuditAction.JOB_RETRIED`), not a counter on the original job.
`count_job_run_attempts()` below surfaces the first of these — the one
directly queryable from what T024/T032 already built."""

from collections.abc import Iterable

from app.domain.jobs import JobCounters, JobRun
from app.pipeline.persist import PersistAction, PersistOutcome
from app.pipeline.validate import RecordQuality, ValidationResult


def compute_job_counters(
    validation_results: Iterable[ValidationResult],
    persist_outcomes: Iterable[PersistOutcome],
) -> JobCounters:
    total_units = 0
    successful_units = 0
    failed_units = 0
    skipped_units = 0
    records_rejected = 0

    for result in validation_results:
        total_units += 1
        if result.quality == RecordQuality.REJECTED:
            failed_units += 1
            records_rejected += 1

    records_created = 0
    records_updated = 0

    for outcome in persist_outcomes:
        if outcome.action == PersistAction.CREATED:
            successful_units += 1
            records_created += 1
        elif outcome.action == PersistAction.UPDATED:
            successful_units += 1
            records_updated += 1
        elif outcome.action == PersistAction.FAILED:
            failed_units += 1
        elif outcome.action in (
            PersistAction.SKIPPED_EXISTING,
            PersistAction.SKIPPED_DUPLICATE_IN_BATCH,
        ):
            skipped_units += 1

    return JobCounters(
        total_units=total_units,
        successful_units=successful_units,
        failed_units=failed_units,
        skipped_units=skipped_units,
        records_created=records_created,
        records_updated=records_updated,
        records_rejected=records_rejected,
    )


def count_job_run_attempts(runs: Iterable[JobRun]) -> int:
    """Number of *retried* attempts for one job — the first attempt is
    not a retry, so this is `max(attempt) - 1`, floored at 0 for a job
    with no runs recorded yet."""
    attempts = [run.attempt for run in runs]
    if not attempts:
        return 0
    return max(attempts) - 1
