# UI --- Deep Design

## Design language

The UI should feel like a professional data operations console.

Priorities:

1.  clarity;
2.  density without clutter;
3.  fast filtering;
4.  visible job state;
5.  safe destructive actions.

## Page tree

``` text
/
├── dashboard
├── projects
│   ├── new
│   └── [id]
│       ├── overview
│       ├── configuration
│       ├── jobs
│       ├── records
│       └── exports
├── jobs
├── records
├── schedules
└── settings
```

## Dashboard

Cards:

``` text
Active Jobs
Completed Jobs
Failed Jobs
Records
```

Recent activity:

``` text
Project | Job | Status | Records | Time
```

## Project creation wizard

### Step 1

Name and description.

### Step 2

Provider and allowed configuration.

### Step 3

Query/location/fields.

### Step 4

Limits and schedule.

### Step 5

Review and confirm.

The review step is important because it prevents accidental large jobs.

## Job page

Top:

``` text
Job #123
RUNNING
```

Progress:

``` text
████████████░░░░ 72%
```

Metrics:

``` text
Work units
Success
Failed
Skipped
Created
Updated
Rejected
```

Logs:

``` text
10:31 configuration validated
10:32 worker claimed job
10:32 provider request started
10:33 records normalized
```

Logs must not show credentials.

## Records page

Use:

-   table;
-   pagination;
-   filters;
-   column selector;
-   record detail drawer.

## Empty state

Explain what to do:

> No records yet. Create a project configuration and run a collection
> job.

## Error state

Show:

-   what failed;
-   whether it is retryable;
-   recommended next action.

Do not expose raw stack traces to normal users.
