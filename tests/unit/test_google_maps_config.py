"""T041 tests: Google-specific config validation — no network, no
SDK. `example_config()` is a literal, fully-valid config satisfying
every rule; each invalid-case test starts from a deep-enough copy of
it and breaks exactly one thing, proving that one rule (not some
interacting combination) causes the rejection."""

import copy
from typing import Any

import pytest
from tests.unit.factories import make_user

from app.db.session import session_scope
from app.providers.google_maps.config import (
    MAX_RESULT_COUNT,
    GoogleMapsConfigValidator,
)
from app.repositories.audit import SqlAlchemyAuditLogRepository
from app.repositories.configs import SqlAlchemyCollectionConfigRepository
from app.repositories.projects import SqlAlchemyProjectRepository
from app.services.audit import AuditService
from app.services.configs import ConfigurationService
from app.services.errors import InvalidStateError
from app.services.projects import ProjectService


def example_config() -> dict[str, Any]:
    return {
        "query": "coffee shops",
        "location": {"latitude": 21.1702, "longitude": 72.8311},
        "radius_meters": 10_000,
        "fields": ["displayName", "formattedAddress", "rating"],
        "max_results": 20,
        "price_levels": ["PRICE_LEVEL_INEXPENSIVE", "PRICE_LEVEL_MODERATE"],
        "rank_preference": "RELEVANCE",
    }


def _validator(api_key: str | None = "fake-api-key") -> GoogleMapsConfigValidator:
    return GoogleMapsConfigValidator(api_key=api_key)


def test_fully_valid_config_is_accepted():
    result = _validator().validate_config("google_maps", example_config())
    assert result.is_valid


def test_missing_api_key_is_rejected():
    result = _validator(api_key=None).validate_config("google_maps", example_config())
    assert not result.is_valid
    assert any("credentials are not configured" in error for error in result.errors)


def test_missing_query_is_rejected():
    config = copy.deepcopy(example_config())
    del config["query"]
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any("query" in error for error in result.errors)


def test_blank_query_is_rejected():
    config = copy.deepcopy(example_config())
    config["query"] = "   "
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid


def test_config_with_no_location_is_still_valid():
    """location is optional — a Text Search query can be unbiased."""
    config = copy.deepcopy(example_config())
    del config["location"]
    del config["radius_meters"]
    result = _validator().validate_config("google_maps", config)
    assert result.is_valid


def test_latitude_out_of_range_is_rejected():
    config = copy.deepcopy(example_config())
    config["location"]["latitude"] = 91.0
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any("latitude" in error for error in result.errors)


def test_longitude_out_of_range_is_rejected():
    config = copy.deepcopy(example_config())
    config["location"]["longitude"] = -181.0
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any("longitude" in error for error in result.errors)


def test_radius_without_location_is_rejected():
    config = copy.deepcopy(example_config())
    del config["location"]
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any("requires config.location" in error for error in result.errors)


def test_radius_over_googles_hard_cap_is_rejected():
    """Google's locationBias radius caps at 50,000 meters."""
    config = copy.deepcopy(example_config())
    config["radius_meters"] = 50_001
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any("radius_meters" in error for error in result.errors)


def test_missing_fields_is_rejected():
    config = copy.deepcopy(example_config())
    del config["fields"]
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any("fields is required" in error for error in result.errors)


def test_empty_fields_list_is_rejected():
    config = copy.deepcopy(example_config())
    config["fields"] = []
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid


def test_unknown_field_name_is_rejected_with_the_exact_field_named():
    config = copy.deepcopy(example_config())
    config["fields"] = ["displayName", "not_a_real_field"]
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any("not_a_real_field" in error for error in result.errors)


def test_max_results_over_googles_hard_cap_is_rejected():
    """docs/07's own conceptual example config uses max_results: 100 —
    this is exactly the unrealistic value this validator must catch,
    with an actionable error naming Google's real 60-result cap."""
    config = copy.deepcopy(example_config())
    config["max_results"] = 100
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any(str(MAX_RESULT_COUNT) in error for error in result.errors)


def test_max_results_at_the_hard_cap_is_accepted():
    config = copy.deepcopy(example_config())
    config["max_results"] = MAX_RESULT_COUNT
    result = _validator().validate_config("google_maps", config)
    assert result.is_valid


def test_non_integer_max_results_is_rejected():
    config = copy.deepcopy(example_config())
    config["max_results"] = "20"
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid


def test_price_level_free_is_rejected_in_requests():
    """Google only ever returns PRICE_LEVEL_FREE, never accepts it as
    a request filter."""
    config = copy.deepcopy(example_config())
    config["price_levels"] = ["PRICE_LEVEL_FREE"]
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid
    assert any("PRICE_LEVEL_FREE" in error for error in result.errors)


def test_invalid_rank_preference_is_rejected():
    config = copy.deepcopy(example_config())
    config["rank_preference"] = "CLOSEST_FIRST"
    result = _validator().validate_config("google_maps", config)
    assert not result.is_valid


def test_multiple_violations_are_all_reported_at_once():
    result = _validator(api_key=None).validate_config("google_maps", {})
    assert not result.is_valid
    assert len(result.errors) > 1


def test_invalid_config_never_reaches_configuration_service_persistence(
    session_factory,
):
    """T041's literal acceptance criterion, exercised through the real
    T034 service: an invalid config is rejected before any row is
    created — 'invalid requests never reach provider execution' starts
    with never letting an invalid config become active in the first
    place."""
    with session_scope(session_factory) as session:
        audit = AuditService(SqlAlchemyAuditLogRepository(session))
        projects = ProjectService(SqlAlchemyProjectRepository(session), audit)
        configs = ConfigurationService(
            SqlAlchemyCollectionConfigRepository(session),
            projects,
            GoogleMapsConfigValidator(api_key=None),  # no credentials configured
            audit,
        )
        user = make_user(session)
        project = projects.create_project(
            user_id=user.id, name="My Project", source_type="google_maps"
        )

        with pytest.raises(InvalidStateError):
            configs.create_version(
                project.id,
                requesting_user_id=user.id,
                provider="google_maps",
                config=example_config(),
            )

        assert configs.get_active(project.id, requesting_user_id=user.id) is None
