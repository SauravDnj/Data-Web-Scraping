"""Database-independent value objects for the provider boundary
(T040). `ConfigValidationResult`/`ProviderConfigValidator` stay in
`app.domain.provider_validation` — that file already exists (added at
T034 to resolve a circular task-graph dependency) and
`ProviderAdapter.validate_config` (app.providers.base) returns the
same `ConfigValidationResult` type, not a duplicate. These are the
remaining pieces T034's docstring said T040 would add: usage
estimation, collection items, normalized output, and error
classification — all pure Python, no SDK, no HTTP, no Google-specific
fields (per docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md's "DO NOT mention
browser automation" / "DO NOT call Google" instructions, which extend
naturally to "don't model Google-specific fields in the generic
contract" — same principle T030 applied to domain entities)."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

# A provider's raw response for one collected entity, before
# normalization — deliberately an opaque mapping, same rationale as
# Record.data (app.domain.records): no provider-specific fields
# modeled in the generic contract.
type RawProviderItem = Mapping[str, Any]


@dataclass(frozen=True)
class UsageEstimate:
    """How much of the provider's budget one `collect()` call for this
    config is expected to consume — checked against the application
    budget (docs/07's lifecycle: estimate → check budget → send
    request) before any request is sent."""

    estimated_units: int
    notes: str | None = None

    def __post_init__(self) -> None:
        if self.estimated_units < 0:
            raise ValueError("UsageEstimate.estimated_units must not be negative.")


@dataclass(frozen=True)
class NormalizedItem:
    """One provider item after `normalize()`, in exactly the shape the
    T052/T053 pipeline needs to build a `Record` — field names
    deliberately match `Record.provider_record_id`/`Record.data`
    (app.domain.records) so that mapping is a direct 1:1 assignment,
    not a rename, when the pipeline tasks land."""

    provider_record_id: str | None
    data: dict[str, Any]


class ProviderErrorCategory(StrEnum):
    """Exactly the 7 categories from
    docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md's "Errors" section — this
    is the authoritative taxonomy `classify_error()` must map into.
    Deliberately generic (no Google-specific error codes here); a real
    adapter's `classify_error()` (T041+) is where SDK-specific
    exceptions get mapped to one of these.

    `app.domain.job_errors.RETRYABLE_ERROR_CLASSES` is a separate,
    already-existing interim retry taxonomy (job-failure classes, not
    provider-error categories) that T044 ("Provider error mapping")
    must reconcile with this one — not something T040 resolves, since
    T040 doesn't touch job retry logic."""

    AUTHENTICATION = "authentication"
    QUOTA = "quota"
    RATE = "rate"
    INVALID_REQUEST = "invalid_request"
    TEMPORARY = "temporary"
    PERMANENT = "permanent"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProviderError:
    """The result of `classify_error()` — never the raw SDK/HTTP
    exception itself, so callers (the worker, T060+) only ever depend
    on this generic shape, never a provider SDK's exception type."""

    category: ProviderErrorCategory
    message: str


@dataclass(frozen=True)
class ProviderHealth:
    """Provider-specific diagnostic status — distinct from T014's
    `/ready` (which checks MySQL/Redis, not any provider). Lets
    operations tooling ask "is this specific adapter reachable/
    configured" independently of the rest of the stack."""

    healthy: bool
    detail: str | None = None
