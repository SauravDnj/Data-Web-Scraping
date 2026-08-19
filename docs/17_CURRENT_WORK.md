# Current Work

## Active task

T021 --- Alembic foundation.

## Previous task

T020 --- SQLAlchemy foundation. COMPLETE (verified against SQLite + a
deterministic connection-error test, no live MySQL needed — see
docs/16_MEMORY.md). See `docs/18_COMPLETED_WORK.md` and
`apps/api/app/db/session.py`.

## Goal

Configure Alembic and verify a clean migration against a real
database.

## Likely hard stop

Alembic's whole point is running real migrations. Unlike T020, there's
probably no honest way to verify "migration applies cleanly" without
an actual reachable MySQL — T012 needs to land first. Will attempt to
get as far as possible (Alembic config/env.py wiring, migration
scaffolding) and flag clearly if/when real execution is required to
call it done.

## Not yet in scope

-   actual table schema (T022-T026 create identity/project/job/record/
    ops tables);
-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T021: T022 (identity DB) → T023 → ... all of which also need
real MySQL. Return to T012/T013 as soon as possible.

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
