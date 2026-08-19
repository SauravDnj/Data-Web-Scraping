# Current Work

## Active task

T065 --- Worker recovery.

## Previous task

T064 --- Cancellation. COMPLETE — new `jobs.cancel_requested`/
`cancel_requested_at` columns (migration `ee8f2297969d`); reconciled
with T035's pre-existing `JobService.cancel_job()` (found it hard-
transitioned a `RUNNING` job's status directly, which could race the
worker's own `finalize_job()` and leave an `InvalidJobTransition`
crash waiting to happen — exactly the "ambiguous state" this task
exists to prevent). `cancel_job()` now cancels
DRAFT/QUEUED/PAUSED jobs immediately (no worker owns them) but only
*requests* cancellation for a `RUNNING` job, via the new atomic
`JobRepository.request_cancellation()` (same conditional-`UPDATE`
shape as T061's `claim_queued_job()`). The worker
(`workers/jobs/execute_collection.py`) checks
`is_cancellation_requested()` between items (same spot as T062's
heartbeat) and stops at that safe boundary, keeping whatever was
already persisted from earlier items in the batch. Already-terminal
jobs (including already-`CANCELLED`) are rejected up front. 10 new
tests. See `docs/18_COMPLETED_WORK.md`.

## Goal

Implement worker recovery (read `docs/T065_PROMPT.md` before assuming
scope) — detect stale `JobRun`s (T062's `list_stale_running_runs()`
already exists and is unused by any caller yet), decide whether the
owning job is retryable and safely requeue it via T063's
`retry_failed_job()` machinery (or an equivalent path — check whether
recovery should create a new attempt on the SAME job or go through
T035/T063's "retry = new Job row" pattern; T065's own IMPLEMENT list
says "increment attempt safely," which may mean a same-job re-run
distinct from T063's user-initiated retry, needs a design decision
same as T041/T052/T063 before writing code), mark exhausted jobs
failed, and guarantee only one active execution owner exists at a
time (no duplicate processing from a crashed-then-recovered worker
racing a still-alive one). Test a simulated crash, duplicate queue
delivery, and recovery after heartbeat loss specifically.

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
