# Current Work

## Active task

T027 --- Database indexes and constraints.

## Previous task

T026 --- Operations database. COMPLETE, done without live MySQL. All 8
database-schema tasks (T020-T026) are now done. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Review query patterns across all tables and add only justified
indexes/constraints, verified against real query plans.

## This is very likely the actual hard stop

Unlike T023/T025/T026 (flagged as possibly needing MySQL, turned out
not to), T027 explicitly requires verifying with query plans — that
cannot be done honestly against SQLite (different query planner,
different index usage). Read the literal T027 prompt to confirm, but
expect to report back to the user here rather than push through.

## Not yet in scope

-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T027: T030 (domain models) onward. Return to T012/T013 — this
time likely truly required before T027 can complete.

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
