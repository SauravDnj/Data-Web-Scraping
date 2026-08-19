# Current Work

## Active task

T040 --- Provider interface.

## Previous task

T039 --- Authorization. COMPLETE — confirmed ownership was already
correctly enforced across Project/Config/Job/Record services
(T033-T036); added the centralized HTTP error mapping
(`app/api/service_errors.py`, so `PermissionDeniedError`/
`NotFoundError`/`InvalidStateError` reach clients as 403/404/409
without every future route needing to catch them by hand) and 6
previously-missing negative cross-user tests. Full review in
`database/AUTHORIZATION_REVIEW.md`. T038 --- Authentication also
COMPLETE before it — password login + opaque server-side session
tokens, account lockout, `/api/v1/auth/{login,logout,me}`. See
`docs/18_COMPLETED_WORK.md`.

## Goal

Define the generic `ProviderAdapter` contract (read `docs/T040_PROMPT.md`
before assuming scope) — the boundary the rest of the application
depends on without knowing Google SDK details. Resolves the interim
`app.domain.provider_validation.ProviderConfigValidator` Protocol T034
created explicitly to be reconciled here (see its docstring and
`docs/16_MEMORY.md`'s T034 section) — do not silently diverge from it,
reconcile or replace it deliberately. Pure Python, no Google SDK calls,
no browser automation — should hold up fine on the SQLite-substitution
approach same as T030-T039.

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
