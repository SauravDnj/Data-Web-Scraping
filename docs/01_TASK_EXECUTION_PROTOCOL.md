# Task Execution Protocol

## Rule

Claude Code executes one task at a time.

## Before task

1.  Read the task prompt.
2.  Read its dependencies' outputs.
3.  Inspect current Git status.
4.  Inspect existing files.
5.  Read MEMORY and CURRENT_WORK.
6.  Confirm task is not already complete.

## During task

-   Implement only the task scope.
-   Use existing abstractions.
-   Add tests with code.
-   Do not rewrite architecture for convenience.
-   Stop if provider/security ambiguity appears.

## After task

1.  Run tests.
2.  Review Git diff.
3.  Verify acceptance criteria one by one.
4.  Update progress/memory/work files.
5.  Record exact test commands.
6.  Record blockers.
7.  Identify next task.

## Never

-   claim tests passed without running them;
-   claim a task is complete because code compiles;
-   expose secrets;
-   bypass third-party controls;
-   skip migrations;
-   mix provider implementation into generic services.
