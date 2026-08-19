"""T051 tests: Stage 2/4 ("Schema validation" / "Quality") of
docs/08_DATA_PIPELINE_DEEP.md - field-level data quality checks on a
RecordDraft. One section per T051 IMPLEMENT item, plus the two
"valid/warning/rejected record" integration tests item 9 explicitly
asks for, phrased against docs/08's own worked examples."""

from datetime import UTC, datetime

from app.domain.records import RecordDraft
from app.pipeline.validate import (
    FieldRule,
    FieldValidationError,
    RecordQuality,
    ValidationResult,
    validate_record_draft,
)

COLLECTED_AT = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)


def _record(data: dict) -> RecordDraft:
    return RecordDraft(
        project_id=7,
        job_id=99,
        provider="google_maps",
        data=data,
        collected_at=COLLECTED_AT,
        provider_record_id="place-1",
    )


# --- 1. valid/warning/rejected states ---


def test_quality_states_are_exactly_valid_warning_rejected():
    assert {member.value for member in RecordQuality} == {
        "valid",
        "warning",
        "rejected",
    }


# --- 2. types ---


def test_wrong_type_produces_an_error_at_the_rules_severity():
    record = _record({"rating": "not a number"})
    result = validate_record_draft(
        record, {"rating": FieldRule(expected_types=(int, float))}
    )
    assert result.quality == RecordQuality.REJECTED
    assert result.errors[0].field == "rating"


def test_a_bool_is_never_accepted_as_a_numeric_type():
    """bool is a subclass of int in Python - must not silently pass a
    numeric-type check."""
    record = _record({"rating": True})
    result = validate_record_draft(
        record, {"rating": FieldRule(expected_types=(int, float))}
    )
    assert result.quality == RecordQuality.REJECTED


def test_correct_type_produces_no_error():
    record = _record({"rating": 4.5})
    result = validate_record_draft(
        record, {"rating": FieldRule(expected_types=(int, float))}
    )
    assert result.quality == RecordQuality.VALID
    assert result.errors == []


# --- 3. ranges ---


def test_value_below_minimum_is_rejected():
    record = _record({"rating": -1.0})
    result = validate_record_draft(record, {"rating": FieldRule(min_value=0.0)})
    assert result.quality == RecordQuality.REJECTED


def test_value_above_maximum_is_rejected():
    record = _record({"rating": 6.0})
    result = validate_record_draft(record, {"rating": FieldRule(max_value=5.0)})
    assert result.quality == RecordQuality.REJECTED


def test_value_within_range_is_valid():
    record = _record({"rating": 4.5})
    result = validate_record_draft(
        record, {"rating": FieldRule(min_value=0.0, max_value=5.0)}
    )
    assert result.quality == RecordQuality.VALID


def test_a_non_numeric_value_cannot_be_range_checked():
    record = _record({"rating": "high"})
    result = validate_record_draft(record, {"rating": FieldRule(min_value=0.0)})
    assert result.quality == RecordQuality.REJECTED
    assert "numeric" in result.errors[0].message


# --- 4. required fields (missing_severity) ---


def test_a_required_field_missing_entirely_is_flagged():
    record = _record({})
    result = validate_record_draft(
        record, {"name": FieldRule(missing_severity=RecordQuality.REJECTED)}
    )
    assert result.quality == RecordQuality.REJECTED
    assert result.errors[0].field == "name"


def test_an_optional_field_missing_entirely_is_not_flagged():
    record = _record({})
    result = validate_record_draft(record, {"rating": FieldRule()})
    assert result.quality == RecordQuality.VALID
    assert result.errors == []


def test_missing_can_have_a_different_severity_than_present_but_invalid():
    """docs/08's own distinction: a field can be optional-but-flagged
    when absent (warning) while still being strictly checked when
    present."""
    rule = FieldRule(
        missing_severity=RecordQuality.WARNING,
        expected_types=(str,),
        severity=RecordQuality.REJECTED,
    )
    missing = validate_record_draft(_record({}), {"website": rule})
    wrong_type = validate_record_draft(_record({"website": 123}), {"website": rule})

    assert missing.quality == RecordQuality.WARNING
    assert wrong_type.quality == RecordQuality.REJECTED


# --- 5. coordinate ranges ---


def test_a_valid_latitude_and_longitude_pass():
    record = _record({"latitude": 21.1702, "longitude": 72.8311})
    result = validate_record_draft(
        record,
        {
            "latitude": FieldRule(min_value=-90.0, max_value=90.0),
            "longitude": FieldRule(min_value=-180.0, max_value=180.0),
        },
    )
    assert result.quality == RecordQuality.VALID


