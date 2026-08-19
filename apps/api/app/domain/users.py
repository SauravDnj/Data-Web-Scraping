"""Database-independent domain object for users. Centralizes
UserStatus here (T030 didn't — its entity list never included User;
this is the same "centralize when actually needed" pattern as
T037 adding AuditLogEntry). app.db.models.user.User imports
UserStatus from here rather than redefining it."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    PENDING = "pending"


@dataclass(frozen=True)
class User:
    id: int | None
    email: str
    password_hash: str
    status: UserStatus = UserStatus.PENDING
    name: str | None = None
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
