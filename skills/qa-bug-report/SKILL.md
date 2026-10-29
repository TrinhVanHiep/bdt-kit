---
name: qa-bug-report
description: Write a bug report a developer can reproduce on the first try — environment and build, account role, preconditions, numbered steps, expected result with its source versus actual, evidence (screenshot, console, request, response, requestId), reproducibility, severity and priority on the project's scale — drafted in the tracker's format and the team's tone, posted only on request. Use when a test case fails, when the user says "log bug", "viết bug report", "báo lỗi cho dev", or after qa-run, qa-verify or qa-click-path finds a defect.
---

# qa-bug-report

**Input:** a failure (a failed test case, a finding from `qa-verify` or `qa-click-path`, or what the user saw), the environment and build, the requirements behind the expected result.
**Output:** `bugs/BUG-<AREA>-NNN.md` per defect and a paste-ready version in the tracker's format, language and tone from `.bdt/PROJECT.md` (the user posts it, or approves posting).

Template: `../bdt-flow/templates/bug.md`. Write to `.bdt/work/<TICKET-ID or feature>/bugs/`.

## Before writing
- **Reproduce** at least twice on the same build and record the rate (3/3, or 1/5 with the conditions that seem to matter). A bug seen once is reported as such, with everything known about that time.
- **Reduce** the steps to the shortest path that still fails, from a stated starting point.
- **Check for duplicates** in the tracker (read only). A match gets a comment draft with the new evidence, not a new report.
- **Check the expected result has a source:** AC, BR, design frame, API spec or a client decision. Without one it is a question for `ask-questions`, not a bug.
- **Find the layer when the evidence shows it:** the request body is wrong (frontend), the response breaks the spec (backend), the design has no state for it (design). Say which evidence points there; do not guess the code cause.

## Write
Fill `bug.md`:
- Title: `[<screen or area>] <action> → <wrong result>`, specific enough to find it again in a search.
- Environment: URL, build or commit, browser and device, account role (never a password).
- Steps numbered, one action each, with the exact test data and the exact UI labels.
- Expected with its source; Actual in observable terms (screen, message text, status code).
- Evidence: screenshot with personal data masked; console line; request without tokens or personal data; status, `error.code`, response excerpt and `requestId` (as in `ask-questions` for a backend bug).
- Severity is the impact, priority is the urgency; use the scale in `.bdt/PROJECT.md`, else the default in the template. Propose a priority; the team sets it.
- Regression: yes (worked in which build), no, or unknown. Link the test cases, ACs and related bugs.

One defect per report. Two symptoms with one cause are one report that lists both; one symptom with two causes is two reports.

## Hand-off
- Show the user the title, severity, priority and reproducibility of each draft, and the paste-ready text in the tracker's format.
- Post only after the user says so, and only the reports they pick. After posting, the tracker ID replaces `BUG-<AREA>-NNN` in the bug file, and `qa-run` writes it into the sheet's Bug ID column.
- When the bug is marked fixed, `qa-run` retests it.
