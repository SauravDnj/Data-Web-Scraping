from typing import Protocol

from sqlalchemy import select

from app.db.models import Record as RecordRow
from app.db.models import RecordProvenance as RecordProvenanceRow
from app.domain.record_search import RecordSearchFilters, RecordSort, RecordSortField
from app.domain.records import Record, RecordProvenance
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page, SqlAlchemyRepository

# Hard ceiling on a single page, enforced regardless of what a caller
# asks for — "DO NOT load all records into memory" (T036) holds even
# if a caller bypasses RecordService and calls the repository directly.
MAX_RECORD_PAGE_LIMIT = 200


class RecordRepository(Protocol):
    def get(self, record_id: int) -> Record | None: ...

    def create(self, record: Record) -> Record: ...

    def get_by_canonical_key(
        self, project_id: int, canonical_key: str
    ) -> Record | None: ...

    def list_for_project(
        self,
        project_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Record]: ...

    def search(
        self,
        project_id: int,
        *,
        filters: RecordSearchFilters | None = None,
        sort: RecordSort | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Record]: ...

    def add_provenance(self, provenance: RecordProvenance) -> RecordProvenance: ...


class SqlAlchemyRecordRepository(SqlAlchemyRepository[RecordRow, Record]):
    model = RecordRow

    def _to_domain(self, row: RecordRow) -> Record:
        return Record(
            id=row.id,
            project_id=row.project_id,
            job_id=row.job_id,
            provider=row.provider,
            canonical_key=row.canonical_key,
            data=row.data_json,
            provider_record_id=row.provider_record_id,
            collected_at=row.collected_at,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    def create(self, record: Record) -> Record:
        row = RecordRow(
            project_id=record.project_id,
            job_id=record.job_id,
            provider=record.provider,
            provider_record_id=record.provider_record_id,
            canonical_key=record.canonical_key,
            data_json=record.data,
            collected_at=record.collected_at,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def get_by_canonical_key(
        self, project_id: int, canonical_key: str
    ) -> Record | None:
        """The dedup lookup T053 will use — canonical_key uniqueness
        is project-scoped (docs/16_MEMORY.md, T000 decision)."""
        row = self._session.scalar(
            select(RecordRow).where(
                RecordRow.project_id == project_id,
                RecordRow.canonical_key == canonical_key,
            )
        )
        return self._to_domain(row) if row is not None else None

    def list_for_project(
        self,
        project_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Record]:
        statement = (
            select(RecordRow)
            .where(RecordRow.project_id == project_id)
            .order_by(RecordRow.collected_at.desc())
        )
        return self._paginate(
            statement, limit=min(limit, MAX_RECORD_PAGE_LIMIT), offset=offset
        )

    def search(
        self,
        project_id: int,
        *,
        filters: RecordSearchFilters | None = None,
        sort: RecordSort | None = None,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Record]:
        filters = filters or RecordSearchFilters()
        sort = sort or RecordSort()

        statement = select(RecordRow).where(RecordRow.project_id == project_id)
        if filters.provider is not None:
            statement = statement.where(RecordRow.provider == filters.provider)
        if filters.collected_after is not None:
            statement = statement.where(
                RecordRow.collected_at >= filters.collected_after
            )
        if filters.collected_before is not None:
            statement = statement.where(
                RecordRow.collected_at <= filters.collected_before
            )
        if filters.has_provider_id is True:
            statement = statement.where(RecordRow.provider_record_id.is_not(None))
        elif filters.has_provider_id is False:
            statement = statement.where(RecordRow.provider_record_id.is_(None))

        sort_column = (
            RecordRow.collected_at
            if sort.field == RecordSortField.COLLECTED_AT
            else RecordRow.created_at
        )
        statement = statement.order_by(
            sort_column.desc() if sort.descending else sort_column.asc()
        )

        return self._paginate(
            statement, limit=min(limit, MAX_RECORD_PAGE_LIMIT), offset=offset
        )

    def add_provenance(self, provenance: RecordProvenance) -> RecordProvenance:
        row = RecordProvenanceRow(
            record_id=provenance.record_id,
            provider_operation=provenance.provider_operation,
            collected_at=provenance.collected_at,
            source_reference=provenance.source_reference,
            metadata_json=provenance.metadata,
        )
        self._session.add(row)
        self._session.flush()
        return RecordProvenance(
            id=row.id,
            record_id=row.record_id,
            provider_operation=row.provider_operation,
            collected_at=row.collected_at,
            source_reference=row.source_reference,
            metadata=row.metadata_json,
        )
