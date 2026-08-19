# Current Work

## Active task

T042 --- Google client.

## Previous task

T041 --- Google configuration. COMPLETE —
`app/providers/google_maps/config.py`: `GoogleMapsConfigValidator`,
the first real (non-fake) `ProviderConfigValidator` plugged into T034's
`ConfigurationService`. Selected operation: Places API (New) Text
Search — resolved as a design decision, recorded for T042 to build
against. Field names/limits verified against Google's live docs on
2026-08-20 (fetched, not recalled). 19 new tests, including one proving
docs/07's own example `max_results: 100` is correctly rejected (40 over
Google's real 60-result cap). T040 --- Provider interface, T039 ---
Authorization, T038 --- Authentication all complete before it. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Implement the real Google Maps Platform HTTP client boundary (read
`docs/T042_PROMPT.md` before assuming scope) — server-side credential
loading (`Settings.google_maps_api_key`, T014), request timeout,
documented-transient-error retry, request construction (translating
T041's snake_case config into the real camelCase Places API (New) Text
Search body + `X-Goog-FieldMask` header), response parsing, pagination
(`pageToken`/`nextPageToken`, up to the 60-result cap T041 already
validates against), structured provider errors (map into T040's
`ProviderErrorCategory`), credential redaction from logs, dependency
injection so tests never need a live API key. Must NOT bypass CAPTCHA,
evade quotas, rotate proxies, use fake credentials, or collect private
data (T042's explicit DO NOT list) — acceptance is mock-based (verify
request construction/response handling), no real credentials
committed or used in the automated suite.

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
