# Current Work

## Active task

T071 --- Dashboard UI.

## Previous task

T070 --- Next.js app shell. COMPLETE — auth-aware shell
(`app/(app)/layout.tsx`), sidebar/top nav, placeholder pages for all
6 top-level routes, `EmptyState`/`ErrorState`/`Toast` primitives.
**Built a minimal `/login` page + `lib/auth/AuthContext.tsx`, a
genuinely necessary decision with no dedicated task or doc backing
it** — T070 requires "auth-aware layout" but no task T070-T078 ever
builds a login screen; without one, auth-awareness could never be
exercised. Session token architecture: bearer token in
`sessionStorage`, browser calls the FastAPI backend directly (matches
the CORS config + `apiFetch` client T011 already set up, not a new
Next.js server-proxy architecture). Found and fixed a real bug in
T011's `apiFetch` (threw on a 204 response, e.g. `/auth/logout`), a
real test-setup gap (`@testing-library/react` auto-cleanup never
registered — `vitest.config.mts` has no `test.globals`, fixed
centrally in `vitest.setup.ts`), and a real
`react-hooks/set-state-in-effect` lint finding in `AuthContext`
(fixed via a `useState` lazy initializer). Browser extension
unavailable in this environment — verified via a real `uvicorn` +
scratch-SQLite backend with a seeded user, curling the exact 3 auth
endpoints the frontend calls, plus curling every route against a real
`next dev` server; genuine interactive browser behavior (mobile nav
drawer, live redirect) was NOT visually confirmed, flagged honestly
rather than assumed. 12 new tests. **Phase 7 (Frontend) started.** See
`docs/18_COMPLETED_WORK.md`.

## Goal

Build the operational dashboard (read `docs/T071_PROMPT.md` before
assuming scope) — active/completed/failed job cards, a records count,
a recent-jobs list, a recent-failures list, loading/empty/error
states (reuse T070's `EmptyState`/`ErrorState`), retry actions where
appropriate. Backend metrics are authoritative — DO NOT compute
counts from partial frontend data.

**Likely blocker to resolve first, flagged by T039's own memory entry
and confirmed still true**: T071 depends on T035 (Job service) and
T036 (Record service), but **no HTTP route exists for jobs, records,
or projects yet** — only `/api/v1/auth/*` (T038) is mounted anywhere
in `apps/api`. "API-backed metrics" cannot work without at least a
thin dashboard-metrics endpoint (and/or job-list/record-count routes)
wired through the existing services with `Depends(get_current_user)`
and T039's centralized error-handler registration. Building that
minimal backend surface is very likely in scope for T071 itself (no
other task in `docs/00_TASK_INDEX.md` owns it) — confirm this reading
of scope before starting, rather than assuming the frontend alone is
what's being asked for here.

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
