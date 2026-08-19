"""Database-independent domain objects for records and their
provenance."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Record:
    """`data` is deliberately an opaque dict — provider-specific
    fields are not modeled here. `canonical_key` must never be derived
    from name alone (docs/T025_PROMPT.md)."""

    id: int | None
    project_id: int
    job_id: int
    provider: str
    canonical_key: str
    data: dict[str, Any]
    provider_record_id: str | None = None
    collected_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.canonical_key.strip():
            raise ValueError("Record canonical_key must not be empty.")


@dataclass(frozen=True)
class RecordProvenance:
    id: int | None
    record_id: int
    provider_operation: str
    collected_at: datetime | None = None
    source_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
