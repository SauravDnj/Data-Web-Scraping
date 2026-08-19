# UI Design

## Design goals

-   simple;
-   professional;
-   fast;
-   desktop-first for data operations;
-   responsive enough for monitoring;
-   no unnecessary visual complexity.

## Main navigation

``` text
Dashboard
Projects
Jobs
Records
Exports
Schedules
Settings
```

## Dashboard

Show:

-   active jobs;
-   completed jobs;
-   failed jobs;
-   total records;
-   recent projects;
-   recent failures.

## Project list

Columns:

``` text
Project
Source
Status
Last job
Records
Updated
Actions
```

## Create project

Step 1: Basic information

``` text
Name
Description
Source/provider
```

Step 2: Collection configuration

``` text
Query
Geographic parameters
Requested fields
Maximum work units
```

Step 3: Limits and schedule

``` text
Per-job limit
Schedule
Timezone
```

Step 4: Review

Display an exact configuration summary and provider/compliance notices.

Step 5: Create

Create project and optionally create a first job.

## Job detail

Show:

``` text
Status
Started
Duration
Progress
Success
Failures
Records created
Records updated
Records rejected
```

Include a live log panel with safe redaction.

Actions:

-   Pause
-   Resume
-   Cancel
-   Retry if eligible

## Records

Use server-side pagination.

Filters:

-   project;
-   date;
-   provider;
-   category where permitted;
-   quality status.

A record detail drawer should show normalized fields and provenance.

## Export

Export dialog:

``` text
Format
Filters
Columns
Filename
```

Show export status and download action.

## UI state requirements

Every page needs:

-   loading state;
-   empty state;
-   error state;
-   success feedback;
-   disabled state for unsafe/invalid actions.

Do not display provider credentials.

## Accessibility

Use semantic controls, keyboard navigation, visible focus, form labels,
error association, and adequate contrast.
