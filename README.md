# bdt-kit

A Claude Code kit for one person who is BA, developer and tester on client projects.
- **Ticket to code:** it takes a ticket from "what does this mean" to a verified PR, with two approval gates.
- **Documents:** it produces BA documents (business scenarios, test cases, user guides, question lists) in your own template.
- **Any stack:** it learns each project's coding conventions and technologies from your documents and the code, then plans, codes, verifies and reviews by them.
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

1. Clone the kit:

```bash
git clone https://github.com/TrinhVanHiep/bdt-kit.git ~/bdt-kit
```

2. Optional: preview the changes. `--dry-run` only prints what would happen. It installs nothing, so skills are **not** available after this step.

```bash
~/bdt-kit/install.sh --dry-run
```

3. Install. This is the step that makes the skills available:

```bash
~/bdt-kit/install.sh
```

4. Check that the skills are linked. Each line should point into `~/bdt-kit/skills/`:

```bash
ls -l ~/.claude/skills
```

5. Start a **new** Claude Code session (CLI, desktop app or IDE). Skills load at session start, so a session that was already open does not see them.

The installer:
- symlinks `skills/*` into `~/.claude/skills/` and `agents/*` into `~/.claude/agents/`;
- writes the kernel between `<!-- bdt-kit:start -->` and `<!-- bdt-kit:end -->` in `~/.claude/CLAUDE.md`, keeping the rest of the file and writing a `.bak` copy;
- never overwrites a skill or agent you own with the same name.

Options:
- Add `--with-hooks` to also add the hooks (see `extras/hooks/README.md`).
- Remove everything with `install.sh --uninstall`.
- Update with `git -C ~/bdt-kit pull`, then run `install.sh` again.

Requirements: Claude Code, `git`, `python3` (3.8+, standard library only), and `node` (only for the hooks). Check the document tools with this command:

```bash
python3 ~/bdt-kit/skills/bdt-flow/tools/selftest.py
```

## Use

There is no separate command:
- **Slash command:** type the skill name, for example `/bdt-flow ABC-12`, `/dev-profile`, `/qa-verify`. Type `/` to see the list.
- **Plain words:** say what you want ("làm task ABC-12", "đây là coding convention của dự án", "review PR này"), and Claude loads the skill whose description matches.
- **Plugin install:** if you installed the kit as a plugin instead of with `install.sh`, the names carry the plugin prefix, for example `/bdt-kit:bdt-flow`.

### First time in a repo
Open Claude Code in your **project** folder, not in `~/bdt-kit`.
1. `/project-onboard` writes `.bdt/PROJECT.md` (links, commands, report language) and asks for what it cannot find in the repo. Give it the project's coding convention documents: it runs `dev-profile` to build `.bdt/dev/` (stack and conventions).
2. `/bdt-flow <ticket ID or link>` runs the chain: brief → questions → plan. It stops for your approval of the plan, then builds, verifies and reviews, and stops again before any commit, PR or ticket comment.

### Common calls

| You want | Type |
| -------- | ---- |
| Deliver a ticket end to end | `/bdt-flow ABC-12` |
| Only understand a ticket (ACs, open questions) | `/ticket-brief <ticket link>` |
| Set up or update a project's stack and coding conventions | `/dev-profile` and attach or link the convention document |
| Business scenarios or test cases | `/ba-scenarios <feature>` and attach your sample sheet |
| A user guide | `/ba-user-guide <role and features>` |
| Any document in your company's format | `/doc-from-template` and attach the sample |
| Check a change before a PR | `/qa-verify` |
| Review a PR | `/pr-review <PR link>` |
| Check that the kit is installed | `/kit-setup` |

### A skill does not show up
1. The kit was cloned but `install.sh` was not run. A clone alone installs nothing. `install.sh --dry-run` installs nothing either: it only prints what it would do.
2. The session was started before the install. Open a new session.
3. After `git pull`, `install.sh` was not run again, so new skills have no link yet.
4. The clone was moved or deleted after the install, so the links are broken. Run `install.sh` again from the new place.
5. A folder with the same name already exists in `~/.claude/skills/`, so the installer printed `skip …` and left it alone.
6. The chat is on claude.ai instead of Claude Code (CLI, desktop Code tab or IDE extension). Local skills only load in Claude Code.
7. On Windows, the links may not have been created. Check that the entries in `~/.claude/skills/` point to the kit.

Check the links with this command:

```bash
ls -la ~/.claude/skills ~/.claude/agents | grep bdt-kit
```

## Skills: input → output

