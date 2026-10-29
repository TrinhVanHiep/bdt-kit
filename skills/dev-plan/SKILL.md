---
name: dev-plan
description: Write an implementation plan grounded in the real codebase — impact analysis with grep evidence, patterns to mirror with file:line, a not-building list, and tasks each with mirror, gotcha and validation — then wait for approval. Use after a brief is ready, or whenever a change needs more than 3 steps.
---

# dev-plan

**Input:** an approved brief (or a clear request), the repo, the dev profile in `.bdt/dev/`.
**Output:** `plan.md` (must-read files, conventions that apply, patterns to mirror with file:line, impact, not-building, tasks with validate steps, confidence), then Gate 1.

Template: `../bdt-flow/templates/plan.md`. Reads `.bdt/work/<TICKET-ID>/brief.md`, writes `plan.md` beside it.

Dev profile: `.bdt/dev/STACK.md`, `.bdt/dev/CONVENTIONS.md` and the stack packs STACK.md lists (kit packs: `../dev-profile/stacks/`). When there is none, suggest `dev-profile`; for a quick change, continue with golden files found by grep and write in the plan that the conventions are unverified.

## Ambiguity gate (before exploring)
Stop and ask if the deliverable is vague, success is undefined, or two readings lead to different behaviour. Point at the brief's question.

## Explore with evidence
- Find the closest existing implementation of the same kind of thing (reference implementations named in project rules first, then the golden files of the dev profile). Mirror it; never invent a new pattern when one exists.
- List the CONV rules whose "Applies to" matches the files you will touch, and the pack's plan gotchas that apply. A rule still `observed` or `conflict` that the change depends on is a question, not a choice.
- For every shared thing you will touch (types, constants, routes, API layer, UI primitives, i18n keys used in many places), grep its importers and write the count.
- Check the API docs for each endpoint used: path, method, body, response, error codes.

## Impact (the six questions)
Code · data and interfaces · tests · docs · release (env vars, config) · shared ground. Mark anything not proven by a read or grep as **unverified**. Shared ground or risky areas (auth, payment, tokens, redirects, destructive actions) are stop-and-confirm items per project rules.

## Tasks
Small, ordered, each one: Action (CREATE/UPDATE/DELETE path), Implement, Mirror (file:line), Conventions (CONV ids), Gotcha (the trap; from the pack when it has one), Validate (the check right after it), Covers (AC ids). Every Required AC is covered by at least one task.

## Not building
Explicit list. It is what keeps the diff small.

## Confidence
1–10 that someone new to the repo could ship from this plan alone, and what would raise it.

## Gate 1
Show the user: impact summary, task list (one line each), not-building, confidence, stop-and-confirm items. Wait for approval before editing code.
