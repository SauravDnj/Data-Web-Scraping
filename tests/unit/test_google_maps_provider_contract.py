"""T045: the complete fake-provider contract suite — proves the fully
assembled `GoogleMapsProvider` (composing T041's config validator,
T042's HTTP client, T043's response mapper, and T044's error
classifier) behaves correctly end to end, entirely through
`httpx.MockTransport`. No real network call, no live Google
credentials anywhere in this file — matching T045's literal acceptance
criterion: "Provider adapter behavior is covered without requiring
live Google credentials."""

import json
from collections.abc import Callable
from pathlib import Path

import httpx
import pytest
from app.domain.provider_contracts import ProviderErrorCategory
from app.providers.base import ProviderAdapter
from app.providers.google_maps.client import GoogleMapsApiError
from app.providers.google_maps.mapper import normalize_place
from app.providers.google_maps.provider import GoogleMapsProvider

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "google_maps"

EXAMPLE_CONFIG = {
    "query": "coffee shops",
    "fields": ["displayName", "formattedAddress", "rating"],
    "max_results": 5,
}


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _provider_with_handler(
    handler: Callable[[httpx.Request], httpx.Response],
) -> GoogleMapsProvider:
    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    return GoogleMapsProvider("fake-api-key", http_client=http_client)


def _json_response(status_code: int, fixture_name: str) -> httpx.Response:
    return httpx.Response(status_code, json=_load_fixture(fixture_name))


# --- 1. synthetic fixtures: see tests/fixtures/google_maps/ ---


def test_google_maps_provider_satisfies_the_provider_adapter_protocol():
    provider = _provider_with_handler(lambda request: httpx.Response(200, json={}))
    assert isinstance(provider, ProviderAdapter)


# --- 2. valid collection response ---


def test_valid_collection_response_yields_every_place():
    provider = _provider_with_handler(
        lambda request: _json_response(200, "text_search_response_valid.json")
    )
    items = list(provider.collect(EXAMPLE_CONFIG))
    assert [item["id"] for item in items] == [
        "ChIJrTLr-GyuEmsRBfy61i59si0",
        "ChIJanotherPlaceId456",
    ]


# --- 3. empty response ---


def test_empty_response_yields_nothing():
    provider = _provider_with_handler(
        lambda request: _json_response(200, "text_search_response_empty.json")
    )
    assert list(provider.collect(EXAMPLE_CONFIG)) == []


# --- 4. malformed response ---


def test_malformed_top_level_response_yields_nothing_without_crashing():
    provider = _provider_with_handler(
        lambda request: _json_response(200, "text_search_response_malformed.json")
    )
    assert list(provider.collect(EXAMPLE_CONFIG)) == []


# --- 5. pagination fixture ---


def test_pagination_across_two_fixture_pages():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        fixture = (
            "text_search_response_page1.json"
            if call_count == 1
            else "text_search_response_page2.json"
        )
        return _json_response(200, fixture)

    provider = _provider_with_handler(handler)
    config = {**EXAMPLE_CONFIG, "max_results": 3}

    items = list(provider.collect(config))

    assert call_count == 2
    assert [item["id"] for item in items] == [
        "page1-place-1",
        "page1-place-2",
        "page2-place-1",
    ]


# --- 6. quota error ---


def test_quota_error_is_classified_correctly_and_never_retried():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return _json_response(429, "error_quota.json")

    provider = _provider_with_handler(handler)

    with pytest.raises(GoogleMapsApiError) as exc_info:
        list(provider.collect(EXAMPLE_CONFIG))

    classified = provider.classify_error(exc_info.value)
    assert classified.category == ProviderErrorCategory.QUOTA
    assert classified.retryable is False
    assert call_count == 1  # never retried in-client


# --- 7. authentication error ---


def test_authentication_error_is_classified_correctly_and_never_retried():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return _json_response(401, "error_authentication.json")

    provider = _provider_with_handler(handler)

    with pytest.raises(GoogleMapsApiError) as exc_info:
        list(provider.collect(EXAMPLE_CONFIG))

    classified = provider.classify_error(exc_info.value)
    assert classified.category == ProviderErrorCategory.AUTHENTICATION
    assert classified.retryable is False
    assert call_count == 1  # never retried in-client


# --- 8. transient error ---


def test_transient_error_is_retried_in_client_then_classified_as_retryable():
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return _json_response(503, "error_transient.json")

    provider = _provider_with_handler(handler)

    with pytest.raises(GoogleMapsApiError) as exc_info:
        list(provider.collect(EXAMPLE_CONFIG))

    classified = provider.classify_error(exc_info.value)
    assert classified.category == ProviderErrorCategory.TEMPORARY
    assert classified.retryable is True
    assert call_count > 1  # GoogleMapsClient's own retry policy kicked in


# --- 9. normalization ---


def test_normalize_delegates_to_the_real_mapper():
    provider = _provider_with_handler(lambda request: httpx.Response(200, json={}))
    raw_item = _load_fixture("text_search_response_valid.json")["places"][0]

    assert provider.normalize(raw_item) == normalize_place(raw_item)


# --- 10. provenance ---


def test_provider_record_id_survives_the_full_collect_then_normalize_chain():
    provider = _provider_with_handler(
        lambda request: _json_response(200, "text_search_response_valid.json")
    )

    raw_items = list(provider.collect(EXAMPLE_CONFIG))
    normalized = [provider.normalize(item) for item in raw_items]

    assert [item.provider_record_id for item in normalized] == [
        "ChIJrTLr-GyuEmsRBfy61i59si0",
        "ChIJanotherPlaceId456",
    ]


# --- 11. deterministic mapping ---


def test_normalizing_the_same_raw_item_twice_is_deterministic():
    provider = _provider_with_handler(lambda request: httpx.Response(200, json={}))
    raw_item = _load_fixture("text_search_response_valid.json")["places"][0]

    assert provider.normalize(raw_item) == provider.normalize(raw_item)


# --- validate_config / estimate / health_check delegation ---


def test_validate_config_delegates_to_the_real_validator():
    provider = _provider_with_handler(lambda request: httpx.Response(200, json={}))
    assert not provider.validate_config({}).is_valid
    assert provider.validate_config(EXAMPLE_CONFIG).is_valid


def test_estimate_reflects_the_configured_max_results():
    provider = _provider_with_handler(lambda request: httpx.Response(200, json={}))
    estimate = provider.estimate({**EXAMPLE_CONFIG, "max_results": 42})
    assert estimate.estimated_units == 42


def test_health_check_reports_healthy_once_constructed():
    provider = _provider_with_handler(lambda request: httpx.Response(200, json={}))
    assert provider.health_check().healthy is True


def test_classify_error_falls_back_to_unknown_for_a_non_google_exception():
    provider = _provider_with_handler(lambda request: httpx.Response(200, json={}))
    classified = provider.classify_error(RuntimeError("something unrelated"))
    assert classified.category == ProviderErrorCategory.UNKNOWN
    assert classified.retryable is False
