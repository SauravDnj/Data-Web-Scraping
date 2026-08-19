"""Maps raw Google Places API (New) Text Search response items into
the platform's normalized internal representation (T043). Pure
functions, no I/O, no HTTP — operates on already-fetched raw dicts
(what `app.providers.google_maps.client.GoogleMapsClient.search_text()`
yields).

**Field mapping is exhaustive and explicit** (T043 items 1/6: map
every supported field, never invent one that isn't actually in the
response) — matches exactly the `ALLOWED_FIELDS` set T041 validates a
config's `fields` list against
(`app.providers.google_maps.config`); a field this module doesn't
handle was never requested in the first place, so there is nothing to
map for it.

**A field present in the raw item but of the wrong type — i.e. a
malformed response (T043 item 10 explicitly asks for a test proving
this doesn't crash) — is treated exactly like a missing field: it is
silently omitted from the normalized `data`, never coerced or guessed
at.** True schema/quality *validation* (flagging a record `warning`/
`rejected` for a suspicious value) is Stages 2/4 of
`docs/08_DATA_PIPELINE_DEEP.md` — `GOOGLE_FIELD_RULES`/
`validate_google_place_record()` below (T051) — kept as an explicit,
separately-callable step, not silently chained into
`map_place_to_record_draft()`, matching the composable-pipeline-stages
pattern established since T041/T042 (config validation and HTTP
client stayed separate calls too, never merged into one).

**Provider/source reference (T043 item 3)**: Places API (New) has no
separate "reference" field distinct from the place `id` itself (the
legacy Places API's `reference` field was dropped) —
`GOOGLE_MAPS_TEXT_SEARCH_OPERATION` below is what T054 (persistence)
should record as `RecordProvenance.provider_operation`;
`RecordProvenance.source_reference` should stay `None` for this
operation — a deliberate decision, not an oversight."""

from datetime import datetime
from typing import Any

from app.domain.provider_contracts import NormalizedItem, RawProviderItem
from app.domain.records import RecordDraft
from app.pipeline.normalize import FieldKind, normalize_record_data
from app.pipeline.validate import (
    FieldRule,
    RecordQuality,
    ValidationResult,
    validate_record_draft,
)

GOOGLE_MAPS_TEXT_SEARCH_OPERATION = "google_maps.places.text_search"

# Stage 3 normalization (T050) field kinds for this mapper's own output
# keys — declared here, not guessed from value shape, per
# app.pipeline.normalize's own design principle. `open_now` (bool) is
# deliberately absent: FieldKind.TEXT (the default for an undeclared
# key) only touches strings, so a bool passes through untouched either
# way, but leaving it out makes it visible in review that no data key
# here needs a NUMBER/URL/TIMESTAMP/CATEGORY treatment for it.
FIELD_KINDS: dict[str, FieldKind] = {
    "name": FieldKind.TEXT,
    "formatted_address": FieldKind.TEXT,
    "phone_number": FieldKind.TEXT,
    "weekday_descriptions": FieldKind.TEXT,
    "website": FieldKind.URL,
    "business_status": FieldKind.CATEGORY,
    "primary_type": FieldKind.CATEGORY,
    "types": FieldKind.CATEGORY,
    "price_level": FieldKind.CATEGORY,
    "rating": FieldKind.NUMBER,
    "user_rating_count": FieldKind.NUMBER,
    "latitude": FieldKind.NUMBER,
    "longitude": FieldKind.NUMBER,
}

# Stage 2/4 validation (T051) field rules for this mapper's own output
# keys. Directly matches docs/08's own two worked examples: a missing
# `website` is a WARNING (`missing_severity`), an out-of-range
# `latitude`/`longitude` is REJECTED (the default `severity`). `name`
# missing entirely is REJECTED — a record with no name is not usable.
# `rating` out of Google's documented 0.0-5.0 range is a WARNING, not
# a hard rejection — a slightly-off rating is still a usable record.
GOOGLE_FIELD_RULES: dict[str, FieldRule] = {
    "name": FieldRule(missing_severity=RecordQuality.REJECTED, expected_types=(str,)),
    "latitude": FieldRule(expected_types=(int, float), min_value=-90.0, max_value=90.0),
    "longitude": FieldRule(
        expected_types=(int, float), min_value=-180.0, max_value=180.0
    ),
    "rating": FieldRule(
        expected_types=(int, float),
        min_value=0.0,
        max_value=5.0,
        severity=RecordQuality.WARNING,
    ),
    "website": FieldRule(
        missing_severity=RecordQuality.WARNING,
        is_url=True,
        severity=RecordQuality.WARNING,
    ),
}


