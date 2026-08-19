# API --- Deep Specification

## API lifecycle

Every endpoint follows:

``` text
request
 ↓
authentication
 ↓
authorization
 ↓
schema validation
 ↓
service
 ↓
repository/provider
 ↓
response
```

## Project creation

``` http
POST /api/v1/projects
```

Input:

``` json
{
  "name": "Restaurant Collection",
  "description": "Approved Google Maps Platform workflow",
  "source_type": "google_maps"
}
```

Output contains:

-   project ID;
-   status;
-   timestamps.

## Configuration validation

``` http
POST /api/v1/configs/{id}/validate
```

Validation checks:

-   required fields;
-   provider connection;
-   field availability;
-   limits;
-   schedule;
-   permission/compliance metadata required by the application.

The endpoint must not start a collection job.

## Job creation

``` http
POST /api/v1/projects/{id}/jobs
```

The endpoint:

1.  validates project;
2.  selects active config;
3.  creates job;
4.  commits;
5.  queues work;
6.  returns job ID.

## Job status

``` http
GET /api/v1/jobs/{id}
```

Response should include:

``` text
status
progress
metrics
timestamps
error
```

## Authorization

For every project-scoped endpoint:

``` text
current_user owns project?
```

or future role policy.

Never trust a project ID from the client.

## Error codes

Recommended:

``` text
AUTH_REQUIRED
FORBIDDEN
NOT_FOUND
VALIDATION_ERROR
CONFLICT
PROVIDER_AUTH_ERROR
PROVIDER_QUOTA_ERROR
PROVIDER_RATE_ERROR
PROVIDER_BAD_RESPONSE
JOB_NOT_RETRYABLE
EXPORT_TOO_LARGE
INTERNAL_ERROR
```

## Observability

Every response has a request ID.

Every job has a job ID.

Logs include both when applicable.
