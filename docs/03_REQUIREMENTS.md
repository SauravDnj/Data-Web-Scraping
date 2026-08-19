# Requirements

## Functional requirements

### FR-001 Project management

A user can create, edit, archive, and inspect a collection project.

### FR-002 Collection configuration

A project stores provider, query, geographic parameters, requested
fields, schedule, and retention settings.

### FR-003 Configuration validation

Invalid or incomplete configurations must be rejected before a job is
created.

### FR-004 Job lifecycle

Jobs support:

``` text
draft
queued
running
paused
completed
partially_completed
failed
cancelled
```

### FR-005 Job metrics

Track total work units, successful units, failed units, skipped units,
records created, records updated, and records rejected.

### FR-006 Record management

Users can search, filter, sort, inspect, and export permitted records.

### FR-007 Provenance

Every stored record links to project, job, provider, collection time,
and source reference where permitted.

### FR-008 Deduplication

The system must have deterministic deduplication rules and database
constraints.

### FR-009 Retry

Recoverable failures can be retried with bounded exponential backoff.

### FR-010 Audit

Configuration changes, job actions, exports, and authentication events
are auditable.

### FR-011 Export

Users can export records to CSV and JSON in V1. Excel may be added
immediately after V1.

### FR-012 Scheduling

Schedules can create future jobs. Scheduling must honor provider usage
limits and user-configured limits.

## Non-functional requirements

### NFR-001 Reliability

A worker crash must not corrupt job state.

### NFR-002 Performance

List pages should use pagination and indexed queries.

### NFR-003 Security

Secrets are never stored in source control.

### NFR-004 Privacy

Do not collect sensitive personal data unless there is a documented
lawful and permitted use case.

### NFR-005 Observability

Every job has structured logs and error categories.

### NFR-006 Testability

Core business logic must be testable without making external provider
requests.

### NFR-007 Maintainability

Provider code is isolated from domain logic.

## Acceptance criteria

A V1 release must pass:

-   clean database migration;
-   API health check;
-   authenticated project CRUD;
-   configuration validation;
-   job creation;
-   worker execution;
-   successful persistence;
-   duplicate handling;
-   failure handling;
-   retry behavior;
-   record search;
-   CSV/JSON export;
-   audit event creation;
-   frontend end-to-end happy path;
-   documented local setup from a clean machine.
