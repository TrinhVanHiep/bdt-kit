---
name: qa-automate
description: Turn test cases, acceptance criteria or a fixed bug into automated tests in the project's own test suite — at the lowest level that can catch the failure (unit, integration, API, end to end), mirroring the existing tests, stable (no fixed sleeps, selectors by role or label, data the test owns), and proven by failing without the fix. Use when the project has a test suite and the user says "viết test tự động", "automate test case này", "thêm test cho bug này", or after a bug fix in a repo whose rules ask for tests.
---

# qa-automate

**Input:** what to automate (test-case IDs, ACs, a bug), the project's test suite, its rules and the dev profile in `.bdt/dev/` (TEST conventions, stack packs).
**Output:** test files that follow the suite's own patterns, the command and its result, and rows in `.bdt/TESTS.md` (level, test file in Method, tags).

## Gate
- The project has a test suite and its rules allow new tests (`.bdt/PROJECT.md` → Commands → Tests and "Project rules that override the kit", and the project's own rules). Some projects forbid tests: then stop here.
- No suite: do not set one up. A new framework, dependency or CI step is a stop-and-confirm item; offer it as a proposal.

## Pick the level
- The lowest level that would have caught the failure: logic → unit; a component with its state, or the API layer against a mocked server → integration; an endpoint's contract → API test on a local server; a flow across pages → end to end.
- One end-to-end test per critical flow, not one per case. Data-heavy boundaries belong in unit or API tests.
- Automate what repeats (smoke, regression, boundaries); a one-off visual check stays manual.

## Mirror the suite
Find the closest existing test of the same kind (near the code under test, same level) and copy its structure, helpers, fixtures, naming and file placement. Follow the TEST rules in `.bdt/dev/CONVENTIONS.md` and the stack pack's Implement and Verify sections.

## Write a stable test
- One behaviour per test, named by that behaviour, with the case or bug ID in the name or a comment so `TESTS.md` can point to it.
- The test creates the data it needs (inside the test or a fixture it owns) and cleans up; it never depends on test order or on data another test left.
- Wait for a condition (element visible, request finished), never a fixed sleep.
- Find elements the way a user does (role, label, visible text) or by the project's test IDs; never by CSS paths or generated class names.
- Control time, timezone and randomness for date and ID cases (fake timers, a fixed date, seeded values).
- Network: the project's mock layer for unit and integration; a local server for API and end-to-end tests; never shared dev or staging, never production.
- Assert the observable result of the case (text, state, request body, response), not implementation details.

## Prove it
- For a bug: run the new test against the code without the fix and see it fail for the bug's reason, then pass with the fix. A test that passes on broken code proves nothing.
- For a case: break the behaviour once on purpose (or invert the assertion), see the test fail, and restore it.
- Run the new tests three times; a test that flips is not done.
- Never weaken an assertion, skip a test, add a retry or silence a check to get green (the stack pack lists the forms).

## Record
- `TESTS.md`: one row per automated case with Level, Method = test file and name, Tags (`smoke`, `regression`), Evidence = command, result and date.
- The test-case sheet: "automated: <test file>" in the Note column, written with `qa-run` (`docfill.py results`).
- Report the command, the result line and the fail-before-fix evidence. Do not commit; the change goes through `qa-verify` and Gate 2 like any other.
