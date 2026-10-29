---
name: ba-scenarios
description: Write business scenarios (kịch bản nghiệp vụ / 業務シナリオ) and the test cases derived from them — actors, preconditions, main, alternative and exception flows, business rules with sources, data rules, and a test-case table — from requirements, tickets, design, API and the running app, exported in the user's template. Use when the user asks for "kịch bản nghiệp vụ", use cases, test scenarios, test cases, a test sheet, or acceptance tests for a feature.
---

# ba-scenarios

Templates: `../bdt-flow/templates/scenarios.md` and `test-cases.csv` (kit defaults). A project or user sample wins: run `doc-from-template` for the final file.

## Input
Any of: ticket or story (with comments and attachments), requirements doc section, design brief, design frames, API spec, the existing code or running app, meeting notes or chat pasted by the user, a brief from `ticket-brief`. Read sources the way `ticket-brief` does (whole sections, every environment's spec, parent tickets).

## Output
1. **Scenario document** (default `scenarios.md`, or the user's template): per feature —
   - ID and name (`SCN-<AREA>-01`), goal, actors and roles, screen IDs, preconditions, trigger;
   - **main flow**: numbered steps, each "actor does → system shows", with the exact UI label in the product language;
   - **alternative flows** (`A1`, `A2`): branch step, condition, steps, rejoin point;
   - **exception flows** (`E1`, `E2`): condition, system response, the exact message or `error.code`, recovery;
   - **business rules** (`BR-<AREA>-001`): the rule, its source (doc section, ticket, client decision), and whether it is enforced in the frontend, the backend, or both;
   - **data rules**: field, type, required, limits, format, default, source of the value;
   - postconditions; open questions with owner (never invent an answer).
2. **Test cases** (default `test-cases.csv`, or the user's sheet): one row per case with ID, scenario/BR covered, preconditions, steps, test data, expected result, priority, type (positive / negative / boundary / permission / state / transition / date / concurrency), and empty result columns for the tester. Group rows by screen or flow (a `_section` row in workbook templates).
3. **Test data plan**: the accounts each case needs by role and status (where they are defined, never passwords), records in each state the cases use, list sizes (0, 1, exactly one page, one page + 1), long and special text, and how the data is made (seed, fixture, local mock). No real personal data.
4. A coverage line: every BR and every flow has at least one test case; list any that do not and why.

## How to derive the cases
- Main flow → one positive case per role or status that sees a different result.
- Each alternative and exception flow → at least one case.
- Each BR → a case that proves it holds and one that tries to break it.
- Each data rule → boundaries (empty, whitespace only, max length and max + 1, full-width characters, emoji, invalid format, pasted text).
- States from the project glossary (membership status, publication status…) → one case per state that changes what the user sees.
- **Conditions that combine** (role × status × plan…) → a decision table: one case per column that changes the result. When many independent factors combine, cover every pair of values (pairwise) instead of every combination, and say so in the coverage line.
- **State transitions** (order, subscription, approval) → a transition table from the requirements: each allowed transition once, and each forbidden one the UI or the API could still be asked for (for example cancelled → active), expecting a refusal.
- **Dates and times** → end of month, 29 February, year end, the moment of an expiry or deadline (just before, at, just after), the user's timezone against the server's, and the product's date format. Missing rules (which timezone decides?) are questions.
- **Access** → each role on each action; another user's record reached by changing the ID in the URL or the request (expect a refusal, never the data); a signed-out user on a deep link.
- **Concurrency** → two users or two tabs changing the same record. The expected rule (conflict error, last write wins, lock) comes from the requirements; without one it is a question.
- Platform columns in the template (PC / Tablet / iOS / Android, or breakpoints) are left for the tester; do not mark results you did not run. To run the cases and fill the results, use `qa-run`.

## Test-case quality (check every row before handing over)
- One expected result per case, observable on the screen, in the response or in the data. Banned without detail: "correctly", "normally", "as expected", "works".
- Concrete test data (the value, not "a valid email"); steps someone new can run with exact UI labels.
- Cases are independent: a case that needs data from another says so in its preconditions.
- Priority follows the risk: main flows and BRs with money, access or data loss are High.

## Rules
- Business rules come from requirements, tickets or the client. Behaviour read from the code is labelled "current behaviour" and becomes a question when it differs from the documents.
- Exact UI labels and messages come from the product's i18n files or the live screen, not paraphrase.
- Write in the language of the template or `.bdt/PROJECT.md`; keep product labels in the product language.
- Store working files in `.bdt/work/<ticket-or-feature>/`; add the BR and test IDs to `.bdt/TESTS.md` when the cases become regression checks.
