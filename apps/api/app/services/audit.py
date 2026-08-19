"""Centralized audit event recording and querying. Every service that
records an audit event goes through this one, not AuditLogRepository
directly — that's what guarantees action names come from
app.domain.audit_actions.AuditAction (not ad-hoc strings) and details
are redacted (app.domain.audit_redaction) before they're ever
persisted. No HTTP, no SQLAlchemy."""

from typing import Any

from app.domain.audit import AuditLogEntry
from app.domain.audit_actions import AuditAction
from app.domain.audit_redaction import redact_details
from app.repositories.audit import AuditLogRepository
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page


class AuditService:
    def __init__(self, audit_log: AuditLogRepository) -> None:
        self._audit_log = audit_log

    def record_event(
        self,
        *,
        actor_user_id: int | None,
        action: AuditAction,
        entity_type: str,
        entity_id: int | None,
        details: dict[str, Any] | None = None,
    ) -> AuditLogEntry:
        return self._audit_log.create(
            AuditLogEntry(
                id=None,
                user_id=actor_user_id,
                action=action.value,
                entity_type=entity_type,
                entity_id=entity_id,
                details=redact_details(details or {}),
            )
        )

    def list_for_user(
        self, user_id: int, *, limit: int = DEFAULT_PAGE_LIMIT, offset: int = 0
    ) -> Page[AuditLogEntry]:
        return self._audit_log.list_for_user(user_id, limit=limit, offset=offset)

    def list_for_entity(
        self,
        entity_type: str,
        entity_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[AuditLogEntry]:
        return self._audit_log.list_for_entity(
            entity_type, entity_id, limit=limit, offset=offset
        )
