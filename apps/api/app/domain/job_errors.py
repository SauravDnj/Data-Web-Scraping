"""Job failure-class retryability rules — reconciled at T044 with
`app.domain.provider_contracts.ProviderErrorCategory` (T040), the
authoritative taxonomy for *provider-caused* failures.

`Job.error_code` (set by the worker, T060+, when it marks a job
FAILED) holds one of three kinds of value:

-   One of `ProviderErrorCategory`'s own string values
    (`"authentication"`, `"quota"`, `"rate"`, `"invalid_request"`,
    `"temporary"`, `"permanent"`, `"unknown"`) — the failure came from
    a classified `ProviderError` (e.g.
    `app.providers.google_maps.errors.classify_google_maps_error`).
-   `PERSISTENCE_ERROR_CODE` (`"persistence"`) — a job can also fail
    for a reason that has nothing to do with the provider at all (a
    transient database error while writing collected records) —
    `ProviderErrorCategory` was never meant to cover that, so it stays
    a separate, explicit, always-retryable code rather than being
    force-fit into the provider taxonomy.
-   `WORKER_CRASHED_ERROR_CODE` (`"worker_crashed"`, T065) — a job a
    recovery process (`workers.jobs.recovery`) found abandoned by a
    worker whose heartbeat went stale. Also non-provider, also
    always-retryable (a crash is an infrastructure failure, not a
    policy rejection) — bounded the same way as every other retry, by
    T063's `max_attempts` ceiling, so a worker that keeps crashing on
    the same job still stops retrying eventually rather than looping
    forever.

This replaces T035's original provisional set
(`"transient_network"`/`"rate_limit"`/`"persistence"`) — the first two
are superseded by `ProviderErrorCategory.TEMPORARY`/`.RATE`'s own
string values now that the real taxonomy exists;
`tests/unit/test_job_service.py` was updated accordingly (it used to
assert on `"transient_network"`)."""

from app.domain.provider_contracts import (
    ProviderErrorCategory,
    default_retryable_for_category,
)

PERSISTENCE_ERROR_CODE = "persistence"
WORKER_CRASHED_ERROR_CODE = "worker_crashed"

_NON_PROVIDER_RETRYABLE_CODES = frozenset(
    {PERSISTENCE_ERROR_CODE, WORKER_CRASHED_ERROR_CODE}
)


def is_retryable(error_code: str | None) -> bool:
    if error_code is None:
        return False
    if error_code in _NON_PROVIDER_RETRYABLE_CODES:
        return True
    try:
        category = ProviderErrorCategory(error_code)
    except ValueError:
        return False
    return default_retryable_for_category(category)
