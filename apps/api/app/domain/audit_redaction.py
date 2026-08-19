"""Strip likely-sensitive values out of audit details before they are
ever persisted (T037: "secrets never enter audit details"). This is a
safety net, not a substitute for services simply not putting secrets
into details in the first place."""

from typing import Any

_SENSITIVE_KEY_MARKERS = (
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "private_key",
)

REDACTED_PLACEHOLDER = "[redacted]"


def redact_details(details: dict[str, Any]) -> dict[str, Any]:
    """Recursively scrubs any key matching a sensitive marker
    (case-insensitive substring match), at any nesting depth."""
    redacted: dict[str, Any] = {}
    for key, value in details.items():
        if _looks_sensitive(key):
            redacted[key] = REDACTED_PLACEHOLDER
        elif isinstance(value, dict):
            redacted[key] = redact_details(value)
        else:
            redacted[key] = value
    return redacted


def _looks_sensitive(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in _SENSITIVE_KEY_MARKERS)
