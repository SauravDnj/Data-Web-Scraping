"""The generic provider boundary (T040) — the application depends on
this, never on a specific provider SDK. Method names/order match the
conceptual interface and lifecycle in
docs/07_PROVIDER_AND_GOOGLE_WORKFLOW.md exactly (validate → estimate →
collect → normalize; classify_error handles the failure path), and the
`validate_config`/`estimate`/`collect`/`normalize`/`classify_error`
naming was fixed at T000 (docs/16_MEMORY.md, "Resolved design
decisions") specifically so a future `GoogleMapsProvider` (T041-T044)
implements this contract exactly rather than inventing its own names.

DO NOT import a provider SDK, an HTTP client, or a browser-automation
library here — this module must stay implementation-free, per T040's
own instruction ("DO NOT mention browser automation in generic
interface; DO NOT call Google")."""

from collections.abc import Iterator
from typing import Any, Protocol, runtime_checkable

from app.domain.provider_contracts import (
    NormalizedItem,
    ProviderError,
    ProviderHealth,
    RawProviderItem,
    UsageEstimate,
)
from app.domain.provider_validation import ConfigValidationResult


@runtime_checkable
class ProviderAdapter(Protocol):
    """One instance represents one specific provider (e.g. Google
    Maps) — unlike `app.domain.provider_validation.
    ProviderConfigValidator`, which `ConfigurationService` uses as a
    provider-agnostic dispatcher across possibly many registered
    adapters (docs/07's future `ProviderRegistry`, not built here —
    out of T040's scope, no task lists it yet). A concrete adapter
    naturally supplies `ProviderConfigValidator`'s
    `validate_config(provider, config)` shape too, by ignoring
    `provider` (it already knows which one it is) — nothing about
    that dispatch registry needs to exist for this Protocol to be
    useful today."""

    def validate_config(self, config: dict[str, Any]) -> ConfigValidationResult:
        """Structural/semantic validation of this provider's own
        config shape — no network call."""
        ...

    def estimate(self, config: dict[str, Any]) -> UsageEstimate:
        """How much of the provider's budget `collect()` would use for
        this config — checked against the application budget before
        any request is sent (docs/07's lifecycle)."""
        ...

    def collect(self, config: dict[str, Any]) -> Iterator[RawProviderItem]:
        """Yields raw items one at a time rather than returning a
        buffered list — a real adapter paginating through thousands of
        results must not require the whole response in memory at once
        (same "never load everything into memory" principle T036
        applied to `RecordService`/`RecordRepository`)."""
        ...

    def normalize(self, raw_item: RawProviderItem) -> NormalizedItem:
        """Maps one raw item from `collect()` into the
        provider-agnostic shape the pipeline (T052/T053) turns into a
        `Record`. Never raises for malformed input — an item this
        can't make sense of is a normalization/validation-pipeline
        concern (T051), not this method's."""
        ...

    def classify_error(self, error: Exception) -> ProviderError:
        """Maps an exception raised during `collect()` (a provider
        SDK/HTTP error, never exposed to callers directly) into one of
        the 7 generic categories in
        `app.domain.provider_contracts.ProviderErrorCategory`."""
        ...

    def health_check(self) -> ProviderHealth:
        """Provider-specific reachability/configuration diagnostic —
        distinct from T014's `/ready` (MySQL/Redis only)."""
        ...
