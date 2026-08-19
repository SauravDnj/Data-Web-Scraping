# Local Setup

## Target environment

The primary development environment is Windows, with macOS/Linux
compatibility as a goal.

## Install

Install current stable supported versions of:

-   Git
-   Python
-   Node.js LTS
-   MySQL 8.x
-   Redis
-   VS Code

Verify:

``` text
git --version
python --version
node --version
npm --version
mysql --version
redis-server --version
```

## Python environment

Create a virtual environment:

``` text
python -m venv .venv
```

Activate it according to the operating system.

Install project dependencies from the project's lock/requirements
configuration.

## Frontend

Create the Next.js application under `apps/web`.

## Backend

Create FastAPI under `apps/api`.

## Database

MySQL Community Server (8.x or newer — 9.7 verified working on the
primary dev machine as of T012) must already be installed and running
as a service before this step.

1.  Generate a local dev password (not a real secret, just avoids a
    predictable default):
    `python -c "import secrets,string; a=string.ascii_letters+string.digits; print(''.join(secrets.choice(a) for _ in range(24)))"`
2.  Edit `scripts/mysql_dev_setup.sql` and replace
    `REPLACE_WITH_LOCAL_DEV_PASSWORD` with that value.
3.  Run it as an administrative account (you will be prompted for the
    root password — Claude Code does not have and should not be given
    this password):
    `mysql -u root -p < scripts/mysql_dev_setup.sql`
4.  Put the same password in your local `.env`'s `DATABASE_URL`
    (`mysql+pymysql://app_user:<password>@localhost:3306/google_data_platform`).
    Never commit `.env`.
5.  Verify: `mysql -u app_user -p google_data_platform -e "SELECT 1;"`

To reset the development database (drops all data,
`scripts/mysql_dev_reset.sql`), run the same way. `app_user` has only
DML plus the DDL Alembic migrations need, scoped to the
`google_data_platform` database — never the root account, never
cross-database access.

## Environment file

Create:

``` text
.env
```

from:

``` text
.env.example
```

Never commit `.env`.

## First boot

Run:

``` text
MySQL
Redis
FastAPI
Worker
Next.js
```

Then verify:

``` text
GET /health
GET /ready
```

## Redis

Redis has no official native Windows build. Options, in order of
preference for this project (Windows dev machine, Ubuntu VPS
production target):

1.  **Memurai** (Windows-native, Redis-protocol-compatible, free
    Developer edition) — no WSL required.
2.  **WSL2 + real Redis** — heavier to set up, not used here per
    project decision (2026-08-19).
3.  Skip local Redis entirely and defer verification to the Ubuntu
    deployment target, where Redis installs natively
    (`apt install redis-server`).

Start/stop commands depend on which option is chosen; document the
actual commands here once decided (see `docs/16_MEMORY.md`).

Verify connectivity: `python scripts/redis_ping.py` (reads
`REDIS_URL` from the environment; defaults to
`redis://localhost:6379/0`). A clear `FAIL: could not connect...`
message is expected and correct when no Redis is running yet.

## Local ports

Suggested:

``` text
Next.js  3000
FastAPI  8000
MySQL    3306
Redis    6379
```

Change ports if they conflict with an existing service.
