# T102 --- Release gate

## Task purpose

Run the V1 definition-of-done checklist and resolve failures.

## Dependencies

T090,T091,T092,T093,T094,T100,T101

## Full Claude Code implementation prompt

You are implementing T102 --- V1 Release Gate.

READ: - docs/28_V1_DEFINITION_OF_DONE.md -
docs/35_RISKS_AND_BLOCKERS.md - all architecture and requirements
documents.

OBJECTIVE: Determine whether V1 is actually complete.

DO: 1. Run backend tests. 2. Run frontend tests. 3. Run integration
tests. 4. Run E2E tests. 5. Test fresh migrations. 6. Test worker
recovery. 7. Test exports. 8. Review authentication/authorization. 9.
Review provider configuration. 10. Review environment/secrets. 11.
Review logs. 12. Review backup/restore. 13. Review documentation. 14.
Fix defects discovered during the gate. 15. Record evidence.

DO NOT: - mark complete because the UI looks finished; - ignore failing
tests; - suppress known security issues.

ACCEPTANCE: Every mandatory V1 criterion has evidence.

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
