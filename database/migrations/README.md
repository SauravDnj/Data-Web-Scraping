# database/migrations

Alembic migrations. Config lives at `apps/api/alembic.ini` (Alembic is
an `apps/api` dependency); this directory is only `script_location` —
`env.py`, `script.py.mako`, and `versions/`.

The database URL always comes from `DATABASE_URL` (via
`app.core.config.get_settings()`), never from `alembic.ini` — no
credentials are ever committed here.

## Commands

Run from `apps/api/`, with its virtual environment active:

```bash
alembic upgrade head           # apply all migrations
alembic downgrade base         # roll back to empty
alembic current                 # show current revision
alembic history                  # show all revisions
alembic revision --autogenerate -m "describe the change"   # new migration
```

## Reset

There is no separate "reset" command — downgrade to `base` then
upgrade to `head` again, or use `scripts/mysql_dev_reset.sql` to drop
and recreate the whole database, then `alembic upgrade head`.

## Conventions

- One logical schema change per migration (see
  `docs/CODING_STANDARDS.md`).
- Every migration implements both `upgrade()` and `downgrade()`.
- No destructive migration without a documented recovery plan.
