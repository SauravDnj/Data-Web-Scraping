from typing import Protocol

from sqlalchemy import select

from app.db.models import CollectionConfig as CollectionConfigRow
from app.domain.projects import CollectionConfig
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page, SqlAlchemyRepository


class CollectionConfigRepository(Protocol):
    def get(self, config_id: int) -> CollectionConfig | None: ...

    def create(self, config: CollectionConfig) -> CollectionConfig: ...

    def get_active_for_project(self, project_id: int) -> CollectionConfig | None: ...

    def list_for_project(
        self,
        project_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[CollectionConfig]: ...


class SqlAlchemyCollectionConfigRepository(
    SqlAlchemyRepository[CollectionConfigRow, CollectionConfig]
):
    model = CollectionConfigRow

    def _to_domain(self, row: CollectionConfigRow) -> CollectionConfig:
        return CollectionConfig(
            id=row.id,
            project_id=row.project_id,
            provider=row.provider,
            config=row.config_json,
            version=row.version,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def create(self, config: CollectionConfig) -> CollectionConfig:
        """One immutable row per version — never call this to update
        an existing config, only to add a new version
        (docs/16_MEMORY.md, T023)."""
        row = CollectionConfigRow(
            project_id=config.project_id,
            provider=config.provider,
            config_json=config.config,
            version=config.version,
            is_active=config.is_active,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def get_active_for_project(self, project_id: int) -> CollectionConfig | None:
        row = self._session.scalar(
            select(CollectionConfigRow).where(
                CollectionConfigRow.project_id == project_id,
                CollectionConfigRow.is_active.is_(True),
            )
        )
        return self._to_domain(row) if row is not None else None

    def list_for_project(
        self,
        project_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[CollectionConfig]:
        statement = (
            select(CollectionConfigRow)
            .where(CollectionConfigRow.project_id == project_id)
            .order_by(CollectionConfigRow.version.desc())
        )
        return self._paginate(statement, limit=limit, offset=offset)
