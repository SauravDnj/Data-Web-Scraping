"""T054 tests: Stage 7 ("Persistence") of docs/08_DATA_PIPELINE_DEEP.md
- against SQLite in-memory via a real session_scope() commit cycle
(not just a single flush), since this task is specifically about
transaction/rollback boundaries. Placed in tests/integration/ (not
tests/unit/, unlike most repository-touching pipeline tests this
session) because item 7 explicitly asks for integration tests and
these exercise a full commit-at-the-end lifecycle, not just
mid-transaction state."""

from datetime import UTC, datetime
from typing import Any

from app.db.models import RecordProvenance as RecordProvenanceRow
from app.db.session import session_scope
from app.domain.records import Record, RecordDraft
from app.pipeline.persist import PersistAction, persist_batch
from app.repositories.records import RecordRepository, SqlAlchemyRecordRepository
from sqlalchemy import select

from tests.unit.factories import make_job, make_user_project_config

BASE_TIME = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)
OPERATION = "google_maps.places.text_search"


def _draft(project_id, job_id, *, provider_record_id="place-1", data=None):
    return RecordDraft(
        project_id=project_id,
        job_id=job_id,
        provider="google_maps",
        data=data or {"name": "Example Cafe"},
        collected_at=BASE_TIME,
        provider_record_id=provider_record_id,
    )


class _StaleCheckRepository:
    """Wraps a real RecordRepository but always reports "not found"
    from get_by_canonical_key - simulates a concurrent insert that
    slipped in between another process's own check and its write,
    exercising the real DB UniqueConstraint (T025) as the thing that
    actually raises IntegrityError, not a mock."""

    def __init__(self, inner: RecordRepository) -> None:
        self._inner = inner

    def get(self, record_id: int):
        return self._inner.get(record_id)

    def create(self, record: Record) -> Record:
        return self._inner.create(record)

    def get_by_canonical_key(self, project_id: int, canonical_key: str):
        return None

    def update_collected_data(
        self, record_id: int, *, job_id: int, data: dict[str, Any], collected_at
    ) -> Record:
        return self._inner.update_collected_data(
            record_id, job_id=job_id, data=data, collected_at=collected_at
        )

    def list_for_project(self, project_id: int, *, limit=50, offset=0):
        return self._inner.list_for_project(project_id, limit=limit, offset=offset)

    def search(self, project_id: int, **kwargs):
        return self._inner.search(project_id, **kwargs)

    def add_provenance(self, provenance):
        return self._inner.add_provenance(provenance)


# --- 1. insert new records ---


def test_new_records_are_created(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)
        draft = _draft(project.id, job.id)

        outcomes, summary = persist_batch(
            session, [draft], repository, provider_operation=OPERATION
        )

        assert summary.created == 1
        assert outcomes[0].action == PersistAction.CREATED
        assert outcomes[0].record_id is not None


# --- 2. update existing records according to policy ---


def test_a_repeat_collection_updates_the_existing_record(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job_1 = make_job(session, project.id, config.id)
        job_2 = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)

        persist_batch(
            session,
            [_draft(project.id, job_1.id, data={"rating": 4.0})],
            repository,
            provider_operation=OPERATION,
        )
        _outcomes, summary = persist_batch(
            session,
            [_draft(project.id, job_2.id, data={"rating": 4.8})],
            repository,
            provider_operation=OPERATION,
        )

        assert summary.updated == 1
        assert repository.list_for_project(project.id).items[0].data == {"rating": 4.8}


def test_update_existing_false_skips_without_writing(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)

        persist_batch(
            session,
            [_draft(project.id, job.id, data={"rating": 4.0})],
            repository,
            provider_operation=OPERATION,
        )
        _outcomes, summary = persist_batch(
            session,
            [_draft(project.id, job.id, data={"rating": 4.8})],
            repository,
            provider_operation=OPERATION,
            update_existing=False,
        )

        assert summary.skipped_existing == 1
        assert repository.list_for_project(project.id).items[0].data == {"rating": 4.0}


# --- 3. store provenance ---


def test_provenance_is_stored_for_a_created_record(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)
        draft = _draft(project.id, job.id)

        outcomes, _summary = persist_batch(
            session, [draft], repository, provider_operation=OPERATION
        )

        record_id = outcomes[0].record_id
        provenance = session.execute(
            select(RecordProvenanceRow).where(
                RecordProvenanceRow.record_id == record_id
            )
        ).scalar_one()

        # SQLite (and MySQL) DATETIME columns drop tzinfo on read-back
        # (docs/16_MEMORY.md, T038) - compare the naive form.
        assert provenance.provider_operation == OPERATION
        assert provenance.collected_at == BASE_TIME.replace(tzinfo=None)