def normalize_place(raw_item: RawProviderItem) -> NormalizedItem:
    """Matches `app.providers.base.ProviderAdapter.normalize()`'s
    signature exactly — this is that method's real Google
    implementation."""
    data: dict[str, Any] = {}

    name = _extract_display_name(raw_item)
    if name is not None:
        data["name"] = name

    formatted_address = _extract_str(raw_item, "formattedAddress")
    if formatted_address is not None:
        data["formatted_address"] = formatted_address

    latitude, longitude = _extract_location(raw_item)
    if latitude is not None and longitude is not None:
        data["latitude"] = latitude
        data["longitude"] = longitude

    business_status = _extract_str(raw_item, "businessStatus")
    if business_status is not None:
        data["business_status"] = business_status.lower()

    primary_type = _extract_str(raw_item, "primaryType")
    if primary_type is not None:
        data["primary_type"] = primary_type

    types = _extract_str_list(raw_item, "types")
    if types is not None:
        data["types"] = types

    rating = _extract_float(raw_item, "rating")
    if rating is not None:
        data["rating"] = rating

    user_rating_count = _extract_int(raw_item, "userRatingCount")
    if user_rating_count is not None:
        data["user_rating_count"] = user_rating_count

    price_level = _extract_str(raw_item, "priceLevel")
    if price_level is not None:
        data["price_level"] = price_level.lower()

    phone_number = _extract_str(raw_item, "internationalPhoneNumber")
    if phone_number is not None:
        data["phone_number"] = phone_number

    website = _extract_str(raw_item, "websiteUri")
    if website is not None:
        data["website"] = website

    open_now, weekday_descriptions = _extract_opening_hours(raw_item)
    if open_now is not None:
        data["open_now"] = open_now
    if weekday_descriptions is not None:
        data["weekday_descriptions"] = weekday_descriptions

    provider_record_id = _extract_str(raw_item, "id")
    return NormalizedItem(provider_record_id=provider_record_id, data=data)


def map_place_to_record_draft(
    raw_item: RawProviderItem,
    *,
    project_id: int,
    job_id: int,
    collected_at: datetime,
) -> RecordDraft:
    """Combines `normalize_place()` with the job/project context and
    collection timestamp a stateless `ProviderAdapter.normalize()`
    call has no way to know on its own (T043 items 7/8), **and** runs
    the result through Stage 3 normalization (T050,
    `app.pipeline.normalize`) — `normalize_place()` alone only does
    Stage 1's field mapping (matching `ProviderAdapter.normalize()`'s
    Protocol exactly, T040); this function is where the full pipeline
    up to (not including) canonical-key computation (T052) actually
    runs. The worker (T060+) is expected to call this, not
    `normalize_place()` directly, once it orchestrates a real
    collection run."""
    normalized = normalize_place(raw_item)
    return RecordDraft(
        project_id=project_id,
        job_id=job_id,
        provider="google_maps",
        data=normalize_record_data(normalized.data, FIELD_KINDS),
        collected_at=collected_at,
        provider_record_id=normalized.provider_record_id,
    )


def validate_google_place_record(record: RecordDraft) -> ValidationResult:
    """Stage 2/4 validation (T051) for a `RecordDraft` built by
    `map_place_to_record_draft()` — an explicit, separately-callable
    step, not folded into that function (see this module's docstring
    for why). The worker calls this after building the draft and
    before Stage 5 canonical-key computation (T052); a `REJECTED`
    record should not proceed to persistence."""
    return validate_record_draft(record, GOOGLE_FIELD_RULES)


def _extract_str(raw_item: RawProviderItem, key: str) -> str | None:
    value = raw_item.get(key)
    return value if isinstance(value, str) and value.strip() else None


def _extract_float(raw_item: RawProviderItem, key: str) -> float | None:
    value = raw_item.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _extract_int(raw_item: RawProviderItem, key: str) -> int | None:
    value = raw_item.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _extract_str_list(raw_item: RawProviderItem, key: str) -> list[str] | None:
    value = raw_item.get(key)
    if not isinstance(value, list):
        return None
    strings = [item for item in value if isinstance(item, str)]
    return strings or None


def _extract_display_name(raw_item: RawProviderItem) -> str | None:
    display_name = raw_item.get("displayName")
    if not isinstance(display_name, dict):
        return None
    return _extract_str(display_name, "text")


def _extract_location(
    raw_item: RawProviderItem,
) -> tuple[float | None, float | None]:
    location = raw_item.get("location")
    if not isinstance(location, dict):
        return None, None
    return _extract_float(location, "latitude"), _extract_float(location, "longitude")


def _extract_opening_hours(
    raw_item: RawProviderItem,
) -> tuple[bool | None, list[str] | None]:
    hours = raw_item.get("currentOpeningHours")
    if not isinstance(hours, dict):
        return None, None
    open_now_raw = hours.get("openNow")
    open_now = open_now_raw if isinstance(open_now_raw, bool) else None
    weekday_descriptions = _extract_str_list(hours, "weekdayDescriptions")
    return open_now, weekday_descriptions
