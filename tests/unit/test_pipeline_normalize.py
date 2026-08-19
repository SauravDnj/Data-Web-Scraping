"""T050 tests: Stage 3 ("Normalization") of docs/08_DATA_PIPELINE_DEEP.md
- pure, provider-agnostic value transformations. One test class per
transformation category, per T050's own instruction ("create unit
tests for each transformation"), plus a regression-fixture-style test
proving strict determinism (T050's literal acceptance criterion).

This file is written in plain ASCII throughout, including the Unicode
test below, which builds its non-ASCII characters from \\uXXXX code
points via chr() rather than typing them as literal source characters
- keeps the file's own encoding unambiguous regardless of editor/tool."""

import json
from pathlib import Path

from app.pipeline.normalize import FieldKind, normalize_record_data

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures" / "pipeline"

# --- 1. whitespace ---


def test_leading_and_trailing_whitespace_is_trimmed():
    result = normalize_record_data({"name": "  Example Cafe  "}, {})
    assert result["name"] == "Example Cafe"


def test_internal_whitespace_is_left_alone():
    """ "Trim" means edges only - collapsing internal whitespace would
    be a content change, not a normalization."""
    result = normalize_record_data({"name": "Example   Cafe"}, {})
    assert result["name"] == "Example   Cafe"


# --- 2. Unicode (NFC only, never NFKC) ---


def test_unicode_is_canonically_composed():
    # NFD (decomposed): "e" (U+0065) + combining acute accent
    # (U+0301). NFC (composed): the single precomposed character
    # U+00E9. Built with chr() from explicit code points, not typed as
    # source characters, so there is no ambiguity about which form is
    # which regardless of the file's own encoding.
    decomposed_name = "caf" + chr(0x0065) + chr(0x0301)
    composed_name = "caf" + chr(0x00E9)
    assert decomposed_name != composed_name  # sanity check the fixture

    result = normalize_record_data({"name": decomposed_name}, {})

    assert result["name"] == composed_name


def test_compatibility_variants_are_not_folded():
    """NFKC would turn the trademark sign (U+2122) into plain "TM" -
    content-changing, so NFKC is never used here."""
    trademark_name = "Example" + chr(0x2122)
    result = normalize_record_data({"name": trademark_name}, {})
    assert result["name"] == trademark_name


# --- 3. URLs ---


def test_url_scheme_and_host_are_lowercased():
    result = normalize_record_data(
        {"website": "HTTPS://Example-Cafe.TEST/Menu"}, {"website": FieldKind.URL}
    )
    assert result["website"] == "https://example-cafe.test/Menu"


def test_url_path_case_is_preserved():
    """Paths can be case-sensitive on the server - only scheme/host
    are safe to lowercase unconditionally."""
    result = normalize_record_data(
        {"website": "https://example.test/CaseSensitivePath"},
        {"website": FieldKind.URL},
    )
    assert result["website"] == "https://example.test/CaseSensitivePath"


def test_a_string_that_is_not_actually_a_url_is_left_as_text():
    result = normalize_record_data(
        {"website": "not a url at all"}, {"website": FieldKind.URL}
    )
    assert result["website"] == "not a url at all"


# --- 4. numeric fields ---


def test_a_clean_integer_string_is_converted_to_int():
    result = normalize_record_data({"count": "128"}, {"count": FieldKind.NUMBER})
    assert result["count"] == 128
    assert isinstance(result["count"], int)


def test_a_clean_decimal_string_is_converted_to_float():
    result = normalize_record_data({"rating": "4.5"}, {"rating": FieldKind.NUMBER})
    assert result["rating"] == 4.5
    assert isinstance(result["rating"], float)


def test_an_already_numeric_value_is_left_untouched():
    result = normalize_record_data({"rating": 4.5}, {"rating": FieldKind.NUMBER})
    assert result["rating"] == 4.5
    assert isinstance(result["rating"], float)


def test_an_ambiguous_numeric_looking_string_is_never_guessed_at():
    """Currency symbols/thousand separators are locale-specific -
    never coerced, to avoid inventing a value."""
    result = normalize_record_data({"price": "$1,234.56"}, {"price": FieldKind.NUMBER})
    assert result["price"] == "$1,234.56"


# --- 5. timestamps ---


