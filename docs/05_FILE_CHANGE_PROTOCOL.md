# File Change Protocol

For every task, Claude should identify:

## Must change

Files directly required.

## May change

Files needed for integration/tests.

## Must not change

Unrelated files.

## Generated

Generated files that should not be committed.

Before completion, compare the actual Git diff against this list.
