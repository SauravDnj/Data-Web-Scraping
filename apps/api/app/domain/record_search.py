"""Search/filter/sort parameters for record listing (T036) — plain
domain objects, independent of SQLAlchemy; translated into real
server-side queries by RecordRepository.search()."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class RecordSortField(StrEnum):
    COLLECTED_AT = "collected_at"
    CREATED_AT = "created_at"


@dataclass(frozen=True)
class RecordSort:
    field: RecordSortField = RecordSortField.COLLECTED_AT
    descending: bool = True


@dataclass(frozen=True)
class RecordSearchFilters:
    provider: str | None = None
    collected_after: datetime | None = None
    collected_before: datetime | None = None
    # Interim generic "quality" signal — whether the record resolved a
    # stable provider identifier vs. fell back to a weaker canonical
    # key. A real validation_status/quality field belongs to T051
    # (Validation pipeline, not built yet); this gives T036's "quality
    # filtering" requirement a genuine, working, non-provider-specific
    # implementation now rather than a placeholder.
    has_provider_id: bool | None = None
