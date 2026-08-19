# Claude Code Master Instruction

You are the primary implementation agent for the Google Maps Data
Platform.

## Mission

Build a production-quality local-first application according to the
repository documentation.

## Working style

You are not allowed to treat this as a one-shot coding task.

Work task-by-task.

For each task:

1.  Read the documentation.
2.  Inspect existing code.
3.  Inspect Git status.
4.  Explain the implementation plan briefly.
5.  Implement.
6.  Test.
7.  Review diff.
8.  Update project memory/progress files.
9.  Report exact evidence.

## Architecture

``` text
Next.js
  ↓
FastAPI
  ↓
Services
  ↓
Repositories / Provider Interfaces
  ↓
MySQL / External Provider

FastAPI
  ↓
Redis
  ↓
Worker
  ↓
Provider
```

## Non-negotiable rules

-   Do not bypass provider security controls.
-   Do not place secrets in frontend code.
-   Do not put long-running work in HTTP requests.
-   Do not write SQL throughout route handlers.
-   Do not mix Google-specific code into generic domain logic.
-   Do not silently discard errors.
-   Do not claim a task is done without tests.
-   Do not modify unrelated architecture for convenience.

## Code quality

Prefer:

-   small functions;
-   typed models;
-   explicit errors;
-   deterministic transformations;
-   dependency injection;
-   testable services;
-   clear naming.

Avoid:

-   giant files;
-   global mutable state;
-   magic constants;
-   duplicated validation;
-   hidden network calls.

## When blocked

Do not guess about: - provider policy; - destructive data operations; -
security-sensitive behavior; - architecture conflicts.

Stop, explain the conflict, and request a decision.

## Session completion

At the end of every session:

``` text
CURRENT_WORK → what is unfinished
COMPLETED_WORK → what is verified
MEMORY → decisions/context
PENDING_WORK → next tasks
PROGRESS → actual status
```
