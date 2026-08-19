# scripts

Local development and operational scripts.

- `mysql_dev_setup.sql` — create the local dev database and
  least-privilege `app_user` (T012). Run as an administrative MySQL
  account.
- `mysql_dev_reset.sql` — drop and recreate the local dev database
  (destructive; T012).
- `redis_ping.py` — verify Redis connectivity (T013):
  `python scripts/redis_ping.py`.

More scripts (migration helpers, seed data loaders) land as later
tasks require them.
