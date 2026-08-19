# Current Work

## Active task

T022 --- Identity database.

## Previous task

T021 --- Alembic foundation. COMPLETE. Turned out solvable without
live MySQL too — the migration harness itself was verifiable against
a temporary SQLite file (empty schema so far, so dialect didn't
matter). See `docs/18_COMPLETED_WORK.md` and
`database/migrations/env.py`.

## Goal

Create the identity/users table and its first real migration.

## Likely actual hard stop

T022 is the first task creating real business schema. Its acceptance
criteria will presumably want a real migration verified against a
real database, and there's no more "no schema yet, dialect doesn't
matter" escape hatch like T020/T021 had. This is probably where
progress genuinely pauses for T012, though will read the exact T022
prompt before concluding that.

## Not yet in scope

-   project/job/record/ops tables (T023-T026);
-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T022: T023 → ... all needing real MySQL. Return to T012/T013 as
soon as possible.

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
