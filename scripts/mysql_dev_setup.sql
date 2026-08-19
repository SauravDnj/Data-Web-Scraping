-- T012: local development database + least-privilege application user.
-- Run once, as an account with administrative privileges (e.g. root):
--
--   mysql -u root -p < scripts/mysql_dev_setup.sql
--
-- Idempotent: safe to re-run. Does not drop or reset existing data —
-- see scripts/mysql_dev_reset.sql for that.

CREATE DATABASE IF NOT EXISTS google_data_platform
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

-- Password set via the FILE variable below is a local development
-- placeholder only — replace it before running, then put the same
-- value in your local .env (never commit it). See
-- apps/api/README.md for the exact command used to generate it.
CREATE USER IF NOT EXISTS 'app_user'@'localhost'
  IDENTIFIED BY 'REPLACE_WITH_LOCAL_DEV_PASSWORD';

-- DML + the DDL Alembic needs for migrations, scoped to this one
-- database only. No GRANT OPTION, no access to any other schema.
GRANT SELECT, INSERT, UPDATE, DELETE,
      CREATE, ALTER, DROP, INDEX, REFERENCES
  ON google_data_platform.*
  TO 'app_user'@'localhost';

FLUSH PRIVILEGES;
