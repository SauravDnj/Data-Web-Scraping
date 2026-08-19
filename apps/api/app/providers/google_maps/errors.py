"""Classifies `app.providers.google_maps.client.GoogleMapsApiError`
into `app.domain.provider_contracts.ProviderErrorCategory` (T044) —
the real Google implementation of `ProviderAdapter.classify_error()`
(T040's Protocol). Never retries anything itself (T044's own DO NOT
list: "retry policy/authorization failures automatically") — this
module only classifies; `default_retryable_for_category()`
(app.domain.provider_contracts) supplies the retry *decision*, and
`JobService.retry_job()` (T035) is what actually acts on it, later,
with real elapsed time between attempts.

**Google's error model, verified against the same live docs fetched
for T041/T042**: error responses carry a `google.rpc.Code`-style
`error.status` string (`UNAUTHENTICATED`, `INVALID_ARGUMENT`,
`RESOURCE_EXHAUSTED`, `UNAVAILABLE`, ...) alongside the HTTP status
code. **Google does not expose a status distinct from
`RESOURCE_EXHAUSTED` for "you're sending requests too fast" versus
"you've used your quota allotment"** — both surface identically. This
adapter maps `RESOURCE_EXHAUSTED`/429 to `QUOTA`, matching Google's own
terminology ("quota exceeded") and docs/09_JOB_QUEUE_WORKER_DEEP.md's
"do not retry ... provider policy rejection" instruction.
`ProviderErrorCategory.RATE` exists for providers that DO distinguish
the two — this Google adapter simply never produces it, which is an
honest limitation of the upstream API, not a gap in this module."""

from app.domain.provider_contracts import (
    ProviderError,
    ProviderErrorCategory,
    default_retryable_for_category,
)
from app.providers.google_maps.client import GoogleMapsApiError

_AUTHENTICATION_STATUSES = frozenset({"UNAUTHENTICATED", "PERMISSION_DENIED"})
_INVALID_REQUEST_STATUSES = frozenset(
    {"INVALID_ARGUMENT", "FAILED_PRECONDITION", "NOT_FOUND", "OUT_OF_RANGE"}
)
_QUOTA_STATUSES = frozenset({"RESOURCE_EXHAUSTED"})
_TEMPORARY_STATUSES = frozenset(
    {"UNAVAILABLE", "DEADLINE_EXCEEDED", "INTERNAL", "ABORTED"}
)


def classify_google_maps_error(error: GoogleMapsApiError) -> ProviderError:
    category = _categorize(error)
    return ProviderError(
        category=category,
        message=str(error),
        retryable=default_retryable_for_category(category),
        http_status_code=error.status_code,
        provider_status=error.google_error_status,
    )


def _categorize(error: GoogleMapsApiError) -> ProviderErrorCategory:
    if error.status_code is None:
        # A transport-level failure — GoogleMapsClient already retried
        # this up to its own max_retries before giving up; what's left
        # is genuine, still-unresolved infrastructure trouble.
        return ProviderErrorCategory.TEMPORARY

    status = error.google_error_status
    if status is not None:
        if status in _AUTHENTICATION_STATUSES:
            return ProviderErrorCategory.AUTHENTICATION
        if status in _INVALID_REQUEST_STATUSES:
            return ProviderErrorCategory.INVALID_REQUEST
        if status in _QUOTA_STATUSES:
            return ProviderErrorCategory.QUOTA
        if status in _TEMPORARY_STATUSES:
            return ProviderErrorCategory.TEMPORARY

    # Google's error.status was absent, unparseable, or unrecognized —
    # fall back to the HTTP status code alone.
    if error.status_code in (401, 403):
        return ProviderErrorCategory.AUTHENTICATION
    if error.status_code == 400:
        return ProviderErrorCategory.INVALID_REQUEST
    if error.status_code == 429:
        return ProviderErrorCategory.QUOTA
    if error.status_code in (500, 502, 503, 504):
        return ProviderErrorCategory.TEMPORARY
    if 400 <= error.status_code < 500:
        # Some other 4xx Google doesn't classify further here — never
        # safe to assume it will resolve on retry.
        return ProviderErrorCategory.PERMANENT
    return ProviderErrorCategory.UNKNOWN