def test_skipped_records_get_no_provenance_row(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)
        draft = _draft(project.id, job.id)

        persist_batch(session, [draft], repository, provider_operation=OPERATION)
        persist_batch(
            session,
            [draft],
            repository,
            provider_operation=OPERATION,
            update_existing=False,
        )

        record_id = repository.list_for_project(project.id).items[0].id
        provenance_rows = (
            session.execute(
                select(RecordProvenanceRow).where(
                    RecordProvenanceRow.record_id == record_id
                )
            )
            .scalars()
            .all()
        )

        assert len(provenance_rows) == 1  # only from the first (CREATED) call


# --- 4/8. rollback / no partial inconsistent state ---


def test_a_constraint_conflict_is_marked_failed_not_raised(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        real_repository = SqlAlchemyRecordRepository(session)
        draft = _draft(project.id, job.id, provider_record_id="place-conflict")

        # A real row already exists with this canonical key - the
        # wrapped repository below will fail to notice via its own
        # (stubbed) check, so the actual INSERT collides for real.
        persist_batch(session, [draft], real_repository, provider_operation=OPERATION)

        stale_repository = _StaleCheckRepository(real_repository)
        outcomes, summary = persist_batch(
            session, [draft], stale_repository, provider_operation=OPERATION
        )

        assert summary.failed == 1
        assert outcomes[0].action == PersistAction.FAILED
        assert outcomes[0].error is not None


def test_a_failed_record_does_not_roll_back_earlier_successes_in_the_same_batch(
    session_factory,
):
    """T054's literal acceptance criterion: a failed transaction does
    not leave partial inconsistent state - here, "partial" means the
    FAILURE doesn't wipe out the SUCCESSES that already happened
    earlier in the same batch/outer transaction."""
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        real_repository = SqlAlchemyRecordRepository(session)

        conflicting_draft = _draft(
            project.id, job.id, provider_record_id="place-conflict"
        )
        persist_batch(
            session, [conflicting_draft], real_repository, provider_operation=OPERATION
        )

        good_draft_1 = _draft(project.id, job.id, provider_record_id="place-good-1")
        good_draft_2 = _draft(project.id, job.id, provider_record_id="place-good-2")
        stale_repository = _StaleCheckRepository(real_repository)

        outcomes, summary = persist_batch(
            session,
            [good_draft_1, conflicting_draft, good_draft_2],
            stale_repository,
            provider_operation=OPERATION,
        )

        assert summary.created == 2
        assert summary.failed == 1
        assert [outcome.action for outcome in outcomes] == [
            PersistAction.CREATED,
            PersistAction.FAILED,
            PersistAction.CREATED,
        ]

    # Re-open a fresh session after the outer transaction committed -
    # proves the successes are durably persisted, not just visible
    # mid-transaction.
    with session_scope(session_factory) as session:
        repository = SqlAlchemyRecordRepository(session)
        all_records = repository.list_for_project(project.id).items
        provider_ids = {record.provider_record_id for record in all_records}
        assert provider_ids == {"place-conflict", "place-good-1", "place-good-2"}


# --- 5. counters only increment after successful operations ---


def test_the_reported_summary_matches_the_committed_row_count(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        real_repository = SqlAlchemyRecordRepository(session)

        conflicting_draft = _draft(
            project.id, job.id, provider_record_id="place-conflict"
        )
        persist_batch(
            session, [conflicting_draft], real_repository, provider_operation=OPERATION
        )
        stale_repository = _StaleCheckRepository(real_repository)

        good_draft = _draft(project.id, job.id, provider_record_id="place-good")
        _outcomes, summary = persist_batch(
            session,
            [good_draft, conflicting_draft],
            stale_repository,
            provider_operation=OPERATION,
        )
        project_id = project.id

    with session_scope(session_factory) as session:
        repository = SqlAlchemyRecordRepository(session)
        total_rows = len(repository.list_for_project(project_id).items)

    # 1 pre-existing (place-conflict) + summary.created new ones.
    assert total_rows == 1 + summary.created
    assert summary.failed == 1
