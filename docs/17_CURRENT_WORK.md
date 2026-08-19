# Current Work

## Active task

T060 --- Redis queue (first task of Phase 6, Worker).

## Previous task

T055 --- Pipeline metrics. COMPLETE — `app/pipeline/metrics.py`:
`compute_job_counters()` aggregates T051 validation + T054 persist
outcomes into `JobCounters` (T024's existing shape, now filled in for
real); `count_job_run_attempts()` surfaces "retries" from `JobRun.
attempt` rather than inventing a new concept. New `JobRepository.
update_counters()`. Bucket mapping is a documented design decision
(DB-conflict FAILED ≠ quality-rejected, kept as separate counters).
Atomicity proven by committing counters + records in the same
transaction, then re-reading from a fresh session. 15 new tests. Hit
and fixed a real pytest module-basename collision between the new
`tests/unit/` and `tests/integration/` files (renamed the integration
one). **Phase 5 (Data pipeline) is now fully complete** — T050 through
T055, every stage of `docs/08_DATA_PIPELINE_DEEP.md` implemented and
tested. See `docs/18_COMPLETED_WORK.md`.

## Goal

Implement the Redis-backed job queue (read `docs/T060_PROMPT.md`
before assuming scope) — first task of Phase 6 (Worker). Define a
generic queue interface (Protocol, matching every repository this
project has built), a real Redis implementation (`redis-py`, already a
dependency since T014), enqueue/dequeue/acknowledgement, worker-failure
handling, and a minimal payload — **only the job ID**, never job
details (those stay in MySQL, the system of record; Redis is
coordination-only per docs/16_MEMORY.md's technology decisions).
Acceptance: a queued job can be delivered to a worker, and Redis loss
must not erase the durable job record (`Job` rows in MySQL are
unaffected by Redis being wiped). **T013 (Redis) is still not
locally verified** (no live Redis instance — Memurai vs. skip still
undecided by the user, WSL ruled out) — decide how to test this
task's queue logic without one before writing it (a real, protocol-
faithful in-memory Redis substitute, matching this project's
SQLite-for-MySQL testing strategy, is worth investigating before
resorting to a hand-rolled fake).

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
