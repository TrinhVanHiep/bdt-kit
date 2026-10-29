# Changelog

## 0.5.2 (2026-10-29)
`ask-questions` after a review:
- Question lifecycle: IDs `Q-01…` shared by questions.md, the brief, CONTEXT.md and scenarios; status Open / Answered / Default applied / Obsolete; answers matched by ID and carried into the brief (`[revised rN]`), CONTEXT.md, scenarios, test cases and anything already built on the default.
- Defaults: a non-blocking question goes on with its default as an assumption; a blocking one never does; client-owned values stay placeholders. A non-blocking question past its needed-by date becomes Default applied. Test-case Expected follows the decision or the default in force; open points go in Note with the Q-ID, never "cần xác nhận" in Expected.
- Conflicts between sources or owners: one question to the decision owner ("Decides conflicts" in PROJECT.md; default BA for rules and copy, PO for scope) with both sides and their versions.
- Owners PO/PM and third parties; needed-by dates; document versions and the places checked in Evidence; neutral wording; blocking first and at most 10 questions per message; personal data masked in screenshots.
- Fallbacks without a ticket (branch name), PROJECT.md (user's language, numbered, no greeting) or template (columns defined in the skill). questions.md becomes one table with an Owner column plus per-owner messages; PROJECT.md and project-onboard ask for PO/PM, third parties and the decision owner.

## 0.5.1 (2026-10-29)
`qa-verify` after a tester's review:
- Step 0 Inputs: no ticket → branch name; no brief → ACs derived from the diff, marked `Derived`, verdict at best READY WITH GAPS; no plan → step 3 skipped as a gap; no PROJECT.md → commands from the project rules and manifest scripts.
- Verdicts: READY / READY WITH GAPS / NOT READY with explicit rules; the runtime verdict never overrides them (DO NOT SHIP, or INCONCLUSIVE on a Required AC, means NOT READY).
- AC status PASS / FAIL / BLOCKED / NOT VERIFIED with the brief's priority and an evidence format; personal data and tokens masked in screenshots and logs.
- A red step 1 gives NOT READY at once; steps 2–3 still run so every static problem is reported together; runtime steps are marked not run.
- Step 2: secret patterns for any stack, the stack pack's debug and unsafe-code patterns, new dependencies and lockfile changes.
- Regression finds the features that share the changed code by grepping the importers of changed components, API functions, stores, hooks, types and constants, with or without a plan.
- Runtime: cases that change data are BLOCKED without a local mock or an approved environment, never skipped; offline, session expiry in the middle of a flow, two tabs; Vietnamese and Japanese text, date, number, currency and timezone formats; idempotency of write endpoints.
- The skill verifies only; a Re-run section after a fix. `report.md` gets Inputs, AC priority, Gaps and Re-run; the `react-next` pack gets `innerHTML`, `eval(` and `new Function(`.

## 0.5.0 (2026-10-29)
Testing as a full loop: run the cases, record results with evidence, log bugs, retest, regression, report, automate.
- `qa-run` skill: runs a test-case sheet, `ba-scenarios` output or `TESTS.md` rows on an environment the user names. Pass / Fail / Blocked / Not run with evidence per case; never a Pass for a case not run; platform columns only for platforms actually run (desktop Chrome at 375 is not iOS). Cases that change data on a shared environment need one go-ahead per run. Modes: run, retest, regression, explore (time-boxed charter). Ends with `summary.md`: counts, coverage by requirement, bugs, risks, GO / NO-GO recommendation.
- `qa-bug-report` skill: reproduce twice, reduce the steps, check duplicates, expected result with a source (no source → a question); drafts in the tracker's format and tone, posted only on request.
- `qa-automate` skill: automated tests in the project's own suite only, at the lowest level that catches the failure, mirroring the existing tests, without fixed sleeps or CSS-path selectors, proven to fail without the fix. No suite: proposes one and stops.
- `docfill.py results`: writes results into the existing rows of a filled .xlsx / .csv sheet, matched by ID, into a copy in the same format; styles, dropdowns and formulas kept and recalculated on open. It refuses to write over the input (also under another name on a case-insensitive disk or through a symlink) and refuses a column name the header repeats; `header_rows` forces a two-row header.
- `docfill.py` reads workbook text without furigana (`<rPh>`), so Japanese headers such as 結果 are no longer read as 結果ケッカ (fixed for `text`, `inspect`, `fill` and `results`). `selftest.py`: 28 checks.
- `qa-verify`: a Regression step (`TESTS.md` rows of the touched areas plus smoke rows); throttled network and CPU for loading states and races; another user's record by ID; browsers and devices not run are reported as not run.
- `ba-scenarios`: decision tables and pairwise, state transitions including forbidden ones, date and timezone boundaries, access to another user's record, concurrent edits; a test data plan; test-case quality checks.
- Templates: `bug.md` (default severity and priority scale), `test-summary.md`; `TESTS.md` gets Tags (`smoke`, `regression`); `report.md` gets a Regression table and the browsers run; `scenarios.md` gets transitions, decision tables and test data; `brief.md` edge cases get dates, another user's record, forbidden transitions and concurrent edits; `PROJECT.md` gets supported browsers and devices, test data, test environments and a Testing section (sheet, tracker, severity scale, release criteria), which `project-onboard` asks for.
- `bdt-flow`: a Testing table; a bug fix in a repo with a test suite gets a regression test through `qa-automate`.
- Evals: testing prompts and behaviour checks.

## 0.4.0 (2026-10-29)
The dev steps no longer assume a stack. Each project gets a dev profile built from its own inputs.
- `dev-profile` skill: reads coding convention and architecture documents (md, docx, pdf, Google Doc, wiki), lint/formatter/CI config, manifests and lockfiles. It writes `.bdt/dev/STACK.md` (installed versions, app types, architecture with golden files) and `.bdt/dev/CONVENTIONS.md`: CONV rules, each with a source, golden files, today's violation count and a check. Rule status is `confirmed` / `observed` / `conflict` / `legacy` / `retired`. It also has an update mode and an optional export as a project skill (asks first).
- Stack packs in `skills/dev-profile/stacks/`: `_template.md` and `react-next.md` (moved from the React content of 0.1–0.3). Stacks without a kit pack get a project pack drafted from the project's inputs and the docs for the installed version; promotion into the kit after two projects.
- `bdt-stack-reviewer` agent: walks the CONV rules a diff touches and any pack's review checklist; `observed` and `conflict` rules become questions, not findings.
- `dev-plan`: conventions that apply per task (CONV ids), gotchas from the pack. `dev-implement`: follows the CONV rules, with debug and check-silencing patterns from the pack. `qa-verify`: CONV checks, runtime QA by app type (web UI, API/backend, mobile, CLI/library/worker). `pr-review`: stack and conventions lanes driven by the profile.
- `project-onboard` reads manifests of every ecosystem and builds the profile through `dev-profile`. `lesson-eval` absorbs lessons as CONV rules and promotes stack lessons into packs. `kit-audit` walks the CONV rules.
- Templates: `STACK.md`, `CONVENTIONS.md`; PROJECT.md gets convention links, the dev profile and more commands; plan and report get conventions and runtime QA sections.
- Kernel: `.bdt/dev/` is read before the first code edit.
- README: how to call the skills and what to check when a skill does not show up.
- Trial on a sample FastAPI API, a stack the kit had no pack for:
  - `dev-profile` found every planted violation and marked the patterns seen only in the code `observed`. It dropped the prose section and drafted FastAPI and SQLAlchemy packs with a source on each line.
  - `bdt-stack-reviewer` found every planted defect in a new endpoint, including a SQL injection caught through the pack's security section, and raised the `observed` rules as questions.
  - What the trial sharpened: the conflict vs violation threshold, inferred MUST/SHOULD, pack granularity, vendors with docs only for the latest version, a missing PROJECT.md, the questions file, a severity scale, and companion changes outside the diff.

## 0.3.0 (2026-10-28)
- BA deliverables with clear input and output: `ba-scenarios` (business scenarios + test cases), `ba-user-guide` (guides with screenshots), `doc-from-template` (any output in the user's sample format).
- `tools/docfill.py` (standard library only): text / inspect / fill / build / check for .docx, .xlsx, .csv, .md. Tested on a real company test-case workbook (two-row merged header, label fields, group rows, COUNTIF formulas) and a real user guide without heading styles (prototype build with screenshots). `tools/selftest.py`: 18 checks.
- `fill` for workbooks: `keep_sheets` / `rename_sheets` (use one sheet of a company workbook as the model), row heights fitted to the text; the output keeps no text, image or title from the sample (shared strings, media and relationships pruned; core properties cleaned); test added.
- Trial on a real project (an admin video screen): scenarios, 15 test cases in a company test-case workbook, a user guide rebuilt in a company guide format with 3 screenshots from a local mock.
- guard-bash: patterns stay within one command line (a later line with `~/` no longer triggers a false block).
- Default templates: scenarios.md, test-cases.csv, user-guide.md; `references/inputs.md` (how to read each source).
- Input / Output line in every skill; README table.
- From ECC: hooks `compact-save` + `compact-restore` (progress survives a context compaction), `rule-check` (periodic self-audit reminder) and `stop-check` (debug leftovers; lesson reminder on fix branches); `kit-audit` skill for the full audit; `install.sh --with-hooks` with a safe settings merge and uninstall.

## 0.2.0 (2026-10-28)
Lessons from the first trial (a subscription story whose sub-task had no description):
- ticket-brief: read the parent story and the FE/BE sibling tickets when the description is empty; open image attachments; read the design brief's screen table and check screen IDs across documents; read every environment's API spec; API readiness check; consistency scan for business values shown on several screens; source table and BLOCKED status in the hand-off.
- bdt-flow: "When the ticket is blocked" section (deliver the brief, the questions and the safe parallel work, then ask).
- PROJECT.md template: design brief and ticket structure fields.
- Design file fallback: open it in the browser when the design connector is not authorised.

## 0.1.0 (2026-10-28)
- First version: kernel, 12 skills (bdt-flow chain, ticket-brief, ask-questions, project-onboard, dev-plan, dev-implement, qa-verify, qa-click-path, pr-review, council, lesson-eval, kit-setup), 4 read-only agents, templates, opt-in guard hook, symlink installer and plugin manifest.
