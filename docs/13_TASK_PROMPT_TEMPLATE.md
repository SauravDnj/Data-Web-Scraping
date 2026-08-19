# Task Prompt Template

Copy this template for every new Claude Code task.

``` text
You are implementing TASK-ID in the Google Maps Data Platform.

FIRST READ:
- docs/00_MASTER_README.md
- docs/01_SYSTEM_EXPLANATION.md
- docs/02_SYSTEM_ARCHITECTURE_DEEP.md
- docs/15_MEMORY.md
- docs/17_PROGRESS.md
- docs/18_CURRENT_WORK.md
- the task-specific design documents

CURRENT TASK:
[exact task]

GOAL:
[one paragraph]

SCOPE:
[list exact files/components]

DO NOT:
[list related work that must not be implemented]

IMPLEMENTATION REQUIREMENTS:
1. ...
2. ...
3. ...

ARCHITECTURE RULES:
- UI must not access DB directly.
- API must not contain provider implementation.
- long-running work must run in worker.
- provider credentials must remain server-side.
- do not bypass provider access controls.
- use typed interfaces.
- add tests.

ACCEPTANCE CRITERIA:
- [ ] ...
- [ ] ...
- [ ] ...

TESTS TO RUN:
- ...
- ...

DOCUMENTATION:
After implementation update:
- docs/13_COMPLETED_WORK.md
- docs/14_WORKING_FILES.md
- docs/15_MEMORY.md
- docs/16_PENDING_WORK.md
- docs/17_PROGRESS.md
- docs/18_CURRENT_WORK.md

STOP CONDITIONS:
Stop and ask if:
- requirements conflict;
- a destructive migration is needed;
- provider policy is unclear;
- credentials are exposed;
- access-control bypass would be required.

Do not claim completion without evidence.
```
