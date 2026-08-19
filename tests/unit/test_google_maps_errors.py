"""T044 tests: classifying GoogleMapsApiError into
app.domain.provider_contracts.ProviderErrorCategory — every mapping
this task's IMPLEMENT list names, plus retryability and diagnostic
context. No network, no real Google error — GoogleMapsApiError is
constructed directly."""

import pytest

from app.domain.provider_contracts import ProviderErrorCategory
from app.providers.google_maps.client import GoogleMapsApiError
from app.providers.google_maps.errors import classify_google_maps_error


def _error(
    message: str = "boom",
    *,
    status_code: int | None,
    google_error_status: str | None = None,
) -> GoogleMapsApiError:
    return GoogleMapsApiError(
        message, status_code=status_code, google_error_status=google_error_status
    )


@pytest.mark.parametrize(
    "google_error_status,http_status,expected_category",
    [
        ("UNAUTHENTICATED", 401, ProviderErrorCategory.AUTHENTICATION),
        ("PERMISSION_DENIED", 403, ProviderErrorCategory.AUTHENTICATION),
        ("INVALID_ARGUMENT", 400, ProviderErrorCategory.INVALID_REQUEST),
        ("FAILED_PRECONDITION", 400, ProviderErrorCategory.INVALID_REQUEST),
        ("NOT_FOUND", 404, ProviderErrorCategory.INVALID_REQUEST),
        ("RESOURCE_EXHAUSTED", 429, ProviderErrorCategory.QUOTA),
        ("UNAVAILABLE", 503, ProviderErrorCategory.TEMPORARY),
        ("DEADLINE_EXCEEDED", 504, ProviderErrorCategory.TEMPORARY),
        ("INTERNAL", 500, ProviderErrorCategory.TEMPORARY),
        ("ABORTED", 409, ProviderErrorCategory.TEMPORARY),
    ],
)
def test_maps_each_documented_google_error_status(
    google_error_status, http_status, expected_category
):
    error = _error(status_code=http_status, google_error_status=google_error_status)
    classified = classify_google_maps_error(error)
    assert classified.category == expected_category


def test_transport_level_failure_with_no_status_code_is_temporary():
    error = _error(status_code=None)
    classified = classify_google_maps_error(error)
    assert classified.category == ProviderErrorCategory.TEMPORARY
    assert classified.retryable is True


@pytest.mark.parametrize(
    "http_status,expected_category",
    [
        (401, ProviderErrorCategory.AUTHENTICATION),
        (403, ProviderErrorCategory.AUTHENTICATION),
        (400, ProviderErrorCategory.INVALID_REQUEST),
        (429, ProviderErrorCategory.QUOTA),
        (503, ProviderErrorCategory.TEMPORARY),
    ],
)
def test_falls_back_to_http_status_when_google_error_status_is_missing(
    http_status, expected_category
):
    error = _error(status_code=http_status, google_error_status=None)
    classified = classify_google_maps_error(error)
    assert classified.category == expected_category


def test_unrecognized_4xx_with_no_google_status_is_permanent_not_retryable():
    error = _error(status_code=418, google_error_status=None)
    classified = classify_google_maps_error(error)
    assert classified.category == ProviderErrorCategory.PERMANENT
    assert classified.retryable is False


def test_unrecognized_status_code_outside_4xx_5xx_is_unknown():
    error = _error(status_code=999, google_error_status=None)
    classified = classify_google_maps_error(error)
    assert classified.category == ProviderErrorCategory.UNKNOWN
    assert classified.retryable is False


def test_authentication_and_quota_errors_are_marked_not_retryable():
    auth_error = classify_google_maps_error(
        _error(status_code=401, google_error_status="UNAUTHENTICATED")
    )
    quota_error = classify_google_maps_error(
        _error(status_code=429, google_error_status="RESOURCE_EXHAUSTED")
    )
    assert auth_error.retryable is False
    assert quota_error.retryable is False


def test_temporary_errors_are_marked_retryable():
    classified = classify_google_maps_error(
        _error(status_code=503, google_error_status="UNAVAILABLE")
    )
    assert classified.retryable is True


def test_diagnostic_context_is_preserved():
    error = _error(
        "Quota exceeded for this project.",
        status_code=429,
        google_error_status="RESOURCE_EXHAUSTED",
    )
    classified = classify_google_maps_error(error)

    assert classified.message == "Quota exceeded for this project."
    assert classified.http_status_code == 429
    assert classified.provider_status == "RESOURCE_EXHAUSTED"


def test_worker_can_make_a_deterministic_retry_decision_from_two_identical_errors():
    """T044's literal acceptance criterion."""
    first = classify_google_maps_error(
        _error(status_code=503, google_error_status="UNAVAILABLE")
    )
    second = classify_google_maps_error(
        _error(status_code=503, google_error_status="UNAVAILABLE")
    )
    assert first.retryable is True
    assert second.retryable is True
