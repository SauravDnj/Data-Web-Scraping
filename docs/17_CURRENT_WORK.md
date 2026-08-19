# Current Work

## Active task

T020 --- SQLAlchemy foundation.

## Previous task

T015 --- Worker skeleton. COMPLETE (done ahead of T012/T013 — see
below). See `docs/18_COMPLETED_WORK.md` and `workers/worker_main.py`.

## Goal

Create the database engine, session management, declarative base
model, and naming/typing conventions that later schema tasks
(T021-T027) build on.

## Not yet in scope

-   actual table schema (T022-T026 create identity/project/job/record/
    ops tables);
-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T020:

T021 (Alembic foundation) → T022 (identity DB) → ... Return to
T012/T013 once unblocked — T021's migrations will need a real MySQL
connection to actually run against, so T012 should land before T021
finishes, even though T020 itself (engine/session code only, no live
connection required) doesn't block on it.

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
