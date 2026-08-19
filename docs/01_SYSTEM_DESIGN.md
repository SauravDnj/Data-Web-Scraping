# System Design

## 1. Product vision

Build a reliable data collection platform that turns a user-defined
collection configuration into a controlled job, obtains data through an
approved provider/collector, normalizes it, validates it, deduplicates
it, stores it in MySQL, and exposes the result through a web dashboard
and exports.

The product should be source-agnostic internally even though Google Maps
is the primary V1 source.

## 2. Design principles

### Reliability

Every job has an explicit lifecycle and recoverable failure state.

### Provider isolation

Google-specific behavior lives behind a provider adapter. The rest of
the application does not depend directly on Google-specific code.

### Data provenance

Every record must retain enough metadata to explain where it came from,
when it was collected, which job produced it, and which provider
operation produced it.

### Idempotency

Repeating a job should not blindly create duplicate business records.

### Explicit compliance

Provider terms and data retention rules are configuration and product
concerns, not an afterthought.

### Local-first development

The system must run without Docker during V1 development.

### Observability

A developer should be able to determine why a job failed without opening
the browser automation internals.

## 3. Primary user workflow

``` text
Create project
  -> choose source/provider
  -> configure query/location/fields
  -> validate configuration
  -> create job
  -> queue job
  -> collector executes
  -> raw response captured where permitted
  -> normalize
  -> validate
  -> deduplicate
  -> persist
  -> update metrics
  -> export/view
```

## 4. Major domains

-   Identity and users
-   Projects
-   Collection configurations
-   Provider connections
-   Jobs and job runs
-   Records
-   Record provenance
-   Data quality
-   Exports
-   Schedules
-   Audit logs
-   System settings

## 5. V1 boundaries

### In scope

-   single local developer/user environment;
-   MySQL;
-   FastAPI;
-   Next.js;
-   one Google Maps Platform provider integration;
-   controlled collection jobs;
-   record storage;
-   exports;
-   logs and audit events.

### Out of scope for V1

-   CAPTCHA solving;
-   anti-bot bypass;
-   stealth fingerprinting;
-   credential harvesting;
-   proxy rotation intended to evade controls;
-   scraping private/restricted information;
-   autonomous decisions to circumvent provider restrictions;
-   billing;
-   Kubernetes;
-   multi-region deployment.

## 6. Failure philosophy

Failures are classified as:

-   configuration;
-   authentication;
-   provider rejection;
-   rate/usage limit;
-   transient network;
-   malformed response;
-   validation;
-   persistence;
-   export;
-   internal programming error.

Only explicitly retryable classes may be automatically retried.

## 7. Future extensibility

Add new providers through:

``` text
ProviderAdapter
  -> validate_config()
  -> estimate()
  -> collect()
  -> normalize()
  -> provider_health()
```

The core job manager should not know implementation details of
individual providers.