def test_a_timestamp_with_explicit_utc_offset_is_canonicalized_to_z_form():
    result = normalize_record_data(
        {"collected_at": "2026-08-20T12:00:00+00:00"},
        {"collected_at": FieldKind.TIMESTAMP},
    )
    assert result["collected_at"] == "2026-08-20T12:00:00Z"


def test_a_timestamp_already_in_z_form_round_trips():
    result = normalize_record_data(
        {"collected_at": "2026-08-20T12:00:00Z"},
        {"collected_at": FieldKind.TIMESTAMP},
    )
    assert result["collected_at"] == "2026-08-20T12:00:00Z"


def test_a_non_utc_offset_is_converted_to_utc():
    result = normalize_record_data(
        {"collected_at": "2026-08-20T09:00:00-03:00"},
        {"collected_at": FieldKind.TIMESTAMP},
    )
    assert result["collected_at"] == "2026-08-20T12:00:00Z"


def test_a_timestamp_with_no_explicit_timezone_is_left_as_text():
    """Assuming UTC (or any zone) for a naive timestamp would invent
    information that was never actually stated."""
    result = normalize_record_data(
        {"collected_at": "2026-08-20T12:00:00"},
        {"collected_at": FieldKind.TIMESTAMP},
    )
    assert result["collected_at"] == "2026-08-20T12:00:00"


def test_an_unparseable_timestamp_is_left_as_text_not_crashed_on():
    result = normalize_record_data(
        {"collected_at": "not a timestamp"}, {"collected_at": FieldKind.TIMESTAMP}
    )
    assert result["collected_at"] == "not a timestamp"


# --- 6. category values ---


def test_category_values_are_lowercased():
    result = normalize_record_data(
        {"business_status": "OPERATIONAL"}, {"business_status": FieldKind.CATEGORY}
    )
    assert result["business_status"] == "operational"


def test_category_list_values_are_each_lowercased():
    result = normalize_record_data(
        {"types": ["CAFE", "Food"]}, {"types": FieldKind.CATEGORY}
    )
    assert result["types"] == ["cafe", "food"]


# --- 7/8. preserve source semantics / never invent missing values ---


def test_a_key_absent_from_the_input_is_never_added():
    result = normalize_record_data(
        {"name": "Example Cafe"}, {"rating": FieldKind.NUMBER}
    )
    assert "rating" not in result


def test_non_string_values_are_never_coerced_by_a_text_or_category_kind():
    result = normalize_record_data(
        {"open_now": True, "count": 5}, {"count": FieldKind.CATEGORY}
    )
    assert result == {"open_now": True, "count": 5}


def test_none_values_pass_through_unchanged():
    result = normalize_record_data({"phone_number": None}, {})
    assert result["phone_number"] is None


def test_the_input_mapping_is_never_mutated():
    original = {"name": "  Example Cafe  "}
    normalize_record_data(original, {})
    assert original == {"name": "  Example Cafe  "}


def test_an_undeclared_field_kind_defaults_to_text():
    result = normalize_record_data({"anything": "  padded  "}, {})
    assert result["anything"] == "padded"


# --- 10. regression fixture ---


def test_normalize_regression_fixture():
    """A dedicated regression fixture (tests/fixtures/pipeline/
    normalize_regression.json, T050 item 10) covering every kind at
    once, distinct from the inline per-transformation tests above —
    guards against a future change accidentally altering already-
    correct output for a realistic mixed record."""
    fixture = json.loads(
        (FIXTURES_DIR / "normalize_regression.json").read_text(encoding="utf-8")
    )
    field_kinds = {
        key: FieldKind(value) for key, value in fixture["field_kinds"].items()
    }

    result = normalize_record_data(fixture["input"], field_kinds)

    assert result == fixture["expected_output"]


# --- determinism (T050's literal acceptance criterion) ---


def test_normalizing_the_same_input_twice_produces_identical_output():
    data = {
        "name": "  Example   Cafe  ",
        "website": "HTTPS://Example.TEST/Menu",
        "rating": "4.5",
        "business_status": "OPERATIONAL",
        "collected_at": "2026-08-20T12:00:00Z",
    }
    field_kinds = {
        "website": FieldKind.URL,
        "rating": FieldKind.NUMBER,
        "business_status": FieldKind.CATEGORY,
        "collected_at": FieldKind.TIMESTAMP,
    }

    first = normalize_record_data(data, field_kinds)
    second = normalize_record_data(data, field_kinds)

    assert first == second
