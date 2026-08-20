# Current Work

## Active task

T072 --- Project UI.

## Previous task

T071 --- Dashboard UI. COMPLETE — real dashboard
(`app/(app)/dashboard/page.tsx`): 4 cards, recent-activity table,
recent-failures table, loading/empty/error+retry, every number
straight from a backend field (never client-derived, T071's own DO
NOT rule). **Resolved the blocker flagged at the end of T070**: built
the first backend HTTP routes beyond auth — `GET /jobs` (matches
docs/05_API_DESIGN.md exactly), `GET /jobs/summary`,
`GET /records/count` (both small, justified additions where the
design doc was silent) — plus the FastAPI dependency-injection
plumbing (`get_job_service`/`get_record_service`/etc. in
`app/api/dependencies.py`) every future business route will reuse.
Cross-project aggregation added real repository methods
(`JobRepository.list_for_user()`/`count_by_status_for_user()`,
`RecordRepository.count_for_user()`), all joining through `projects`
since `Job`/`Record` have no `user_id` of their own. New
`JobStatusSummary` domain type documents a real design decision (which
`JobStatus` values count as "active"/"completed"/"failed" for the 3
dashboard cards — `CANCELLED` counts toward none of them). Hit the
same `react-hooks/set-state-in-effect` rule as T070 but needed a
different fix — worth reading if any future data-fetch-on-mount
component trips it again. 17 new tests (7 backend, 6 HTTP, 4
frontend). Verified against real seeded data via scratch
`uvicorn`+SQLite (browser extension still unavailable in this
environment). See `docs/18_COMPLETED_WORK.md`.

## Goal

Build project management (read `docs/T072_PROMPT.md` before assuming
scope) — a project list, optional search/filter, a create-project
form, edit, archive (with a confirmation step — it's a destructive/
state-changing action), a project detail page, validation feedback,
loading/empty/error states (reuse T070/T071's `EmptyState`/
`ErrorState`), and connect it all through a typed API client. Literal
acceptance criterion: a created project appears immediately in the
list after a successful API response.

**Same class of blocker as T071, expected this time**: `ProjectService`
(T033) exists and is fully tested, but **no `/projects` HTTP route
exists yet** — `docs/05_API_DESIGN.md` lists the full CRUD surface
(`GET/POST /projects`, `GET/PATCH/DELETE /projects/{id}}`, archive is
`ProjectService.archive_project()` — check whether that's exposed via
`PATCH .../archive` or folded into the generic `PATCH`). Build this
now the same way T071 built `app/api/v1/jobs.py`/`records.py`:
`get_project_service` already exists in `app/api/dependencies.py`
(built at T071) — reuse it directly, no new plumbing needed there.

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
