"""FastAPI dependencies for authentication. Protects downstream routes
— T038's "Protect API routes" — by requiring Depends(get_current_user)."""

from typing import Annotated

from fastapi import Depends, Header, status
from sqlalchemy.orm import Session as DbSession

from app.core.errors import ApiError
from app.db.session import get_db
from app.domain.users import User
from app.repositories.sessions import SqlAlchemySessionRepository
from app.repositories.users import SqlAlchemyUserRepository
from app.services.auth import AuthService


def get_auth_service(db: Annotated[DbSession, Depends(get_db)]) -> AuthService:
    return AuthService(SqlAlchemyUserRepository(db), SqlAlchemySessionRepository(db))


def get_current_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    if authorization is None or not authorization.startswith("Bearer "):
        raise ApiError("Not authenticated.", status.HTTP_401_UNAUTHORIZED)

    token = authorization.removeprefix("Bearer ").strip()
    user = auth_service.get_current_user(token)
    if user is None:
        raise ApiError("Invalid or expired session.", status.HTTP_401_UNAUTHORIZED)
    return user
