# Current Work

## Active task

T026 --- Operations database.

## Previous task

T025 --- Record database. COMPLETE, done without live MySQL (the
earlier "might need real MySQL" flag turned out overcautious — always
check the literal acceptance criteria). Also fixed a real gap: `tests/`
had never been linted; 17 issues fixed, CI extended. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Create `exports`, `schedules`, and `audit_logs` tables + migration,
per `docs/04_DATABASE_DESIGN.md`.

## Not yet in scope

-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T026: T027 (indexes/constraints review — needs real query
plans, likely the actual hard stop for the SQLite-substitution
pattern) → T030 (domain models). Return to T012/T013 as soon as
possible.

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
