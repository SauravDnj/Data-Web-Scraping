"""`GoogleMapsProvider` (T045) — composes every piece built across
T041-T044 into one object satisfying `app.providers.base.
ProviderAdapter` (T040's Protocol) end to end. The first, and so far
only, concrete `ProviderAdapter` in the codebase; `tests/unit/fakes.
FakeProviderAdapter` is a separate, deliberately independent
implementation used for testing code that depends on the Protocol
generically (T040), not on Google specifically.

Each method here is a thin delegation to the module that actually
implements it — this class adds no new business logic of its own,
only composition:

-   `validate_config` → `GoogleMapsConfigValidator` (T041)
-   `collect`         → `GoogleMapsClient.search_text` (T042)
-   `normalize`        → `normalize_place` (T043)
-   `classify_error`   → `classify_google_maps_error` (T044)

`estimate`/`health_check` have no prior implementation anywhere (no
task before T045 claimed them) — both are written here, honestly
scoped: Google's Places API (New) exposes no pre-call usage-estimate
endpoint (verified against the same live docs fetched for
T041/T042/T043), so `estimate()` reports exactly the bounded
`max_results` the config itself asks for, not a real prediction.
`health_check()` only confirms this adapter was constructed with a
credential — it deliberately does not spend real API quota on a live
request just to answer a routine health check; no task asks for that,
and inventing it would be scope creep."""

from collections.abc import Iterator
from typing import Any

import httpx

from app.domain.provider_contracts import (
    NormalizedItem,
    ProviderError,
    ProviderErrorCategory,
    ProviderHealth,
    RawProviderItem,
    UsageEstimate,
)
from app.domain.provider_validation import ConfigValidationResult
from app.providers.google_maps.client import GoogleMapsApiError, GoogleMapsClient
from app.providers.google_maps.config import MAX_RESULT_COUNT, GoogleMapsConfigValidator
from app.providers.google_maps.errors import classify_google_maps_error
from app.providers.google_maps.mapper import normalize_place


class GoogleMapsProvider:
    def __init__(
        self,
        api_key: str,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._config_validator = GoogleMapsConfigValidator(api_key=api_key)
        self._client = GoogleMapsClient(api_key, http_client=http_client)

    def validate_config(self, config: dict[str, Any]) -> ConfigValidationResult:
        return self._config_validator.validate_config("google_maps", config)

    def estimate(self, config: dict[str, Any]) -> UsageEstimate:
        return UsageEstimate(
            estimated_units=config.get("max_results", MAX_RESULT_COUNT),
            notes=(
                "Google Places API (New) has no pre-call usage-estimate "
                "endpoint — this is the requested max_results, already "
                "bounded by MAX_RESULT_COUNT (T041), not a real prediction."
            ),
        )

    def collect(self, config: dict[str, Any]) -> Iterator[RawProviderItem]:
        yield from self._client.search_text(config)

    def normalize(self, raw_item: RawProviderItem) -> NormalizedItem:
        return normalize_place(raw_item)

    def classify_error(self, error: Exception) -> ProviderError:
        if isinstance(error, GoogleMapsApiError):
            return classify_google_maps_error(error)
        return ProviderError(
            category=ProviderErrorCategory.UNKNOWN, message=str(error), retryable=False
        )

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(
            healthy=True,
            detail=(
                "Credential present and client constructed — this does not "
                "verify live reachability, which would spend real API quota."
            ),
        )
