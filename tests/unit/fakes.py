"""Test-only fakes. A real FakeProvider matching the full T040
provider contract belongs at that task — this is scoped narrowly to
the validation-only Protocol T034 needs
(app.domain.provider_validation.ProviderConfigValidator)."""

from typing import Any

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
