"""Stage 2 ("Schema validation") + Stage 4 ("Quality") of
docs/08_DATA_PIPELINE_DEEP.md (T051), combined into one pass — a field
either passes, or it fails with a severity, and a record's overall
verdict is the worst severity among its fields. Operates on a
`RecordDraft`'s `data` (T043's output, already Stage-3-normalized by
T050). Pure, deterministic, makes no network call (URL checks are
syntax-only, never a real HTTP request) — T051's own literal
acceptance criterion.

**Same "caller declares the rules, this module never guesses"
principle as T050's `FieldKind`**: which fields are required, what
type/range they should have, whether they're a URL — all supplied by
the caller via `FieldRule`, never inferred from a field's name or
value shape.

**Missing is not binary required-vs-optional — it has its own
severity, matching docs/08's own examples exactly**: "missing website
-> warning" and "invalid coordinate -> rejected" are two different
*kinds* of problem (an absent field vs. a present-but-wrong-value
field) that can independently warrant different severities.
`FieldRule.missing_severity` (`None` = fine if absent) captures the
first; `FieldRule.severity` (for a type/range/URL-syntax failure)
captures the second — deliberately not the same knob."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from urllib.parse import urlsplit

from app.domain.records import RecordDraft


class RecordQuality(StrEnum):
    VALID = "valid"
    WARNING = "warning"
    REJECTED = "rejected"


_SEVERITY_RANK: dict[RecordQuality, int] = {
    RecordQuality.VALID: 0,
    RecordQuality.WARNING: 1,
    RecordQuality.REJECTED: 2,
}


@dataclass(frozen=True)
class FieldRule:
    missing_severity: RecordQuality | None = None
    expected_types: tuple[type, ...] | None = None
    min_value: float | None = None
    max_value: float | None = None
    is_url: bool = False
    severity: RecordQuality = RecordQuality.REJECTED


@dataclass(frozen=True)
class FieldValidationError:
    field: str
    message: str
    severity: RecordQuality


@dataclass(frozen=True)
class ValidationResult:
    """`project_id`/`job_id` preserve the original job context (T051
    item 8) — the caller doesn't have to go back to the `RecordDraft`
    to know which job a rejected/warned record came from."""

    quality: RecordQuality
    errors: list[FieldValidationError] = field(default_factory=list)
    project_id: int | None = None
    job_id: int | None = None


def validate_record_draft(
    record: RecordDraft, field_rules: Mapping[str, FieldRule]
) -> ValidationResult:
    errors = [
        error
        for field_name, rule in field_rules.items()
        if (error := _validate_field(record.data, field_name, rule)) is not None
    ]

    quality = RecordQuality.VALID
    for error in errors:
        if _SEVERITY_RANK[error.severity] > _SEVERITY_RANK[quality]:
            quality = error.severity

    return ValidationResult(
        quality=quality,
        errors=errors,
        project_id=record.project_id,
        job_id=record.job_id,
    )


def _validate_field(
    data: Mapping[str, Any], field_name: str, rule: FieldRule
) -> FieldValidationError | None:
    value = data.get(field_name)

    if value is None:
        if rule.missing_severity is not None:
            return FieldValidationError(
                field_name, f"{field_name} is missing.", rule.missing_severity
            )
        return None

    if rule.expected_types is not None and not _isinstance_strict(
        value, rule.expected_types
    ):
        return FieldValidationError(
            field_name,
            f"{field_name} must be of type "
            f"{_type_names(rule.expected_types)}, got {type(value).__name__}.",
            rule.severity,
        )

    if rule.min_value is not None or rule.max_value is not None:
        if not _isinstance_strict(value, (int, float)):
            return FieldValidationError(
                field_name,
                f"{field_name} must be numeric to check its range, "
                f"got {type(value).__name__}.",
                rule.severity,
            )
        if rule.min_value is not None and value < rule.min_value:
            return FieldValidationError(
                field_name,
                f"{field_name} must be >= {rule.min_value}, got {value}.",
                rule.severity,
            )
        if rule.max_value is not None and value > rule.max_value:
            return FieldValidationError(
                field_name,
                f"{field_name} must be <= {rule.max_value}, got {value}.",
                rule.severity,
            )

    if rule.is_url and not (
        isinstance(value, str) and _is_syntactically_valid_url(value)
    ):
        return FieldValidationError(
            field_name, f"{field_name} is not a syntactically valid URL.", rule.severity
        )

    return None


def _isinstance_strict(value: Any, expected_types: tuple[type, ...]) -> bool:
    # bool is a subclass of int - isinstance(True, int) is True, which
    # would wrongly pass a boolean off as a valid int/numeric field.
    if isinstance(value, bool) and bool not in expected_types:
        return False
    return isinstance(value, expected_types)


def _is_syntactically_valid_url(value: str) -> bool:
    try:
        parts = urlsplit(value)
    except ValueError:
        return False
    return parts.scheme in ("http", "https") and bool(parts.netloc)


def _type_names(expected_types: tuple[type, ...]) -> str:
    return " or ".join(t.__name__ for t in expected_types)
