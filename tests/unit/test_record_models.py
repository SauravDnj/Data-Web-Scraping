"""T025 tests: insert, provenance linkage, and the project-scoped
canonical_key uniqueness/dedup strategy — against SQLite in-memory
(see tests/unit/test_db_session.py)."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, normalize_email
from app.db.models import CollectionConfig, Job, Project, Record, RecordProvenance, User
from app.db.session import build_session_factory, session_scope


def _make_user_project_job(session, email: str = "owner@example.com"):
    user = User(
        email=normalize_email(email),
        password_hash=hash_password("correct horse battery staple"),
    )
    session.add(user)
    session.flush()

    project = Project(user_id=user.id, name="My Project", source_type="google_maps")
    session.add(project)
    session.flush()

    config = CollectionConfig(
        project_id=project.id,
        provider="google_maps",
        config_json={},
        version=1,
        is_active=True,
    )
    session.add(config)
    session.flush()

    job = Job(project_id=project.id, config_id=config.id)
    session.add(job)
    session.flush()

    return project, job


def _make_record(project_id: int, job_id: int, canonical_key: str) -> Record:
    return Record(
        project_id=project_id,
        job_id=job_id,
        provider="google_maps",
        provider_record_id="places/abc123",
        canonical_key=canonical_key,
        data_json={"name": "Example Cafe"},
        collected_at=datetime.now(UTC),
    )


def test_record_can_be_inserted_and_retrieved(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project, job = _make_user_project_job(session)
        session.add(_make_record(project.id, job.id, "google_maps:places/abc123"))
        project_id = project.id

    with session_scope(factory) as session:
        record = session.query(Record).filter_by(project_id=project_id).one()
        assert record.provider_record_id == "places/abc123"
        assert record.data_json == {"name": "Example Cafe"}


def test_record_requires_existing_project_and_job(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        _project, job = _make_user_project_job(session)
        job_id = job.id

    with pytest.raises(IntegrityError), session_scope(factory) as session:
        session.add(_make_record(999_999, job_id, "google_maps:places/xyz"))


def test_duplicate_canonical_key_within_a_project_is_rejected(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project, job = _make_user_project_job(session)
        session.add(_make_record(project.id, job.id, "google_maps:places/abc123"))
        project_id, job_id = project.id, job.id

    with pytest.raises(IntegrityError), session_scope(factory) as session:
        # Same canonical_key, different provider_record_id/data —
        # the key alone determines identity, not the payload.
        record = _make_record(project_id, job_id, "google_maps:places/abc123")
        record.provider_record_id = "places/different"
        session.add(record)


def test_same_canonical_key_is_allowed_across_different_projects(sqlite_engine):
    """Dedup scope is per-project (T000 decision), not global — two
    projects independently collecting the same real-world place are
    not the same business record."""
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project_a, job_a = _make_user_project_job(session, email="owner-a@example.com")
        session.add(_make_record(project_a.id, job_a.id, "google_maps:places/abc123"))

    with session_scope(factory) as session:
        project_b, job_b = _make_user_project_job(session, email="owner-b@example.com")
        session.add(_make_record(project_b.id, job_b.id, "google_maps:places/abc123"))

    with session_scope(factory) as session:
        assert (
            session.query(Record)
            .filter_by(canonical_key="google_maps:places/abc123")
            .count()
            == 2
        )


def test_record_provenance_belongs_to_a_record(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project, job = _make_user_project_job(session)
        record = _make_record(project.id, job.id, "google_maps:places/abc123")
        session.add(record)
        session.flush()
        session.add(
            RecordProvenance(
                record_id=record.id,
                provider_operation="places.details",
                collected_at=datetime.now(UTC),
                metadata_json={"request_id": "req-1"},
            )
        )
        record_id = record.id

    with session_scope(factory) as session:
        provenance = (
            session.query(RecordProvenance).filter_by(record_id=record_id).one()
        )
        assert provenance.provider_operation == "places.details"


def test_record_provenance_requires_existing_record(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with pytest.raises(IntegrityError), session_scope(factory) as session:
        session.add(
            RecordProvenance(
                record_id=999_999,
                provider_operation="places.details",
                collected_at=datetime.now(UTC),
            )
        )
