# Current Work

## Active task

T023 --- Project database.

## Previous task

T022 --- Identity database. COMPLETE — also verifiable without live
MySQL (SQLite substitution held up even for a real business table),
and it surfaced a genuine cross-dialect bug (BigInteger PKs don't
autoincrement under SQLite) that's now fixed via `BigIntegerPK` in
`app/db/base.py`. See `docs/18_COMPLETED_WORK.md`.

## Goal

Create `projects` and `collection_configs` tables + migration, per
`docs/04_DATABASE_DESIGN.md`. Use `BigIntegerPK` from `app.db.base`
for all `id` columns — don't redeclare `BigInteger` directly.

## Not yet in scope

-   job/record/ops tables (T024-T026);
-   Google provider calls;
-   scraping;
-   real queue consumption logic (T060/T061);
-   frontend business screens.

## Handoff

After T023: T024 (job DB) → T025 (record DB) → T026 (ops DB) → T027
(indexes/constraints review) → T030 (domain models). Each of these has
so far been verifiable without live MySQL via the SQLite-substitution
pattern — keep applying it, but stay alert for more cross-dialect
surprises like the BigInteger one. Return to T012/T013 as soon as
possible regardless, since eventually (deduplication, JSON columns,
real query performance) MySQL-specific behavior will need real
verification.

## Open blockers (user action needed)

-   **T012 (MySQL)**: `scripts/mysql_dev_setup.sql` ready; needs the
    user to run it with their own MySQL admin access (this agent
    doesn't have and shouldn't be given the root password).
-   **T013 (Redis)**: needs a user decision — install Memurai locally
    (native Windows, no WSL) to verify now, or skip local verification
    and rely on the Ubuntu VPS deployment target for real Redis
    testing later. WSL was explicitly ruled out by the user.

T015 (worker skeleton) can still proceed: it only needs the *ability*
to attempt a Redis connection and shut down gracefully if it's
unreachable, matching T014's readiness-check pattern.
