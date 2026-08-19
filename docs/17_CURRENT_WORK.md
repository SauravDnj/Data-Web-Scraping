# Current Work

## Active task

T041 --- Google configuration.

## Previous task

T040 --- Provider interface. COMPLETE — `app/providers/base.py`
(`ProviderAdapter` Protocol: `validate_config`/`estimate`/`collect`/
`normalize`/`classify_error`/`health_check`), `app/domain/
provider_contracts.py` (`UsageEstimate`, `NormalizedItem`,
`ProviderErrorCategory` — the 7 categories from docs/07 —
`ProviderError`, `ProviderHealth`), `FakeProviderAdapter`
(`tests/unit/fakes.py`). `ConfigValidationResult` reused from T034's
`app.domain.provider_validation`, not duplicated. 12 new tests. T039
--- Authorization and T038 --- Authentication complete before it. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Validate Google-specific configuration before execution (read
`docs/T041_PROMPT.md` before assuming scope) — supported operation(s),
allowed request fields, query/location/numeric-range validation,
max-usage limits, server-side credential-presence check, actionable
validation errors. Needs current, accurate Google Maps Platform
API/product documentation (field names, limits) verified via web
search before writing validation rules — do not rely on
possibly-stale training knowledge for exact current field names/quota
values. Must NOT implement CAPTCHA solving, bypass rate limits, or use
unauthorized browser scraping as a fallback (T041's explicit DO NOT
list). This is where `app/providers/google_maps/` (T040's file-plan
placeholder) gets its first real file.

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
