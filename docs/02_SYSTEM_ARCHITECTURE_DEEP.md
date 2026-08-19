# Deep System Architecture

## Component map

``` text
                         USER
                          |
                          v
                +-------------------+
                | Next.js Dashboard |
                +---------+---------+
                          |
                     HTTPS/JSON
                          |
                          v
                +-------------------+
                |   FastAPI API     |
                +---------+---------+
                          |
        +-----------------+------------------+
        |                 |                  |
        v                 v                  v
   Auth Service      Project Service     Job Service
        |                 |                  |
        +-----------------+------------------+
                          |
                          v
                    Repository Layer
                          |
                          v
                       MySQL

Job Service
    |
    v
Redis Queue
    |
    v
Worker
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
Repository
    |
    v
MySQL
```

## Clean responsibility boundaries

### UI

Presentation only.

### API

HTTP transport and request validation.

### Service layer

Business rules.

### Repository layer

Persistence.

### Provider layer

External provider communication.

### Worker layer

Long-running orchestration.

### Pipeline layer

Transforming provider data into internal records.

## Recommended code organization

``` text
apps/
  web/
  api/

backend/
  app/
    api/
    auth/
    config/
    domain/
    services/
    repositories/
    providers/
    pipeline/
    jobs/
    exports/
    audit/
    db/
    observability/

workers/
  worker_main.py

tests/
  unit/
  integration/
  provider/
  e2e/

docs/
```

## Dependency direction

Preferred:

``` text
API → Services → Domain
             → Repositories
             → Provider interfaces

Provider implementation → Provider interface
Repository implementation → Repository interface
```

Avoid:

``` text
API → SQL directly
API → Google SDK directly
UI → database directly
Provider → frontend
```

## Transaction boundaries

Creating a job should be transactional:

``` text
validate
 ↓
insert job
 ↓
commit
 ↓
enqueue
```

If enqueue fails after commit, the system needs a recovery mechanism. Do
not pretend the job is running.

For a mature implementation, an outbox/event pattern can be introduced.

## Idempotency

Job execution must tolerate duplicate delivery.

If the same job ID reaches two workers, only one worker should be
allowed to own the active run.

Use database locking/state transitions to enforce this.

## Scaling

V1:

``` text
1 API
1 worker
1 Redis
1 MySQL
```

Later:

``` text
1 API
N workers
Redis
managed MySQL
```

Scale only after measuring actual bottlenecks.
