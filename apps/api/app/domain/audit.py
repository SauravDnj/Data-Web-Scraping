"""Database-independent domain object for audit log entries. Added at
T032 (not T030 — T030's entity list didn't include User/AuditLog, but
the audit repository needs a domain type to return, same as every
other repository)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class AuditLogEntry:
    """`user_id` None means a system-initiated action, not a missing
    field — audit rows are append-only and never mutated after
    creation."""

    id: int | None
    action: str
    entity_type: str
    user_id: int | None = None
    entity_id: int | None = None
    details: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.action.strip():
            raise ValueError("AuditLogEntry action must not be empty.")
        if not self.entity_type.strip():
            raise ValueError("AuditLogEntry entity_type must not be empty.")
