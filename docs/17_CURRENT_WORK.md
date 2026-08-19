# Current Work

## Active task

T061 --- Worker job execution (the first major vertical slice).

## Previous task

T060 --- Redis queue. COMPLETE — `workers/queue.py` extended (not a
new file — T015 left it as a placeholder for exactly this) with
`JobQueue` (Protocol) + `RedisJobQueue` (BLMOVE-based reliable-queue
pattern: dequeue moves into an in-flight list, acknowledge removes it,
requeue moves it back — a crashed worker never silently loses a job
ID). Payload is always a bare job ID, never job details. **Decided and
verified a real Redis-testing strategy before writing any code**:
added `fakeredis` (dev-only) as a faithful in-memory Redis substitute,
same role SQLite plays for MySQL — sanity-checked its real command
behavior first, not assumed. Fixed two real redis-py mypy stub
awkwardnesses (a `float` timeout stub-typed as `int`; sync-client
methods typed as returning `X | Awaitable[X]`) with targeted
`cast()`/`type: ignore`, not blanket suppression. 11 new tests. **Phase
6 (Worker) now started.** See `docs/18_COMPLETED_WORK.md`.

## Goal

Build the complete worker workflow end-to-end, using T040's
`FakeProviderAdapter` first, before any real Google call (read
`docs/T061_PROMPT.md` before assuming scope — 17 IMPLEMENT items, "the
first major vertical slice") — this is where every piece built across
T038-T060 finally gets composed together for real: dequeue (T060) →
atomically claim the queued job (docs/09's `UPDATE ... WHERE
status='queued'` claim pattern — not yet built anywhere) → create a
`JobRun` + status→running (T024/T032) → start a heartbeat → load the
exact active configuration version (T034) → validate it (T041-shaped,
but via the generic `ProviderAdapter.validate_config`, T040) → call
`ProviderAdapter.collect()`/`normalize()` (T040, fake provider for
this task) → Stage 3-6 pipeline (T050-T053) → persist transactionally
(T054) → update metrics (T055) → finalize job status (via the T031
state machine) → record errors → stop heartbeat → acknowledge the
queue message (T060). Acceptance: a fake provider yielding 3 records
produces a `completed` job and exactly 3 `Record` rows — a genuine,
observable end-to-end proof, not per-piece unit tests alone.

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
