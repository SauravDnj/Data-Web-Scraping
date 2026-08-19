# Current Work

## Active task

T050 --- Normalization pipeline.

## Previous task

T045 --- Provider contract tests. COMPLETE — `app/providers/
google_maps/provider.py`: `GoogleMapsProvider`, the first concrete
`ProviderAdapter` in the codebase, assembled purely by composition
from T041-T044 (`estimate()`/`health_check()` written here, honestly
scoped — no pre-call usage estimate exists on Google's side, and
`health_check()` doesn't spend real quota on a live probe). **Found
and fixed a real robustness gap in T042's client**: a malformed
top-level response could have made `search_text()` iterate a string's
characters instead of failing gracefully — hardened, matching T043's
"never invent, never crash" principle applied consistently at the
collection layer too. 15 new tests
(`tests/unit/test_google_maps_provider_contract.py`), one per T045
IMPLEMENT item, plus new fixtures under `tests/fixtures/google_maps/`.
**Phase 4 (Provider) is now fully complete** — T040-T045 all done,
every `ProviderAdapter` method has a real, tested Google
implementation. T044 --- Provider error mapping, T043 --- Google
response mapper, T042 --- Google client, T041 --- Google
configuration, T040 --- Provider interface, T039 --- Authorization,
T038 --- Authentication all complete before it. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Build the provider-agnostic normalization pipeline stage (read
`docs/T050_PROMPT.md` before assuming scope) — Stage 3 of
`docs/08_DATA_PIPELINE_DEEP.md`, distinct from T043's Google-specific
field mapping: pure, deterministic transformations applied to a
`NormalizedItem`'s already-mapped `data` (whitespace trimming, safe
Unicode normalization, URL normalization, numeric/timestamp/category
normalization) that any current or future provider's output passes
through uniformly, not duplicated per adapter. Must never invent a
value for something genuinely missing (T050's own explicit
instruction, echoing T043's same principle at this next stage). Unit
tests per transformation + regression fixtures; acceptance is strict
determinism (same input → identical output).

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
