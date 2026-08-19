"""Google Maps Platform configuration validation (T041) — no network
call, no SDK, satisfies exactly `app.domain.provider_validation.
ProviderConfigValidator` so `GoogleMapsConfigValidator` can be plugged
into `ConfigurationService` (T034) as its real validator (today only
test fakes implement that Protocol in this codebase).

**Selected operation, a design decision this task had to make** (no
task or doc pins one down explicitly — docs/07's conceptual example
config, `{"query", "location", "radius_meters", "fields",
"max_results"}`, matches exactly one Google Maps Platform operation):
**Places API (New) — Text Search** (`POST
https://places.googleapis.com/v1/places:searchText`), not the legacy
Places API (deprecated in favor of "New") and not Nearby Search (which
filters by place type, not a free-text query). T042 (Google client)
must build requests against this exact endpoint or explicitly revise
this decision, not silently pick a different one.

**This module's config field names are snake_case, matching
`docs/CODING_STANDARDS.md`'s app-wide JSON convention — they are NOT
literally Google's request body field names** (Google's are
camelCase: `textQuery`, `locationBias`, `pageSize`, ...). Translating
this stored `CollectionConfig.config` shape into the real Google
request body is T042's job, not this one — T041 only validates that a
config *could* become a legal Google request, before any request is
attempted.

**Assumptions verified against Google's public documentation on
2026-08-20 (docs/16_MEMORY.md's T041 entry has the fetch details) —
MUST be reverified against the live docs
(https://developers.google.com/maps/documentation/places/web-service/text-search)
before this goes anywhere near production, since Google can change
field lists, tiers, and limits at any time**:

-   `pageSize`/`maxResultCount`: 1-20 per page, defaults to 20; the API
    returns a maximum of 60 results total across all pages
    (`MAX_RESULT_COUNT`).
-   `locationBias` circular radius: 0.0-50,000.0 meters
    (`MAX_RADIUS_METERS`).
-   Response field mask (`X-Goog-FieldMask`) is required by Google and
    billed by SKU tier (Pro vs. Enterprise vs. Enterprise+Atmosphere);
    `ALLOWED_FIELDS` here is deliberately a curated subset actually
    useful to this product (name/address/location/rating/hours/etc.),
    not Google's entire field catalog — extend it deliberately, don't
    silently allow arbitrary strings through.
-   `priceLevels` values exclude `PRICE_LEVEL_FREE` in *requests*
    (Google only returns it, never accepts it as a filter).
"""

from typing import Any

from app.domain.provider_validation import ConfigValidationResult

MAX_RESULT_COUNT = 60
MIN_RESULT_COUNT = 1
MAX_RADIUS_METERS = 50_000.0
MIN_RADIUS_METERS = 0.0
MIN_LATITUDE = -90.0
MAX_LATITUDE = 90.0
MIN_LONGITUDE = -180.0
MAX_LONGITUDE = 180.0

ALLOWED_FIELDS = frozenset(
    {
        "id",
        "displayName",
        "formattedAddress",
        "location",
        "businessStatus",
        "primaryType",
        "types",
        "rating",
        "userRatingCount",
        "priceLevel",
        "internationalPhoneNumber",
        "websiteUri",
        "currentOpeningHours",
    }
)

VALID_PRICE_LEVELS = frozenset(
    {
        "PRICE_LEVEL_INEXPENSIVE",
        "PRICE_LEVEL_MODERATE",
        "PRICE_LEVEL_EXPENSIVE",
        "PRICE_LEVEL_VERY_EXPENSIVE",
    }
)

VALID_RANK_PREFERENCES = frozenset({"RELEVANCE", "DISTANCE"})


class GoogleMapsConfigValidator:
    """Satisfies `app.domain.provider_validation.ProviderConfigValidator`.
    `api_key` is the server-side credential (from
    `app.core.config.Settings.google_maps_api_key`, added at T014 —
    never sourced from the frontend, never logged, per
    `docs/10_SECURITY_DEEP.md`'s "Provider secrets" rule) — passed in
    at construction, not read from `config` (a request body must never
    be able to smuggle in a credential)."""

    def __init__(self, api_key: str | None) -> None:
        self._api_key = api_key

    def validate_config(
        self, provider: str, config: dict[str, Any]
    ) -> ConfigValidationResult:
        errors: list[str] = []

        if not self._api_key:
            # Deliberately generic — never states *why* a key is
            # missing/invalid in a way that could help probe the
            # credential store; matches T038's "same message" logic
            # for a different reason (avoid leaking operational detail).
            errors.append("Google Maps Platform credentials are not configured.")

        errors.extend(_validate_query(config))
        errors.extend(_validate_location_and_radius(config))
        errors.extend(_validate_fields(config))
        errors.extend(_validate_max_results(config))
        errors.extend(_validate_price_levels(config))
        errors.extend(_validate_rank_preference(config))

        if errors:
            return ConfigValidationResult.failed(*errors)
        return ConfigValidationResult.ok()


