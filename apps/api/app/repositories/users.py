from datetime import datetime
from typing import Protocol

from sqlalchemy import select

from app.db.models import User as UserRow
from app.domain.users import User, UserStatus
from app.repositories.base import SqlAlchemyRepository


class UserRepository(Protocol):
    def get(self, user_id: int) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def record_failed_login(
        self, user_id: int, *, locked_until: datetime | None = None
    ) -> User: ...

    def reset_failed_logins(self, user_id: int) -> User: ...


class SqlAlchemyUserRepository(SqlAlchemyRepository[UserRow, User]):
    model = UserRow

    def _to_domain(self, row: UserRow) -> User:
        return User(
            id=row.id,
            email=row.email,
            password_hash=row.password_hash,
            status=UserStatus(row.status),
            name=row.name,
            failed_login_attempts=row.failed_login_attempts,
            locked_until=row.locked_until,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def get_by_email(self, email: str) -> User | None:
        row = self._session.scalar(select(UserRow).where(UserRow.email == email))
        return self._to_domain(row) if row is not None else None

    def record_failed_login(
        self, user_id: int, *, locked_until: datetime | None = None
    ) -> User:
        row = self._session.get(UserRow, user_id)
        if row is None:
            raise LookupError(f"User {user_id} does not exist.")
        row.failed_login_attempts += 1
        if locked_until is not None:
            row.locked_until = locked_until
        self._session.flush()
        return self._to_domain(row)

    def reset_failed_logins(self, user_id: int) -> User:
        row = self._session.get(UserRow, user_id)
        if row is None:
            raise LookupError(f"User {user_id} does not exist.")
        row.failed_login_attempts = 0
        row.locked_until = None
        self._session.flush()
        return self._to_domain(row)
