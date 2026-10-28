---
name: project-onboard
description: First session in a repo — map the architecture and conventions, record links and commands in .bdt/PROJECT.md, start the domain glossary (CONTEXT.md) and the verification registry (TESTS.md). Use when entering a new or inherited project, when .bdt/PROJECT.md is missing, or when the user asks to "onboard", "đọc hiểu repo", or set up the kit for a project.
---

# project-onboard

**Input:** a repo; links the repo cannot tell (ticket system, docs, design, API, environments, tone); optional sample documents.
**Output:** `.bdt/PROJECT.md`, `.bdt/CONTEXT.md`, `.bdt/TESTS.md`, `.bdt/templates/` with registered samples, an architecture summary.

Templates: `../bdt-flow/templates/` (`PROJECT.md`, `CONTEXT.md`, `TESTS.md`). Read-only until step 5.

## 1. Recon (read, do not change)
- Manifests and scripts (`package.json`, lockfile, CI workflows, git hooks) → the real lint / typecheck / build / test commands.
- Project rules: `AGENTS.md`, `CLAUDE.md`, `README` (trust code over a stale README), `.claude/skills/*`, lint and formatter config, commit rules.
- Structure: entry points, routing, data layer, auth, i18n, styling tokens, shared UI primitives.
- Git: default branch, PR target branch, branch naming, recent commit style.

## 2. Conventions as evidence
For each convention, cite 2+ files that follow it (golden files). Where the code disagrees with itself, list both and ask which one is the standard. Do not pick.

## 3. Overrides
Write down project rules that contradict common kit defaults (for example "no test suite", "tokens in localStorage on purpose", "no middleware on purpose"). Kit skills read this section and step aside.

## 4. Ask the user only for what the repo cannot tell
Ticket system URL, requirements doc, design file, API docs URL, shared environments, report language, comment tone, owners.

## 5. Write (after showing the user a summary)
- `.bdt/PROJECT.md` from the template.
- `.bdt/CONTEXT.md` with the business terms found so far (Needs confirmation for unknowns).
- `.bdt/TESTS.md` empty registry.
- `.bdt/templates/`: ask for the team's or client's sample documents (scenarios, test cases, user guide, report). Save each as `<kind>.<ext>` and record mode and conventions in `.bdt/templates/README.md` (see `doc-from-template`).
- Add `.bdt/` to `.git/info/exclude` (local only, never to the shared `.gitignore` without asking).

Do not write or rewrite the project's `CLAUDE.md`/`AGENTS.md`. If they are missing, offer a draft as a separate file for the user to review.

## 6. Report
Architecture in 6–10 bullets, commands, overrides, golden files, open questions.
