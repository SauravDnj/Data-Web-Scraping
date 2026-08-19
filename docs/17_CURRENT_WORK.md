# Current Work

## Active task

T052 --- Canonical identity.

## Previous task

T051 --- Validation pipeline. COMPLETE — `app/pipeline/validate.py`:
`RecordQuality`/`FieldRule`/`FieldValidationError`/`ValidationResult`/
`validate_record_draft()`, Stage 2+4 combined. `missing_severity` vs.
`severity` are deliberately separate knobs, directly matching docs/08's
two worked examples ("missing website → warning", "invalid coordinate
→ rejected"). URL syntax check is syntax-only, never a real request.
Wired into `app/providers/google_maps/mapper.py` via
`GOOGLE_FIELD_RULES` + `validate_google_place_record()`, kept as an
explicit separate step from `map_place_to_record_draft()`. 28 new
tests. T050 --- Normalization pipeline and all of Phase 4 complete
before it. See `docs/18_COMPLETED_WORK.md`.

## Goal

Create the deterministic record identity strategy (read
`docs/T052_PROMPT.md` before assuming scope) — Stage 5 of
`docs/08_DATA_PIPELINE_DEEP.md`: prefer a stable provider identifier
when permitted (Google's place `id` — already `RecordDraft.
provider_record_id`, per T043/`database/DATABASE_DEEP.md`'s "prefer
it if permitted" guidance), define a fallback canonicalization only
where genuinely needed, scope the key by project+provider (T000's
resolved decision: `project_scope + provider + provider_id`, matching
`records(project_id, canonical_key)`'s unique constraint from T025).
Must NOT use business name alone as identity. Test repeated-identical/
minor-formatting-difference/different-businesses cases, and explicitly
document known collision limitations — acceptance is "false merges
minimized and documented," not "zero collisions," which would be an
impossible claim for a fallback heuristic.

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
