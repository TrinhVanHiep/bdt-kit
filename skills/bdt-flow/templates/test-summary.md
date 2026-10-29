# Test summary: <ticket, feature or release>

Recommendation: GO | GO WITH CONDITIONS | NO-GO (the team decides; this is the tester's recommendation) · Run: <run-YYYYMMDD> · Date: <date>

## Scope
- Test cases: <!-- sheet and sections or IDs run; what was out of scope and why -->
- Build / commit:
- Environment: <!-- URL; local, dev or staging -->
- Browsers / devices actually run: <!-- only what was run; desktop Chrome at 375 is a layout check, not a device -->
- Not run on: <!-- browsers or devices the project supports that were not run -->

## Results
| Section / flow | Total | Pass | Fail | Blocked | Not run |
| -------------- | ----- | ---- | ---- | ------- | ------- |
| **Total** | | | | | |

Pass rate: <pass> / <run> run (<run> / <total> of the scope executed).

## Coverage by requirement
<!-- From the sheet's scenario / rule column. A requirement with no case, or only Blocked / Not run cases, is a risk below. -->
| Requirement (AC / BR / screen) | Test cases | Result | Bugs |
| ------------------------------ | ---------- | ------ | ---- |

## Bugs
| Bug | Title | Severity | Priority | Status | Test cases |
| --- | ----- | -------- | -------- | ------ | ---------- |

By severity: Critical <n> · Major <n> · Minor <n> · Trivial <n>. Open: <n>.

## Blocked and not run
| Test case | Status | Reason | Owner |
| --------- | ------ | ------ | ----- |
<!-- e.g. Blocked: environment down, missing data, blocked by BUG-…, step unclear (question #), needs a shared mutation the user did not approve -->

## Risks
<!-- What could still fail in production and why: areas not run, open Major bugs, platforms not run, cases that passed only on a mock. -->

## Conditions for GO
<!-- Only when the recommendation is GO WITH CONDITIONS: the bugs to fix or the cases to rerun first. -->
