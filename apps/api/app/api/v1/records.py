"""Record routes. `GET /records/count` (T071's dashboard "Records"
card) is the only route built here — the full records surface
(`GET /projects/{project_id}/records`, `GET /records/{record_id}`,
per docs/05_API_DESIGN.md) is T075's job (Records UI), not T071's.

Note for whoever adds `GET /records/{record_id}` next: register it
AFTER `/count` (or accept that FastAPI already resolves `/records/count`
correctly regardless of order, since `{record_id}` is typed `int` and
"count" cannot parse as one) — kept literal-first here for clarity."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_record_service
from app.api.envelope import Envelope, envelope
from app.domain.users import User
from app.services.records import RecordService

router = APIRouter(prefix="/records", tags=["records"])


class RecordCountResponse(BaseModel):
    total: int


@router.get("/count", response_model=Envelope[RecordCountResponse])
def get_record_count(
    current_user: Annotated[User, Depends(get_current_user)],
    records: Annotated[RecordService, Depends(get_record_service)],
) -> Envelope[RecordCountResponse]:
    assert current_user.id is not None
    total = records.count_for_user(requesting_user_id=current_user.id)
    return envelope(RecordCountResponse(total=total))
