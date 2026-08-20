"""FastAPI dependencies for authentication and business services.
Authentication protects downstream routes — T038's "Protect API
routes" — by requiring Depends(get_current_user). The service
dependencies (added T071, the first business routes beyond auth) are
thin factories only: each wraps the request-scoped `db` session
(`get_db`, T020) in the same repository/service composition already
established and tested at T032-T037 — no new business logic lives
here."""

from typing import Annotated

from fastapi import Depends, Header, status
from sqlalchemy.orm import Session as DbSession

from app.core.config import get_settings
from app.core.errors import ApiError
from app.db.session import get_db
from app.domain.users import User
from app.providers.google_maps.config import GoogleMapsConfigValidator
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.configs import SqlAlchemyCollectionConfigRepository
from app.repositories.jobs import SqlAlchemyJobRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.repositories.records import SqlAlchemyRecordRepository
from app.repositories.sessions import SqlAlchemySessionRepository
from app.repositories.users import SqlAlchemyUserRepository
from app.services.audit import AuditService
from app.services.auth import AuthService
from app.services.configs import ConfigurationService
from app.services.jobs import JobService
from app.services.projects import ProjectService
from app.services.records import RecordService


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


def get_audit_service(db: Annotated[DbSession, Depends(get_db)]) -> AuditService:
    return AuditService(SqlAlchemyAuditLogRepository(db))


def get_project_service(
    db: Annotated[DbSession, Depends(get_db)],
    audit: Annotated[AuditService, Depends(get_audit_service)],
) -> ProjectService:
    return ProjectService(SqlAlchemyProjectRepository(db), audit)


def get_configuration_service(
    db: Annotated[DbSession, Depends(get_db)],
    projects: Annotated[ProjectService, Depends(get_project_service)],
    audit: Annotated[AuditService, Depends(get_audit_service)],
) -> ConfigurationService:
    # V1 is Google-Maps-only (ConfigurationService.SUPPORTED_PROVIDERS)
    # — a single real validator, same as every other place this
    # service is constructed. No ProviderRegistry exists (T040's
    # memory entry: no task asks for one).
    validator = GoogleMapsConfigValidator(get_settings().google_maps_api_key)
    return ConfigurationService(
        SqlAlchemyCollectionConfigRepository(db), projects, validator, audit
    )


def get_job_service(
    db: Annotated[DbSession, Depends(get_db)],
    projects: Annotated[ProjectService, Depends(get_project_service)],
    configs: Annotated[ConfigurationService, Depends(get_configuration_service)],
    audit: Annotated[AuditService, Depends(get_audit_service)],
) -> JobService:
    return JobService(SqlAlchemyJobRepository(db), projects, configs, audit)


def get_record_service(
    db: Annotated[DbSession, Depends(get_db)],
    projects: Annotated[ProjectService, Depends(get_project_service)],
) -> RecordService:
    return RecordService(SqlAlchemyRecordRepository(db), projects)
