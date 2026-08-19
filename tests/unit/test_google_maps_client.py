"""T042 tests: the Google Places API (New) Text Search HTTP client —
every real network call is replaced with `httpx.MockTransport`
(dependency injection, T042 item 10), matching the task's own
acceptance criterion: "Mock tests verify request construction and
response handling; no real credentials are committed." No test here
ever contacts the real Google API."""

import json
from collections.abc import Callable

import httpx
import pytest

from app.providers.google_maps.client import GoogleMapsApiError, GoogleMapsClient

EXAMPLE_CONFIG = {
    "query": "coffee shops",
    "location": {"latitude": 21.1702, "longitude": 72.8311},
    "radius_meters": 10_000,
    "fields": ["displayName", "formattedAddress", "rating"],
    "max_results": 5,
}


def _client_with_handler(
    handler: Callable[[httpx.Request], httpx.Response], **kwargs: object
) -> GoogleMapsClient:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    return GoogleMapsClient(
        "fake-api-key",
        http_client=http_client,
        **kwargs,  # type: ignore[arg-type]
    )


def _places_response(
    count: int, *, next_page_token: str | None = None
) -> httpx.Response:
    body: dict[str, object] = {
        "places": [
            {"id": f"place-{i}", "displayName": {"text": f"Place {i}"}}
            for i in range(count)
        ]
    }
    if next_page_token is not None:
        body["nextPageToken"] = next_page_token
    return httpx.Response(200, json=body)


def test_empty_api_key_is_rejected_at_construction():
    with pytest.raises(ValueError, match="non-empty api_key"):
        GoogleMapsClient("")


def test_request_uses_the_documented_endpoint_and_credential_header():
    seen_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return _places_response(1)

    client = _client_with_handler(handler)
    list(client.search_text(EXAMPLE_CONFIG))

    assert len(seen_requests) == 1
    request = seen_requests[0]
    assert str(request.url) == "https://places.googleapis.com/v1/places:searchText"
    assert request.headers["X-Goog-Api-Key"] == "fake-api-key"


def test_field_mask_is_prefixed_and_includes_id_and_next_page_token():
    seen_requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_requests.append(request)
        return _places_response(1)

    client = _client_with_handler(handler)
    list(client.search_text(EXAMPLE_CONFIG))

    field_mask = seen_requests[0].headers["X-Goog-FieldMask"]
    assert field_mask == (
        "places.id,places.displayName,places.formattedAddress,places.rating,"
        "nextPageToken"
    )


def test_request_body_maps_query_location_and_radius():
    seen_bodies: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_bodies.append(json.loads(request.content))
        return _places_response(1)

    client = _client_with_handler(handler)
    list(client.search_text(EXAMPLE_CONFIG))

    body = seen_bodies[0]
    assert body["textQuery"] == "coffee shops"
    assert body["locationBias"]["circle"]["center"] == {
        "latitude": 21.1702,
        "longitude": 72.8311,
    }
    assert body["locationBias"]["circle"]["radius"] == 10_000
    assert "pageToken" not in body


def test_request_body_omits_location_bias_when_no_location_configured():
    config = {"query": "coffee shops", "fields": ["displayName"], "max_results": 1}
    seen_bodies: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_bodies.append(json.loads(request.content))
        return _places_response(1)

    client = _client_with_handler(handler)
    list(client.search_text(config))

    assert "locationBias" not in seen_bodies[0]


def test_yields_every_place_from_a_single_page():
    client = _client_with_handler(lambda request: _places_response(3))
    config = {**EXAMPLE_CONFIG, "max_results": 3}

    places = list(client.search_text(config))

    assert [place["id"] for place in places] == ["place-0", "place-1", "place-2"]


def test_stops_once_max_results_is_reached_within_a_single_page():
    client = _client_with_handler(lambda request: _places_response(20))
    config = {**EXAMPLE_CONFIG, "max_results": 3}

    places = list(client.search_text(config))

    assert len(places) == 3


def test_follows_pagination_across_multiple_pages():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return _places_response(20, next_page_token="page-2-token")
        return _places_response(5)

    client = _client_with_handler(handler)
    config = {**EXAMPLE_CONFIG, "max_results": 25}

    places = list(client.search_text(config))

    assert call_count == 2
    assert len(places) == 25


def test_second_page_request_includes_the_page_token():
    seen_bodies: list[dict] = []
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        seen_bodies.append(json.loads(request.content))
        if call_count == 1:
            return _places_response(20, next_page_token="page-2-token")
        return _places_response(1)

    client = _client_with_handler(handler)
    config = {**EXAMPLE_CONFIG, "max_results": 21}
    list(client.search_text(config))

    assert "pageToken" not in seen_bodies[0]
    assert seen_bodies[1]["pageToken"] == "page-2-token"


def test_stops_when_google_reports_no_next_page_token():
    client = _client_with_handler(lambda request: _places_response(5))
    config = {**EXAMPLE_CONFIG, "max_results": 100}

    places = list(client.search_text(config))

    assert len(places) == 5


def test_transient_5xx_error_is_retried_and_then_succeeds():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return httpx.Response(503, json={"error": {"message": "unavailable"}})
        return _places_response(1)

    client = _client_with_handler(handler, max_retries=2)
    places = list(client.search_text(EXAMPLE_CONFIG))

    assert call_count == 2
    assert len(places) == 1


def test_persistent_5xx_error_raises_after_retries_exhausted():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": {"message": "unavailable"}})

    client = _client_with_handler(handler, max_retries=1)

    with pytest.raises(GoogleMapsApiError) as exc_info:
        list(client.search_text(EXAMPLE_CONFIG))
    assert exc_info.value.status_code == 503


def test_transport_error_is_retried_and_then_succeeds():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.ConnectError("connection refused")
        return _places_response(1)

    client = _client_with_handler(handler, max_retries=2)
    places = list(client.search_text(EXAMPLE_CONFIG))

    assert call_count == 2
    assert len(places) == 1


def test_persistent_transport_error_raises_after_retries_exhausted():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    client = _client_with_handler(handler, max_retries=1)

    with pytest.raises(GoogleMapsApiError):
        list(client.search_text(EXAMPLE_CONFIG))


def test_authentication_error_is_never_retried():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            401,
            json={
                "error": {
                    "code": 401,
                    "message": "API key not valid.",
                    "status": "UNAUTHENTICATED",
                }
            },
        )

    client = _client_with_handler(handler, max_retries=3)

    with pytest.raises(GoogleMapsApiError) as exc_info:
        list(client.search_text(EXAMPLE_CONFIG))

    assert call_count == 1  # never retried
    assert exc_info.value.status_code == 401
    assert exc_info.value.google_error_status == "UNAUTHENTICATED"


def test_quota_error_is_never_retried():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(
            429,
            json={
                "error": {
                    "code": 429,
                    "message": "Quota exceeded.",
                    "status": "RESOURCE_EXHAUSTED",
                }
            },
        )

    client = _client_with_handler(handler, max_retries=3)

    with pytest.raises(GoogleMapsApiError) as exc_info:
        list(client.search_text(EXAMPLE_CONFIG))

    assert call_count == 1  # never retried — docs/07: never bypass a quota denial
    assert exc_info.value.google_error_status == "RESOURCE_EXHAUSTED"


def test_api_key_never_appears_in_a_raised_error_message():
    client = _client_with_handler(
        lambda request: httpx.Response(401, json={"error": {"message": "denied"}})
    )

    with pytest.raises(GoogleMapsApiError) as exc_info:
        list(client.search_text(EXAMPLE_CONFIG))

    assert "fake-api-key" not in str(exc_info.value)
