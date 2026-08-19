from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

# Business endpoints (projects, configs, jobs, records, exports,
# schedules) are added by their respective tasks (T033+), not here.
