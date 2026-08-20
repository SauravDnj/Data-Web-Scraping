"""Job routes: `GET /jobs` (cross-project list, docs/05_API_DESIGN.md)
and `GET /jobs/summary` (T071's dashboard cards). Thin — every field
comes straight from `app.services.jobs.JobService`; no business logic
here. Single-job detail and the action routes (cancel/pause/resume/
retry, also listed in docs/05_API_DESIGN.md) are T074's job (Job UI),
not built here — T071 only needs list + summary."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_job_service
from app.api.envelope import Envelope, envelope
from app.api.pagination import PagedResponse
from app.domain.jobs import Job, JobStatus
from app.domain.users import User
from app.services.jobs import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


class JobCountersResponse(BaseModel):
    total_units: int
    successful_units: int
    failed_units: int
    skipped_units: int
    records_created: int
    records_updated: int
    records_rejected: int


class JobResponse(BaseModel):
    id: int
    project_id: int
    status: str
    counters: JobCountersResponse
    requested_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    error_code: str | None
    error_message: str | None


class JobSummaryResponse(BaseModel):
    active_jobs: int
    completed_jobs: int
    failed_jobs: int


@router.get("/summary", response_model=Envelope[JobSummaryResponse])
def get_job_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    jobs: Annotated[JobService, Depends(get_job_service)],
) -> Envelope[JobSummaryResponse]:
    assert current_user.id is not None
    summary = jobs.summarize_for_user(requesting_user_id=current_user.id)
    return envelope(
        JobSummaryResponse(
            active_jobs=summary.active_jobs,
            completed_jobs=summary.completed_jobs,
            failed_jobs=summary.failed_jobs,
        )
    )


@router.get("", response_model=Envelope[PagedResponse[JobResponse]])
def list_jobs(
    current_user: Annotated[User, Depends(get_current_user)],
    jobs: Annotated[JobService, Depends(get_job_service)],
    status: JobStatus | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> Envelope[PagedResponse[JobResponse]]:
    assert current_user.id is not None
    page = jobs.list_for_user(
        requesting_user_id=current_user.id, status=status, limit=limit, offset=offset
    )
    return envelope(
        PagedResponse(
            items=[_to_job_response(job) for job in page.items],
            total=page.total,
            limit=page.limit,
            offset=page.offset,
        )
    )


def _to_job_response(job: Job) -> JobResponse:
    assert job.id is not None  # always set for a persisted Job
    return JobResponse(
        id=job.id,
        project_id=job.project_id,
        status=job.status.value,
        counters=JobCountersResponse(
            total_units=job.counters.total_units,
            successful_units=job.counters.successful_units,
            failed_units=job.counters.failed_units,
            skipped_units=job.counters.skipped_units,
            records_created=job.counters.records_created,
            records_updated=job.counters.records_updated,
            records_rejected=job.counters.records_rejected,
        ),
        requested_at=job.requested_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        error_code=job.error_code,
        error_message=job.error_message,
    )
