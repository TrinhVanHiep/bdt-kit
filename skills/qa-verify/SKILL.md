---
name: qa-verify
description: Verify a change before handing it over — static checks, build, security grep, diff-vs-plan review, every acceptance criterion with a status and evidence, the project's convention checks, regression of the features that share the changed code, and a runtime QA pass for the app type (browser at 375/768/1440 with console and network for web UI, local HTTP calls for an API, simulator for mobile, sample runs for a CLI) — ending in a READY / READY WITH GAPS / NOT READY report. Works without a brief, ticket or plan and says what that leaves unproven. Use after implementing, before a commit or PR, or when the user asks "test giúp tôi", "check lại", "đã ổn chưa".
---

# qa-verify

**Input:** the change, the brief's ACs, the project's commands, the dev profile in `.bdt/dev/` (app types, conventions, stack packs), a local or test environment. Any of them may be missing (step 0).
**Output:** `report.md` with READY / READY WITH GAPS / NOT READY and a runtime verdict, a status and evidence per AC, the regression rows run, new rows in `.bdt/TESTS.md`.

This skill verifies and reports; it never changes code. Fixes go back to `dev-implement` or the developer, then the skill runs again (see Re-run after a fix).

Template: `../bdt-flow/templates/report.md`; if it is missing, use the sections Verdict, Inputs, Verification, Acceptance criteria, Regression, Runtime QA, Gaps, Open items. Write `.bdt/work/<TICKET-ID>/report.md`. Rows added to `.bdt/TESTS.md` use the columns of `../bdt-flow/templates/TESTS.md` (ID, Source, State, Level, Tags, Method, Input → expected, Evidence).

## 0. Inputs (decide before step 1; write the choices in the report's Inputs line)
- **No ticket ID:** use the branch name for the work folder (`.bdt/work/<branch>/`).
- **No brief or ACs:** derive ACs from the diff, the commit messages and the user's description. Mark each one `Derived`; give Required to the behaviour the change clearly targets. Derived ACs prove that the code does what it seems to intend, not what the client asked for, so the verdict is at best READY WITH GAPS.
- **No plan:** skip step 3 and record it as a gap; step 5 finds the regression targets by grep.
- **No `.bdt/PROJECT.md`:** take the commands from the project rules and the manifest scripts (`package.json`, `composer.json`, `Makefile`, …) and say where each came from.

## 1. Static and build (commands from `.bdt/PROJECT.md` or the project rules)
Lint, typecheck, build, tests if the project has them. Record the exact command and the result line. A missing command is a gap, never a pass.
Then the Check of every `confirmed` CONV rule in `.bdt/dev/CONVENTIONS.md` whose "Applies to" matches a touched file and that has a grep or lint check; record each rule ID with its result.

**When a check is red:** the verdict is NOT READY. Still run steps 2 and 3: they are cheap and need no working build, so the report lists every static problem at once. Skip steps 4–6 and write "not run: step 1 red" for them.

## 2. Security and hygiene grep on the added lines of the diff
- **Secrets:** `api[_-]?key`, `secret`, `passw(or)?d\s*[:=]`, `token\s*[:=]`, `BEGIN [A-Z ]*PRIVATE KEY`, long random-looking literals, `.env` values; personal data in logs or URLs.
- **Debug output, unsafe HTML and dynamic code:** the stack pack's patterns (for JavaScript: `console.log`, `debugger`, `dangerouslySetInnerHTML`, `innerHTML`, `eval(`).
- **Dependencies:** a new package or a changed lockfile that the plan does not name is a finding; a new dependency is a stop-and-confirm item.
- Redirects taken from the URL without validation, hardcoded UI text or magic values when the project forbids them, duplicate i18n keys in the touched JSON (parsers keep the last one silently), and the stack pack's Security section.

A match is a lead, not a finding: read the line in context before reporting it.

## 3. Diff vs plan (skipped without a plan, see step 0)
Files outside the plan, behaviour beyond the declared scope, temporary code, mock data, leftover TODOs.

## 4. Acceptance criteria
Each AC keeps its priority from the brief (Required / Important / Optional; `Derived` when step 0 derived it) and gets one status:

| Status | When |
| ------ | ---- |
| PASS | The expected result was seen and the evidence is attached |
| FAIL | The result differs from the expected result |
| BLOCKED | Could not run: no data, no account, no local mock for a change of data, step 1 red |
| NOT VERIFIED | Not attempted, with the reason (out of time, needs a device) |

