# T039 --- Authorization

## Task purpose

Implement project-level authorization and resource isolation.

## Dependencies

T038,T033,T035,T036

## Full Claude Code implementation prompt

You are implementing T039 --- Authorization.

READ: - docs/10_SECURITY_DEEP.md - docs/05_API_DEEP.md

OBJECTIVE: Guarantee users can access only authorized projects and
derived resources.

IMPLEMENT: 1. Define ownership policy. 2. Enforce it in project service.
3. Enforce it for configs. 4. Enforce it for jobs. 5. Enforce it for
records. 6. Enforce it for exports. 7. Enforce it for schedules. 8. Add
negative tests for cross-project access. 9. Review every project-scoped
endpoint.

ACCEPTANCE: A user cannot access another user's project by changing an
ID in a request.

## Task completion record

Claude Code must not mark this task complete until: - implementation is
present; - acceptance criteria are verified; - relevant tests pass; -
Git diff is reviewed; - project tracking documents are updated.

## Required tracking updates

-   `docs/15_PROGRESS.md`
-   `docs/16_MEMORY.md`
-   `docs/17_CURRENT_WORK.md`
-   `docs/18_COMPLETED_WORK.md`
-   `docs/19_PENDING_WORK.md`
-   `docs/20_WORKING_FILES.md`
