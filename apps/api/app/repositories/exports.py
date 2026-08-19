from datetime import datetime
from typing import Protocol

from sqlalchemy import select

from app.db.models import Export as ExportRow
from app.domain.exports import Export, ExportStatus
from app.repositories.base import DEFAULT_PAGE_LIMIT, Page, SqlAlchemyRepository


class ExportRepository(Protocol):
    def get(self, export_id: int) -> Export | None: ...

    def create(self, export: Export) -> Export: ...

    def update_status(
        self,
        export_id: int,
        status: ExportStatus,
        *,
        file_path: str | None = None,
        completed_at: datetime | None = None,
    ) -> Export: ...

    def list_for_project(
        self,
        project_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Export]: ...


class SqlAlchemyExportRepository(SqlAlchemyRepository[ExportRow, Export]):
    model = ExportRow

    def _to_domain(self, row: ExportRow) -> Export:
        return Export(
            id=row.id,
            project_id=row.project_id,
            requested_by=row.requested_by,
            format=row.format,
            status=ExportStatus(row.status),
            filters=row.filters_json,
            file_path=row.file_path,
            created_at=row.created_at,
            completed_at=row.completed_at,
        )

    def create(self, export: Export) -> Export:
        row = ExportRow(
            project_id=export.project_id,
            requested_by=export.requested_by,
            format=export.format,
            status=export.status,
            filters_json=export.filters,
        )
        self._session.add(row)
        self._session.flush()
        return self._to_domain(row)

    def update_status(
        self,
        export_id: int,
        status: ExportStatus,
        *,
        file_path: str | None = None,
        completed_at: datetime | None = None,
    ) -> Export:
        row = self._session.get(ExportRow, export_id)
        if row is None:
            raise LookupError(f"Export {export_id} does not exist.")
        row.status = status
        if file_path is not None:
            row.file_path = file_path
        if completed_at is not None:
            row.completed_at = completed_at
        self._session.flush()
        return self._to_domain(row)

    def list_for_project(
        self,
        project_id: int,
        *,
        limit: int = DEFAULT_PAGE_LIMIT,
        offset: int = 0,
    ) -> Page[Export]:
        statement = (
            select(ExportRow)
            .where(ExportRow.project_id == project_id)
            .order_by(ExportRow.created_at.desc())
        )
        return self._paginate(statement, limit=limit, offset=offset)
