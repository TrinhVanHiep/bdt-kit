# BUG-<AREA>-NNN [<screen or area>] <action> → <wrong result>

<!-- One defect per report. A developer should reproduce it on the first try from this page alone. The tracker ID replaces BUG-<AREA>-NNN once the user posts it. -->

Status: draft | posted <tracker ID> | fixed | verified | reopened · Found by: <test case ID, qa-verify, qa-click-path, user> · Date: <date>

## Environment
| Item | Value |
| ---- | ----- |
| URL / app | <!-- environment the user named; local, dev or staging --> |
| Build / commit | <!-- version label, commit sha or deploy time --> |
| Browser / device | <!-- e.g. Chrome 130 desktop at 1440; iPhone 15 iOS 18 Safari. Desktop Chrome at 375 is a layout check, not a device --> |
| Account role | <!-- role and status of the test account; never a password --> |

## Preconditions and test data
<!-- What must be true before step 1: data that exists, settings, feature flags. Test data only, no real personal data. -->

## Steps
1.
2.

## Expected
<!-- What should happen, with its source: AC-NNN, BR-<AREA>-NNN, design frame, API spec. No source means it is a question for ask-questions, not a bug. -->

Source:

## Actual
<!-- What happened, in observable terms: the screen, the message text, the status code. -->

## Evidence
| Kind | Detail |
| ---- | ------ |
| Screenshot / video | <!-- evidence/<CASE-ID or BUG-ID>.png; personal data masked --> |
| Console | <!-- the error line, if any --> |
| Request | <!-- method, path, body without tokens or personal data --> |
| Response | <!-- status, error.code, excerpt, requestId --> |

## Classification
- Reproducible: <!-- e.g. 3/3, or 1/5 with the conditions that seem to matter -->
- Severity: <!-- impact on the user and the business -->
- Priority: <!-- how soon it should be fixed -->
- Regression: <!-- yes (worked in <build>) / no / unknown -->
- Related: <!-- test case IDs, AC IDs, other bugs, PR -->

<!-- Default scales, used only when .bdt/PROJECT.md has none (the project's scale wins):
Severity: Critical (data loss, security hole, a main flow blocked with no workaround) · Major (a feature wrong or blocked, a workaround exists) · Minor (wrong behaviour with little impact, layout or copy that misleads) · Trivial (cosmetic).
Priority: High (fix before release) · Medium (fix in this sprint) · Low (when there is time). Priority is the team's call; the report proposes one. -->

## Retest log
| Date | Build | Result | Evidence |
| ---- | ----- | ------ | -------- |
<!-- verified | reopened (what still fails) -->
