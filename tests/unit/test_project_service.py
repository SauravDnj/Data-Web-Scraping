"""T033 tests: project business rules and authorization boundaries —
against SQLite in-memory via the real repositories (T032), same
rationale as tests/unit/test_db_session.py."""

import pytest
from tests.unit.factories import make_user

from app.db.session import session_scope
from app.domain.projects import ProjectStatus
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.services.errors import InvalidStateError, NotFoundError, PermissionDeniedError
from app.services.projects import ProjectService


def _make_service(session) -> ProjectService:
    return ProjectService(
        SqlAlchemyProjectRepository(session), SqlAlchemyAuditLogRepository(session)
    )


def test_create_project_succeeds_and_records_audit_event(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        service = _make_service(session)

        project = service.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )
        assert project.id is not None
        assert project.status == ProjectStatus.ACTIVE

        audit = SqlAlchemyAuditLogRepository(session).list_for_user(user.id)
        assert audit.total == 1
        assert audit.items[0].action == "project.created"
        assert audit.items[0].entity_id == project.id


def test_create_project_rejects_empty_name(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        service = _make_service(session)

        with pytest.raises(ValueError, match="name"):
            service.create_project(
                user_id=user.id, name="   ", source_type="google_maps"
            )


def test_user_cannot_access_another_users_project(session_factory):
    with session_scope(session_factory) as session:
        owner = make_user(session, email="owner@example.com")
        stranger = make_user(session, email="stranger@example.com")
        service = _make_service(session)
        project = service.create_project(
            user_id=owner.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(PermissionDeniedError):
            service.get_project(project.id, requesting_user_id=stranger.id)


def test_get_nonexistent_project_raises_not_found(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        service = _make_service(session)

        with pytest.raises(NotFoundError):
            service.get_project(999_999, requesting_user_id=user.id)


def test_update_project_changes_fields_and_records_audit_event(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        service = _make_service(session)
        project = service.create_project(
            user_id=user.id, name="Old Name", source_type="google_maps"
        )

        updated = service.update_project(
            project.id, requesting_user_id=user.id, name="New Name"
        )
        assert updated.name == "New Name"

        audit = SqlAlchemyAuditLogRepository(session).list_for_user(user.id)
        assert any(entry.action == "project.updated" for entry in audit.items)


def test_update_project_rejects_empty_name(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        service = _make_service(session)
        project = service.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(ValueError, match="name"):
            service.update_project(project.id, requesting_user_id=user.id, name="   ")


def test_stranger_cannot_update_another_users_project(session_factory):
    with session_scope(session_factory) as session:
        owner = make_user(session, email="owner@example.com")
        stranger = make_user(session, email="stranger@example.com")
        service = _make_service(session)
        project = service.create_project(
            user_id=owner.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(PermissionDeniedError):
            service.update_project(
                project.id, requesting_user_id=stranger.id, name="Hijacked"
            )


def test_archive_project_sets_status_and_records_audit_event(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        service = _make_service(session)
        project = service.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        archived = service.archive_project(project.id, requesting_user_id=user.id)
        assert archived.status == ProjectStatus.ARCHIVED

        audit = SqlAlchemyAuditLogRepository(session).list_for_user(user.id)
        assert any(entry.action == "project.archived" for entry in audit.items)


def test_archived_project_cannot_start_new_jobs(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        service = _make_service(session)
        project = service.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )
        service.archive_project(project.id, requesting_user_id=user.id)

        with pytest.raises(InvalidStateError):
            service.ensure_can_start_job(project.id, requesting_user_id=user.id)


def test_active_project_can_start_new_jobs(session_factory):
    with session_scope(session_factory) as session:
        user = make_user(session)
        service = _make_service(session)
        project = service.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        checked = service.ensure_can_start_job(project.id, requesting_user_id=user.id)
        assert checked.status == ProjectStatus.ACTIVE


def test_list_projects_only_returns_requesting_users_projects(session_factory):
    with session_scope(session_factory) as session:
        owner = make_user(session, email="owner@example.com")
        other = make_user(session, email="other@example.com")
        service = _make_service(session)
        service.create_project(user_id=owner.id, name="Mine", source_type="google_maps")
        service.create_project(
            user_id=other.id, name="Theirs", source_type="google_maps"
        )

        page = service.list_projects(requesting_user_id=owner.id)
        assert page.total == 1
        assert page.items[0].name == "Mine"
