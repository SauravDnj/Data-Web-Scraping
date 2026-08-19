# Deep System Explanation

## 1. Think of the application as a factory

A user does not directly "run a scraper."

The user creates a **collection project**.

Example:

``` text
Project:
Restaurant Lead Collection

Provider:
Google Maps Platform

Search:
Restaurants

Area:
Surat

Fields:
name
address
phone
website
rating
review_count
maps_reference
```

The system turns this configuration into repeatable jobs.

## 2. Why the system needs multiple layers

A scraper script can do:

``` text
request → parse → save
```

A real platform needs:

``` text
user
 ↓
UI
 ↓
API
 ↓
configuration
 ↓
validation
 ↓
job
 ↓
queue
 ↓
worker
 ↓
provider
 ↓
normalization
 ↓
validation
 ↓
deduplication
 ↓
database
 ↓
metrics
 ↓
UI
 ↓
export
```

Each layer has a different responsibility.

## 3. Frontend

Next.js is responsible for:

-   displaying projects;
-   collecting user configuration;
-   displaying validation errors;
-   showing jobs;
-   showing progress;
-   showing records;
-   starting/cancelling/retrying jobs;
-   creating exports.

The frontend must NOT contain provider secrets or database credentials.

## 4. FastAPI

FastAPI is the application's control plane.

It receives:

``` text
create project
create configuration
validate configuration
create job
cancel job
list records
create export
```

FastAPI should not perform a 30-minute collection inside an HTTP
request.

Instead:

``` text
POST /jobs
 ↓
create DB job
 ↓
enqueue job
 ↓
return job ID
```

The worker performs the long-running work.

## 5. MySQL

MySQL stores durable application state:

``` text
projects
configs
jobs
job_runs
records
provenance
exports
schedules
audit_logs
```

If Redis disappears, the important application state must still exist in
MySQL.

## 6. Redis

Redis is a temporary coordination/queue layer.

Example:

``` text
FastAPI
 ↓
Redis
 ↓
Worker
```

Redis says:

> "Worker, process job 123."

MySQL says:

> "Job 123 exists, belongs to project 7, started at 10:30, has 120
> successful records, and is currently running."

## 7. Worker

The worker performs long-running operations.

It should:

1.  claim a job;
2.  create a job run;
3.  heartbeat;
4.  call provider adapter;
5.  process responses;
6.  save records;
7.  update counters;
8.  handle errors;
9.  finalize job.

## 8. Provider adapter

The provider adapter is the boundary between your application and
Google.

Core application code should say:

``` text
provider.collect(config)
```

It should NOT know the details of Google SDK requests.

This makes future providers possible.

## 9. Data pipeline

A provider response is not immediately inserted blindly.

``` text
provider response
 ↓
schema validation
 ↓
normalization
 ↓
quality checks
 ↓
canonical identity
 ↓
deduplication
 ↓
upsert
```

## 10. Why provenance matters

Suppose a record appears in your database.

You need to know:

-   which project produced it;
-   which job produced it;
-   which provider produced it;
-   when it was collected;
-   what provider reference identifies it, if permitted.

This is provenance.

## 11. Job state

A job is a state machine.

``` text
draft
  ↓
queued
  ↓
running
  ├── paused
  │     ↓
  │   running
  ├── cancelled
  ├── failed
  └── completed
```

Invalid transitions must be rejected.

For example:

``` text
completed → running
```

must not be allowed.

## 12. Why this architecture is useful

It allows you to add:

-   Google Search provider later;
-   other approved data providers;
-   scheduled jobs;
-   APIs;
-   webhooks;
-   multiple workers;
-   advanced analytics;

without rewriting the entire application.
