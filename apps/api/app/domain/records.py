"""Database-independent domain objects for records and their
provenance."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Record:
    """`data` is deliberately an opaque dict — provider-specific
    fields are not modeled here. `canonical_key` must never be derived
    from name alone (docs/T025_PROMPT.md). `collected_at` is required,
    not optional — the schema has it NOT NULL (docs/04_DATABASE_DESIGN.md)
    and the repository forwards it as-is at creation time; giving it a
    None default here would only defer the failure to a confusing
    NOT NULL SQL error instead of a clear one at construction time."""

    id: int | None
    project_id: int
    job_id: int
    provider: str
    canonical_key: str
    data: dict[str, Any]
    collected_at: datetime
    provider_record_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.canonical_key.strip():
            raise ValueError("Record canonical_key must not be empty.")


@dataclass(frozen=True)
class RecordDraft:
    """A `Record` before Stage 5 of `docs/08_DATA_PIPELINE_DEEP.md`
    ("Canonical identity", T052) computes its `canonical_key` —
    everything the pipeline knows before that stage. Produced by a
    provider's response mapper (e.g.
    `app.providers.google_maps.mapper.map_place_to_record_draft`,
    T043) combined with job/project context and a collection
    timestamp that a stateless `ProviderAdapter.normalize()` call has
    no way to know on its own — attached by whoever orchestrates
    collection (the worker, T060+)."""

    project_id: int
    job_id: int
    provider: str
    data: dict[str, Any]
    collected_at: datetime
    provider_record_id: str | None = None


@dataclass(frozen=True)
class RecordProvenance:
    """`collected_at` is required for the same reason as on Record —
    the schema has it NOT NULL."""

    id: int | None
    record_id: int
    provider_operation: str
    collected_at: datetime
    source_reference: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
