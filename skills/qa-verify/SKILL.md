---
name: qa-verify
description: Verify a change before handing it over — static checks, build, security grep, diff-vs-plan review, every acceptance criterion with evidence, the project's convention checks, and a runtime QA pass for the app type (browser at 375/768/1440 with console and network for web UI, local HTTP calls for an API, simulator for mobile, sample runs for a CLI) — ending in a READY / NOT READY report. Use after implementing, before a commit or PR, or when the user asks "test giúp tôi", "check lại", "đã ổn chưa".
---

# qa-verify

**Input:** the change, the brief's ACs, the project's commands, the dev profile in `.bdt/dev/` (app types, conventions, stack packs), a local or test environment.
**Output:** `report.md` with READY / NOT READY and SHIP / … verdicts, evidence per AC, new rows in `.bdt/TESTS.md`.

Template: `../bdt-flow/templates/report.md`. Write `.bdt/work/<TICKET-ID>/report.md`; add rows to `.bdt/TESTS.md`.

## 1. Static and build (commands from `.bdt/PROJECT.md` or the project rules)
Lint, typecheck, build, tests if the project has them. Record the exact command and the result line. A missing command is a gap, never a pass.
Then the Check of every `confirmed` CONV rule in `.bdt/dev/CONVENTIONS.md` whose "Applies to" matches a touched file and that has a grep or lint check; record each rule ID with its result.

## 2. Security and hygiene grep on the diff
Debug output (patterns from the stack pack), secrets or tokens, `.env` values, unsafe HTML injection, redirects taken from the URL without validation, personal data in logs or URLs, hardcoded UI text or magic values when the project forbids them, duplicate i18n keys in the touched JSON (parsers keep the last one silently), and the stack pack's Security section.

## 3. Diff vs plan
Files outside the plan, behaviour beyond the declared scope, temporary code, mock data, leftover TODOs.

## 4. Acceptance criteria
For each AC: the evidence you actually saw (screen state, request body, response, command output). "The command ran" is not evidence that the behaviour is right.

## 5. Runtime QA (by app type)
App types come from `.bdt/dev/STACK.md`; with no profile, judge from the change and say which you chose. Run the recipe for each app type the change touches, plus the stack pack's Verify section.
- Read-only by default. Mutations only against a local mock, a local server or a local database, never shared dev/staging unless the user says so.

### Web UI (browser)
- **Smoke:** page loads, console has no new errors, network has no unexpected 4xx/5xx.
- **Interaction:** valid input, invalid input, empty, double submit, back, reload, deep link, signed out.
- **States:** loading, empty, error, permission/role variants from the brief.
- **Layout:** the breakpoints in PROJECT.md (default 375, 768, 1440); long strings without spaces; keyboard only; accessible names on inputs and icon buttons. Automation alone never proves "accessible".
- **Design:** compare with the design frame when available. No baseline means INCONCLUSIVE, not pass.
- Check the request payloads in the network tab for every mutation the change touches.

### API / backend
- Run the service locally against a local database, container or mock.
- Call each changed endpoint with valid input, invalid input, missing or expired auth, the wrong role and a missing resource; check status codes, body shape and error codes against the API spec.
- Check the side effects in the local database (rows written, nothing extra), and that a migration applies and rolls back on a local database.
- Logs: no stack traces for expected errors, no personal data or secrets.

### Mobile
Simulator or emulator: the web UI interaction and state checks, plus small and large screens, rotation when supported, background and resume, offline, and permission prompts denied.

### CLI / library / worker
Run with sample inputs, including empty, invalid and large ones; check exit codes, stdout and stderr; for a library, call the changed public API the way a consumer would; for a job, run it twice to check that a retry does no harm.

## 6. Verdict
- READY only when every Required AC has evidence and nothing in 1–3 is red.
- Runtime verdict: SHIP / SHIP WITH FIXES / DO NOT SHIP / INCONCLUSIVE.
- List what you could not verify and why (no account, no data, needs a shared mutation).
