"""T035 tests: job creation, authorization, lifecycle commands,
idempotency, and gated retry — against SQLite in-memory via the real
repositories/services, same rationale as tests/unit/test_db_session.py."""

import pytest
from tests.unit.factories import make_user
from tests.unit.fakes import AlwaysValidValidator

from app.db.models import Job as JobRow
from app.db.session import session_scope
from app.domain.job_state_machine import InvalidJobTransition
from app.domain.jobs import JobStatus
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.configs import SqlAlchemyCollectionConfigRepository
from app.repositories.jobs import SqlAlchemyJobRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.services.audit import AuditService
from app.services.configs import ConfigurationService
from app.services.errors import InvalidStateError, NotFoundError, PermissionDeniedError
from app.services.jobs import JobService
from app.services.projects import ProjectService


def _make_services(session):
    audit = AuditService(SqlAlchemyAuditLogRepository(session))
    projects = ProjectService(SqlAlchemyProjectRepository(session), audit)
    configs = ConfigurationService(
        SqlAlchemyCollectionConfigRepository(session),
        projects,
        AlwaysValidValidator(),
        audit,
    )
    jobs = JobService(SqlAlchemyJobRepository(session), projects, configs, audit)
    return projects, configs, jobs


def _make_project_with_active_config(projects, configs, user_id: int):
    project = projects.create_project(
        user_id=user_id, name="My Project", source_type="google_maps"
    )
    configs.create_version(
        project.id,
        requesting_user_id=user_id,
        provider="google_maps",
        config={"query": "coffee shops"},
    )
    return project


def test_create_job_from_active_config_succeeds_and_records_audit_event(
    session_factory,
):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)

        job = jobs.create_job(project.id, requesting_user_id=user.id)
        assert job.status == JobStatus.QUEUED

        audit = SqlAlchemyAuditLogRepository(session).list_for_user(user.id)
        assert any(entry.action == "job.created" for entry in audit.items)


def test_create_job_fails_without_an_active_configuration(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, _configs, jobs = _make_services(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(InvalidStateError, match="no active configuration"):
            jobs.create_job(project.id, requesting_user_id=user.id)


def test_create_job_fails_for_an_archived_project(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)
        projects.archive_project(project.id, requesting_user_id=user.id)

        with pytest.raises(InvalidStateError, match="archived"):
            jobs.create_job(project.id, requesting_user_id=user.id)


def test_duplicate_idempotency_key_does_not_create_a_duplicate_job(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)

        first = jobs.create_job(
            project.id, requesting_user_id=user.id, idempotency_key="req-123"
        )
        second = jobs.create_job(
            project.id, requesting_user_id=user.id, idempotency_key="req-123"
        )

        assert first.id == second.id
        all_jobs = SqlAlchemyJobRepository(session).list_for_project(project.id)
        assert all_jobs.total == 1


def test_different_idempotency_keys_create_separate_jobs(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)

        first = jobs.create_job(
            project.id, requesting_user_id=user.id, idempotency_key="req-1"
        )
        second = jobs.create_job(
            project.id, requesting_user_id=user.id, idempotency_key="req-2"
        )

        assert first.id != second.id


def test_cancel_job_transitions_and_records_audit_event(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)
        job = jobs.create_job(project.id, requesting_user_id=user.id)

        cancelled = jobs.cancel_job(job.id, requesting_user_id=user.id)
        assert cancelled.status == JobStatus.CANCELLED

        audit = SqlAlchemyAuditLogRepository(session).list_for_user(user.id)
        assert any(entry.action == "job.cancelled" for entry in audit.items)


def test_pause_only_legal_from_running(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)
        job = jobs.create_job(project.id, requesting_user_id=user.id)  # QUEUED

        with pytest.raises(InvalidJobTransition):
            jobs.pause_job(job.id, requesting_user_id=user.id)

        SqlAlchemyJobRepository(session).update_status(job.id, JobStatus.RUNNING)
        paused = jobs.pause_job(job.id, requesting_user_id=user.id)
        assert paused.status == JobStatus.PAUSED


def test_resume_transitions_paused_back_to_running(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)
        job = jobs.create_job(project.id, requesting_user_id=user.id)
        SqlAlchemyJobRepository(session).update_status(job.id, JobStatus.RUNNING)
        jobs.pause_job(job.id, requesting_user_id=user.id)

        resumed = jobs.resume_job(job.id, requesting_user_id=user.id)
        assert resumed.status == JobStatus.RUNNING


def _fail_job(session, job_id: int, error_code: str) -> None:
    """Test-only arrangement: simulate a job the worker has already
    marked FAILED with a given error class — JobService itself has no
    "mark failed" command (that's worker-level, T061/T063), so this
    reaches into the row directly rather than through JobService."""
    SqlAlchemyJobRepository(session).update_status(job_id, JobStatus.RUNNING)
    row = session.get(JobRow, job_id)
    row.status = JobStatus.FAILED
    row.error_code = error_code
    session.flush()


def test_retry_creates_a_new_job_when_error_is_retryable(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)
        original = jobs.create_job(project.id, requesting_user_id=user.id)
        _fail_job(session, original.id, "transient_network")

        retried = jobs.retry_job(original.id, requesting_user_id=user.id)

        assert retried.id != original.id
        assert retried.status == JobStatus.QUEUED
        assert retried.project_id == original.project_id
        assert retried.config_id == original.config_id

        still_failed = jobs.get_job(original.id, requesting_user_id=user.id)
        assert still_failed.status == JobStatus.FAILED  # original untouched


def test_retry_rejected_when_error_is_not_retryable(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)
        original = jobs.create_job(project.id, requesting_user_id=user.id)
        _fail_job(session, original.id, "authentication")

        with pytest.raises(InvalidStateError, match="not retryable"):
            jobs.retry_job(original.id, requesting_user_id=user.id)


def test_retry_rejected_when_job_is_not_failed(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, user.id)
        job = jobs.create_job(project.id, requesting_user_id=user.id)  # QUEUED

        with pytest.raises(InvalidStateError, match="not failed"):
            jobs.retry_job(job.id, requesting_user_id=user.id)


def test_get_nonexistent_job_raises_not_found(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        _projects, _configs, jobs = _make_services(session)

        with pytest.raises(NotFoundError):
            jobs.get_job(999_999, requesting_user_id=user.id)


def test_stranger_cannot_act_on_another_users_job(session_factory):
    with session_scope(session_factory) as session:
        owner = make_user(session, email="owner@example.com")
        stranger = make_user(session, email="stranger@example.com")
        projects, configs, jobs = _make_services(session)
        project = _make_project_with_active_config(projects, configs, owner.id)
        job = jobs.create_job(project.id, requesting_user_id=owner.id)

        with pytest.raises(PermissionDeniedError):
            jobs.get_job(job.id, requesting_user_id=stranger.id)
        with pytest.raises(PermissionDeniedError):
            jobs.cancel_job(job.id, requesting_user_id=stranger.id)