def _validate_query(config: dict[str, Any]) -> list[str]:
    query = config.get("query")
    if not isinstance(query, str) or not query.strip():
        return ["config.query is required and must be a non-empty string."]
    return []


def _validate_location_and_radius(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    location = config.get("location")

    if location is not None:
        if not isinstance(location, dict):
            errors.append("config.location must be an object with latitude/longitude.")
        else:
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            if not _in_range(latitude, MIN_LATITUDE, MAX_LATITUDE):
                errors.append(
                    f"config.location.latitude must be a number between "
                    f"{MIN_LATITUDE} and {MAX_LATITUDE}."
                )
            if not _in_range(longitude, MIN_LONGITUDE, MAX_LONGITUDE):
                errors.append(
                    f"config.location.longitude must be a number between "
                    f"{MIN_LONGITUDE} and {MAX_LONGITUDE}."
                )

    radius_meters = config.get("radius_meters")
    if radius_meters is not None:
        if location is None:
            errors.append("config.radius_meters requires config.location to be set.")
        if not _in_range(radius_meters, MIN_RADIUS_METERS, MAX_RADIUS_METERS):
            errors.append(
                f"config.radius_meters must be a number between "
                f"{MIN_RADIUS_METERS} and {MAX_RADIUS_METERS} "
                "(Google Places API (New)'s locationBias limit)."
            )

    return errors


def _validate_fields(config: dict[str, Any]) -> list[str]:
    fields = config.get("fields")
    if fields is None:
        return [
            "config.fields is required — Google rejects any Text Search "
            "request with no field mask."
        ]
    if not isinstance(fields, list) or not fields:
        return ["config.fields must be a non-empty list of field names."]

    unknown = sorted(set(fields) - ALLOWED_FIELDS)
    if unknown:
        return [
            f"config.fields contains unsupported field(s): {', '.join(unknown)}. "
            f"Allowed: {', '.join(sorted(ALLOWED_FIELDS))}."
        ]
    return []


def _validate_max_results(config: dict[str, Any]) -> list[str]:
    max_results = config.get("max_results")
    if max_results is None:
        return []
    if not isinstance(max_results, int) or isinstance(max_results, bool):
        return ["config.max_results must be an integer."]
    if not (MIN_RESULT_COUNT <= max_results <= MAX_RESULT_COUNT):
        return [
            f"config.max_results must be between {MIN_RESULT_COUNT} and "
            f"{MAX_RESULT_COUNT} — Google Places API (New)'s Text Search "
            f"returns a maximum of {MAX_RESULT_COUNT} results across all "
            "pages, however many are requested."
        ]
    return []


def _validate_price_levels(config: dict[str, Any]) -> list[str]:
    price_levels = config.get("price_levels")
    if price_levels is None:
        return []
    if not isinstance(price_levels, list) or not price_levels:
        return ["config.price_levels must be a non-empty list if provided."]
    unknown = sorted(set(price_levels) - VALID_PRICE_LEVELS)
    if unknown:
        return [
            f"config.price_levels contains unsupported value(s): "
            f"{', '.join(unknown)}. Allowed: {', '.join(sorted(VALID_PRICE_LEVELS))}."
        ]
    return []


def _validate_rank_preference(config: dict[str, Any]) -> list[str]:
    rank_preference = config.get("rank_preference")
    if rank_preference is None:
        return []
    if rank_preference not in VALID_RANK_PREFERENCES:
        return [
            f"config.rank_preference must be one of "
            f"{', '.join(sorted(VALID_RANK_PREFERENCES))}."
        ]
    return []


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _in_range(value: Any, minimum: float, maximum: float) -> bool:
    return _is_number(value) and minimum <= value <= maximum
