# Current Work

## Active task

T025 --- Record database.

## Previous task

T024 --- Job database. COMPLETE, done without live MySQL. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Create `records` and `record_provenance` tables + migration, with
deterministic canonical-key deduplication support, per
`docs/04_DATABASE_DESIGN.md`.

## Read T025's exact prompt before assuming the usual pattern applies

Two real cross-dialect bugs were found in T022/T023 by testing against
SQLite instead of skipping verification — that pattern has held up
through T024. But `canonical_key` uniqueness-at-project-scope and
dedup behavior are the kind of thing worth confirming against real
MySQL specifically. Check T025's literal acceptance criteria first;
don't assume the SQLite shortcut still applies without checking.

## Not yet in scope

-   ops tables (T026: exports/schedules/audit_logs);
-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T025: T026 (ops DB) → T027 (indexes/constraints review, needs
real query plans) → T030 (domain models). Return to T012/T013 as soon
as possible — T027 in particular cannot be honestly done without real
MySQL.

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
