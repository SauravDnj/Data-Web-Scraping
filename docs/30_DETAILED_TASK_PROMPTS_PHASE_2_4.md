# Detailed Claude Code Prompts --- Database, Backend, Provider

## T020 --- SQLAlchemy

``` text
Implement T020.

Read:
docs/04_DATABASE_DEEP.md
docs/24_BACKEND_FILE_PLAN.md

Create:
- SQLAlchemy engine;
- session factory;
- declarative base;
- naming conventions;
- environment-driven database configuration.

Requirements:
- no global request-sharing sessions;
- safe connection handling;
- tests.

Do not create all models in this task.
```

## T021 --- Alembic

``` text
Implement T021.

Configure Alembic against SQLAlchemy metadata.

Requirements:
- environment-driven DB URL;
- migration discovery;
- migration command documentation;
- test against clean DB.

Do not hand-edit generated migration logic unless reviewed.
```

## T022--T026 --- Database tables

``` text
Implement the database table task assigned to you.

Read docs/05_DATABASE_DEEP.md.

For each table:
1. define model;
2. define relationships;
3. define constraints;
4. define indexes;
5. create migration;
6. write repository/model tests;
7. verify migration from empty DB.

Do not put business workflows into model classes.
```

## T030 --- Domain models

``` text
Implement T030.

Create internal domain models independent from SQLAlchemy models.

Goal:
The provider, API, and database should not share one giant model.

Define:
- Project;
- CollectionConfig;
- Job;
- JobRun;
- Record;
- Export.

Acceptance:
domain models are usable without a database.
```

## T031 --- Job state machine

``` text
Implement T031.

Define legal states and transitions from docs/09_JOB_QUEUE_WORKER_DEEP.md.

Requirements:
- explicit transition function;
- invalid transition exception;
- unit tests for every valid and invalid transition.

Do not add retry logic here.
```

## T032 --- Repositories

``` text
Implement T032.

Create repository interfaces and MySQL implementations.

Repositories should:
- persist;
- query;
- update;
- transaction safely.

They must not contain HTTP or provider logic.

Add tests.
```

## T033 --- Project service

``` text
Implement T033.

Business rules:
- user owns project;
- name validation;
- create/update/archive;
- audit important changes.

Add API tests only after service tests.
```

## T034 --- Configuration service

``` text
Implement T034.

Requirements:
- provider configuration;
- version number;
- active version;
- validation status;
- immutable historical version.

Changing configuration creates a new version instead of mutating historical job configuration.

Add tests.
```

## T035 --- Job service

``` text
Implement T035.

Requirements:
- create job from active config;
- enforce authorization;
- initial status queued;
- idempotency;
- cancellation/pause/resume/retry rules;
- audit events.

Do not call provider directly.
```

## T040 --- Provider interface

``` text
Implement T040.

Create a provider abstraction.

Methods:
- validate_config
- estimate_usage
- collect
- classify_error
- normalize

Use typed request/response models.

The interface must not mention browser automation.
```

## T041 --- Google configuration

``` text
Implement T041.

Implement validation for the selected Google Maps Platform API/product configuration.

Validate:
- required parameters;
- field selection;
- numeric ranges;
- location syntax;
- max requested work;
- credential presence on server.

Do not call the provider for malformed configuration.

Document any provider-specific limitations.
```

## T042 --- Google client

``` text
Implement T042.

Use the official/documented Google Maps Platform API/SDK workflow selected for the project.

Requirements:
- server-side credentials;
- timeouts;
- bounded retries for transient errors;
- structured errors;
- no secrets in logs;
- no CAPTCHA/anti-bot/rate-limit bypass.

Use dependency injection so tests can replace the real client.
```

## T043 --- Response mapper

``` text
Implement T043.

Map provider responses into the platform's internal record model.

Requirements:
- explicit field mapping;
- type conversion;
- missing-field handling;
- provenance;
- tests using synthetic fixtures.

Do not silently invent values.
```

## T044 --- Provider errors

``` text
Implement T044.

Map provider errors into:
- authentication;
- quota;
- rate;
- invalid request;
- temporary;
- permanent;
- unknown.

Define which classes are retryable.

Add tests for each class.
```
