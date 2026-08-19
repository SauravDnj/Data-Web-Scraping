# T075 --- Records UI

## Task purpose

Build scalable records table, filtering, and detail view.

## Dependencies

T036,T054,T074

## Full Claude Code implementation prompt

You are implementing T075 --- Records UI.

OBJECTIVE: Provide a practical data-review interface.

IMPLEMENT: 1. Server-side pagination. 2. Search/filter controls. 3.
Sorting. 4. Column selection. 5. Record detail drawer/page. 6.
Provenance display where permitted. 7. Data-quality warnings. 8.
Empty/loading/error states. 9. Preserve filters in URL/query state where
appropriate. 10. Avoid loading the entire dataset.

ACCEPTANCE: Synthetic large dataset remains responsive because
pagination is server-side.

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
