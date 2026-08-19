"""Database-independent domain objects for projects and their
versioned collection configuration. No SQLAlchemy, no HTTP — these are
plain business concepts, unit-testable without MySQL."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any


class ProjectStatus(StrEnum):
    """The single source of truth for project status values —
    app.db.models.project.Project imports this rather than redefining
    it."""

    ACTIVE = "active"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class Project:
    id: int | None
    user_id: int
    name: str
    source_type: str
    status: ProjectStatus = ProjectStatus.ACTIVE
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Project name must not be empty.")


@dataclass(frozen=True)
class CollectionConfig:
    """`config` is deliberately an opaque dict, never a typed
    provider-specific schema — provider details stay inside the
    provider adapter (T040+), not here."""

    id: int | None
    project_id: int
    provider: str
    config: dict[str, Any]
    version: int
    is_active: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.version < 1:
            raise ValueError("CollectionConfig version must be >= 1.")
