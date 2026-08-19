"""Minimal validation contract a provider adapter must satisfy.

T040 ("Provider interface") will define the full provider contract
(collect, normalize, classify_error, ...) — this is deliberately just
the validation slice T034 needs now, to resolve a circular dependency
in the task graph (T034 depends on T040, and T040 depends on T034).
A full ProviderAdapter built at T040 should satisfy this Protocol as a
subset of its interface, not replace it."""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ConfigValidationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)

    @staticmethod
    def ok() -> "ConfigValidationResult":
        return ConfigValidationResult(is_valid=True)

    @staticmethod
    def failed(*errors: str) -> "ConfigValidationResult":
        return ConfigValidationResult(is_valid=False, errors=list(errors))


class ProviderConfigValidator(Protocol):
    def validate_config(
        self, provider: str, config: dict[str, Any]
    ) -> ConfigValidationResult: ...
