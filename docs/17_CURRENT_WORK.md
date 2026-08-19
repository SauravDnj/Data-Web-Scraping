# Current Work

## Active task

T063 --- Retry system.

## Previous task

T062 --- Worker heartbeat. COMPLETE — `workers/jobs/heartbeat.py`:
`HeartbeatUpdater` (interval-gated periodic `JobRun.heartbeat_at`
updates, `HEARTBEAT_INTERVAL=30s`) + `find_stale_job_runs()`
(`STALE_THRESHOLD=5min`). Two new `JobRepository` methods
(`touch_heartbeat`, `list_stale_running_runs`). Healthy runs are never
falsely flagged — structurally, via the stale query's own WHERE
clause, verified directly. Heartbeat write failures are caught/logged,
never crash the monitored job. Wired into T061's `execute_collection.py`
loop (currently a no-op there in practice, since T061 still uses one
fixed timestamp for the whole run — documented as deferred until a
real slow multi-page provider call needs a genuinely ticking clock).
9 new tests, all with controlled/injected time, no real sleeps. Found
and fixed two real test-helper bugs (an illegal direct DRAFT→RUNNING
transition; a duplicate-email unique-constraint collision). See
`docs/18_COMPLETED_WORK.md`.

## Goal

Implement bounded, classified retry behavior (read
`docs/T063_PROMPT.md` before assuming scope) — maximum attempts,
exponential backoff (+ jitter if useful), classify the error before
deciding to retry (`app.domain.job_errors.is_retryable()`, already
reconciled with `ProviderErrorCategory` at T044), persist the attempt
count (`JobRun.attempt`, already tracked since T024;
`app.pipeline.metrics.count_job_run_attempts()` from T055 already
surfaces it), requeue retryable jobs
(`workers.queue.RedisJobQueue.requeue()`, T060, or
`JobService.retry_job()`, T035, depending on which "retry" concept
this task means — re-examine both before assuming), mark permanent
failures as final, prevent retry storms (a real abuse-control concern,
`docs/10_SECURITY_DEEP.md`). Must NOT retry policy/authorization
failures automatically, retry indefinitely, or bypass quotas — directly
enforced already by `default_retryable_for_category()` (T044:
`AUTHENTICATION`/`QUOTA`/`INVALID_REQUEST`/`PERMANENT` are all
non-retryable by design) and needs a hard attempt ceiling on top of
that. Test every error class explicitly.

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
