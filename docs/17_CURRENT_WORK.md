# Current Work

## Active task

T033 --- Project service.

## Previous task

T032 --- Repository layer. COMPLETE — 7 repositories, 16 new tests,
still no live MySQL needed (found/fixed a real domain/schema
mismatch along the way: 3 domain fields had misleading optional
defaults for NOT-NULL columns). See `docs/18_COMPLETED_WORK.md`.

## Goal

Implement project business rules and authorization boundaries, built
on `app.repositories.projects.ProjectRepository`.

## Still open

T027 (index review) remains PARTIAL, genuinely blocked on real MySQL
for EXPLAIN verification — see `database/INDEX_REVIEW.md`. T012/T013
still not resolved by the user. The SQLite-substitution pattern has
now carried all the way through the repository layer (T032) — T033+
introduces authorization/business-rule logic that's still plausibly
pure-Python-testable, but real integration testing against MySQL
would give stronger confidence than unit tests alone from here on.

## Not yet in scope

-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T033: T034 (configuration service) → T035 (job service) → ...
T038/T039 (auth) will likely be the next place a real hard stop shows
up (session/token handling benefits strongly from integration tests).

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
