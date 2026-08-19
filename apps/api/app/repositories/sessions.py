from datetime import datetime
from typing import Protocol

from sqlalchemy import select

from app.db.models import Session as SessionRow
from app.domain.auth import AuthSession
from app.repositories.base import SqlAlchemyRepository


class SessionRepository(Protocol):
    def create(self, session: AuthSession) -> AuthSession: ...

    def get_by_token_hash(self, token_hash: str) -> AuthSession | None: ...

    def revoke(self, session_id: int, *, revoked_at: datetime) -> AuthSession: ...


class SqlAlchemySessionRepository(SqlAlchemyRepository[SessionRow, AuthSession]):
    model = SessionRow

    def _to_domain(self, row: SessionRow) -> AuthSession:
        return AuthSession(
            id=row.id,
            user_id=row.user_id,
            token_hash=row.token_hash,
            expires_at=row.expires_at,
            created_at=row.created_at,
            revoked_at=row.revoked_at,
        )

    def create(self, session: AuthSession) -> AuthSession:
        row = SessionRow(
            user_id=session.user_id,
            token_hash=session.token_hash,
            expires_at=session.expires_at,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def get_by_token_hash(self, token_hash: str) -> AuthSession | None:
        row = self._session.scalar(
            select(SessionRow).where(SessionRow.token_hash == token_hash)
        )
        return self._to_domain(row) if row is not None else None

    def revoke(self, session_id: int, *, revoked_at: datetime) -> AuthSession:
        row = self._session.get(SessionRow, session_id)
        if row is None:
            raise LookupError(f"Session {session_id} does not exist.")
        row.revoked_at = revoked_at
        self._session.flush()
        return self._to_domain(row)