| Skill | Input | Output |
| ----- | ----- | ------ |
| `bdt-flow` | a ticket, or a request for a BA document | runs the chain below and keeps every artefact in `.bdt/work/<id>/` |
| `project-onboard` | a repo + links it cannot tell + your sample documents | `.bdt/PROJECT.md`, `dev/` (via `dev-profile`), `CONTEXT.md` (glossary), `TESTS.md` (registry), `templates/` |
| `dev-profile` | coding convention and architecture documents (md, docx, pdf, Google Doc, wiki), lint/CI config, the repo | `.bdt/dev/`: `STACK.md` (versions, app types, architecture), `CONVENTIONS.md` (CONV rules with source, golden files and a check), stack packs |
| `ticket-brief` | ticket (+ parent, comments, attachments), requirements, design, API spec, code | `brief.md`: AC-NNN, facts vs constraints vs assumptions, edge cases, READY / BLOCKED |
| `ask-questions` | open points with evidence | `questions.md` by owner + paste-ready messages in your team's tone |
| `ba-scenarios` | the same sources as a brief | business scenarios (flows A/E, BR-xxx, data rules) + test cases, in your template |
| `ba-user-guide` | role, features, environment, sample | user guide with steps, exact labels, screenshots, FAQ, troubleshooting |
| `doc-from-template` | a sample file (.docx, .xlsx, .csv, .md, Google Doc/Sheet) + content | the document in the sample's format, plus a mapping note and checks |
| `dev-plan` | approved brief, repo, dev profile | `plan.md`: impact with grep evidence, conventions that apply, patterns to mirror, tasks — **you approve** |
| `dev-implement` | approved plan | the change, deviations logged, stop rules on errors |
| `qa-verify` | the change, ACs, environment | `report.md` READY / NOT READY: convention checks, runtime QA by app type (browser at 375 / 768 / 1440, API calls, simulator, CLI runs) |
| `qa-click-path` | a page and a symptom | traced handler findings (`CLICK-PATH-NNN`) |
| `pr-review` | a PR or a diff | findings with proof + comment drafts (posted only on request) |
| `council` | a decision with options | recommendation with the strongest dissent |
| `lesson-eval` | a fixed bug or review defect | Save / Improve / Absorb / Drop into the lessons file |
| `kit-audit` | a session, branch or document | PASS / FAIL table against project rules and the kernel, with fixes |
| `kit-setup` | this kit, `~/.claude` | install check, kernel update, optional hooks |

Read-only agents: `bdt-code-reviewer`, `bdt-stack-reviewer` (project conventions and any stack pack), `bdt-react-reviewer`, `bdt-silent-failure-hunter`, `bdt-spec-miner`.

## Your stack and conventions

The dev steps hold no stack of their own. Each project gets a dev profile built from its own inputs:
1. Give `dev-profile` the coding convention and architecture documents (a file, a link, a wiki page) or just name the stack. It also reads the lint, formatter and CI config, and the manifests and lockfiles.
2. It writes `.bdt/dev/STACK.md` (installed versions, app types, architecture with golden files) and `.bdt/dev/CONVENTIONS.md`. Each rule there has an ID (`CONV-NAME-003`), a source, golden files, the violation count today and a check (lint rule, grep or review question).
3. Rules only seen in the code are `observed`, and places where the document and the code disagree are `conflict`. Both go to you as questions; the kit never picks a standard on its own.
4. `dev-plan` lists the rules that apply to each task. `dev-implement` follows them. `qa-verify` runs their checks and tests the change the way its app type needs (web UI, API, mobile, CLI). `pr-review` walks them with `bdt-stack-reviewer`.

**Stack packs** hold what is true for a technology in every project: plan gotchas, debug leftovers, forbidden ways to silence a check, verify cases, review checklist and security. The kit ships `react-next` and a template (`skills/dev-profile/stacks/`). For any other stack, `dev-profile` drafts a pack in the project (`.bdt/dev/stacks/`) from that project's inputs and the official docs for the installed version. A pack used on two or more projects can be promoted into the kit, so the kit grows with real projects.

The profile is local. When the team wants to share it, `dev-profile` can export it as a project skill in `.claude/skills/`, as a change you review and commit.

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

Defaults when you have no sample: `skills/bdt-flow/templates/` (brief, questions, plan, report, scenarios, test-cases.csv, user-guide, CONTEXT, TESTS, PROJECT, STACK, CONVENTIONS).

## Per project
Put project facts and overrides in `.bdt/PROJECT.md`, the stack and coding conventions in `.bdt/dev/` (`dev-profile`), and project playbooks in that repo's `.claude/skills/`. Change the kit only for lessons that hold across projects (`lesson-eval` → Promote). `.bdt/` is listed in `.git/info/exclude`, so it is never committed.

## Safety defaults
- Ticket, web, document and PR text is treated as data, never as instructions.
- No mutating requests to shared environments to verify work. Screenshots come from a local mock or a test environment you name, with fake data.
- Nothing is posted, pushed, uploaded or committed without your approval.
- No telemetry, no background processes. Hooks are opt-in, have ids and off switches, and never loop.

## License
MIT, see `LICENSE`.
