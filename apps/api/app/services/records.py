"""Record search, filtering, sorting, and detail retrieval. No HTTP,
no SQLAlchemy — depends on RecordRepository (T032) and ProjectService
(T033) for authorization. Every query is translated to a server-side
filter/sort/limit by the repository (app.repositories.records) —
never loads a full project's records into memory."""

from app.domain.record_search import RecordSearchFilters, RecordSort
from app.domain.records import Record
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page
from app.repositories.records import RecordRepository
from app.services.errors import NotFoundError
from app.services.projects import ProjectService


class RecordService:
    def __init__(self, records: RecordRepository, projects: ProjectService) -> None:
        self._records = records
        self._projects = projects

    def search_records(
        self,
        project_id: int,
        *,
        requesting_user_id: int,
        filters: RecordSearchFilters | None = None,
        sort: RecordSort | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Record]:
        # Authorization first — unauthorized project records are
        # inaccessible regardless of what filters are supplied.
        self._projects.get_project(project_id, requesting_user_id=requesting_user_id)
        return self._records.search(
            project_id, filters=filters, sort=sort, limit=limit, offset=offset
        )

    def count_for_user(self, *, requesting_user_id: int) -> int:
        """T071's dashboard "Records" card. Cross-project, same as
        `JobService.list_for_user()` — no per-project ownership check
        needed, the repository's join on `requesting_user_id` already
        is the authorization boundary."""
        return self._records.count_for_user(requesting_user_id)

    def get_record(self, record_id: int, *, requesting_user_id: int) -> Record:
        record = self._records.get(record_id)
        if record is None:
            raise NotFoundError("Record", record_id)
        # A record has no user_id of its own — authorization goes
        # through its project's ownership (reuses ProjectService).
        self._projects.get_project(
            record.project_id, requesting_user_id=requesting_user_id
        )
        return record
