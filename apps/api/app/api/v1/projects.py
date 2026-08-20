"""Project routes — the full CRUD surface docs/05_API_DESIGN.md lists
(`GET/POST /projects`, `GET/PATCH/DELETE /projects/{project_id}`),
built directly on `app.services.projects.ProjectService` (T033,
already fully tested). `DELETE` maps to `archive_project()` — the
service has always been archive-only by design ("Archive rather than
destructively delete — no delete method exists", ProjectService's own
docstring); there is no row-deletion path anywhere in this codebase
for a project, so `DELETE` here is a soft delete, not a hard one."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi import status as http_status
from pydantic import BaseModel, field_validator

from app.api.dependencies import get_current_user, get_project_service
from app.api.envelope import Envelope, envelope
from app.api.pagination import PagedResponse
from app.domain.projects import Project, ProjectStatus
from app.domain.users import User
from app.services.projects import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectResponse(BaseModel):
    id: int
    name: str
    source_type: str
    status: str
    description: str | None
    created_at: datetime | None
    updated_at: datetime | None


def _to_response(project: Project) -> ProjectResponse:
    assert project.id is not None  # always set for a persisted Project
    return ProjectResponse(
        id=project.id,
        name=project.name,
        source_type=project.source_type,
        status=project.status.value,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


def _non_empty_name(value: str) -> str:
    if not value.strip():
        raise ValueError("Project name must not be empty.")
    return value


class CreateProjectRequest(BaseModel):
    name: str
    source_type: str
    description: str | None = None

    _validate_name = field_validator("name")(_non_empty_name)


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None

    _validate_name = field_validator("name")(
        lambda value: _non_empty_name(value) if value is not None else value
    )


@router.get("", response_model=Envelope[PagedResponse[ProjectResponse]])
def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    projects: Annotated[ProjectService, Depends(get_project_service)],
    status_filter: Annotated[ProjectStatus | None, Query(alias="status")] = None,
) -> Envelope[PagedResponse[ProjectResponse]]:
    assert current_user.id is not None
    page = projects.list_projects(
        requesting_user_id=current_user.id, status=status_filter
    )
    return envelope(
        PagedResponse(
            items=[_to_response(project) for project in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
    )


@router.post(
    "",
    response_model=Envelope[ProjectResponse],
    status_code=http_status.HTTP_201_CREATED,
)
def create_project(
    payload: CreateProjectRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> Envelope[ProjectResponse]:
    assert current_user.id is not None
    created = projects.create_project(
        user_id=current_user.id,
        name=payload.name,
        source_type=payload.source_type,
        description=payload.description,
    )
    return envelope(_to_response(created))


@router.get("/{project_id}", response_model=Envelope[ProjectResponse])
def get_project(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> Envelope[ProjectResponse]:
    assert current_user.id is not None
    project = projects.get_project(project_id, requesting_user_id=current_user.id)
    return envelope(_to_response(project))


@router.patch("/{project_id}", response_model=Envelope[ProjectResponse])
def update_project(
    project_id: int,
    payload: UpdateProjectRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> Envelope[ProjectResponse]:
    assert current_user.id is not None
    updated = projects.update_project(
        project_id,
        requesting_user_id=current_user.id,
        name=payload.name,
        description=payload.description,
    )
    return envelope(_to_response(updated))


@router.delete("/{project_id}", response_model=Envelope[ProjectResponse])
def archive_project(
    project_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> Envelope[ProjectResponse]:
    assert current_user.id is not None
    archived = projects.archive_project(project_id, requesting_user_id=current_user.id)
    return envelope(_to_response(archived))
