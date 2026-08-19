"""T055 tests: Stage 8 ("Metrics") of docs/08_DATA_PIPELINE_DEEP.md -
pure aggregation, no DB. Scenarios named to match T055's own test
list: all-success job, partial failure, retry, duplicate, rejected
record."""

from app.domain.jobs import JobCounters, JobRun, JobRunStatus
from app.pipeline.metrics import compute_job_counters, count_job_run_attempts
from app.pipeline.persist import PersistAction, PersistOutcome
from app.pipeline.validate import RecordQuality, ValidationResult


def _valid_result() -> ValidationResult:
    return ValidationResult(quality=RecordQuality.VALID, errors=[])


def _rejected_result() -> ValidationResult:
    return ValidationResult(quality=RecordQuality.REJECTED, errors=[])


# --- all-success job ---


def test_all_success_job_counts_every_item_as_successful():
    validation_results = [_valid_result() for _ in range(3)]
    persist_outcomes = [
        PersistOutcome("k1", PersistAction.CREATED, record_id=1),
        PersistOutcome("k2", PersistAction.CREATED, record_id=2),
        PersistOutcome("k3", PersistAction.UPDATED, record_id=3),
    ]

    counters = compute_job_counters(validation_results, persist_outcomes)

    assert counters == JobCounters(
        total_units=3,
        successful_units=3,
        failed_units=0,
        skipped_units=0,
        records_created=2,
        records_updated=1,
        records_rejected=0,
    )


# --- partial failure ---


def test_partial_failure_counts_the_failed_persistence_separately_from_rejection():
    """A PersistAction.FAILED (DB constraint conflict, T054) is a
    different kind of problem from a validation REJECTED - both land
    in failed_units, but only REJECTED touches records_rejected."""
    validation_results = [_valid_result(), _valid_result()]
    persist_outcomes = [
        PersistOutcome("k1", PersistAction.CREATED, record_id=1),
        PersistOutcome("k2", PersistAction.FAILED, error="constraint conflict"),
    ]

    counters = compute_job_counters(validation_results, persist_outcomes)

    assert counters.successful_units == 1
    assert counters.failed_units == 1
    assert counters.records_created == 1
    assert counters.records_rejected == 0


# --- retry ---


def test_a_job_with_no_runs_has_zero_retries():
    assert count_job_run_attempts([]) == 0


def test_a_job_run_at_the_first_attempt_has_zero_retries():
    run = JobRun(id=1, job_id=1, worker_id="worker-a", attempt=1)
    assert count_job_run_attempts([run]) == 0


def test_a_job_with_three_attempts_has_two_retries():
    runs = [
        JobRun(
            id=i, job_id=1, worker_id="worker-a", status=JobRunStatus.FAILED, attempt=i
        )
        for i in range(1, 4)
    ]
    assert count_job_run_attempts(runs) == 2


# --- duplicate ---


def test_duplicates_are_counted_as_skipped_not_failed_or_successful():
    validation_results = [_valid_result(), _valid_result()]
    persist_outcomes = [
        PersistOutcome("k1", PersistAction.CREATED, record_id=1),
        PersistOutcome("k1", PersistAction.SKIPPED_DUPLICATE_IN_BATCH),
    ]

    counters = compute_job_counters(validation_results, persist_outcomes)

    assert counters.skipped_units == 1
    assert counters.successful_units == 1
    assert counters.failed_units == 0


def test_an_existing_record_skip_is_also_counted_as_skipped():
    validation_results = [_valid_result()]
    persist_outcomes = [PersistOutcome("k1", PersistAction.SKIPPED_EXISTING)]

    counters = compute_job_counters(validation_results, persist_outcomes)

    assert counters.skipped_units == 1
    assert counters.successful_units == 0


# --- rejected record ---


def test_a_rejected_record_never_reaches_persistence_but_is_still_counted():
    validation_results = [_valid_result(), _rejected_result()]
    persist_outcomes = [
        PersistOutcome("k1", PersistAction.CREATED, record_id=1)
    ]  # only the valid one was ever attempted

    counters = compute_job_counters(validation_results, persist_outcomes)

    assert counters.total_units == 2
    assert counters.records_rejected == 1
    assert counters.failed_units == 1
    assert counters.successful_units == 1


# --- the total_units invariant ---


def test_total_units_always_equals_successful_plus_failed_plus_skipped():
    validation_results = [_valid_result(), _valid_result(), _rejected_result()]
    persist_outcomes = [
        PersistOutcome("k1", PersistAction.CREATED, record_id=1),
        PersistOutcome("k2", PersistAction.SKIPPED_EXISTING),
    ]

    counters = compute_job_counters(validation_results, persist_outcomes)

    assert counters.total_units == (
        counters.successful_units + counters.failed_units + counters.skipped_units
    )


def test_no_negative_counters_are_ever_produced():
    counters = compute_job_counters([], [])
    assert counters == JobCounters()
