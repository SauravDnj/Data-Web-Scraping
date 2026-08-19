# System Architecture

## 1. Logical architecture

``` text
Browser
  |
  v
Next.js Web App
  |
  v
FastAPI REST API
  |
  +--------------------+
  |                    |
  v                    v
MySQL               Redis Queue
                         |
                         v
                    Worker Process
                         |
                         v
                 Provider Adapter
                         |
                         v
              Google Maps Platform
                         |
                         v
                 Normalization
                         |
                         v
                   Validation
                         |
                         v
                  Deduplication
                         |
                         v
                       MySQL
```

## 2. Repository layout

``` text
google-data-platform/
├── apps/
│   ├── web/
│   └── api/
├── workers/
│   ├── collection/
│   └── jobs/
├── packages/
│   ├── domain/
│   ├── config/
│   └── shared/
├── database/
│   ├── migrations/
│   └── seeds/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
├── scripts/
├── exports/
├── .env.example
├── .gitignore
├── README.md
└── pyproject.toml
```

## 3. Runtime components

### Web

Next.js renders project management, job monitoring, records, and
exports.

### API

FastAPI owns authentication, authorization, validation, job creation,
record querying, and configuration.

### Worker

The worker executes long-running collection jobs outside the HTTP
request lifecycle.

### Redis

Redis is a queue/coordination component. It must not become the system
of record.

### MySQL

MySQL is the system of record for application state and permitted
collected data.

## 4. Security boundaries

The frontend never talks directly to MySQL or provider credentials.

``` text
Browser -> API -> Service -> Repository -> MySQL
                 |
                 -> Provider adapter -> external provider
```

## 5. Configuration

Use environment variables for:

-   database URL;
-   Redis URL;
-   application secret;
-   provider API credentials;
-   allowed frontend origins;
-   logging level.

Never commit secrets.

## 6. Local processes

V1 can run as:

``` text
Terminal 1: Next.js
Terminal 2: FastAPI
Terminal 3: Redis
Terminal 4: Worker
Terminal 5: MySQL service
```

## 7. Scaling path

Local V1 -\> single-server deployment -\> multiple workers -\> managed
MySQL/Redis -\> containerized deployment if useful -\> distributed
deployment only when measured demand justifies it.
