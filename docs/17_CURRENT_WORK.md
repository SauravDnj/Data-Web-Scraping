# Current Work

## Active task

T024 --- Job database.

## Previous task

T023 --- Project database. COMPLETE. Found/fixed a second real
cross-dialect gap (SQLite doesn't enforce FKs without a pragma) —
fixed at the engine level in `app/db/session.py`, applies
automatically to every future SQLite-backed test. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Create `jobs` and `job_runs` tables + migration, with metrics and
lifecycle fields, per `docs/04_DATABASE_DESIGN.md`. Use `BigIntegerPK`
for `id` columns (and matching type for FK columns pointing at them).

## Not yet in scope

-   record/ops tables (T025-T026);
-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T024: T025 (record DB) → T026 (ops DB) → T027 (indexes/
constraints review) → T030 (domain models). Two real cross-dialect
bugs found so far this way (BigInteger autoincrement, FK enforcement)
— keep applying the SQLite-substitution pattern, but stay alert for
more. Return to T012/T013 as soon as possible regardless.

## Open blockers (user action needed)

-   **T012 (MySQL)**: `scripts/mysql_dev_setup.sql` ready; needs the
    user to run it with their own MySQL admin access (this agent
    doesn't have and shouldn't be given the root password).
-   **T013 (Redis)**: needs a user decision — install Memurai locally
    (native Windows, no WSL) to verify now, or skip local verification
    and rely on the Ubuntu VPS deployment target for real Redis
    testing later. WSL was explicitly ruled out by the user.

T015 (worker skeleton) can still proceed: it only needs the *ability*
to attempt a Redis connection and shut down gracefully if it's
unreachable, matching T014's readiness-check pattern.
