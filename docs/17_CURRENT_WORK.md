# Current Work

## Active task

T054 --- Transactional persistence.

## Previous task

T053 --- Deduplication. COMPLETE — `app/pipeline/deduplicate.py`:
`deduplicate_within_batch()` (pure, streaming, within+across pages) +
`resolve_against_existing()` (DB-touching, create/update/skip) +
`deduplicate_batch()` (composes both, tracks `DedupSummary`). New
`RecordRepository.update_collected_data()` (T032 never needed an
update path before now). Default policy: `update_existing=True`
(repeat collections refresh stale data), fully supports
`update_existing=False` too. Database-constraint test proves the T025
`UniqueConstraint` is the final safety net independent of this
module's own logic. 11 new tests. T052 --- Canonical identity and all
of T050-T051/Phase 4 complete before it. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Make database writes reliable (read `docs/T054_PROMPT.md` before
assuming scope) — Stage 7 of `docs/08_DATA_PIPELINE_DEEP.md`: wrap
T053's per-record insert/update decisions in a real atomic
transaction (a whole batch succeeds or rolls back together, matching
`docs/08`'s "never hide failures" principle — partial success must be
reported honestly, e.g. `partially_completed`, not silently swept
under a bare "completed"), store `RecordProvenance` rows (genuinely
new — T043 left `GOOGLE_MAPS_TEXT_SEARCH_OPERATION` specifically for
this), increment created/updated/rejected counters only after a
successful commit (never optimistically before), handle DB constraint
conflicts gracefully (e.g. a concurrent-write race past the app-level
`get_by_canonical_key` check), and add rollback-behavior tests
proving a failed transaction leaves no partial, inconsistent state —
T054's literal acceptance criterion.

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
