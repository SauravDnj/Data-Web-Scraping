# System Working Model

## End-to-end flow

### 1. User creates project

Frontend sends project configuration to FastAPI.

### 2. API validates

The API checks:

-   required fields;
-   provider configuration;
-   limits;
-   authorization;
-   allowed fields.

### 3. Job created

A job record is inserted into MySQL with `queued` status.

### 4. Job queued

The worker queue receives the job ID.

### 5. Worker claims job

Worker creates a job run and changes the job to `running`.

### 6. Provider call

Provider adapter performs the approved collection operation.

### 7. Normalize

Response becomes the platform's internal record format.

### 8. Validate

Invalid records are rejected or marked with quality warnings.

### 9. Deduplicate

Existing records are identified through canonical keys/provider IDs.

### 10. Persist

MySQL receives new/updated records.

### 11. Metrics

Job counters are updated.

### 12. Finish

Job becomes:

``` text
completed
```

or:

``` text
partially_completed
failed
cancelled
```

### 13. Dashboard

Frontend polls or subscribes to job status and displays progress.

### 14. Export

User selects filters and format. Export service creates an authorized
export.

## Recovery

If worker dies:

``` text
heartbeat expires
   ↓
job run detected as stale
   ↓
recoverable job requeued
   ↓
attempt counter incremented
```

Never requeue indefinitely.

## Observability

Every job should expose:

-   request/job ID;
-   timestamps;
-   provider operation;
-   work-unit counts;
-   record counts;
-   error code;
-   retry count;
-   worker ID.
