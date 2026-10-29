# Report: <TICKET-ID> <title>

Verdict: READY | READY WITH GAPS | NOT READY · Plan: ./plan.md · Branch: <branch> · Commit: <sha>
Inputs: <!-- brief revision, or "none: ACs derived" · plan, or "none: step 3 skipped" · commands from PROJECT.md / project rules / manifest -->

## Verification
| Check | Command / method | Result |
| ----- | ---------------- | ------ |
| Lint | | |
| Typecheck | | |
| Build | | |
| Tests | | |
| Conventions | CONV checks from .bdt/dev/CONVENTIONS.md (ids) | |
| Security grep | debug output, secrets, unsafe HTML, unvalidated redirects, stack pack security | |
| Diff review | scope vs plan, leftovers | |

## Acceptance criteria
<!-- Priority from the brief: Required | Important | Optional, plus "Derived" for an AC derived from the diff. Status: PASS | FAIL | BLOCKED | NOT VERIFIED.
Evidence: a screenshot path (evidence/<AC-ID>.png), a log or command excerpt, or a request and response (method, path, body, status, error.code, requestId); personal data and tokens masked. -->
| AC | Priority | Status | Evidence |
| -- | -------- | ------ | -------- |

## Regression
<!-- TESTS.md rows of the areas the change touches, plus smoke rows. "Not run" with a reason is allowed; a silent gap is not. -->
| TEST ID | Why picked | Result | Evidence |
| ------- | ---------- | ------ | -------- |

## Runtime QA
Verdict: SHIP | SHIP WITH FIXES | DO NOT SHIP | INCONCLUSIVE · App type: <!-- web UI | API | mobile | CLI/library | worker -->
Browsers / devices run: <!-- e.g. Chrome 130 desktop --> · Not run: <!-- supported ones from PROJECT.md that were not run -->
<!-- Web UI: one row per page or state at each breakpoint in PROJECT.md. -->
| Page / state | 375 | 768 | 1440 | Console / network | Notes |
| ------------ | --- | --- | ---- | ----------------- | ----- |

<!-- API, mobile, CLI/library, worker: replace the table above with this one. -->
| Case | Call / command / screen | Expected | Seen | Notes |
| ---- | ----------------------- | -------- | ---- | ----- |

## Deviations from the plan
| What changed | Why | AC affected |
| ------------ | --- | ----------- |

## Impact check (after coding)
- Diff beyond declared scope:
- Temporary code left:
- Evidence covers the criteria (not only "the command ran"):

## Gaps
<!-- What this report does not prove: Derived ACs, missing plan or commands, ACs not PASS, regression rows or browsers not run, cases BLOCKED for want of a local mock. Empty only when the verdict is READY. -->

## Open items
| Item | Owner | Blocking |
| ---- | ----- | -------- |

<!-- After a fix: add "## Re-run <date>" with steps 1–3, the ACs that were not PASS, the regression of the touched files, and the new verdict. -->
