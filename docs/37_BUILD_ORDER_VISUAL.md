# Build Order Visual

Do not build everything at once.

``` text
WEEK/PHASE A
Repository
   ↓
Local environment
   ↓
FastAPI health
   ↓
Next.js shell

PHASE B
MySQL
   ↓
Migrations
   ↓
Project CRUD
   ↓
Configuration versioning

PHASE C
Job state machine
   ↓
Queue
   ↓
Worker
   ↓
Fake provider
   ↓
Database records

PHASE D
Google provider adapter
   ↓
Real approved provider workflow
   ↓
Normalization
   ↓
Deduplication

PHASE E
Dashboard
   ↓
Project wizard
   ↓
Job monitoring
   ↓
Records

PHASE F
Exports
   ↓
Schedules
   ↓
Usage budgets
   ↓
Observability

PHASE G
Security
   ↓
Reliability
   ↓
Performance
   ↓
E2E
   ↓
Release
```

## Critical development strategy

Before connecting the real provider, make the entire pipeline work with
a fake provider:

``` text
fake provider
 ↓
worker
 ↓
pipeline
 ↓
MySQL
 ↓
dashboard
```

Then swap in the real provider adapter.

This dramatically reduces debugging complexity.
