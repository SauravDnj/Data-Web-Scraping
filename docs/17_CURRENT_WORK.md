# Current Work

## Active task

Paused, awaiting user input. T027 is PARTIAL (see
`database/INDEX_REVIEW.md`) — genuinely blocked on real MySQL for
EXPLAIN verification, confirmed by reading its literal prompt (not a
false alarm like T023/T025/T026 turned out to be).

## Previous task

T026 --- Operations database. COMPLETE. All 8 database-schema tasks
(T020-T026) are now done. See `docs/18_COMPLETED_WORK.md`.

## Why paused here specifically

This is the first task in the whole run (T000-T026) whose acceptance
criteria cannot be honestly satisfied without live MySQL. Every prior
"might need real MySQL" flag (T023, T025, T026) turned out to be
overcautious once the literal prompt was checked — T027 is different,
it explicitly says "Use EXPLAIN on representative synthetic queries."

## Not yet in scope

-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

Resume T027's EXPLAIN step once T012 is done. T030 (domain models) is
pure Python and doesn't need MySQL, so it COULD proceed first if the
user prefers not to wait — but T031+ (repository layer, services)
increasingly benefit from real integration testing, so raising this
with the user before choosing a direction.

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