Evidence is what was seen and where it is: a screenshot path (`evidence/<AC-ID>.png`), a log or command excerpt, or a request and response (method, path, body, status, `error.code`, `requestId`). "The command ran" is not evidence that the behaviour is right. Mask personal data and tokens in every screenshot and log the report links.

## 5. Regression
What the change could break beyond its own ACs:
- Find what shares the changed code: the plan's Impact and, with or without a plan, a grep for the importers of each changed component, API function, store, hook, type and constant. Every screen, endpoint or job that uses them is a regression target.
- Pick the `.bdt/TESTS.md` rows of those areas, plus every `smoke` row of the app types touched. A target with no row gets a smoke check of its main path.
- Run them (automated rows by their command, manual rows by their method) and record each in the report's Regression table with why it was picked.
- A row that could not be run is listed with the reason; it keeps its old evidence date.

## 6. Runtime QA (by app type)
App types come from `.bdt/dev/STACK.md`; with no profile, judge from the change and say which you chose. Run the recipe for each app type the change touches, plus the stack pack's Verify section.
- Read-only by default. Cases that change data (a valid submit, a double submit, create, update, delete) run only against a local mock, a local server or a local database, or on a shared environment the user names for this run. With none of these, those cases are BLOCKED in the report, never skipped silently.

### Web UI (browser)
- **Smoke:** page loads, console has no new errors, network has no unexpected 4xx/5xx.
- **Interaction:** valid input, invalid input, empty, double submit, back, reload, deep link, signed out, the URL or ID of another user's record.
- **Network and session:** throttle the network and CPU to see loading states, a second click while a request is pending and responses that arrive out of order (on a fast local machine they are otherwise never seen); offline and back online; the session expiring in the middle of a flow (refresh, then the redirect to login); the same page open in two tabs.
- **States:** loading, empty, error, permission/role variants from the brief.
- **Language and format:** long text in the product's languages (Vietnamese with diacritics, Japanese without spaces), dates, numbers and currency in the product's format, and times in the user's timezone against the server's.
- **Layout:** the breakpoints in PROJECT.md (default 375, 768, 1440); keyboard only; accessible names on inputs and icon buttons. Automation alone never proves "accessible".
- **Browsers and devices:** resizing a desktop browser checks layout only. Report the browsers and devices actually run; any in PROJECT.md's supported list that were not run are "not run", never pass.
- **Design:** compare with the design frame when available. No baseline means INCONCLUSIVE, not pass.
- Check the request payloads in the network tab for every mutation the change touches.

### API / backend
- Run the service locally against a local database, container or mock.
- Call each changed endpoint with valid input, invalid input, missing or expired auth (401), the wrong role (403), a missing resource and another user's resource (change the ID in the path or body: expect 403 or 404, never the data); check status codes, the response against the spec's schema, and error codes.
- **Idempotency:** send each changed request that writes data twice, and once more as a retry after a timeout: a create must not duplicate, and a payment or status change must not run twice.
- Check the side effects in the local database (rows written, nothing extra), and that a migration applies and rolls back on a local database.
- Logs: no stack traces for expected errors, no personal data or secrets.

### Mobile
Simulator or emulator: the web UI interaction and state checks, plus small and large screens, rotation when supported, background and resume, offline, and permission prompts denied.

### CLI / library / worker
Run with sample inputs, including empty, invalid and large ones; check exit codes, stdout and stderr; for a library, call the changed public API the way a consumer would; for a job, run it twice to check that a retry does no harm.

## 7. Verdict
The runtime verdict (SHIP / SHIP WITH FIXES / DO NOT SHIP / INCONCLUSIVE) judges step 6 alone. The overall verdict follows these rules and the runtime verdict never overrides them:
- **NOT READY:** any check in steps 1–3 is red; a Required AC is FAIL, BLOCKED or NOT VERIFIED; a regression row fails; the runtime verdict is DO NOT SHIP, or INCONCLUSIVE on a Required AC.
- **READY WITH GAPS:** nothing above, but the report lists gaps: Derived ACs, a missing plan or command, Important or Optional ACs not PASS, regression rows not run, supported browsers or devices not run, or SHIP WITH FIXES whose fixes touch no Required AC.
- **READY:** every Required AC is PASS with evidence and none is Derived, steps 1–3 are green, every regression row picked passed, the runtime verdict is SHIP, and the Gaps section is empty.

List what could not be verified and why (no account, no data, needs a shared mutation) in Gaps.

## Re-run after a fix
Run steps 1–3 again in full (a fix can break the build or leave debug output), then the ACs that were FAIL, BLOCKED or NOT VERIFIED, then the regression targets of the files the fix touched. Add a dated "Re-run" section to the report instead of overwriting the first run, and recompute the verdict.
