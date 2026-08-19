# API Design

## API conventions

Base path:

``` text
/api/v1
```

Return consistent envelopes.

Success:

``` json
{
  "data": {},
  "request_id": "..."
}
```

Error:

``` json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": {}
  },
  "request_id": "..."
}
```

## Endpoints

### Health

``` text
GET /health
GET /ready
```

### Projects

``` text
GET    /projects
POST   /projects
GET    /projects/{project_id}
PATCH  /projects/{project_id}
DELETE /projects/{project_id}
```

### Collection configurations

``` text
GET    /projects/{project_id}/configs
POST   /projects/{project_id}/configs
GET    /configs/{config_id}
PATCH  /configs/{config_id}
POST   /configs/{config_id}/validate
```

### Jobs

``` text
GET  /jobs
POST /projects/{project_id}/jobs
GET  /jobs/{job_id}
POST /jobs/{job_id}/cancel
POST /jobs/{job_id}/pause
POST /jobs/{job_id}/resume
POST /jobs/{job_id}/retry
```

### Records

``` text
GET /projects/{project_id}/records
GET /records/{record_id}
```

### Exports

``` text
POST /projects/{project_id}/exports
GET  /exports/{export_id}
```

### Schedules

``` text
GET    /projects/{project_id}/schedules
POST   /projects/{project_id}/schedules
PATCH  /schedules/{schedule_id}
DELETE /schedules/{schedule_id}
```

## Service boundaries

Routers should be thin.

``` text
Router
  -> Service
     -> Domain logic
        -> Repository
           -> Database
```

Provider calls must occur through provider services/adapters, not
directly from route handlers.

## Idempotency

Job creation should support an idempotency key for clients that may
retry requests.

## Pagination

Use cursor pagination for large record sets where practical. Offset
pagination is acceptable for small administrative lists.

## Authentication

Use secure session or token architecture selected during implementation.
Never place provider secrets in frontend code.
