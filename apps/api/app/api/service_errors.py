"""Maps app.services.errors.ServiceError subclasses to HTTP responses
(T039). Lives in app.api, not app.core.errors, because app.core must
not depend on app.services (see app/core/errors.py's layering — every
existing app.core import stays within app.core). Without this, every
future project-scoped route (T070+) would need to catch
NotFoundError/PermissionDeniedError/InvalidStateError manually or leak
them as unhandled 500s — app.api.v1.auth.py already had to do this by
hand for login, which is exactly the duplication this centralizes."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.core.request_context import get_request_id
from app.services.errors import InvalidStateError, NotFoundError, PermissionDeniedError


def _error_response(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {"message": message},
            "request_id": get_request_id(),
        },
    )


def register_service_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def handle_not_found(_: Request, exc: NotFoundError) -> JSONResponse:
        return _error_response(str(exc), status.HTTP_404_NOT_FOUND)

    @app.exception_handler(PermissionDeniedError)
    async def handle_permission_denied(
        _: Request, exc: PermissionDeniedError
    ) -> JSONResponse:
        # Not 401: by the time a service raises this, the caller is
        # already authenticated (T038) — this is "authenticated but
        # not authorized for this specific resource."
        return _error_response(str(exc), status.HTTP_403_FORBIDDEN)

    @app.exception_handler(InvalidStateError)
    async def handle_invalid_state(_: Request, exc: InvalidStateError) -> JSONResponse:
        return _error_response(str(exc), status.HTTP_409_CONFLICT)
