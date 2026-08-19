"""T055 integration test: JobRepository.update_counters() applied
within the same transaction as the batch's own record writes (T054),
proving counters never claim success for uncommitted records - T055's
literal acceptance criterion. Placed in tests/integration/, matching
tests/integration/test_pipeline_persist.py's precedent for this same
kind of transaction-boundary test."""

from datetime import UTC, datetime

from tests.unit.factories import make_job, make_user_project_config

from app.db.session import session_scope
from app.domain.jobs import JobCounters
from app.domain.records import RecordDraft
from app.pipeline.metrics import compute_job_counters
from app.pipeline.persist import persist_batch
from app.pipeline.validate import RecordQuality, ValidationResult
from app.repositories.jobs import SqlAlchemyJobRepository
from app.repositories.records import SqlAlchemyRecordRepository

BASE_TIME = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)
OPERATION = "google_maps.places.text_search"


def _draft(project_id, job_id, *, provider_record_id):
    return RecordDraft(
        project_id=project_id,
        job_id=job_id,
        provider="google_maps",
        data={"name": "Example Cafe"},
        collected_at=BASE_TIME,
        provider_record_id=provider_record_id,
    )


def test_counters_are_committed_atomically_with_the_records_they_describe(
    session_factory,
):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        record_repository = SqlAlchemyRecordRepository(session)
        job_repository = SqlAlchemyJobRepository(session)

        drafts = [
            _draft(project.id, job.id, provider_record_id="place-1"),
            _draft(project.id, job.id, provider_record_id="place-2"),
        ]
        validation_results = [
            ValidationResult(quality=RecordQuality.VALID) for _ in drafts
        ]

        outcomes, _summary = persist_batch(
            session, drafts, record_repository, provider_operation=OPERATION
        )
        counters = compute_job_counters(validation_results, outcomes)
        job_repository.update_counters(job.id, counters)

        project_id, job_id = project.id, job.id

    # Re-open a fresh session after commit - counters and records must
    # agree, since both were written in the one transaction above.
    with session_scope(session_factory) as session:
        job_repository = SqlAlchemyJobRepository(session)
        record_repository = SqlAlchemyRecordRepository(session)

        persisted_job = job_repository.get(job_id)
        record_count = len(record_repository.list_for_project(project_id).items)

        assert persisted_job.counters == JobCounters(
            total_units=2,
            successful_units=2,
            failed_units=0,
            skipped_units=0,
            records_created=2,
            records_updated=0,
            records_rejected=0,
        )
        assert record_count == 2
        assert persisted_job.counters.records_created == record_count