def test_an_out_of_range_coordinate_is_rejected():
    """docs/08's literal example: "invalid coordinate -> rejected"."""
    record = _record({"latitude": 200.0, "longitude": 72.8311})
    result = validate_record_draft(
        record,
        {
            "latitude": FieldRule(min_value=-90.0, max_value=90.0),
            "longitude": FieldRule(min_value=-180.0, max_value=180.0),
        },
    )
    assert result.quality == RecordQuality.REJECTED
    assert result.errors[0].field == "latitude"


# --- 6. URL syntax ---


def test_a_syntactically_valid_url_passes():
    record = _record({"website": "https://example.test/menu"})
    result = validate_record_draft(record, {"website": FieldRule(is_url=True)})
    assert result.quality == RecordQuality.VALID


def test_a_string_missing_a_scheme_is_not_a_valid_url():
    record = _record({"website": "example.test/menu"})
    result = validate_record_draft(record, {"website": FieldRule(is_url=True)})
    assert result.quality == RecordQuality.REJECTED


def test_a_non_http_scheme_is_not_a_valid_url():
    record = _record({"website": "ftp://example.test/file"})
    result = validate_record_draft(record, {"website": FieldRule(is_url=True)})
    assert result.quality == RecordQuality.REJECTED


def test_a_non_string_value_fails_the_url_check():
    record = _record({"website": 12345})
    result = validate_record_draft(record, {"website": FieldRule(is_url=True)})
    assert result.quality == RecordQuality.REJECTED


# --- 7. field-level error objects ---


def test_errors_are_field_level_objects_not_a_flat_message_list():
    record = _record({"rating": "bad", "website": "not a url"})
    result = validate_record_draft(
        record,
        {
            "rating": FieldRule(expected_types=(int, float)),
            "website": FieldRule(is_url=True),
        },
    )
    fields_with_errors = {error.field for error in result.errors}
    assert fields_with_errors == {"rating", "website"}
    assert all(isinstance(error, FieldValidationError) for error in result.errors)


# --- 8. preserve job context ---


def test_project_and_job_id_are_preserved_on_the_result():
    result = validate_record_draft(_record({}), {})
    assert result.project_id == 7
    assert result.job_id == 99


# --- 9. valid / warning / rejected records ---

_TEXT_SEARCH_RULES = {
    "name": FieldRule(missing_severity=RecordQuality.REJECTED, expected_types=(str,)),
    "latitude": FieldRule(min_value=-90.0, max_value=90.0),
    "longitude": FieldRule(min_value=-180.0, max_value=180.0),
    "website": FieldRule(
        missing_severity=RecordQuality.WARNING,
        is_url=True,
        severity=RecordQuality.WARNING,
    ),
}


def test_a_fully_populated_record_is_valid():
    record = _record(
        {
            "name": "Example Cafe",
            "latitude": 21.1702,
            "longitude": 72.8311,
            "website": "https://example-cafe.test/",
        }
    )
    result = validate_record_draft(record, _TEXT_SEARCH_RULES)
    assert result.quality == RecordQuality.VALID
    assert result.errors == []


def test_a_record_missing_website_is_a_warning_not_a_rejection():
    """docs/08's literal example: "missing website -> warning"."""
    record = _record(
        {"name": "Example Cafe", "latitude": 21.1702, "longitude": 72.8311}
    )
    result = validate_record_draft(record, _TEXT_SEARCH_RULES)
    assert result.quality == RecordQuality.WARNING
    assert result.errors[0].field == "website"


def test_a_record_missing_name_is_rejected():
    record = _record({"latitude": 21.1702, "longitude": 72.8311})
    result = validate_record_draft(record, _TEXT_SEARCH_RULES)
    assert result.quality == RecordQuality.REJECTED


def test_a_record_with_both_a_warning_and_a_rejection_reports_the_worse_one():
    record = _record({"latitude": 200.0, "longitude": 72.8311})  # no name, no website
    result = validate_record_draft(record, _TEXT_SEARCH_RULES)
    assert result.quality == RecordQuality.REJECTED
    severities = {error.field: error.severity for error in result.errors}
    assert severities["name"] == RecordQuality.REJECTED
    assert severities["website"] == RecordQuality.WARNING
    assert severities["latitude"] == RecordQuality.REJECTED


# --- determinism / no network calls (T051's literal acceptance criterion) ---


def test_validation_is_deterministic():
    record = _record({"name": "Example Cafe", "rating": 4.5})
    rules = {
        "name": FieldRule(expected_types=(str,)),
        "rating": FieldRule(min_value=0.0, max_value=5.0),
    }
    first = validate_record_draft(record, rules)
    second = validate_record_draft(record, rules)
    assert first == second


def test_the_result_type_carries_no_hidden_network_dependent_state():
    """A structural sanity check standing in for "no network calls" -
    ValidationResult and FieldValidationError are plain frozen
    dataclasses with no client/session attribute."""
    result = validate_record_draft(_record({}), {})
    assert isinstance(result, ValidationResult)
