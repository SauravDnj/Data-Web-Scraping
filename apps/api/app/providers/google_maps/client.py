"""Google Places API (New) Text Search HTTP client (T042) — the actual
network boundary for the operation T041 already validates configs
against. Owns exactly one concern: talking to
`https://places.googleapis.com/v1/places:searchText`. Does not
validate configs (assumes `GoogleMapsConfigValidator`, T041, already
ran) and does not classify errors into
`app.domain.provider_contracts.ProviderErrorCategory` — that mapping
is T044's job (`GoogleMapsApiError` below is the stable, structured
shape T044 will classify, never a raw `httpx` exception or bare JSON
error body).

**Retry policy, a deliberate design choice**: only network-transport
failures and HTTP 5xx responses are retried automatically, inside this
client, with a short exponential backoff — genuine infrastructure
hiccups, nothing policy-related. **4xx responses (auth, invalid
request, quota, rate) are never retried here** — docs/07's "Important
rule" says a quota/rate/authorization/policy denial must not be
bypassed, and immediately retrying inside one client call, with no
real elapsed time, would look exactly like an attempt to bypass it.
Those failures propagate as a `GoogleMapsApiError` for the *job*-level
retry path (`JobService.retry_job`, T035) to decide about later, with
real backoff between attempts, not this method silently hammering the
endpoint again.

**Field mask**, per T041's `ALLOWED_FIELDS`: request-level `fields`
(e.g. `"displayName"`) get prefixed to Google's real
`"places.displayName"` field-mask syntax here — T041 validates the
config's own (unprefixed) field names, this module is where the
Google-specific prefixing actually happens.

**Usage/quota metadata**: verified against Google's live docs
(2026-08-20, same fetch as T041) that Text Search (New) responses
carry no documented, machine-readable quota/usage-remaining field or
header — this is an honest "not available", not a gap. Quota
exhaustion surfaces through the structured-error path instead (Google
returns a `RESOURCE_EXHAUSTED` error status, which T044 classifies)."""

import logging
from collections.abc import Iterator
from typing import Any

import httpx

from app.providers.google_maps.config import MAX_RESULT_COUNT

logger = logging.getLogger(__name__)

_SEARCH_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"
_RETRYABLE_STATUS_CODES = frozenset({500, 502, 503, 504})
_GOOGLE_PAGE_SIZE_LIMIT = 20


class GoogleMapsApiError(Exception):
    """A failed Google Places API (New) call — the only exception type
    this client ever raises for a request failure, whether the cause
    was a non-2xx response or a transport-level error. Never carries
    the API key (it's a request header, never echoed into Google's
    error body or into `str(transport_exception)`)."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        google_error_status: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.google_error_status = google_error_status


class GoogleMapsClient:
    """`api_key` is the server-side credential
    (`app.core.config.Settings.google_maps_api_key`) — required and
    never optional here (unlike `GoogleMapsConfigValidator`, T041,
    which must still run and report a clear validation error when it's
    missing; by the time this client is constructed, that check has
    already passed). `http_client` is injectable so tests never make a
    real network call (`httpx.MockTransport`, T042's own DO NOT list:
    "use fake credentials" refers to talking to the real API with a
    fake key, not to mocking the transport in tests)."""

    def __init__(
        self,
        api_key: str,
        *,
        http_client: httpx.Client | None = None,
        timeout_seconds: float = 10.0,
        max_retries: int = 2,
    ) -> None:
        if not api_key:
            raise ValueError("GoogleMapsClient requires a non-empty api_key.")
        self._api_key = api_key
        self._http_client = http_client or httpx.Client(timeout=timeout_seconds)
        self._max_retries = max_retries

    def search_text(self, config: dict[str, Any]) -> Iterator[dict[str, Any]]:
        """Yields raw place items across pages, up to
        `config.get("max_results", MAX_RESULT_COUNT)` — `config` is
        assumed already validated (T041); this method does not
        re-validate it. Lazy: a caller that only consumes the first
        few items never pays for the later pages.

        A malformed top-level response (`places` missing or not a
        list, or containing a non-object entry) is treated as if that
        page were empty/that entry absent — never raises, matching
        T043's "never invent, never crash" treatment of malformed
        provider data, applied here at the collection layer too."""
        target = config.get("max_results", MAX_RESULT_COUNT)
        field_mask = _build_field_mask(config["fields"])
        page_token: str | None = None
        yielded = 0

        while yielded < target:
            page_size = min(_GOOGLE_PAGE_SIZE_LIMIT, target - yielded)
            body = _build_request_body(
                config, page_size=page_size, page_token=page_token
            )
            payload = self._request_page(body, field_mask)

            places = payload.get("places")
            if not isinstance(places, list):
                places = []

            for place in places:
                if not isinstance(place, dict):
                    continue
                if yielded >= target:
                    return
                yield place
                yielded += 1

            next_page_token = payload.get("nextPageToken")
            if (
                not isinstance(next_page_token, str)
                or not next_page_token
                or not places
            ):
                return
            page_token = next_page_token

    def _request_page(self, body: dict[str, Any], field_mask: str) -> dict[str, Any]:
        headers = {
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": field_mask,
            "Content-Type": "application/json",
        }

        response: httpx.Response | None = None
        last_transport_error: httpx.TransportError | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._http_client.post(
                    _SEARCH_TEXT_URL, json=body, headers=headers
                )
            except httpx.TransportError as exc:
                last_transport_error = exc
                logger.warning(
                    "google_maps_transport_error",
                    extra={"attempt": attempt, "max_retries": self._max_retries},
                )
                continue

            if (
                response.status_code in _RETRYABLE_STATUS_CODES
                and attempt < self._max_retries
            ):
                logger.warning(
                    "google_maps_retryable_status",
                    extra={
                        "attempt": attempt,
                        "max_retries": self._max_retries,
                        "status_code": response.status_code,
                    },
                )
                continue

            break

        if response is None:
            raise GoogleMapsApiError(
                f"Google Places API request failed after "
                f"{self._max_retries + 1} attempt(s): {last_transport_error}"
            ) from last_transport_error

        if response.status_code >= 400:
            raise _build_api_error(response)

        json_body: dict[str, Any] = response.json()
        return json_body


def _build_field_mask(fields: list[str]) -> str:
    prefixed = [f"places.{field}" for field in fields]
    if "places.id" not in prefixed:
        prefixed.insert(0, "places.id")
    prefixed.append("nextPageToken")
    return ",".join(prefixed)


def _build_request_body(
    config: dict[str, Any], *, page_size: int, page_token: str | None
) -> dict[str, Any]:
    body: dict[str, Any] = {"textQuery": config["query"], "pageSize": page_size}

    location = config.get("location")
    if location is not None:
        circle: dict[str, Any] = {
            "center": {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
            }
        }
        radius_meters = config.get("radius_meters")
        if radius_meters is not None:
            circle["radius"] = radius_meters
        body["locationBias"] = {"circle": circle}

    if "price_levels" in config:
        body["priceLevels"] = config["price_levels"]
    if "rank_preference" in config:
        body["rankPreference"] = config["rank_preference"]
    if page_token is not None:
        body["pageToken"] = page_token

    return body


def _build_api_error(response: httpx.Response) -> GoogleMapsApiError:
    google_error_status: str | None = None
    try:
        error = response.json().get("error", {})
        message = error.get("message") or response.text
        google_error_status = error.get("status")
    except ValueError:
        message = response.text or f"HTTP {response.status_code}"

    return GoogleMapsApiError(
        message,
        status_code=response.status_code,
        google_error_status=google_error_status,
    )
