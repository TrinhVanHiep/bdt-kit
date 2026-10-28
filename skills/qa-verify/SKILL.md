---
name: qa-verify
description: Verify a change before handing it over — static checks, build, security grep, diff-vs-plan review, every acceptance criterion with evidence, and a browser QA pass at 375/768/1440 with console and network — ending in a READY / NOT READY report. Use after implementing, before a commit or PR, or when the user asks "test giúp tôi", "check lại", "đã ổn chưa".
---

# qa-verify

**Input:** the change, the brief's ACs, the project's commands, a local or test environment.
**Output:** `report.md` with READY / NOT READY and SHIP / … verdicts, evidence per AC, new rows in `.bdt/TESTS.md`.

Template: `../bdt-flow/templates/report.md`. Write `.bdt/work/<TICKET-ID>/report.md`; add rows to `.bdt/TESTS.md`.

## 1. Static and build (commands from `.bdt/PROJECT.md` or the project rules)
Lint, typecheck, build, tests if the project has them. Record the exact command and the result line. A missing command is a gap, never a pass.

## 2. Security and hygiene grep on the diff
Debug output, secrets or tokens, `.env` values, unsafe HTML injection, redirects taken from the URL without validation, personal data in logs or URLs, hardcoded UI text or magic values when the project forbids them, duplicate i18n keys in the touched JSON (parsers keep the last one silently).

## 3. Diff vs plan
Files outside the plan, behaviour beyond the declared scope, temporary code, mock data, leftover TODOs.

## 4. Acceptance criteria
For each AC: the evidence you actually saw (screen state, request body, response, command output). "The command ran" is not evidence that the behaviour is right.

## 5. Browser QA
- Read-only by default. Mutations only against a local mock or a local dev server, never shared dev/staging unless the user says so.
- **Smoke:** page loads, console has no new errors, network has no unexpected 4xx/5xx.
- **Interaction:** valid input, invalid input, empty, double submit, back, reload, deep link, signed out.
- **States:** loading, empty, error, permission/role variants from the brief.
- **Layout:** 375, 768, 1440; long strings without spaces; keyboard only; accessible names on inputs and icon buttons. Automation alone never proves "accessible".
- **Design:** compare with the design frame when available. No baseline means INCONCLUSIVE, not pass.
- Check the request payloads in the network tab for every mutation the change touches.

## 6. Verdict
- READY only when every Required AC has evidence and nothing in 1–3 is red.
- Browser verdict: SHIP / SHIP WITH FIXES / DO NOT SHIP / INCONCLUSIVE.
- List what you could not verify and why (no account, no data, needs a shared mutation).
