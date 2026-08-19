# Current Work

## Active task

T031 --- Job state machine.

## Previous task

T030 --- Domain models. COMPLETE — pure Python, 17 new tests, no DB
touched. Centralized status enums into `app/domain/`, ORM files now
import rather than redefine them. See `docs/18_COMPLETED_WORK.md`.

## Goal

Implement explicit legal job state transitions using
`app.domain.jobs.JobStatus`. Should be pure-Python testable, same as
T030 — a state machine is business logic, not persistence.

## Still open

T027 (index review) remains PARTIAL, genuinely blocked on real MySQL
for EXPLAIN verification — see `database/INDEX_REVIEW.md`. T012/T013
still not resolved by the user. Continuing into T031+ where honestly
possible without live infra, per the user's "continue" instruction,
but T032 (repository layer) and beyond will need real MySQL to
properly integration-test rather than just unit-test.

## Not yet in scope

-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T031: T032 (repository layer — likely wants real MySQL for
integration tests, unit tests alone may not fully satisfy it) → T033+.

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
