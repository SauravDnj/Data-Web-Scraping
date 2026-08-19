# Index Review (T027)

## Status: PARTIAL — blocked on real MySQL for step 9 (EXPLAIN)

Steps 1-8 and 10 below are complete. Step 9 ("Use EXPLAIN on
representative synthetic queries") requires a real MySQL instance —
SQLite's query planner is a different optimizer and would not give
trustworthy evidence about MySQL's actual index usage. This is
recorded as the reason T027 is not marked complete in
`docs/18_COMPLETED_WORK.md`.

## 1-2. Common queries → index mapping

Most indexes below were added incrementally while building each table
(T022-T026), each with an inline comment explaining why. This section
consolidates them against the query patterns the product actually
needs (from `docs/03_PRODUCT_REQUIREMENTS_DEEP.md` /
`docs/05_API_DEEP.md`):

| Query | Table | Index |
|---|---|---|
| Dashboard: a user's projects by status | `projects` | `ix_projects_user_id_status (user_id, status)` |
| Config wizard: active/historical versions for a project | `collection_configs` | `ix_collection_configs_project_id_is_active (project_id, is_active)` |
| Reject duplicate version number | `collection_configs` | `uq_collection_configs_project_id (project_id, version)` |
| Project's jobs by status, newest first | `jobs` | `ix_jobs_project_id_status_requested_at (project_id, status, requested_at)` |
| Worker/scheduler: all queued/running jobs (project-agnostic) | `jobs` | `ix_jobs_status_requested_at (status, requested_at)` |
| A job's execution attempts by status (heartbeat/recovery, T062/T065) | `job_runs` | `ix_job_runs_job_id_status (job_id, status)` |
| Records list: a project's records by collection time | `records` | `ix_records_project_id_collected_at (project_id, collected_at)` |
| Dedup check during ingestion (T053) | `records` | `uq_records_project_id (project_id, canonical_key)` — also serves as the lookup index |
| A project's export history | `exports` | `ix_exports_project_id_created_at (project_id, created_at)` |
| Scheduler: due schedules | `schedules` | `ix_schedules_enabled_next_run_at (enabled, next_run_at)` |
| A user's audit trail | `audit_logs` | `ix_audit_logs_user_id_created_at (user_id, created_at)` |
| Login lookup | `users` | `uq_users_email (email)` |

## 3-6. Covered above (project/status, job lifecycle, record
project/time/canonical, export/schedule) — see table.

## 7. Foreign-key index review

Every FK column is covered by an existing composite index (as its
leading column) **except**: `jobs.config_id`, `records.job_id`,
`record_provenance.record_id`, `exports.requested_by`,
`schedules.project_id`. These are deliberately left without an
explicit single-column index — InnoDB automatically creates one for
any FK column not already covered by a compatible index, so adding
one manually would be a redundant, undocumented duplicate (exactly
what T027 says not to do). This should be confirmed with `SHOW INDEX`
against real MySQL once T012 lands (not yet done — see status above).

## 8. Uniqueness constraint review

- `users.email` — unique (T022, prevents duplicate accounts).
- `collection_configs(project_id, version)` — unique (T023, prevents
  two configs claiming the same version number).
- `records(project_id, canonical_key)` — unique (T025, the dedup
  mechanism itself — project-scoped per the T000 decision, not
  global).

No other uniqueness constraints — every other "should this be unique"
question (e.g. one active config per project) is an application-level
invariant enforced by the service layer (T034), not a DB constraint,
since MySQL has no partial/filtered unique index to express "unique
among is_active=true rows only".

## 9. EXPLAIN verification — NOT DONE, blocked on T012

Once MySQL is available: seed synthetic data (thousands of rows per
table) and run `EXPLAIN` for each query in the table above, confirming
each uses its intended index (not a full table scan). Record results
here.

## 10. Non-obvious index rationale

Documented inline in each model file
(`apps/api/app/db/models/*.py`) and in `docs/16_MEMORY.md` at the time
each table was created. The one genuinely non-obvious case:
`jobs` has TWO indexes with overlapping leading columns in different
orders (`(project_id, status, requested_at)` and
`(status, requested_at)`) — not redundant, because MySQL can only use
a composite index efficiently via its leftmost columns, and worker
polling ("show queued jobs" with no project filter) can't use the
project-scoped index efficiently.
