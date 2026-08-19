from typing import Protocol

from sqlalchemy import select

from app.db.models import AuditLog as AuditLogRow
from app.domain.audit import AuditLogEntry
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page, SqlAlchemyRepository


class AuditLogRepository(Protocol):
    def create(self, entry: AuditLogEntry) -> AuditLogEntry: ...

    def list_for_user(
        self,
        user_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[AuditLogEntry]: ...

    def list_for_entity(
        self,
        entity_type: str,
        entity_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[AuditLogEntry]: ...


class SqlAlchemyAuditLogRepository(SqlAlchemyRepository[AuditLogRow, AuditLogEntry]):
    """Append-only — deliberately no update/delete method. Audit
    entries are a record of what happened, not mutable state."""

    model = AuditLogRow

    def _to_domain(self, row: AuditLogRow) -> AuditLogEntry:
        return AuditLogEntry(
            id=row.id,
            user_id=row.user_id,
            action=row.action,
            entity_type=row.entity_type,
            entity_id=row.entity_id,
            details=row.details_json,
            created_at=row.created_at,
        )

    def create(self, entry: AuditLogEntry) -> AuditLogEntry:
        row = AuditLogRow(
            user_id=entry.user_id,
            action=entry.action,
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            details_json=entry.details,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def list_for_user(
        self,
        user_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[AuditLogEntry]:
        statement = (
            select(AuditLogRow)
            .where(AuditLogRow.user_id == user_id)
            .order_by(AuditLogRow.created_at.desc())
        )
        return self._paginate(statement, limit=limit, offset=offset)

    def list_for_entity(
        self,
        entity_type: str,
        entity_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[AuditLogEntry]:
        """The full history of one entity — "what happened to this
        project/job", not scoped to a single actor."""
        statement = (
            select(AuditLogRow)
            .where(
                AuditLogRow.entity_type == entity_type,
                AuditLogRow.entity_id == entity_id,
            )
            .order_by(AuditLogRow.created_at.desc())
        )
        return self._paginate(statement, limit=limit, offset=offset)
