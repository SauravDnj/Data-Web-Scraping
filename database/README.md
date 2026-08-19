# database

- `migrations/` — Alembic migrations. See
  [`migrations/README.md`](migrations/README.md) for commands.
- [`INDEX_REVIEW.md`](INDEX_REVIEW.md) — T027 index/constraint review
  (partial — needs real MySQL for EXPLAIN verification).
- Seed data: not populated yet.

All tables from `docs/04_DATABASE_DESIGN.md` exist (T022-T026): users,
projects, collection_configs, jobs, job_runs, records,
record_provenance, exports, schedules, audit_logs.
