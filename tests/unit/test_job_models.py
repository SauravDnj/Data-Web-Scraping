"""T024 tests: exact configuration-version reference, execution
attempt recording, safe counter defaults, and lifecycle timestamps —
against SQLite in-memory (see tests/unit/test_db_session.py)."""

from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password, normalize_email
from app.db.models import CollectionConfig, Job, JobRun, JobStatus, Project, User
from app.db.session import build_session_factory, session_scope


def _make_user_project_configs(session):
    user = User(
        email=normalize_email("owner@example.com"),
        password_hash=hash_password("correct horse battery staple"),
    )
    session.add(user)
    session.flush()

    project = Project(user_id=user.id, name="My Project", source_type="google_maps")
    session.add(project)
    session.flush()

    config_v1 = CollectionConfig(
        project_id=project.id,
        provider="google_maps",
        config_json={"query": "coffee shops"},
        version=1,
        is_active=False,
    )
    config_v2 = CollectionConfig(
        project_id=project.id,
        provider="google_maps",
        config_json={"query": "coffee shops", "radius_m": 500},
        version=2,
        is_active=True,
    )
    session.add_all([config_v1, config_v2])
    session.flush()

    return project, config_v1, config_v2


def test_job_references_exact_configuration_version(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project, config_v1, _config_v2 = _make_user_project_configs(session)
        # Deliberately reference the OLDER version, not whatever is
        # currently active — proves a job is pinned to a specific
        # config row, not "whatever is active now".
        job = Job(project_id=project.id, config_id=config_v1.id)
        session.add(job)

    with session_scope(factory) as session:
        job = session.query(Job).filter_by(project_id=project.id).one()
        config = session.query(CollectionConfig).filter_by(id=job.config_id).one()
        assert config.version == 1


def test_job_requires_existing_project_and_config(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        _project, config_v1, _config_v2 = _make_user_project_configs(session)
        config_id = config_v1.id

    with pytest.raises(IntegrityError), session_scope(factory) as session:
        session.add(Job(project_id=999_999, config_id=config_id))


def test_job_counters_have_safe_defaults(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project, config_v1, _config_v2 = _make_user_project_configs(session)
        session.add(Job(project_id=project.id, config_id=config_v1.id))
        project_id = project.id

    with session_scope(factory) as session:
        job = session.query(Job).filter_by(project_id=project_id).one()
        assert job.total_units == 0
        assert job.successful_units == 0
        assert job.failed_units == 0
        assert job.skipped_units == 0
        assert job.records_created == 0
        assert job.records_updated == 0
        assert job.records_rejected == 0
        assert job.status == JobStatus.DRAFT
        assert job.error_code is None


def test_job_lifecycle_timestamps(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project, config_v1, _config_v2 = _make_user_project_configs(session)
        job = Job(project_id=project.id, config_id=config_v1.id)
        session.add(job)
        session.flush()
        assert job.requested_at is not None
        assert job.started_at is None
        assert job.finished_at is None
        job_id = job.id

    with session_scope(factory) as session:
        job = session.query(Job).filter_by(id=job_id).one()
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)

    with session_scope(factory) as session:
        job = session.query(Job).filter_by(id=job_id).one()
        assert job.started_at is not None
        assert job.finished_at is None

        job.status = JobStatus.COMPLETED
        job.finished_at = datetime.now(UTC)

    with session_scope(factory) as session:
        job = session.query(Job).filter_by(id=job_id).one()
        assert job.status == JobStatus.COMPLETED
        assert job.finished_at is not None
        assert job.finished_at >= job.started_at


def test_job_run_records_an_execution_attempt(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project, config_v1, _config_v2 = _make_user_project_configs(session)
        job = Job(project_id=project.id, config_id=config_v1.id)
        session.add(job)
        session.flush()
        session.add(JobRun(job_id=job.id, worker_id="worker-1"))
        job_id = job.id

    with session_scope(factory) as session:
        run = session.query(JobRun).filter_by(job_id=job_id).one()
        assert run.attempt == 1
        assert run.worker_id == "worker-1"
        assert run.metrics_json == {}
        assert run.started_at is not None
        assert run.heartbeat_at is not None


def test_job_run_requires_existing_job(sqlite_engine):
    factory = build_session_factory(sqlite_engine)

    with pytest.raises(IntegrityError), session_scope(factory) as session:
        session.add(JobRun(job_id=999_999, worker_id="worker-1"))


def test_second_attempt_gets_its_own_job_run_row(sqlite_engine):
    """Retries (T063) create a new job_run per attempt, not an update
    to the previous one — execution history stays intact."""
    factory = build_session_factory(sqlite_engine)

    with session_scope(factory) as session:
        project, config_v1, _config_v2 = _make_user_project_configs(session)
        job = Job(project_id=project.id, config_id=config_v1.id)
        session.add(job)
        session.flush()
        session.add(JobRun(job_id=job.id, worker_id="worker-1", attempt=1))
        job_id = job.id

    with session_scope(factory) as session:
        session.add(JobRun(job_id=job_id, worker_id="worker-2", attempt=2))

    with session_scope(factory) as session:
        runs = (
            session.query(JobRun)
            .filter_by(job_id=job_id)
            .order_by(JobRun.attempt)
            .all()
        )
        assert [run.attempt for run in runs] == [1, 2]
        assert [run.worker_id for run in runs] == ["worker-1", "worker-2"]
