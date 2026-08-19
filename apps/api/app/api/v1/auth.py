"""Authentication routes: login, logout, current-user check. The
first real /api/v1 business endpoints (T038) — establishes the
success-envelope pattern (app.api.envelope) later routes should
follow."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, status
from pydantic import BaseModel

from app.api.dependencies import get_auth_service, get_current_user
from app.api.envelope import Envelope, envelope
from app.core.errors import ApiError
from app.domain.users import User
from app.services.auth import AuthService
from app.services.errors import PermissionDeniedError

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_at: str


class CurrentUserResponse(BaseModel):
    id: int
    email: str
    status: str


@router.post("/login", response_model=Envelope[LoginResponse])
def login(
    payload: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Envelope[LoginResponse]:
    try:
        issued = auth_service.login(payload.email, payload.password)
    except PermissionDeniedError as exc:
        raise ApiError(str(exc), status.HTTP_401_UNAUTHORIZED) from exc

    return envelope(
        LoginResponse(
            token=issued.token, expires_at=issued.session.expires_at.isoformat()
        )
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> None:
    if authorization is not None and authorization.startswith("Bearer "):
        auth_service.logout(authorization.removeprefix("Bearer ").strip())


@router.get("/me", response_model=Envelope[CurrentUserResponse])
def me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> Envelope[CurrentUserResponse]:
    assert current_user.id is not None
    return envelope(
        CurrentUserResponse(
            id=current_user.id,
            email=current_user.email,
            status=current_user.status.value,
        )
    )
