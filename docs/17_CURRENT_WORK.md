# Current Work

## Active task

T044 --- Provider error mapping.

## Previous task

T043 --- Google response mapper. COMPLETE —
`app/providers/google_maps/mapper.py`: `normalize_place()` (the real
`ProviderAdapter.normalize()` implementation) and
`map_place_to_record_draft()` (attaches job/project context + a
collection timestamp). New `app.domain.records.RecordDraft` (a
`Record` minus `canonical_key`/`id`/timestamps — Stage 5 canonical-key
computation is T052's job, not T043's). Malformed fields are treated
exactly like missing ones — never coerced, never crash. 10 new
fixture-based tests
(`tests/fixtures/google_maps/{full,minimal,malformed}_place.json`).
T042 --- Google client, T041 --- Google configuration, T040 ---
Provider interface, T039 --- Authorization, T038 --- Authentication
all complete before it. See `docs/18_COMPLETED_WORK.md`.

## Goal

Turn Google-specific failures (from `GoogleMapsApiError`, T042 — HTTP
status + Google's own `error.status` string) into the stable
`app.domain.provider_contracts.ProviderErrorCategory` taxonomy T040
already defined (read `docs/T044_PROMPT.md` before assuming scope) —
map authentication/invalid-request/quota/rate/transient/permanent
errors, preserve safe diagnostic context (never leak the API key or
raw response body verbatim into a log line), mark retryability
explicitly. This is also where the acknowledged tension between this
new taxonomy and `app.domain.job_errors.RETRYABLE_ERROR_CLASSES`
(T035's interim job-failure retry set — see that file's docstring)
must finally be reconciled, not left diverging any longer. Must NOT
auto-retry policy/authorization failures or hide a provider error as a
generic internal one (T044's explicit DO NOT list). Acceptance: "the
worker can make a deterministic retry/no-retry decision from the
classified error" — this is likely where `ProviderAdapter.
classify_error()` (T040's Protocol) gets its real Google
implementation, completing every method except `estimate()`/
`health_check()` (still open — no task currently claims them
explicitly; check whether T045 needs them before assuming they're
truly unclaimed).

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
