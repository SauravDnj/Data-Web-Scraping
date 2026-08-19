-- T012: destructive local development reset. Drops and recreates the
-- development database (application data only — never point this at
-- anything but a local dev MySQL instance). Run as an administrative
-- account:
--
--   mysql -u root -p < scripts/mysql_dev_reset.sql
--
-- The app_user account and its grants are untouched; re-run
-- mysql_dev_setup.sql only if the user itself needs to be recreated.

DROP DATABASE IF EXISTS google_data_platform;

CREATE DATABASE google_data_platform
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

GRANT SELECT, INSERT, UPDATE, DELETE,
      CREATE, ALTER, DROP, INDEX, REFERENCES
  ON google_data_platform.*
  TO 'app_user'@'localhost';

FLUSH PRIVILEGES;
