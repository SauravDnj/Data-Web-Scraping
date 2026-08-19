# Contributing

This repository is built task-by-task from `docs/`. Before working on
anything:

1. Read `docs/00_MASTER_README.md` and `docs/16_MEMORY.md` for current
   state and decisions.
2. Read the specific `docs/T0xx_PROMPT.md` for the task you're doing —
   it lists what to read, what to implement, what not to implement, and
   acceptance criteria.
3. Follow `docs/CODING_STANDARDS.md` for formatting, naming, testing,
   logging, and Git conventions.
4. After the task: run the relevant checks, review the diff, and update
   the tracking docs the task prompt names (typically
   `docs/15_PROGRESS.md`, `docs/16_MEMORY.md`, `docs/17_CURRENT_WORK.md`,
   `docs/18_COMPLETED_WORK.md`, `docs/19_PENDING_WORK.md`,
   `docs/20_WORKING_FILES.md`).

See `docs/01_TASK_EXECUTION_PROTOCOL.md` for the full protocol.

## Hard boundary

Never implement CAPTCHA solving, anti-bot/stealth evasion, or
authentication/rate-limit bypass. Only the documented, approved Google
Maps Platform API workflow is permitted. See
`docs/08_SECURITY_COMPLIANCE.md` and `docs/22_SECURITY_RULES.md`.
