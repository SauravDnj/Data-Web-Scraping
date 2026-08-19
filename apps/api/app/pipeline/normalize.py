"""Stage 3 ("Normalization") of docs/08_DATA_PIPELINE_DEEP.md (T050) —
pure, deterministic transformations applied to a provider's already
field-mapped output (e.g. `app.providers.google_maps.mapper.
normalize_place()`'s `NormalizedItem.data`, T043). Provider-agnostic
and reusable: this module has no Google-specific (or any
provider-specific) field names in it anywhere.

**Field kinds are supplied by the caller, not guessed from a value's
shape** — a URL is only URL-normalized because the caller declared
that field a `FieldKind.URL`, never because a string happens to start
with `"http"`. This is what makes "do not silently replace missing
values with invented defaults" (item 8) hold at the *kind-detection*
level too, not just the value level: guessing a field's kind from its
content risks mis-normalizing a field that only coincidentally looks
like a URL/timestamp/number.

**Unicode normalization uses NFC only, never NFKC** — NFC unifies
canonically-equivalent representations of the *same* character (safe,
lossless); NFKC additionally folds compatibility variants (e.g. "™" →
"TM", fullwidth digits → ASCII digits, ligatures split apart), which
changes the text's actual content. "Normalize Unicode only where
safe" (item 2) is exactly this distinction — NFC is safe, NFKC is not
used here.

**Every transform is total and never raises** — a value that doesn't
match its declared kind's expected shape (a non-numeric string handed
to `FieldKind.NUMBER`, an unparseable timestamp, a malformed URL) is
returned with only the universally-safe text cleanup applied (trim +
NFC), never coerced, never dropped, never replaced with a guessed
value. This is item 8 applied at the value level, mirroring the same
principle T043 already applies to malformed provider responses."""

import re
import unicodedata
from collections.abc import Mapping
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from urllib.parse import urlsplit, urlunsplit

_NUMERIC_STRING_PATTERN = re.compile(r"^-?\d+(\.\d+)?$")


class FieldKind(StrEnum):
    """What kind of normalization a `data` key should get. `TEXT` is
    the safe default for any key not explicitly declared — trimming
    whitespace and NFC-normalizing Unicode is safe for every string,
    regardless of what the field actually holds."""

    TEXT = "text"
    URL = "url"
    NUMBER = "number"
    TIMESTAMP = "timestamp"
    CATEGORY = "category"


def normalize_record_data(
    data: Mapping[str, Any], field_kinds: Mapping[str, FieldKind]
) -> dict[str, Any]:
    """Returns a new dict — never mutates `data`. Keys not present in
    `data` are never added (item 8); keys present in `data` but absent
    from `field_kinds` default to `FieldKind.TEXT`."""
    return {
        key: _normalize_value(value, field_kinds.get(key, FieldKind.TEXT))
        for key, value in data.items()
    }


def _normalize_value(value: Any, kind: FieldKind) -> Any:
    if isinstance(value, list):
        return [_normalize_scalar(item, kind) for item in value]
    return _normalize_scalar(value, kind)


def _normalize_scalar(value: Any, kind: FieldKind) -> Any:
    if not isinstance(value, str):
        return value  # never coerce non-strings (bools, numbers, None, ...)

    text = _normalize_text_scalar(value)
    if kind is FieldKind.URL:
        return _normalize_url_scalar(text)
    if kind is FieldKind.NUMBER:
        return _normalize_number_scalar(text)
    if kind is FieldKind.TIMESTAMP:
        return _normalize_timestamp_scalar(text)
    if kind is FieldKind.CATEGORY:
        return text.lower()
    return text


def _normalize_text_scalar(value: str) -> str:
    # NFC first, then trim — NFC can change what counts as leading/
    # trailing whitespace-adjacent combining characters in rare cases,
    # so normalize composition before trimming edges.
    return unicodedata.normalize("NFC", value).strip()


def _normalize_url_scalar(text: str) -> str:
    try:
        parts = urlsplit(text)
    except ValueError:
        return text  # malformed — leave as text-normalized, don't guess

    if not parts.scheme or not parts.netloc:
        return text  # doesn't actually look like an absolute URL

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path,
            parts.query,
            parts.fragment,
        )
    )


def _normalize_number_scalar(text: str) -> Any:
    if not _NUMERIC_STRING_PATTERN.match(text):
        return text  # not unambiguously numeric — never guess
    return float(text) if "." in text else int(text)


def _normalize_timestamp_scalar(text: str) -> str:
    parsed = _parse_iso8601(text)
    if parsed is None or parsed.tzinfo is None:
        # Unparseable, or no explicit timezone — canonicalizing would
        # mean inventing a timezone that was never actually stated.
        return text
    return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _parse_iso8601(text: str) -> datetime | None:
    candidate = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        return datetime.fromisoformat(candidate)
    except ValueError:
        return None
