# Current Work

## Active task

T034 --- Configuration service.

## Previous task

T033 --- Project service. COMPLETE — 13 new tests, still no live
MySQL needed. `ensure_can_start_job()` guard added for T035 to use.
See `docs/18_COMPLETED_WORK.md`.

## Goal

Implement versioned provider configuration and its validation
workflow, on `app.repositories.configs.CollectionConfigRepository`.

## Still open

T027 (index review) remains PARTIAL, genuinely blocked on real MySQL
for EXPLAIN verification — see `database/INDEX_REVIEW.md`. T012/T013
still not resolved by the user. The SQLite-substitution pattern has
now carried through T033 — still holding, but T038/T039 (auth) will
likely be the next place a real hard stop shows up (session/token
handling benefits strongly from integration tests).

## Not yet in scope

-   Google provider calls (T041+ — T034's "validation" is structural/
    generic only, not calling the real Google API);
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T034: T035 (job service, will use ProjectService.
ensure_can_start_job) → T036 (record service) → T037 (audit service —
may already be substantially covered by AuditLogRepository/the
pattern established in ProjectService) → T038/T039 (auth).

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
