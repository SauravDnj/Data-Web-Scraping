"""T036 tests: project-scoped search, filtering, sorting, safe
pagination against a synthetic large dataset, detail retrieval, and
authorization — against SQLite in-memory (see
tests/unit/test_db_session.py)."""

from datetime import UTC, datetime, timedelta

import pytest
from tests.unit.factories import make_job, make_project, make_user

from app.db.models import CollectionConfig
from app.db.session import session_scope
from app.domain.record_search import RecordSearchFilters, RecordSort, RecordSortField
from app.domain.records import Record
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.repositories.records import MAX_RECORD_PAGE_LIMIT, SqlAlchemyRecordRepository
from app.services.audit import AuditService
from app.services.errors import NotFoundError, PermissionDeniedError
from app.services.projects import ProjectService
from app.services.records import RecordService


def _make_services(session):
    audit = AuditService(SqlAlchemyAuditLogRepository(session))
    projects = ProjectService(SqlAlchemyProjectRepository(session), audit)
    records = RecordService(SqlAlchemyRecordRepository(session), projects)
    return projects, records


def _seed_records(
    session, project_id: int, job_id: int, count: int, provider="google_maps"
):
    repo = SqlAlchemyRecordRepository(session)
    base_time = datetime(2026, 1, 1, tzinfo=UTC)
    for i in range(count):
        repo.create(
            Record(
                id=None,
                project_id=project_id,
                job_id=job_id,
                provider=provider,
                canonical_key=f"{provider}:places/{i}",
                data={"index": i},
                provider_record_id=f"places/{i}" if i % 2 == 0 else None,
                collected_at=base_time + timedelta(minutes=i),
            )
        )


def test_search_records_is_scoped_to_the_project(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project_a = make_project(session, user.id, name="A")
        project_b = make_project(session, user.id, name="B")
        job_a = make_job(session, project_a.id, _config_id(session, project_a.id))
        job_b = make_job(session, project_b.id, _config_id(session, project_b.id))
        _seed_records(session, project_a.id, job_a.id, 3)
        _seed_records(session, project_b.id, job_b.id, 5)

        _projects, records = _make_services(session)
        page = records.search_records(project_a.id, requesting_user_id=user.id)
        assert page.total == 3


def _config_id(session, project_id: int) -> int:
    config = CollectionConfig(
        project_id=project_id,
        provider="google_maps",
        config_json={},
        version=1,
        is_active=True,
    )
    session.add(config)
    session.flush()
    return config.id


def test_pagination_over_a_synthetic_large_dataset(session_factory):
    """T036 item 10: tests with synthetic large datasets."""
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        job = make_job(session, project.id, _config_id(session, project.id))
        _seed_records(session, project.id, job.id, 250)

        _projects, records = _make_services(session)

        first_page = records.search_records(
            project.id, requesting_user_id=user.id, limit=100, offset=0
        )
        assert first_page.total == 250
        assert len(first_page.items) == 100

        second_page = records.search_records(
            project.id, requesting_user_id=user.id, limit=100, offset=100
        )
        assert len(second_page.items) == 100

        third_page = records.search_records(
            project.id, requesting_user_id=user.id, limit=100, offset=200
        )
        assert len(third_page.items) == 50

        # No overlap between pages.
        ids_page_1 = {r.id for r in first_page.items}
        ids_page_2 = {r.id for r in second_page.items}
        assert ids_page_1.isdisjoint(ids_page_2)


def test_query_limit_is_capped_even_if_a_larger_limit_is_requested(session_factory):
    """T036: "DO NOT load all records into memory" — even a caller
    asking for an enormous page gets clamped to MAX_RECORD_PAGE_LIMIT."""
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        job = make_job(session, project.id, _config_id(session, project.id))
        _seed_records(session, project.id, job.id, MAX_RECORD_PAGE_LIMIT + 50)

        _projects, records = _make_services(session)
        page = records.search_records(
            project.id, requesting_user_id=user.id, limit=100_000, offset=0
        )
        assert len(page.items) == MAX_RECORD_PAGE_LIMIT


def test_provider_filter_narrows_results(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        job = make_job(session, project.id, _config_id(session, project.id))
        _seed_records(session, project.id, job.id, 3, provider="google_maps")
        _seed_records(session, project.id, job.id, 2, provider="other_provider")

        _projects, records = _make_services(session)
        page = records.search_records(
            project.id,
            requesting_user_id=user.id,
            filters=RecordSearchFilters(provider="other_provider"),
        )
        assert page.total == 2
        assert all(r.provider == "other_provider" for r in page.items)


def test_date_filtering_narrows_results(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        job = make_job(session, project.id, _config_id(session, project.id))
        _seed_records(session, project.id, job.id, 10)  # minutes 0..9 of 2026-01-01

        _projects, records = _make_services(session)
        cutoff = datetime(2026, 1, 1, 0, 5, tzinfo=UTC)
        page = records.search_records(
            project.id,
            requesting_user_id=user.id,
            filters=RecordSearchFilters(collected_after=cutoff),
        )
        assert page.total == 5  # minutes 5,6,7,8,9


def test_quality_filter_by_provider_id_presence(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        job = make_job(session, project.id, _config_id(session, project.id))
        _seed_records(
            session, project.id, job.id, 10
        )  # even indices have provider_record_id

        _projects, records = _make_services(session)
        with_id = records.search_records(
            project.id,
            requesting_user_id=user.id,
            filters=RecordSearchFilters(has_provider_id=True),
        )
        without_id = records.search_records(
            project.id,
            requesting_user_id=user.id,
            filters=RecordSearchFilters(has_provider_id=False),
        )
        assert with_id.total == 5
        assert without_id.total == 5


def test_sorting_by_created_at_ascending(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        job = make_job(session, project.id, _config_id(session, project.id))
        _seed_records(session, project.id, job.id, 5)

        _projects, records = _make_services(session)
        page = records.search_records(
            project.id,
            requesting_user_id=user.id,
            sort=RecordSort(field=RecordSortField.COLLECTED_AT, descending=False),
        )
        collected_ats = [r.collected_at for r in page.items]
        assert collected_ats == sorted(collected_ats)


def test_get_record_detail(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        project = make_project(session, user.id)
        job = make_job(session, project.id, _config_id(session, project.id))
        _seed_records(session, project.id, job.id, 1)

        _projects, records = _make_services(session)
        page = records.search_records(project.id, requesting_user_id=user.id)
        record_id = page.items[0].id

        detail = records.get_record(record_id, requesting_user_id=user.id)
        assert detail.id == record_id


def test_get_nonexistent_record_raises_not_found(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        _projects, records = _make_services(session)

        with pytest.raises(NotFoundError):
            records.get_record(999_999, requesting_user_id=user.id)


def test_stranger_cannot_search_or_view_another_users_records(session_factory):
    with session_scope(session_factory) as session:
        owner = make_user(session, email="owner@example.com")
        stranger = make_user(session, email="stranger@example.com")
        project = make_project(session, owner.id)
        job = make_job(session, project.id, _config_id(session, project.id))
        _seed_records(session, project.id, job.id, 3)

        _projects, records = _make_services(session)
        page = records.search_records(project.id, requesting_user_id=owner.id)
        record_id = page.items[0].id

        with pytest.raises(PermissionDeniedError):
            records.search_records(project.id, requesting_user_id=stranger.id)
        with pytest.raises(PermissionDeniedError):
            records.get_record(record_id, requesting_user_id=stranger.id)
