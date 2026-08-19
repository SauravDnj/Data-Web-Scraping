"""T061 tests: the full dequeue-to-acknowledge worker workflow,
against SQLite + `fakeredis` (this project's established real-
substitute-system testing strategy, T020-T060) and T040's
`FakeProviderAdapter` — proving the literal acceptance criterion
("Fake provider with 3 records produces a completed job and 3 records
in MySQL") plus every other IMPLEMENT item's own behavior. Placed in
tests/integration/, matching T054/T055's precedent for transaction-
boundary-sensitive tests."""

from datetime import UTC, datetime

import fakeredis
from app.db.session import session_scope
from app.domain.jobs import JobRunStatus, JobStatus
from app.pipeline.validate import FieldRule, RecordQuality
from app.repositories.configs import SqlAlchemyCollectionConfigRepository
from app.repositories.jobs import SqlAlchemyJobRepository
from app.repositories.records import SqlAlchemyRecordRepository

from tests.unit.factories import make_config, make_job, make_project, make_user
from tests.unit.fakes import FakeProviderAdapter
from workers.jobs.execute_collection import process_next_job
from workers.queue import RedisJobQueue

NOW = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)
OPERATION = "fake.collect"


def _setup(session, *, config_json=None, raw_items=None):
    user = make_user(session)
    project = make_project(session, user.id)
    config = make_config(
        session,
        project.id,
        config_json=(
            config_json if config_json is not None else {"query": "coffee shops"}
        ),
    )
    job = make_job(session, project.id, config.id)
    job_repository = SqlAlchemyJobRepository(session)
    job_repository.update_status(job.id, JobStatus.QUEUED)

    queue = RedisJobQueue(fakeredis.FakeRedis())
    queue.enqueue(job.id)

    provider = FakeProviderAdapter(raw_items=raw_items)

    return project, job, queue, provider, job_repository


FIELD_RULES: dict[str, FieldRule] = {
    "name": FieldRule(missing_severity=RecordQuality.REJECTED, expected_types=(str,))
}


