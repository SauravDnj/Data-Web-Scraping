# Current Work

## Active task

T038 --- Authentication.

## Previous task

T037 --- Audit service. COMPLETE — 12 new tests, still no live MySQL
needed. Centralized action names + secret redaction; found
`ConfigurationService` had no audit calls at all and added them. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Implement secure V1 authentication (read `docs/T038_PROMPT.md` before
assuming scope). Likely the real next hard stop: password/session/
token handling benefits strongly from real integration tests, unlike
the business-logic services (T033-T037) that held up fine on SQLite.

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
