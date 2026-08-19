"""Project business rules and authorization boundaries. No HTTP, no
SQLAlchemy — depends only on repository Protocols (T032) and domain
objects (T030), so it's unit-testable without a real API or database."""

from typing import Any

from app.domain.audit import AuditLogEntry
from app.domain.projects import Project, ProjectStatus
from app.repositories.audit import AuditLogRepository
from app.repositories.base import Page
from app.repositories.projects import ProjectRepository
from app.services.errors import InvalidStateError, NotFoundError, PermissionDeniedError


class ProjectService:
    def __init__(
        self, projects: ProjectRepository, audit_log: AuditLogRepository
    ) -> None:
        self._projects = projects
        self._audit_log = audit_log

    def create_project(
        self,
        *,
        user_id: int,
        name: str,
        source_type: str,
        description: str | None = None,
    ) -> Project:
        # Project.__post_init__ (T030) already rejects an empty name.
        project = Project(
            id=None,
            user_id=user_id,
            name=name,
            source_type=source_type,
            description=description,
        )
        created = self._projects.create(project)
        self._record_audit_event(
            user_id, "project.created", created.id, {"name": created.name}
        )
        return created

    def get_project(self, project_id: int, *, requesting_user_id: int) -> Project:
        project = self._require_project(project_id)
        self._require_owner(project, requesting_user_id)
        return project

    def list_projects(
        self, *, requesting_user_id: int, status: ProjectStatus | None = None
    ) -> Page[Project]:
        return self._projects.list_for_user(requesting_user_id, status=status)

    def update_project(
        self,
        project_id: int,
        *,
        requesting_user_id: int,
        name: str | None = None,
        description: str | None = None,
    ) -> Project:
        project = self._require_project(project_id)
        self._require_owner(project, requesting_user_id)

        if name is not None and not name.strip():
            raise ValueError("Project name must not be empty.")

        updated = self._projects.update_fields(
            project_id, name=name, description=description
        )
        changed = {
            key: value
            for key, value in {"name": name, "description": description}.items()
            if value is not None
        }
        self._record_audit_event(
            requesting_user_id, "project.updated", project_id, changed
        )
        return updated

    def archive_project(self, project_id: int, *, requesting_user_id: int) -> Project:
        """Archive rather than destructively delete — no delete method
        exists on this service or on ProjectRepository."""
        project = self._require_project(project_id)
        self._require_owner(project, requesting_user_id)

        archived = self._projects.set_status(project_id, ProjectStatus.ARCHIVED)
        self._record_audit_event(requesting_user_id, "project.archived", project_id, {})
        return archived

    def ensure_can_start_job(
        self, project_id: int, *, requesting_user_id: int
    ) -> Project:
        """Guard for the job service (T035) to call before creating a
        job. Kept here rather than duplicated there, since "can this
        project start work" is a project-level business rule."""
        project = self.get_project(project_id, requesting_user_id=requesting_user_id)
        if project.status == ProjectStatus.ARCHIVED:
            raise InvalidStateError(
                f"Project {project_id} is archived and cannot start new jobs."
            )
        return project

    def _require_project(self, project_id: int) -> Project:
        project = self._projects.get(project_id)
        if project is None:
            raise NotFoundError("Project", project_id)
        return project

    def _require_owner(self, project: Project, requesting_user_id: int) -> None:
        if project.user_id != requesting_user_id:
            raise PermissionDeniedError(
                f"User {requesting_user_id} cannot access project {project.id}."
            )

    def _record_audit_event(
        self,
        user_id: int,
        action: str,
        entity_id: int | None,
        details: dict[str, Any],
    ) -> None:
        self._audit_log.create(
            AuditLogEntry(
                id=None,
                user_id=user_id,
                action=action,
                entity_type="project",
                entity_id=entity_id,
                details=details,
            )
        )
