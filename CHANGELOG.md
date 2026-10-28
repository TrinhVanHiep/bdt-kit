# Changelog

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
