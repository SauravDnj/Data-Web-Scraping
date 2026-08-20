# Current Work

## Active task

T073 --- Configuration wizard.

## Previous task

T072 --- Project UI. COMPLETE — full project list/create/edit/archive
flow (`app/(app)/projects/{page,new/page,[projectId]/page}.tsx`),
backed by the full `/projects` CRUD surface
(`app/api/v1/projects.py`) built on the already-tested
`ProjectService` (T033) and T071's `get_project_service` dependency
(no new plumbing needed). `DELETE` maps to `archive_project()` — a
deliberate reconciliation with T033's original archive-only design,
not a new hard-delete path. Found and fixed a real pre-existing gap:
`ProjectService.update_project()`'s bare `ValueError` for an empty
name was never mapped by T039's error handlers and would have 500'd
over HTTP — fixed with Pydantic validators at the API boundary rather
than touching the already-tested service. **Found and fixed a real,
previously-undetected CI bug**: `npm run typecheck` (bare `tsc
--noEmit`) fails on a clean checkout because `.next/` (and its
generated `PageProps`/`LayoutProps` types) is gitignored and CI never
runs a build step first — this predates T072 (T070's
`LayoutProps<'/'>` was already affected) and is now fixed by making
`typecheck` run `next typegen` first, self-healing for CI and any
fresh clone. Split `app/(app)/projects/[projectId]/page.tsx` into a
thin `use(params)` wrapper plus a new, directly-testable
`components/projects/ProjectDetailView.tsx` after discovering `use()`
on a plain resolved promise doesn't reliably settle under this
project's test stack (vitest+jsdom+React 19) — a test-environment
limitation, not a real bug, confirmed via an isolated repro. Also
fixed a real jsdom gap (`<dialog>.showModal()`/`.close()` unimplemented)
centrally in `vitest.setup.ts` for the new reusable
`components/ui/ConfirmDialog.tsx`. 14 new tests. Verified end-to-end
against a real seeded backend (create→list→detail→update→archive via
curl) and a real `next dev` server for all new routes (Chrome
extension still unavailable in this environment). See
`docs/18_COMPLETED_WORK.md`.

## Goal

Build the multi-step collection configuration wizard (read
`docs/T073_PROMPT.md` before assuming scope) — 7 steps: project
basics, provider, search/query/location, fields, limits, schedule
option, review+confirm. Client-side validation for immediate feedback
but server-side stays authoritative (`GoogleMapsConfigValidator`,
T041, already exists and is exactly what the server-side check should
call); provider-specific help text; usage/limit warnings; an accurate
review summary before submission; save as a versioned configuration
(`ConfigurationService.create_version()`, T034, already exists and
already enforces the single-active-version invariant); never keep a
provider secret in browser state longer than necessary (there
shouldn't be one in this flow at all — Google's API key is
server-side only, per T041's `GoogleMapsConfigValidator` design —
confirm the wizard never asks the user for one). Literal acceptance
criteria: an invalid configuration cannot be activated; the review
screen accurately represents what gets submitted.

**Same class of blocker as T071/T072, now the expected pattern**: no
`/configs` HTTP route exists yet — `docs/05_API_DESIGN.md` lists
`GET/POST /projects/{project_id}/configs`, `GET/PATCH /configs/{id}`,
`POST /configs/{id}/validate`. `ConfigurationService` (T034) and
`GoogleMapsConfigValidator` (T041) are both already fully tested and
ready to wire up; `get_configuration_service` already exists in
`app/api/dependencies.py` (built at T071) — reuse it directly.

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
