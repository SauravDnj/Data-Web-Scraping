# T052 --- Canonical identity

## Task purpose

Create deterministic record identity and collision tests.

## Dependencies

T050,T051

## Full Claude Code implementation prompt

You are implementing T052 --- Canonical Identity.

OBJECTIVE: Create the safest possible deterministic identity strategy.

IMPLEMENT: 1. Prefer stable provider identifiers when permitted. 2.
Define fallback canonicalization only where needed. 3. Normalize
identity inputs. 4. Generate canonical key. 5. Define project/provider
scope. 6. Test repeated identical input. 7. Test minor formatting
differences. 8. Test different businesses. 9. Document known collision
limitations.

DO NOT: - use business name alone as identity.

ACCEPTANCE: False merges are minimized and known limitations are
documented.

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
