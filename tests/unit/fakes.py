"""Test-only fakes."""

from collections.abc import Iterator
from typing import Any

from app.domain.provider_contracts import (
    NormalizedItem,
    ProviderError,
    ProviderErrorCategory,
    ProviderHealth,
    RawProviderItem,
    UsageEstimate,
)
from app.domain.provider_validation import ConfigValidationResult


class AlwaysValidValidator:
    def validate_config(
        self, provider: str, config: dict[str, Any]
    ) -> ConfigValidationResult:
        return ConfigValidationResult.ok()


class AlwaysInvalidValidator:
    def __init__(self, *reasons: str) -> None:
        self._reasons = reasons or ("fake provider rejected this configuration",)

    def validate_config(
        self, provider: str, config: dict[str, Any]
    ) -> ConfigValidationResult:
        return ConfigValidationResult.failed(*self._reasons)


class RequiresQueryFieldValidator:
    """A slightly more realistic fake: rejects a config missing a
    'query' key, to prove provider-specific validation actually
    influences the outcome (not just generic-field checks)."""

    def validate_config(
        self, provider: str, config: dict[str, Any]
    ) -> ConfigValidationResult:
        if "query" not in config:
            return ConfigValidationResult.failed("config.query is required.")
        return ConfigValidationResult.ok()


class FakeProviderAdapter:
    """Deterministic app.providers.base.ProviderAdapter (T040) — no
    SDK, no HTTP, no network. Default raw items are deliberately
    generic (no Google-specific fields), matching what the real
    contract requires of every adapter."""

    def __init__(self, raw_items: list[dict[str, Any]] | None = None) -> None:
        self._raw_items = (
            raw_items
            if raw_items is not None
            else [
                {"id": "item-1", "name": "Example Cafe"},
                {"id": "item-2", "name": "Example Diner"},
            ]
        )

    def validate_config(self, config: dict[str, Any]) -> ConfigValidationResult:
        if "query" not in config:
            return ConfigValidationResult.failed("config.query is required.")
        return ConfigValidationResult.ok()

    def estimate(self, config: dict[str, Any]) -> UsageEstimate:
        return UsageEstimate(estimated_units=len(self._raw_items))

    def collect(self, config: dict[str, Any]) -> Iterator[RawProviderItem]:
        yield from self._raw_items

    def normalize(self, raw_item: RawProviderItem) -> NormalizedItem:
        return NormalizedItem(
            provider_record_id=raw_item.get("id"),
            data={key: value for key, value in raw_item.items() if key != "id"},
        )

    def classify_error(self, error: Exception) -> ProviderError:
        if isinstance(error, TimeoutError):
            return ProviderError(ProviderErrorCategory.TEMPORARY, str(error))
        return ProviderError(ProviderErrorCategory.UNKNOWN, str(error))

    def health_check(self) -> ProviderHealth:
        return ProviderHealth(healthy=True)
