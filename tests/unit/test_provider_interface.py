"""T040 tests: the generic ProviderAdapter contract, exercised through
FakeProviderAdapter — no SDK, no network, no MySQL/Redis. Proves the
literal T040 acceptance criterion: "Fake provider can satisfy the
interface and run through tests." """

import pytest
from tests.unit.fakes import FakeProviderAdapter

from app.domain.provider_contracts import (
    NormalizedItem,
    ProviderErrorCategory,
    ProviderHealth,
    UsageEstimate,
)
from app.providers.base import ProviderAdapter


def test_fake_provider_satisfies_the_protocol():
    assert isinstance(FakeProviderAdapter(), ProviderAdapter)


def test_validate_config_accepts_a_config_with_a_query():
    provider = FakeProviderAdapter()
    result = provider.validate_config({"query": "coffee shops"})
    assert result.is_valid


def test_validate_config_rejects_a_config_missing_query():
    provider = FakeProviderAdapter()
    result = provider.validate_config({})
    assert not result.is_valid
    assert "config.query is required." in result.errors


def test_estimate_reflects_the_number_of_available_items():
    provider = FakeProviderAdapter(raw_items=[{"id": "a"}, {"id": "b"}, {"id": "c"}])
    estimate = provider.estimate({"query": "coffee shops"})
    assert estimate == UsageEstimate(estimated_units=3)


def test_usage_estimate_rejects_a_negative_unit_count():
    with pytest.raises(ValueError, match="not be negative"):
        UsageEstimate(estimated_units=-1)


def test_collect_yields_lazily_rather_than_returning_a_buffered_list():
    provider = FakeProviderAdapter(raw_items=[{"id": "a"}, {"id": "b"}])
    items = provider.collect({"query": "coffee shops"})
    assert iter(items) is items  # a real iterator, not a list


def test_collect_yields_every_raw_item():
    raw_items = [{"id": "a", "name": "A"}, {"id": "b", "name": "B"}]
    provider = FakeProviderAdapter(raw_items=raw_items)
    assert list(provider.collect({"query": "coffee shops"})) == raw_items


def test_normalize_maps_a_raw_item_into_the_provider_agnostic_shape():
    provider = FakeProviderAdapter()
    normalized = provider.normalize({"id": "place-1", "name": "Example Cafe"})
    assert normalized == NormalizedItem(
        provider_record_id="place-1", data={"name": "Example Cafe"}
    )


def test_classify_error_maps_timeout_to_temporary():
    provider = FakeProviderAdapter()
    classified = provider.classify_error(TimeoutError("request timed out"))
    assert classified.category == ProviderErrorCategory.TEMPORARY


def test_classify_error_maps_an_unrecognized_exception_to_unknown():
    provider = FakeProviderAdapter()
    classified = provider.classify_error(RuntimeError("something unexpected"))
    assert classified.category == ProviderErrorCategory.UNKNOWN


def test_health_check_reports_healthy():
    provider = FakeProviderAdapter()
    assert provider.health_check() == ProviderHealth(healthy=True)


def test_full_lifecycle_validate_estimate_collect_normalize():
    """docs/07's lifecycle, minus the budget check (application
    concern, not the provider's) and the network call (this is a
    fake): config -> validate -> estimate -> collect -> normalize."""
    raw_items = [{"id": "place-1", "name": "Example Cafe", "rating": 4.5}]
    provider = FakeProviderAdapter(raw_items=raw_items)
    config = {"query": "coffee shops"}

    validation = provider.validate_config(config)
    assert validation.is_valid

    estimate = provider.estimate(config)
    assert estimate.estimated_units == len(raw_items)

    normalized = [provider.normalize(item) for item in provider.collect(config)]
    assert normalized == [
        NormalizedItem(
            provider_record_id="place-1",
            data={"name": "Example Cafe", "rating": 4.5},
        )
    ]
