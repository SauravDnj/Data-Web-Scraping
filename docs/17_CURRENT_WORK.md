# Current Work

## Active task

T015 --- Worker skeleton.

## Previous task

T014 --- FastAPI skeleton. COMPLETE (done ahead of T012/T013 — see
below). See `docs/18_COMPLETED_WORK.md` and `apps/api/app/main.py`.

## Goal

Create the worker entry point: configuration loading, Redis
connection, graceful shutdown, structured logging. Do not execute
provider work yet.

## Not yet in scope

-   database schema/migrations (T020/T021);
-   Google provider calls;
-   scraping;
-   actual queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T015:

T020 (database) onward, or return to T012/T013 once unblocked.

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
