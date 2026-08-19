"""T052 tests: Stage 5 ("Canonical identity") of
docs/08_DATA_PIPELINE_DEEP.md - deterministic record identity. Covers
every T052 IMPLEMENT/test item: repeated identical input, minor
formatting differences, different businesses, and the DO NOT rule
(never use business name alone)."""

from datetime import UTC, datetime

import pytest

from app.domain.records import RecordDraft
from app.pipeline.canonical_identity import (
    CanonicalIdentityError,
    compute_canonical_key,
)

COLLECTED_AT = datetime(2026, 8, 20, 12, 0, 0, tzinfo=UTC)


def _record(
    *,
    provider: str = "google_maps",
    provider_record_id: str | None = "place-1",
    data: dict | None = None,
) -> RecordDraft:
    return RecordDraft(
        project_id=7,
        job_id=99,
        provider=provider,
        data=data or {},
        collected_at=COLLECTED_AT,
        provider_record_id=provider_record_id,
    )


# --- 1. prefer stable provider identifiers when permitted ---


def test_provider_identifier_is_used_when_present():
    record = _record(provider_record_id="ChIJabc123")
    assert compute_canonical_key(record) == "google_maps:ChIJabc123"


def test_provider_identifier_is_preferred_even_when_name_and_address_exist():
    record = _record(
        provider_record_id="ChIJabc123",
        data={"name": "Example Cafe", "formatted_address": "123 Example St"},
    )
    assert compute_canonical_key(record) == "google_maps:ChIJabc123"


def test_the_provider_is_embedded_so_different_providers_never_collide():
    google = _record(provider="google_maps", provider_record_id="12345")
    other = _record(provider="other_provider", provider_record_id="12345")
    assert compute_canonical_key(google) != compute_canonical_key(other)


# --- 2/3/4. fallback canonicalization, identity-input normalization, key generation ---


def test_fallback_is_used_when_no_provider_identifier_exists():
    record = _record(
        provider_record_id=None,
        data={"name": "Example Cafe", "formatted_address": "123 Example St"},
    )
    key = compute_canonical_key(record)
    assert key.startswith("google_maps:fallback:")


def test_fallback_key_is_a_bounded_length_hash_not_the_raw_text():
    """canonical_key is String(512) (app/db/models/record.py) - a
    hashed fallback stays far under that even for very long input,
    unlike embedding the raw name/address verbatim would."""
    long_name = "A" * 1000
    long_address = "B" * 1000
    record = _record(
        provider_record_id=None,
        data={"name": long_name, "formatted_address": long_address},
    )
    key = compute_canonical_key(record)
    assert len(key) < 200


def test_fallback_raises_when_neither_provider_id_nor_name_and_address_exist():
    record = _record(provider_record_id=None, data={})
    with pytest.raises(CanonicalIdentityError):
        compute_canonical_key(record)


def test_fallback_raises_when_address_is_missing():
    record = _record(provider_record_id=None, data={"name": "Example Cafe"})
    with pytest.raises(CanonicalIdentityError):
        compute_canonical_key(record)


def test_fallback_raises_when_name_is_missing():
    record = _record(
        provider_record_id=None, data={"formatted_address": "123 Example St"}
    )
    with pytest.raises(CanonicalIdentityError):
        compute_canonical_key(record)


def test_do_not_use_business_name_alone_as_identity():
    """T052's explicit DO NOT rule: two different addresses under the
    same name must NOT collide - proves the fallback genuinely
    incorporates address, not just name."""
    record_a = _record(
        provider_record_id=None,
        data={"name": "Example Cafe", "formatted_address": "1 First St"},
    )
    record_b = _record(
        provider_record_id=None,
        data={"name": "Example Cafe", "formatted_address": "2 Second Ave"},
    )
    assert compute_canonical_key(record_a) != compute_canonical_key(record_b)


# --- 6. repeated identical input ---


def test_repeated_identical_input_produces_the_same_key():
    record = _record(
        provider_record_id=None,
        data={"name": "Example Cafe", "formatted_address": "123 Example St"},
    )
    assert compute_canonical_key(record) == compute_canonical_key(record)


def test_repeated_identical_provider_id_input_produces_the_same_key():
    record = _record(provider_record_id="ChIJabc123")
    assert compute_canonical_key(record) == compute_canonical_key(record)


# --- 7. minor formatting differences ---


def test_case_differences_in_the_fallback_input_do_not_change_the_key():
    lower = _record(
        provider_record_id=None,
        data={"name": "example cafe", "formatted_address": "123 example st"},
    )
    upper = _record(
        provider_record_id=None,
        data={"name": "EXAMPLE CAFE", "formatted_address": "123 EXAMPLE ST"},
    )
    assert compute_canonical_key(lower) == compute_canonical_key(upper)


def test_whitespace_differences_in_the_fallback_input_do_not_change_the_key():
    tight = _record(
        provider_record_id=None,
        data={"name": "Example Cafe", "formatted_address": "123 Example St"},
    )
    padded = _record(
        provider_record_id=None,
        data={
            "name": "  Example   Cafe  ",
            "formatted_address": "  123   Example   St  ",
        },
    )
    assert compute_canonical_key(tight) == compute_canonical_key(padded)


# --- 8. different businesses ---


def test_different_business_names_at_the_same_address_produce_different_keys():
    cafe = _record(
        provider_record_id=None,
        data={"name": "Example Cafe", "formatted_address": "123 Example St"},
    )
    diner = _record(
        provider_record_id=None,
        data={"name": "Example Diner", "formatted_address": "123 Example St"},
    )
    assert compute_canonical_key(cafe) != compute_canonical_key(diner)


def test_the_same_business_name_at_different_addresses_produces_different_keys():
    downtown = _record(
        provider_record_id=None,
        data={"name": "Example Cafe", "formatted_address": "1 Downtown Ave"},
    )
    uptown = _record(
        provider_record_id=None,
        data={"name": "Example Cafe", "formatted_address": "2 Uptown Ave"},
    )
    assert compute_canonical_key(downtown) != compute_canonical_key(uptown)
