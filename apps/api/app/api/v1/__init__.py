from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)

# Remaining business endpoints (projects, configs, jobs, records,
# exports, schedules) are added by their respective tasks (T070+, not
# T033-T037 — those built the service layer only, no HTTP routes yet).
