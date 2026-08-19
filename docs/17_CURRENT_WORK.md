# Current Work

## Active task

T070 --- Next.js app shell. Phase 7 (Frontend) starts here.

## Previous task

T065 --- Worker recovery. COMPLETE — `workers/jobs/recovery.py`:
`recover_stale_job_runs()`, composed almost entirely from existing
pieces (T062's `find_stale_job_runs()`, T063's `retry_failed_job()`).
New `JobRepository.close_stale_run()` (same atomic conditional-UPDATE
shape as `claim_queued_job()`/`request_cancellation()`) safely
reclaims a stale `JobRun`; the job is then finalized `FAILED` with a
new `WORKER_CRASHED_ERROR_CODE` and handed to T063's unchanged
retry/exhaustion logic. "Only one active execution owner" is answered
with three combined, already-existing safeguards (atomic reclaim,
`finalize_job()`'s own state-machine guard, and retry-always-creates-
a-new-job-row) rather than a new distributed lock — explicitly
documented as a bounded, honest answer, not a claim of perfect
exactly-once execution. `workers/worker_main.py`'s loop is still a
placeholder — neither `process_next_job()` nor
`recover_stale_job_runs()` is wired into a real running process by any
task through T065; flagged as an open cross-cutting gap, likely closed
around T091 (Reliability review) or an operations task. 10 new tests.
**Phase 6 (Worker) is now fully complete.** See
`docs/18_COMPLETED_WORK.md`.

## Goal

Build the Next.js dashboard shell (read `docs/T070_PROMPT.md`,
`docs/06_UI_DEEP.md`, and `docs/23_UI_FILE_PLAN.md` before assuming
scope) — main layout, sidebar/top navigation, active-route state, an
auth-aware layout (T038's session/login already exists on the backend;
check what the frontend currently has for calling it, from T011), a
generic loading UI, error UI, empty-state component, and a toast/
feedback mechanism, responsive behavior, and accessibility basics.
Route placeholders for Dashboard/Projects/Jobs/Records/Schedules/
Settings — no business forms yet, that's explicitly out of scope here.
Literal acceptance criterion: every navigation item has a route and a
placeholder state.

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
