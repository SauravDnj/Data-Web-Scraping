"""T053 tests: Stage 6 ("Deduplication") of docs/08_DATA_PIPELINE_DEEP.md
- against SQLite in-memory via the real repository (T032), same
rationale as tests/unit/test_db_session.py. One section per T053
IMPLEMENT/test item."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError
from tests.unit.factories import make_job, make_user_project_config

from app.db.models import Record as RecordRow
from app.db.session import session_scope
from app.domain.records import Record, RecordDraft
from app.pipeline.canonical_identity import compute_canonical_key
from app.pipeline.deduplicate import (
    DedupAction,
    deduplicate_batch,
    deduplicate_within_batch,
    resolve_against_existing,
)
from app.repositories.records import SqlAlchemyRecordRepository

BASE_TIME = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)


def _draft(
    project_id: int,
    job_id: int,
    *,
    provider_record_id: str = "place-1",
    data: dict | None = None,
    collected_at: datetime = BASE_TIME,
) -> RecordDraft:
    return RecordDraft(
        project_id=project_id,
        job_id=job_id,
        provider="google_maps",
        data=data or {"name": "Example Cafe"},
        collected_at=collected_at,
        provider_record_id=provider_record_id,
    )


# --- 1/2. deduplicate within a batch, across pages ---


def test_a_duplicate_within_one_page_is_dropped():
    draft = _draft(1, 1)
    page = [draft, draft]

    results = list(deduplicate_within_batch(page))

    assert [is_dup for _, _, is_dup in results] == [False, True]


def test_a_duplicate_spread_across_two_pages_is_still_caught():
    """Streaming across whatever iterable the caller passes - the same
    mechanism handles both "within a page" and "across pages", since a
    real paginated collect() is one continuous generator by the time
    it reaches here."""
    draft = _draft(1, 1)
    page_1 = [draft]
    page_2 = [draft]  # same canonical key, arrives on a later "page"

    def all_pages():
        yield from page_1
        yield from page_2

    results = list(deduplicate_within_batch(all_pages()))

    assert [is_dup for _, _, is_dup in results] == [False, True]


def test_different_records_in_a_batch_are_all_kept():
    drafts = [_draft(1, 1, provider_record_id=f"place-{i}") for i in range(3)]

    results = list(deduplicate_within_batch(drafts))

    assert [is_dup for _, _, is_dup in results] == [False, False, False]


# --- 3/4. compare against existing project records, using canonical identity ---


def test_a_new_record_is_created(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)
        draft = _draft(project.id, job.id)

        outcome = resolve_against_existing(
            draft, compute_canonical_key(draft), repository, update_existing=True
        )

        assert outcome.action == DedupAction.CREATED
        assert outcome.record is not None
        assert outcome.record.data == {"name": "Example Cafe"}


def test_an_existing_record_is_found_by_canonical_identity(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)
        draft = _draft(project.id, job.id)
        canonical_key = compute_canonical_key(draft)

        repository.create(
            Record(
                id=None,
                project_id=project.id,
                job_id=job.id,
                provider="google_maps",
                canonical_key=canonical_key,
                data={"name": "Example Cafe"},
                collected_at=BASE_TIME,
                provider_record_id="place-1",
            )
        )

        outcome = resolve_against_existing(
            draft, canonical_key, repository, update_existing=True
        )

        assert outcome.action == DedupAction.UPDATED


# --- 5. update-vs-skip behavior ---


def test_update_existing_true_refreshes_data_and_collected_at(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job_1 = make_job(session, project.id, config.id)
        job_2 = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)
        first_draft = _draft(project.id, job_1.id, data={"rating": 4.0})
        canonical_key = compute_canonical_key(first_draft)
        resolve_against_existing(
            first_draft, canonical_key, repository, update_existing=True
        )

        later = BASE_TIME + timedelta(days=1)
        second_draft = _draft(
            project.id, job_2.id, data={"rating": 4.8}, collected_at=later
        )
        outcome = resolve_against_existing(
            second_draft, canonical_key, repository, update_existing=True
        )

        assert outcome.action == DedupAction.UPDATED
        assert outcome.record.data == {"rating": 4.8}
        assert outcome.record.collected_at == later
        assert outcome.record.job_id == job_2.id


def test_update_existing_false_leaves_the_existing_row_untouched(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job_1 = make_job(session, project.id, config.id)
        job_2 = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)
        first_draft = _draft(project.id, job_1.id, data={"rating": 4.0})
        canonical_key = compute_canonical_key(first_draft)
        resolve_against_existing(
            first_draft, canonical_key, repository, update_existing=True
        )

        second_draft = _draft(project.id, job_2.id, data={"rating": 4.8})
        outcome = resolve_against_existing(
            second_draft, canonical_key, repository, update_existing=False
        )

        assert outcome.action == DedupAction.SKIPPED_EXISTING
        assert outcome.record.data == {"rating": 4.0}
        assert outcome.record.job_id == job_1.id


# --- 6. track duplicate counts ---


def test_dedup_summary_counts_every_outcome_kind(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)

        existing_draft = _draft(project.id, job.id, provider_record_id="existing")
        resolve_against_existing(
            existing_draft,
            compute_canonical_key(existing_draft),
            repository,
            update_existing=True,
        )

        new_draft = _draft(project.id, job.id, provider_record_id="brand-new")
        repeat_of_existing = _draft(
            project.id, job.id, provider_record_id="existing", data={"rating": 5.0}
        )
        duplicate_new = new_draft  # same object -> duplicate within batch

        _outcomes, summary = deduplicate_batch(
            [repeat_of_existing, new_draft, duplicate_new],
            repository,
            update_existing=True,
        )

        assert summary.updated == 1
        assert summary.created == 1
        assert summary.duplicates_in_batch == 1


# --- 7. false-merge tests ---


def test_two_different_businesses_are_never_merged(session_factory):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)

        cafe = _draft(project.id, job.id, provider_record_id="place-cafe")
        diner = _draft(project.id, job.id, provider_record_id="place-diner")

        outcomes, summary = deduplicate_batch([cafe, diner], repository)

        assert summary.created == 2
        assert {outcome.record.provider_record_id for outcome in outcomes} == {
            "place-cafe",
            "place-diner",
        }


# --- 8. duplicate-batch tests ---


def test_a_batch_with_many_repeats_of_one_record_creates_exactly_one_row(
    session_factory,
):
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        repository = SqlAlchemyRecordRepository(session)
        draft = _draft(project.id, job.id)

        outcomes, summary = deduplicate_batch([draft] * 5, repository)

        assert summary.created == 1
        assert summary.duplicates_in_batch == 4
        assert len(repository.list_for_project(project.id).items) == 1


# --- 9. database constraint tests ---


def test_the_database_constraint_is_the_final_safety_net(session_factory):
    """Even if application-level dedup logic were bypassed entirely,
    the DB itself refuses a second row with the same
    (project_id, canonical_key) - proving T053's literal acceptance
    criterion ("repeated collection does not create uncontrolled
    duplicate rows") holds at the storage layer too, not only in this
    module's own logic. Two separate session_scope blocks, matching
    tests/unit/test_project_and_config_models.py's established
    pattern for asserting an IntegrityError without leaving the
    session in a post-error, uncommittable state."""
    with session_scope(session_factory) as session:
        _user, project, config = make_user_project_config(session)
        job = make_job(session, project.id, config.id)
        session.add(
            RecordRow(
                project_id=project.id,
                job_id=job.id,
                provider="google_maps",
                canonical_key="google_maps:place-1",
                data_json={},
                collected_at=BASE_TIME,
            )
        )
        project_id, job_id = project.id, job.id

    with pytest.raises(IntegrityError), session_scope(session_factory) as session:
        session.add(
            RecordRow(
                project_id=project_id,
                job_id=job_id,
                provider="google_maps",
                canonical_key="google_maps:place-1",
                data_json={},
                collected_at=BASE_TIME,
            )
        )
