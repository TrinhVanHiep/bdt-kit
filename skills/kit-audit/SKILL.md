---
name: kit-audit
description: Audit recent work against the project rules and the bdt-kit kernel — plan and gates, verification evidence, stop-and-confirm items, shared-environment safety, lessons, code hygiene, deliverable format — and report pass/fail with evidence and fixes. Use periodically (the rule-check hook reminds every N prompts), before handing over a branch or a document, or when the user asks "có làm đúng rule không", "audit lại".
---

# kit-audit

**Input:** the scope to audit (this session, a branch vs its base, a work folder, or a delivered document) and the rules: project `AGENTS.md` / `CLAUDE.md` / `.claude/skills/*`, `.bdt/PROJECT.md` overrides, the kit kernel.
**Output:** a compliance table (rule · verdict PASS / FAIL / N/A · evidence · fix), the fixes applied or proposed, and rule changes worth making.

## Collect evidence (read-only)
- `git log` and `git diff <base>...HEAD` for the branch; `git status` for uncommitted work.
- `.bdt/work/<id>/` files: brief status, questions answered or open, plan approval, report verdicts.
- The lessons file and `.bdt/TESTS.md` changes.
- For a document: the output file (`docfill.py check` and `text`) against its template and mapping note.

## Checks
| Area | PASS when |
| ---- | --------- |
| Plan and gates | multi-step work had a plan the user approved; commit, push, PR, ticket comments and posts were approved |
| Stop and confirm | every shared-ground, risky, scope or business-wording item was asked, with the answer recorded |
| Sources | API matches the spec, UI matches the design, business rules cite requirements; disagreements became questions |
| Verification | every "done" has the command or check that proves it; no mutating calls to shared environments |
| Project rules | each rule in the project file that the diff touches is followed (walk the file, do not sample) |
| Hygiene | no debug output, dead code, unused imports, stray files, commented-out code; formatter run on touched files |
| Lessons | each bug fix or review defect has a lesson verdict; the same pattern was searched elsewhere |
| Deliverables | documents follow the template (sections, columns, IDs, language), no placeholders left, file opens |
| Reporting | the summary said what was not verified and what is still open |

## Report
Lead with the count of FAIL. For each FAIL: rule, evidence (file:line, command output, missing artefact), fix. Fix what is safe to fix now (hygiene, missing lesson entry, report wording); ask before anything that changes behaviour or needs a gate.

## Improve the rules
A rule that failed twice, or was impossible to follow as written, goes to `lesson-eval` → Promote: propose a sharper wording, a lint rule, or a kit change. The user approves every change.
