# Claude Code Project Rules

## Before every task

1.  Read `docs/00_README.md`.
2.  Read `docs/15_MEMORY.md`.
3.  Read the task's referenced design documents.
4.  Inspect the current repository.
5.  Inspect current Git status.
6.  Identify the exact task ID.

## During implementation

-   Make the smallest coherent change.
-   Do not rewrite unrelated code.
-   Do not invent dependencies without justification.
-   Do not hard-code secrets.
-   Do not bypass provider controls.
-   Keep provider-specific code isolated.
-   Write tests with the implementation.
-   Prefer typed interfaces.
-   Preserve backward compatibility unless the task explicitly changes
    it.

## After implementation

Run the relevant tests.

Then update:

``` text
docs/13_COMPLETED_WORK.md
docs/14_WORKING_FILES.md
docs/15_MEMORY.md
docs/16_PENDING_WORK.md
docs/17_PROGRESS.md
docs/18_CURRENT_WORK.md
```

Only mark the task complete if its acceptance criteria are verified.

## Stop conditions

Stop and ask for clarification if:

-   the task conflicts with architecture;
-   a provider restriction is unclear;
-   a destructive database migration is required;
-   credentials are requested in source code;
-   an implementation would bypass access controls;
-   a requirement cannot be implemented safely as written.
