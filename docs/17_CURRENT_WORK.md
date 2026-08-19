# Current Work

## Active task

T045 --- Provider contract tests.

## Previous task

T044 --- Provider error mapping. COMPLETE —
`app/providers/google_maps/errors.py`: `classify_google_maps_error()`
(the real `ProviderAdapter.classify_error()` implementation), mapping
Google's `error.status` (+ HTTP status fallback) into T040's
`ProviderErrorCategory`. Extended `ProviderError` itself with
mandatory `retryable` + diagnostic `http_status_code`/
`provider_status` fields; added `default_retryable_for_category()`.
Reconciled `app.domain.job_errors` with the new taxonomy (`Job.
error_code` now holds a `ProviderErrorCategory` value or
`"persistence"`), replacing T035's provisional
`"transient_network"`/`"rate_limit"` codes — updated the one existing
test that used the old value. 22 new tests. T043 --- Google response
mapper, T042 --- Google client, T041 --- Google configuration, T040 ---
Provider interface, T039 --- Authorization, T038 --- Authentication
all complete before it. See `docs/18_COMPLETED_WORK.md`.

## Goal

Assemble a complete, fake-based `ProviderAdapter` contract test suite
(read `docs/T045_PROMPT.md` before assuming scope) — synthetic
fixtures, valid/empty/malformed collection responses, pagination,
quota/authentication/transient-error scenarios, normalization,
provenance, deterministic mapping — proving the whole Google adapter
(config validation T041 + HTTP client T042 + response mapper T043 +
error classifier T044, composed together) is testable end-to-end
without any live Google credentials. This is very likely where a
single `GoogleMapsProvider` class finally gets assembled satisfying
every method of T040's `ProviderAdapter` Protocol (`validate_config`,
`collect`, `normalize`, `classify_error` all already have real
implementations spread across T041-T044; `estimate()`/`health_check()`
still have no real implementation anywhere — check whether T045 is
where those get written, or whether they remain open after it).

## Not yet in scope

-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Still open

-   T027 (index review) remains PARTIAL, genuinely blocked on real
    MySQL for EXPLAIN verification — see `database/INDEX_REVIEW.md`.
-   T012/T013 still not resolved by the user (see below).
-   Any future migration that ALTERs an existing table (not just
    CREATE TABLE) must use `batch_alter_table` and be verified against
    SQLite directly — don't assume autogenerate's plain output works
    there (found the hard way at T035).

## Open blockers (user action needed)

-   **T012 (MySQL)**: `scripts/mysql_dev_setup.sql` ready; needs the
    user to run it with their own MySQL admin access (this agent
    doesn't have and shouldn't be given the root password).
-   **T013 (Redis)**: needs a user decision — install Memurai locally
    (native Windows, no WSL) to verify now, or skip local verification
    and rely on the Ubuntu VPS deployment target for real Redis
    testing later. WSL was explicitly ruled out by the user.