def test_fake_provider_with_three_records_produces_a_completed_job_and_three_records(
    session_factory,
):
    """T061's literal acceptance criterion."""
    raw_items = [{"id": f"item-{i}", "name": f"Example Place {i}"} for i in range(3)]
    with session_scope(session_factory) as session:
        project, job, queue, provider, job_repository = _setup(
            session, raw_items=raw_items
        )
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        outcome = process_next_job(
            session,
            queue,
            provider,
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        assert outcome is not None
        assert outcome.claimed is True
        assert outcome.status == JobStatus.COMPLETED

        project_id, job_id = project.id, job.id

    with session_scope(session_factory) as session:
        job_repository = SqlAlchemyJobRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        persisted_job = job_repository.get(job_id)
        records = record_repository.list_for_project(project_id).items

        assert persisted_job.status == JobStatus.COMPLETED
        assert persisted_job.counters.records_created == 3
        assert len(records) == 3


def test_returns_none_when_the_queue_is_empty(session_factory):
    with session_scope(session_factory) as session:
        queue = RedisJobQueue(fakeredis.FakeRedis())
        provider = FakeProviderAdapter()
        job_repository = SqlAlchemyJobRepository(session)
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        outcome = process_next_job(
            session,
            queue,
            provider,
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
            dequeue_timeout_seconds=0.1,
        )

        assert outcome is None


def test_an_already_claimed_job_is_skipped_and_still_acknowledged(session_factory):
    """Simulates a race: another worker already moved the job to
    RUNNING between this worker's dequeue and its claim attempt."""
    with session_scope(session_factory) as session:
        _project, job, queue, provider, job_repository = _setup(session)
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        job_repository.update_status(job.id, JobStatus.RUNNING)  # "another worker"

        outcome = process_next_job(
            session,
            queue,
            provider,
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        assert outcome is not None
        assert outcome.claimed is False
        assert queue.list_in_flight() == []  # still acknowledged, not stuck


def test_an_invalid_configuration_fails_the_job_without_calling_collect(
    session_factory,
):
    with session_scope(session_factory) as session:
        _project, job, queue, provider, job_repository = _setup(
            session, config_json={}
        )  # missing "query" -> FakeProviderAdapter rejects it
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        outcome = process_next_job(
            session,
            queue,
            provider,
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        assert outcome.status == JobStatus.FAILED
        persisted_job = job_repository.get(job.id)
        assert persisted_job.error_code == "invalid_request"
        assert "query" in persisted_job.error_message


def test_a_collect_level_exception_fails_the_job_with_the_classified_error(
    session_factory,
):
    class _RaisingProvider(FakeProviderAdapter):
        def collect(self, config):
            raise TimeoutError("provider timed out")
            yield  # pragma: no cover - makes this a generator function

    with session_scope(session_factory) as session:
        _project, job, queue, _provider, job_repository = _setup(session)
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        outcome = process_next_job(
            session,
            queue,
            _RaisingProvider(),
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        assert outcome.status == JobStatus.FAILED
        persisted_job = job_repository.get(job.id)
        assert persisted_job.error_code == "temporary"  # FakeProviderAdapter's own
        # classify_error() maps TimeoutError -> TEMPORARY (tests/unit/fakes.py)
        assert queue.list_in_flight() == []


def test_partial_failure_produces_partially_completed_status(session_factory):
    raw_items = [
        {"id": "item-1", "name": "Example Place"},
        {"id": "item-2"},  # no "name" -> REJECTED by FIELD_RULES
    ]
    with session_scope(session_factory) as session:
        _project, job, queue, provider, job_repository = _setup(
            session, raw_items=raw_items
        )
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        outcome = process_next_job(
            session,
            queue,
            provider,
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        assert outcome.status == JobStatus.PARTIALLY_COMPLETED
        persisted_job = job_repository.get(job.id)
        assert persisted_job.counters.records_created == 1
        assert persisted_job.counters.records_rejected == 1


def test_cancellation_requested_mid_processing_stops_at_a_safe_boundary(
    session_factory,
):
    """T064: simulates a cancellation request arriving while the
    worker is partway through a batch. `_CancellingProvider.normalize()`
    requests cancellation (as `JobService.cancel_job()` would, against
    the same job_repository/session) as a side effect of handling the
    second item — the loop's own pre-item check only observes this
    starting with the *third* item, so items 1-2 are processed and
    persisted normally and item 3 is never touched. Proves "stops at a
    safe boundary" rather than "stops immediately no matter what"."""
    raw_items = [
        {"id": "item-1", "name": "Example Place 1"},
        {"id": "item-2", "name": "Example Place 2"},
        {"id": "item-3", "name": "Example Place 3"},
    ]

    class _CancellingProvider(FakeProviderAdapter):
        def __init__(self, job_repository, job_id, raw_items):
            super().__init__(raw_items=raw_items)
            self._job_repository = job_repository
            self._job_id = job_id
            self._normalize_calls = 0

        def normalize(self, raw_item):
            self._normalize_calls += 1
            if self._normalize_calls == 2:
                self._job_repository.request_cancellation(
                    self._job_id, requested_at=NOW
                )
            return super().normalize(raw_item)

    with session_scope(session_factory) as session:
        project, job, queue, _provider, job_repository = _setup(
            session, raw_items=raw_items
        )
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)
        provider = _CancellingProvider(job_repository, job.id, raw_items)

        outcome = process_next_job(
            session,
            queue,
            provider,
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        assert outcome is not None
        assert outcome.status == JobStatus.CANCELLED
        assert provider._normalize_calls == 2  # item 3 never reached

        persisted_job = job_repository.get(job.id)
        assert persisted_job.status == JobStatus.CANCELLED
        assert persisted_job.cancel_requested is True
        assert persisted_job.counters.records_created == 2

        runs = job_repository.list_runs_for_job(job.id)
        assert runs[0].status == JobRunStatus.CANCELLED

        records = record_repository.list_for_project(project.id).items
        assert len(records) == 2

        assert queue.list_in_flight() == []  # still acknowledged


def test_cancellation_requested_before_any_item_persists_nothing(session_factory):
    """The edge case where cancellation lands while collect() itself
    is still running: no item exists yet to check "between", so the
    request is only observable once collect() returns — still before
    anything has been normalized or persisted."""
    raw_items = [{"id": "item-1", "name": "Example Place"}]

    class _PreCancelledProvider(FakeProviderAdapter):
        def __init__(self, job_repository, job_id, raw_items):
            super().__init__(raw_items=raw_items)
            self._job_repository = job_repository
            self._job_id = job_id

        def collect(self, config):
            self._job_repository.request_cancellation(self._job_id, requested_at=NOW)
            yield from self._raw_items

    with session_scope(session_factory) as session:
        _project, job, queue, _provider, job_repository = _setup(
            session, raw_items=raw_items
        )
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)
        provider = _PreCancelledProvider(job_repository, job.id, raw_items)

        outcome = process_next_job(
            session,
            queue,
            provider,
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        assert outcome.status == JobStatus.CANCELLED
        persisted_job = job_repository.get(job.id)
        assert persisted_job.counters.total_units == 0
        assert record_repository.list_for_project(_project.id).items == []


def test_the_job_run_is_created_and_finalized(session_factory):
    with session_scope(session_factory) as session:
        _project, job, queue, provider, job_repository = _setup(session)
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        process_next_job(
            session,
            queue,
            provider,
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        runs = job_repository.list_runs_for_job(job.id)
        assert len(runs) == 1
        assert runs[0].worker_id == "worker-1"
        assert runs[0].attempt == 1
        assert runs[0].status == JobRunStatus.COMPLETED
        assert runs[0].finished_at is not None


def test_the_queue_message_is_always_acknowledged_even_on_total_failure(
    session_factory,
):
    class _RaisingProvider(FakeProviderAdapter):
        def collect(self, config):
            raise RuntimeError("boom")
            yield  # pragma: no cover

    with session_scope(session_factory) as session:
        _project, _job, queue, _provider, job_repository = _setup(session)
        config_repository = SqlAlchemyCollectionConfigRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        process_next_job(
            session,
            queue,
            _RaisingProvider(),
            job_repository,
            config_repository,
            record_repository,
            field_rules=FIELD_RULES,
            provider_operation=OPERATION,
            worker_id="worker-1",
            now=NOW,
        )

        assert queue.list_in_flight() == []
