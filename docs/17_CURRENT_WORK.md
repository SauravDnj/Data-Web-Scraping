# Current Work

## Active task

T043 --- Google response mapper.

## Previous task

T042 --- Google client. COMPLETE — `app/providers/google_maps/client.py`:
`GoogleMapsClient` (real HTTP boundary against Places API (New) Text
Search), `GoogleMapsApiError` (structured, for T044 to classify). httpx
promoted from dev-only to a real runtime dependency. Retry only on
transport/5xx failures, never on 4xx (auth/quota/rate) — those
propagate for job-level retry instead, per docs/07's "never bypass a
denial" rule. All 17 new tests use `httpx.MockTransport` — no real
network call, no real credentials. T041 --- Google configuration, T040
--- Provider interface, T039 --- Authorization, T038 ---
Authentication all complete before it. See `docs/18_COMPLETED_WORK.md`.

## Goal

Convert Google's raw Text Search response items (the dicts
`GoogleMapsClient.search_text()` yields) into the platform's normalized
internal record representation (read `docs/T043_PROMPT.md` before
assuming scope) — map each supported field explicitly (no inventing
fields not actually in the response), preserve the provider identifier
(`place.id`) and a source reference, normalize types, handle missing
fields gracefully, attach a collection timestamp and project/job
context. This is very likely where `app.domain.provider_contracts.
NormalizedItem` (T040, field names already matching `Record.
provider_record_id`/`Record.data`) gets its first real producer, and
where `ProviderAdapter.normalize()` (T040's Protocol) gets a concrete
Google implementation. Fixture-based tests (real captured/synthetic
Google response shapes) — same fixture must always produce the same
internal record deterministically (T043's literal acceptance
criterion), plus explicit tests for malformed responses.

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
