from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.projects import router as projects_router
from app.api.v1.records import router as records_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(jobs_router)
router.include_router(projects_router)
router.include_router(records_router)

# Remaining business endpoints (configs, exports, schedules) are added
# by their respective tasks — T071 added just enough of jobs/records
# (list + summary/count) for the dashboard; T072 added the full
# projects CRUD surface. Full CRUD for jobs/records, plus
# configs/exports/schedules, land at T073+.
