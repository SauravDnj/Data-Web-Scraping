"""T043 tests: mapping raw Google Places API (New) Text Search items
into the platform's normalized internal representation — fixture-based
(real captured/synthetic response shapes under tests/fixtures/
google_maps/), per T043's own instruction. `test_same_fixture_always_
produces_the_same_result` is the literal T043 acceptance criterion."""

import json
from datetime import UTC, datetime
from pathlib import Path

from app.domain.provider_contracts import NormalizedItem
from app.domain.records import RecordDraft
from app.providers.google_maps.mapper import (
    GOOGLE_MAPS_TEXT_SEARCH_OPERATION,
    map_place_to_record_draft,
    normalize_place,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "google_maps"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def test_full_place_maps_every_supported_field():
    raw_item = _load_fixture("full_place.json")

    normalized = normalize_place(raw_item)

    assert normalized.provider_record_id == "ChIJrTLr-GyuEmsRBfy61i59si0"
    assert normalized.data == {
        "name": "Example Cafe",
        "formatted_address": "123 Example St, Surat, Gujarat 395001, India",
        "latitude": 21.1702,
        "longitude": 72.8311,
        "business_status": "operational",
        "primary_type": "cafe",
        "types": ["cafe", "food", "point_of_interest", "establishment"],
        "rating": 4.5,
        "user_rating_count": 128,
        "price_level": "price_level_moderate",
        "phone_number": "+91 98765 43210",
        "website": "https://example-cafe.test/",
        "open_now": True,
        "weekday_descriptions": [
            "Monday: 8:00 AM - 8:00 PM",
            "Tuesday: 8:00 AM - 8:00 PM",
            "Wednesday: 8:00 AM - 8:00 PM",
            "Thursday: 8:00 AM - 8:00 PM",
            "Friday: 8:00 AM - 8:00 PM",
            "Saturday: 9:00 AM - 9:00 PM",
            "Sunday: 9:00 AM - 6:00 PM",
        ],
    }


def test_rating_and_count_are_normalized_to_the_right_numeric_types():
    raw_item = _load_fixture("full_place.json")
    normalized = normalize_place(raw_item)

    assert isinstance(normalized.data["rating"], float)
    assert isinstance(normalized.data["user_rating_count"], int)


def test_minimal_place_omits_every_absent_field_rather_than_inventing_one():
    raw_item = _load_fixture("minimal_place.json")

    normalized = normalize_place(raw_item)

    assert normalized.provider_record_id == "ChIJminimalPlaceId123"
    assert normalized.data == {"name": "Minimal Diner"}
    assert "rating" not in normalized.data
    assert "location" not in normalized.data
    assert "latitude" not in normalized.data


def test_malformed_response_never_crashes_and_produces_no_data():
    """T043 item 10: a response with every field present but wrong
    type must not raise — every field is simply omitted, exactly as if
    it had been absent."""
    raw_item = _load_fixture("malformed_place.json")

    normalized = normalize_place(raw_item)

    assert normalized == NormalizedItem(provider_record_id=None, data={})


def test_partial_location_is_treated_as_fully_absent():
    """Latitude present but longitude malformed (or vice versa) must
    not produce a half-populated, misleading coordinate."""
    raw_item = {
        "id": "place-1",
        "location": {"latitude": 21.1702, "longitude": "oops"},
    }

    normalized = normalize_place(raw_item)

    assert "latitude" not in normalized.data
    assert "longitude" not in normalized.data


def test_types_list_drops_non_string_entries_rather_than_failing():
    raw_item = {"id": "place-1", "types": ["cafe", 42, None, "food"]}

    normalized = normalize_place(raw_item)

    assert normalized.data["types"] == ["cafe", "food"]


def test_same_fixture_always_produces_the_same_result():
    """T043's literal acceptance criterion."""
    raw_item = _load_fixture("full_place.json")

    first = normalize_place(raw_item)
    second = normalize_place(raw_item)

    assert first == second


def test_map_place_to_record_draft_attaches_job_project_and_timestamp():
    raw_item = _load_fixture("full_place.json")
    collected_at = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)

    draft = map_place_to_record_draft(
        raw_item, project_id=7, job_id=99, collected_at=collected_at
    )

    assert draft == RecordDraft(
        project_id=7,
        job_id=99,
        provider="google_maps",
        data=normalize_place(raw_item).data,
        collected_at=collected_at,
        provider_record_id="ChIJrTLr-GyuEmsRBfy61i59si0",
    )


def test_record_draft_from_a_place_with_no_id_has_no_provider_record_id():
    raw_item = {"displayName": {"text": "No ID Place"}}
    collected_at = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)

    draft = map_place_to_record_draft(
        raw_item, project_id=1, job_id=1, collected_at=collected_at
    )

    assert draft.provider_record_id is None


def test_operation_constant_is_the_documented_dotted_name():
    assert GOOGLE_MAPS_TEXT_SEARCH_OPERATION == "google_maps.places.text_search"
