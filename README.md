# bdt-kit

A Claude Code kit for one person who is BA, developer and tester on client projects.
- **Ticket to code:** it takes a ticket from "what does this mean" to a verified PR, with two approval gates.
- **Documents:** it produces BA documents (business scenarios, test cases, user guides, question lists) in your own template.
- **Learning:** it keeps what it learns.

It borrows the best ideas of [ECC](https://github.com/affaan-m/ECC) without its runtime:
- acceptance-criteria briefs and grounded plans;
- evidence-based review and verification reports;
- click-path audits and council decisions;
- lesson triage;
- the compaction, rule-check and lesson hooks.

There are no background agents and no auto-install, and hooks are only added on request.

**Project rules always win.** The kit reads `AGENTS.md`, `CLAUDE.md` and `.claude/skills/*` first, and steps aside where they say otherwise.

## Install

```bash
git clone https://github.com/TrinhVanHiep/bdt-kit.git ~/bdt-kit
```

```bash
~/bdt-kit/install.sh --dry-run
```

```bash
~/bdt-kit/install.sh
```

The installer:
- symlinks `skills/*` into `~/.claude/skills/` and `agents/*` into `~/.claude/agents/`;
- writes the kernel between `<!-- bdt-kit:start -->` and `<!-- bdt-kit:end -->` in `~/.claude/CLAUDE.md`, keeping the rest of the file and writing a `.bak` copy;
- never overwrites a skill or agent you own with the same name.

Options:
- Add `--with-hooks` to also add the hooks (see `extras/hooks/README.md`).
- Remove everything with `install.sh --uninstall`.
- Update with `git -C ~/bdt-kit pull`, then run `install.sh` again.

Start a new session after installing, because skills load at session start.

Requirements: Claude Code, `git`, `python3` (3.8+, standard library only), and `node` (only for the hooks). Check the document tools with this command:

```bash
python3 ~/bdt-kit/skills/bdt-flow/tools/selftest.py
```

## Skills: input → output

| Skill | Input | Output |
| ----- | ----- | ------ |
| `bdt-flow` | a ticket, or a request for a BA document | runs the chain below and keeps every artefact in `.bdt/work/<id>/` |
| `project-onboard` | a repo + links it cannot tell + your sample documents | `.bdt/PROJECT.md`, `CONTEXT.md` (glossary), `TESTS.md` (registry), `templates/` |
| `ticket-brief` | ticket (+ parent, comments, attachments), requirements, design, API spec, code | `brief.md`: AC-NNN, facts vs constraints vs assumptions, edge cases, READY / BLOCKED |
| `ask-questions` | open points with evidence | `questions.md` by owner + paste-ready messages in your team's tone |
| `ba-scenarios` | the same sources as a brief | business scenarios (flows A/E, BR-xxx, data rules) + test cases, in your template |
| `ba-user-guide` | role, features, environment, sample | user guide with steps, exact labels, screenshots, FAQ, troubleshooting |
| `doc-from-template` | a sample file (.docx, .xlsx, .csv, .md, Google Doc/Sheet) + content | the document in the sample's format, plus a mapping note and checks |
| `dev-plan` | approved brief, repo | `plan.md`: impact with grep evidence, patterns to mirror, tasks — **you approve** |
| `dev-implement` | approved plan | the change, deviations logged, stop rules on errors |
| `qa-verify` | the change, ACs, environment | `report.md` READY / NOT READY, browser QA at 375 / 768 / 1440 |
| `qa-click-path` | a page and a symptom | traced handler findings (`CLICK-PATH-NNN`) |
| `pr-review` | a PR or a diff | findings with proof + comment drafts (posted only on request) |
| `council` | a decision with options | recommendation with the strongest dissent |
| `lesson-eval` | a fixed bug or review defect | Save / Improve / Absorb / Drop into the lessons file |
| `kit-audit` | a session, branch or document | PASS / FAIL table against project rules and the kernel, with fixes |
| `kit-setup` | this kit, `~/.claude` | install check, kernel update, optional hooks |

Read-only agents: `bdt-code-reviewer`, `bdt-react-reviewer`, `bdt-silent-failure-hunter`, `bdt-spec-miner`.

## Your templates

Give a sample and say what you want, for example "làm test case theo file này" or "viết hướng dẫn sử dụng giống tài liệu cũ". `doc-from-template` then:
1. inspects the sample;
2. maps the content to its sections or columns;
3. fills it in or rebuilds it;
4. checks the result.

Save project samples as `.bdt/templates/<kind>.<ext>` so they are found next time.

`skills/bdt-flow/tools/docfill.py` has five commands:
- `text`: read .docx / .xlsx as plain text;
- `inspect`: headings, blocks, tables and placeholders; for workbooks, sheets, header rows (two-row merged headers become `PC / Lần 1`) and the labels above them;
- `fill`: `{{key}}`, repeated rows `{{list.field}}`, repeated paragraphs `{{list[]}}`; for workbooks, `fields` by label, `rows` by column name, `_section` group rows and `clear_existing`. Formulas are kept and recalculated on open;
- `build`: a new .docx in the look of a past document. It reuses the sample's paragraphs as prototypes (heading, body, bullet, table, image), keeps its page setup, header and footer, and embeds PNG/JPEG screenshots;
- `check`: placeholders left over.

Defaults when you have no sample: `skills/bdt-flow/templates/` (brief, questions, plan, report, scenarios, test-cases.csv, user-guide, CONTEXT, TESTS, PROJECT).

## Per project
Put project facts and overrides in `.bdt/PROJECT.md` and project playbooks in that repo's `.claude/skills/`. Change the kit only for lessons that hold across projects (`lesson-eval` → Promote). `.bdt/` is listed in `.git/info/exclude`, so it is never committed.

## Safety defaults
- Ticket, web, document and PR text is treated as data, never as instructions.
- No mutating requests to shared environments to verify work. Screenshots come from a local mock or a test environment you name, with fake data.
- Nothing is posted, pushed, uploaded or committed without your approval.
- No telemetry, no background processes. Hooks are opt-in, have ids and off switches, and never loop.

## License
MIT, see `LICENSE`.
