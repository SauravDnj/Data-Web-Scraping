# Current Work

## Active task

T062 --- Worker heartbeat.

## Previous task

T061 --- Worker job execution. COMPLETE — "the first major vertical
slice": `workers/jobs/execute_collection.py`'s `process_next_job()`
composes T038-T060 into the full dequeue→claim→run→persist→metrics→
finalize→acknowledge workflow for one job, using only the generic
`ProviderAdapter` interface (zero Google-specific imports). Three new
`JobRepository` methods: `claim_queued_job()` (a real atomic
conditional `UPDATE`, replacing the racy ORM get-then-mutate pattern
for this one transition), `finalize_job()`, `finish_run()`. Job-level
status decision (COMPLETED/PARTIALLY_COMPLETED/FAILED) documented and
tested against docs/08's own worked example. Found and fixed a real
test-helper bug (`or` silently treating an intentional `{}` as "use
the default") and a real mypy gap (`Result[Any]` needing a
`CursorResult` cast for `.rowcount`). 8 new integration tests,
including the literal acceptance criterion (3 fake records → completed
job + 3 records, re-verified from a fresh post-commit session). See
`docs/18_COMPLETED_WORK.md`.

## Goal

Make worker liveness observable and recoverable (read
`docs/T062_PROMPT.md` before assuming scope) — turn T061's one-time
heartbeat bookend (`JobRun.heartbeat_at` set at run creation, touched
once more at `finish_run()`) into a real *continuously updated* signal
during execution, define the heartbeat interval and the stale
threshold, detect stale job runs (a run whose `heartbeat_at` is older
than the threshold while still `RUNNING` — presumably a crashed
worker), and prove a *healthy* long-running job is never mistakenly
flagged stale. Acceptance: "a stopped worker becomes detectable as
stale without incorrectly recovering healthy jobs" — needs tests with
controlled/injected time (matching this whole session's "never call
`datetime.now()` inside business logic, take time as a parameter"
discipline), not real sleeps.

## Not yet in scope

-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Still open

-   T027 (index review) remains PARTIAL, genuinely blocked on real
    MySQL for EXPLAIN verification — see `database/INDEX_REVIEW.md`.
-   T012/T013 still not resolved by the user (see below).
-   Any future migration that ALTERs an existing table (not just
    CREATE TABLE) must use `batch_alter_table` and be verified against
    SQLite directly — don't assume autogenerate's plain output works
    there (found the hard way at T035).

## Open blockers (user action needed)

-   **T012 (MySQL)**: `scripts/mysql_dev_setup.sql` ready; needs the
    user to run it with their own MySQL admin access (this agent
    doesn't have and shouldn't be given the root password).
-   **T013 (Redis)**: needs a user decision — install Memurai locally
    (native Windows, no WSL) to verify now, or skip local verification
    and rely on the Ubuntu VPS deployment target for real Redis
    testing later. WSL was explicitly ruled out by the user.
