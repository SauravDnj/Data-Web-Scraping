# Authorization Review (T039)

## Status: COMPLETE for everything with a service today; exports/schedules deferred by design

## 1. Ownership policy

Every project-scoped resource is owned transitively through its
project's `user_id` column (`projects.user_id`, set once at creation,
never reassigned in V1). A resource with no `user_id` of its own
(`CollectionConfig`, `Job`, `Record` — all reference `project_id`, not
a user) is authorized by resolving its parent project and checking
that project's ownership — never by trusting a `user_id` value the
resource itself doesn't have.

The single enforcement point is `ProjectService._require_owner()`
(`app/services/projects.py`, introduced at T033): every other service
that needs authorization calls `ProjectService.get_project(...,
requesting_user_id=...)` rather than re-implementing the ownership
check. `PermissionDeniedError` (`app/services/errors.py`) is raised on
denial and — new at T039 — is now mapped centrally to HTTP 403 by
`app/api/service_errors.py`, so no future route handler has to catch
it by hand (T038's `auth.py` login flow still catches
`PermissionDeniedError` itself, deliberately, because a failed login
is a 401 "not authenticated" case, not a 403 "authenticated but not
authorized for this resource" case — the two are semantically
different despite sharing an exception type).

## 2-5. Enforcement per service — already true, verified

These were already built with authorization in place at their own
tasks (T033-T036), each reusing `ProjectService.get_project`/
`ensure_can_start_job` rather than duplicating the check:

| Service | Method | Ownership check |
|---|---|---|
| `ProjectService` | `get_project`, `update_project`, `archive_project` | `_require_owner` directly |
| `ConfigurationService` | `create_version`, `activate_version`, `get_active`, `list_versions` | via `ProjectService.get_project` |
| `JobService` | `create_job` (via `ensure_can_start_job`), `get_job`, `cancel_job`, `pause_job`, `resume_job`, `retry_job` (via `_require_owned_job`) | via `ProjectService.get_project`/`ensure_can_start_job` |
| `RecordService` | `search_records`, `get_record` | via `ProjectService.get_project` |

T039 added the negative-test coverage that was missing for some of
these methods (see section 8) and the centralized HTTP mapping (see
section 1) — no service code changed, since the enforcement itself was
already correct.

## 6-7. Exports and schedules — deliberately deferred

`app.domain.exports`/`app.domain.schedules` and their repositories
exist (T026/T032), but **no `ExportService`/`ScheduleService` exists
yet** — those are built at T080 (CSV export) and T083 respectively,
each of which lists "validate project authorization" as its own first
implementation step. Building authorization enforcement into a service
that doesn't exist yet would mean inventing its method signatures
speculatively and re-doing that work at T080/T083 anyway. When those
services are built, they must follow the exact pattern in section 1
(reuse `ProjectService.get_project`, do not re-implement ownership
checks) — this is now a documented obligation for those tasks, not
just an implicit convention.

## 8. Negative tests for cross-project access

Every method listed in the table above now has a passing test proving
a non-owner (`stranger`) is rejected with `PermissionDeniedError`. New
at T039 (the rest already existed from T033-T036):

- `tests/unit/test_project_service.py::test_stranger_cannot_archive_another_users_project`
- `tests/unit/test_configuration_service.py::test_stranger_cannot_activate_version_or_list_versions`
- `tests/unit/test_job_service.py::test_stranger_cannot_act_on_another_users_job` (extended to also cover `pause_job`/`resume_job`/`retry_job`, not just `get_job`/`cancel_job`)
- `tests/unit/test_job_service.py::test_stranger_cannot_create_a_job_by_supplying_someone_elses_project_id` — the literal T039 acceptance criterion ("changing an ID in a request"), applied to `create_job`'s `project_id` argument.

`RecordService` (`test_stranger_cannot_search_or_view_another_users_records`)
and the rest of `ConfigurationService`/`ProjectService` already had
full coverage from their own tasks — reviewed, not duplicated.

## 9. Review of every project-scoped endpoint

**No project-scoped HTTP endpoint exists yet.** `app/api/v1/__init__.py`
only mounts the T038 auth router (`/auth/login`, `/auth/logout`,
`/auth/me`) — none of those are project-scoped, so there is nothing to
review at the HTTP layer today. The first project-scoped routes land
at T070+ (per `docs/T070_PROMPT.md` onward), and every one of them
must call its service's `requesting_user_id`-checked method (never
query the repository directly from a route handler) so this review
applies transitively. `app/api/service_errors.py`, added at T039,
guarantees a `PermissionDeniedError` raised by any future route
reaches the client as 403 even if the route author forgets to catch it
— this was verified now, ahead of those routes existing, via
`tests/integration/test_service_error_handlers.py`.
