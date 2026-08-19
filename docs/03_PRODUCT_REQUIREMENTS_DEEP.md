# Product Requirements --- Deep

## User roles

V1 can start with one authenticated user role.

Future roles:

``` text
owner
admin
operator
viewer
```

## Project requirements

A project contains:

-   name;
-   description;
-   provider;
-   active configuration;
-   status;
-   created/updated timestamps.

## Configuration requirements

Configuration must include:

-   provider;
-   search parameters;
-   geographic parameters if applicable;
-   requested fields;
-   provider usage limits;
-   optional schedule;
-   retention policy.

Configuration must be versioned.

Why?

If a user changes:

``` text
fields = [name, address]
```

to:

``` text
fields = [name, address, phone, website]
```

a historical job must still point to the old configuration version.

## Job requirements

A job records:

-   project;
-   configuration version;
-   status;
-   creation time;
-   start time;
-   finish time;
-   worker;
-   attempt;
-   metrics;
-   failure.

## Record requirements

A record must have:

-   internal ID;
-   project;
-   job;
-   provider;
-   canonical identity;
-   normalized data;
-   collection timestamp.

## Search requirements

The records page must support server-side filtering.

Do not load 100,000 records into the browser.

## Export requirements

Exports must:

-   be authorized;
-   use server-side filters;
-   record who requested them;
-   have a status;
-   avoid exposing records from another project;
-   produce safe filenames.

## Scheduling requirements

A schedule creates jobs; it does not execute collection itself.

``` text
Scheduler
 ↓
create job
 ↓
queue
 ↓
worker
```

This keeps one execution pathway.

## Nonfunctional requirements

### Reliability

Jobs must recover from worker failures.

### Security

Credentials must never reach the browser.

### Performance

Indexes must support common queries.

### Maintainability

Provider code must remain isolated.

### Observability

Every job needs a traceable ID.
