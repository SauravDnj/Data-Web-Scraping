from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.dependencies import DependencyStatus, check_database, check_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Process health only — does not touch any dependency. If this
    doesn't return, the process itself is the problem."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(
    database: Annotated[DependencyStatus, Depends(check_database)],
    cache: Annotated[DependencyStatus, Depends(check_redis)],
) -> JSONResponse:
    """Reports each dependency's health separately and clearly, without
    exposing connection strings or credentials."""
    dependencies = [database, cache]
    all_healthy = all(dependency.healthy for dependency in dependencies)

    body = {
        "status": "ok" if all_healthy else "unavailable",
        "dependencies": {
            dependency.name: {
                "healthy": dependency.healthy,
                "detail": dependency.detail,
            }
            for dependency in dependencies
        },
    }
    status_code = (
        status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    )
    return JSONResponse(status_code=status_code, content=body)
