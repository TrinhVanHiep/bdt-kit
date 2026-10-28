---
name: dev-implement
description: Execute an approved plan task by task with a check after each file, log every deviation against the acceptance criteria, and apply stop rules for build and type errors. Use after the plan is approved, or when the user says "làm đi" on a planned change, or when a build/typecheck/lint keeps failing.
---

# dev-implement

**Input:** an approved plan.
**Output:** the code change, deviations logged in `report.md`, checks run after each task.

Plan: `.bdt/work/<TICKET-ID>/plan.md`; deviations go into `report.md` beside it.

## Loop per task
1. Re-read the mirror file:line before writing.
2. Make the smallest change for this task. Match surrounding naming, comments and idiom.
3. Run the task's Validate step (at least typecheck or lint of the touched files).
4. Tick the task. If you did something the plan did not say, log it: what changed, why, which AC.

## Deviations
- A deviation that changes behaviour or scope is shown to the user before continuing.
- An AC that turns out impossible: mark `[revised]` in the brief, add a question, tell the user.

## Stop rules (build, type and lint errors)
Fix one error at a time and re-run. Stop and report when:
- the same error survives 3 attempts;
- a fix creates more errors than it removes;
- the cause is architectural (wrong layer, missing contract) rather than local.
Never silence a check (`any`, ignore comments, disabling a rule, `--no-verify`) to get green.

## Hygiene before leaving this step
No debug output, no commented-out code, no unused imports, no stray files, formatter run on touched files only, lockfile unchanged unless dependencies changed.

## Then
Run `qa-verify`. Do not commit yet.
