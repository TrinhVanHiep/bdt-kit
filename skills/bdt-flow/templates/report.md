# Report: <TICKET-ID> <title>

Verdict: READY | NOT READY · Plan: ./plan.md · Branch: <branch> · Commit: <sha>

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
| AC | Evidence | Status |
| -- | -------- | ------ |

## Runtime QA
Verdict: SHIP | SHIP WITH FIXES | DO NOT SHIP | INCONCLUSIVE · App type: <!-- web UI | API | mobile | CLI/library | worker -->
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

## Open items
| Item | Owner | Blocking |
| ---- | ----- | -------- |
