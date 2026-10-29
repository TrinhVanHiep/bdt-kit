---
name: qa-run
description: Execute test cases on an environment the user names — a test-case sheet (.xlsx/.csv), the cases from ba-scenarios, or regression rows of .bdt/TESTS.md — recording Pass / Fail / Blocked / Not run with evidence for each case, writing the results into a copy of the sheet, drafting a bug for each failure, retesting fixed bugs, and ending with a test summary. Use when the user says "chạy test case", "test theo sheet này", "retest bug", "chạy regression", "smoke test bản build mới", or asks for a test run report.
---

# qa-run

**Input:** the test cases (a sheet, a Google Sheet exported to .xlsx, the cases from `ba-scenarios`, or rows of `.bdt/TESTS.md`), the environment and build the user names, test accounts by role (the user signs in), the test data.
**Output:** a result with evidence for every case in scope, written into a copy of the sheet; a bug draft per failure (`qa-bug-report`); `summary.md`; updated rows in `.bdt/TESTS.md`.

Templates: `../bdt-flow/templates/test-summary.md`, `../bdt-flow/templates/bug.md`. Work folder: `.bdt/work/<ticket, feature or release>/run-<YYYYMMDD>/` (`results.json`, `evidence/`, `summary.md`); bugs go in `.bdt/work/<id>/bugs/`.

Modes: **run** (a set of cases), **retest** (bugs marked fixed), **regression** (registry rows or a regression sheet).

## 0. Before the first case
- **Scope:** the case IDs, sections or priorities to run. Write it down: it is the denominator of the summary.
- **Environment:** URL, build or commit, browser and device actually used. A result without its build is not evidence.
- **Accounts:** one per role and status the cases need. The user signs in; the kit never types a password (`../bdt-flow/references/inputs.md`).
- **Test data:** check that the data each case needs exists. A case whose data is missing is Blocked, not improvised.
- **The sheet:** `python3 ../bdt-flow/tools/docfill.py inspect <sheet>` for the column names (a two-row header gives names like `PC / Lần 1`), `text` for the cases. Read the sheet's own result words (dropdown, legend, the criteria in its count formulas, for example OK / NG / Pending) and map Pass / Fail / Blocked / Not run to them; ask when they are unclear.
- **Cases that change data:** list the cases that create, change or delete data. On a local server or mock, run them. On a shared environment (dev, staging), ask once for this run, showing the list, the environment and the accounts. Without a yes they are Blocked ("needs a shared mutation") or run against a local mock. Never on production.

## 1. Run each case
- Follow the steps as written, in order, with the case's test data. A step that is unclear or does not match the screen makes the case Blocked with a question (`ask-questions`), never a guess.
- Compare labels and messages with the expected result word for word.
- Evidence for each case in `evidence/<CASE-ID>.png`: the final state; for a change of data, the request body and the response (no tokens, no personal data); console errors. For a Fail, also the failing step.
- Web UI, API, mobile and CLI cases use the recipes in `../qa-verify/SKILL.md` (Runtime QA), on the environment named in step 0.
- When the environment goes down, or a bug makes the rest of a section pointless, stop that section, mark its cases Blocked with the reason and tell the user.

| Status | When |
| ------ | ---- |
| Pass | The expected result was seen and the evidence is saved |
| Fail | The result differs from the expected result: a bug |
| Blocked | Could not run: environment, data, a blocking bug, an unclear step, a change of data not approved |
| Not run | Out of scope or out of time |

- Never Pass a case that was not run, or on evidence from another build.
- Platform columns (PC / Tablet / iOS / Android, or breakpoints): fill only the platforms actually run. Desktop Chrome resized to 375 is a layout check, not iOS or Android; those columns stay Not run unless a simulator or device was used, and the note says which.
- A pass against a local mock proves the UI handles that response, not that the backend sends it: write "mock" in the note.

## Failures become bugs
Each Fail goes to `qa-bug-report`. Failures with the same cause share one bug, and each case carries its ID in the Bug ID column. A Fail whose expected result has no source (AC, BR, design frame, API spec) is a question, not a bug.

## 2. Write the results back
1. Write `results.json`: `{"sheet": "<name>", "id_column": "<ID column>", "rows": [{"<ID column>": "TC-001", "<result column>": "OK", "<tested on column>": "Chrome 130 / 1440", "<date column>": "<date>", "<bug column>": "BUG-…"}]}`, with the sheet's own column names and result words.
2. Run `python3 ../bdt-flow/tools/docfill.py results <sheet> results.json <sheet name>-results-<YYYYMMDD>.xlsx`. It writes a copy and never overwrites the user's file. Only the named cells change; styles, dropdowns and formulas stay, and the counts recalculate when the file is opened.
3. A Google Sheet: export it to .xlsx and write the copy. Writing into the Google Sheet itself (Sheets connector) is a separate step the user approves.
4. Show the user the rows updated, the counts and the file path.

## Retest
- Input: bug IDs or tracker links, and the build that carries the fix.
- Re-run the bug's steps on that build, then the test cases linked to it, then the cases of the same screen or section (a fix can break its neighbours).
- Result: **verified**, or **reopened** with what still fails and new evidence. Add a line to the bug's Retest log, draft the tracker comment in the team's tone (posted only on request), and update the sheet with `results`.

## Regression
- Input: rows of `.bdt/TESTS.md` (by area or tag), or a regression sheet.
- Record results as in a run. Update each row's Evidence (date) in `TESTS.md`; a row that was not run keeps its old date and is listed in the summary.

## 3. Summary
Write `summary.md` from `test-summary.md`: counts from the results, bugs, Blocked and Not run with reasons, risks, and a recommendation. Recommend GO only when every case in scope was run and no Critical or Major bug in scope is open; the team's own release criteria win, and the decision is theirs.

## Rules
- Test data and test accounts only; no real personal data in inputs, screenshots or reports.
- Nothing is posted to the tracker, a chat or a shared sheet without the user's go-ahead.
