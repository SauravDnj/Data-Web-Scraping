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

Create a development database and a dedicated development user.

Do not use the MySQL root account from the application.

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

## Local ports

Suggested:

``` text
Next.js  3000
FastAPI  8000
MySQL    3306
Redis    6379
```

Change ports if they conflict with an existing service.
