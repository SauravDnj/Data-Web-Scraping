# Current Work

## Active task

T051 --- Validation pipeline.

## Previous task

T050 --- Normalization pipeline. COMPLETE — `app/pipeline/normalize.py`:
`FieldKind` + `normalize_record_data()`, Stage 3 of the data pipeline.
Field kinds are declared by the caller, never guessed from a value's
shape. NFC-only Unicode normalization (never NFKC). Every transform
falls back to safe text-only cleanup when a value doesn't match its
declared kind, never coercing/guessing. Wired immediately into
`app/providers/google_maps/mapper.py`'s `map_place_to_record_draft()`
via a new `FIELD_KINDS` constant — not left an orphaned module. 25 new
tests, including a dedicated regression fixture
(`tests/fixtures/pipeline/normalize_regression.json`). **Phase 5 (Data
pipeline) now started.** T045 --- Provider contract tests and all of
Phase 4 complete before it. See `docs/18_COMPLETED_WORK.md`.

## Goal

Build the field-level data quality system (read `docs/T051_PROMPT.md`
before assuming scope) — Stage 2/4 of `docs/08_DATA_PIPELINE_DEEP.md`
("Schema validation" / "Quality"): define valid/warning/rejected
states, validate types/ranges/required fields/coordinate ranges/URL
syntax, produce field-level error objects, preserve job context. This
operates on a `RecordDraft` (T043's output, now normalized by T050) —
likely the first real consumer of `app.domain.record_search`'s
"quality filtering" concept (T036 flagged `has_provider_id` as a
placeholder pending this task). Acceptance: deterministic, no network
calls — pure validation logic, same testing approach as every prior
pipeline/provider task this session.

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
