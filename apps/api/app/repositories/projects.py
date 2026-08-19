from typing import Protocol

from sqlalchemy import select

from app.db.models import Project as ProjectRow
from app.domain.projects import Project, ProjectStatus
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page, SqlAlchemyRepository


class ProjectRepository(Protocol):
    def get(self, project_id: int) -> Project | None: ...

    def create(self, project: Project) -> Project: ...

    def list_for_user(
        self,
        user_id: int,
        *,
        status: ProjectStatus | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Project]: ...

    def update_fields(
        self,
        project_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> Project: ...

    def set_status(self, project_id: int, status: ProjectStatus) -> Project: ...


class SqlAlchemyProjectRepository(SqlAlchemyRepository[ProjectRow, Project]):
    model = ProjectRow

    def _to_domain(self, row: ProjectRow) -> Project:
        return Project(
            id=row.id,
            user_id=row.user_id,
            name=row.name,
            source_type=row.source_type,
            status=ProjectStatus(row.status),
            description=row.description,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def create(self, project: Project) -> Project:
        row = ProjectRow(
            user_id=project.user_id,
            name=project.name,
            source_type=project.source_type,
            status=project.status,
            description=project.description,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def list_for_user(
        self,
        user_id: int,
        *,
        status: ProjectStatus | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Project]:
        statement = select(ProjectRow).where(ProjectRow.user_id == user_id)
        if status is not None:
            statement = statement.where(ProjectRow.status == status)
        statement = statement.order_by(ProjectRow.created_at.desc())
        return self._paginate(statement, limit=limit, offset=offset)

    def update_fields(
        self,
        project_id: int,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> Project:
        row = self._session.get(ProjectRow, project_id)
        if row is None:
            raise LookupError(f"Project {project_id} does not exist.")
        if name is not None:
            row.name = name
        if description is not None:
            row.description = description
        self._session.flush()
        return self._to_domain(row)

    def set_status(self, project_id: int, status: ProjectStatus) -> Project:
        row = self._session.get(ProjectRow, project_id)
        if row is None:
            raise LookupError(f"Project {project_id} does not exist.")
        row.status = status
        self._session.flush()
        return self._to_domain(row)
