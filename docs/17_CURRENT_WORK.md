# Current Work

## Active task

T064 --- Cancellation.

## Previous task

T063 --- Retry system. COMPLETE — `workers/jobs/retry.py`:
`RetryPolicy`/`should_retry()`/`compute_backoff_delay()` (pure) +
`count_retry_chain_length()`/`retry_failed_job()` (DB-touching).
Discovered T035's `retry_job()` (already the canonical "new Job row"
retry mechanism, since `FAILED` is a terminal state in T031's machine)
had no attempt bound at all — a genuine "retry indefinitely" gap,
closed here via `count_retry_chain_length()` walking the existing
`JOB_RETRIED` audit trail (T037) backward, no schema migration needed.
Backoff is defined and thoroughly tested as a pure function but not
yet enforced as real delayed queue delivery (no delayed-delivery
primitive exists in `RedisJobQueue`, T060) — documented as a
deliberate scope boundary; the hard attempt ceiling alone already
prevents retry storms. All 7 `ProviderErrorCategory` values tested
against their actual retry outcome. 25 new tests. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Implement cooperative job cancellation (read `docs/T064_PROMPT.md`
before assuming scope) — a cancellation-request state distinct from
the terminal `CANCELLED` status (T031's state machine already allows
`queued→cancelled`/`running→cancelled`/`paused→cancelled`, but has no
"please stop, still running" intermediate signal), an API-facing way
to record that request (though no job API routes exist yet, T070+ —
check whether this task expects a service-layer method only, or a
real route), the worker checking for a pending cancellation between
safe units of work during `collect()`/persistence (T061's loop),
stopping at a safe boundary rather than mid-record, and finalizing as
`CANCELLED` cleanly — no ambiguous partial DB state, no orphaned
in-flight queue message. Prevent cancelling an already-terminal job.
Test cancellation actually interrupting active processing, not just
a pre-emptive check before any work starts.

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
