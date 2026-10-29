---
name: project-onboard
description: First session in a repo — map the architecture, record links and commands in .bdt/PROJECT.md, build the dev profile (stack and coding conventions, via dev-profile), start the domain glossary (CONTEXT.md) and the verification registry (TESTS.md). Use when entering a new or inherited project, when .bdt/PROJECT.md is missing, or when the user asks to "onboard", "đọc hiểu repo", or set up the kit for a project.
---

# project-onboard

**Input:** a repo; links the repo cannot tell (ticket system, docs, design, API, environments, tone); the project's coding convention and architecture documents; optional sample documents.
**Output:** `.bdt/PROJECT.md`, `.bdt/dev/` (from `dev-profile`), `.bdt/CONTEXT.md`, `.bdt/TESTS.md`, `.bdt/templates/` with registered samples, an architecture summary.

Templates: `../bdt-flow/templates/` (`PROJECT.md`, `CONTEXT.md`, `TESTS.md`). Read-only until step 5.

## 1. Recon (read, do not change)
- Manifests, lockfiles and scripts of every ecosystem in the repo (`package.json`, `composer.json`, `pom.xml`, `build.gradle`, `go.mod`, `pyproject.toml`, `pubspec.yaml`, `*.csproj`, `Gemfile`, `Makefile`, …), CI workflows, git hooks → the real install / run / lint / format / typecheck / build / test commands.
- Project rules: `AGENTS.md`, `CLAUDE.md`, `README` (trust code over a stale README), `.claude/skills/*`, lint and formatter config, commit rules.
- Structure: entry points, routing, data layer, auth, i18n, styling tokens, shared UI primitives; for a backend, modules, handlers, services, data access, migrations and jobs.
- Git: default branch, PR target branch, branch naming, recent commit style.

## 2. Stack and conventions: run `dev-profile`
Ask for the project's coding convention and architecture documents, then run `dev-profile`. It writes `.bdt/dev/STACK.md` and `.bdt/dev/CONVENTIONS.md`: each rule with its source, 2+ golden files and a check, and every place where the code disagrees with itself or with the documents listed as a question. Do not pick a standard.

## 3. Overrides
Write down project rules that contradict common kit defaults (for example "no test suite", "tokens in localStorage on purpose", "no middleware on purpose"). Kit skills read this section and step aside.

## 4. Ask the user only for what the repo cannot tell
Ticket system URL, requirements doc, design file, API docs URL, coding convention and architecture documents, shared environments, report language, comment tone, owners. For testing: supported browsers and devices, the test-case sheet and its result words, the bug tracker and its required fields, the severity scale and the release criteria (each one may be "none yet").

## 5. Write (after showing the user a summary)
- `.bdt/PROJECT.md` from the template.
- `.bdt/dev/` (step 7 of `dev-profile`).
- `.bdt/CONTEXT.md` with the business terms found so far (Needs confirmation for unknowns).
- `.bdt/TESTS.md` empty registry.
- `.bdt/templates/`: ask for the team's or client's sample documents (scenarios, test cases, user guide, report). Save each as `<kind>.<ext>` and record mode and conventions in `.bdt/templates/README.md` (see `doc-from-template`).
- Add `.bdt/` to `.git/info/exclude` (local only, never to the shared `.gitignore` without asking).

Do not write or rewrite the project's `CLAUDE.md`/`AGENTS.md`. If they are missing, offer a draft as a separate file for the user to review.

## 6. Report
Architecture in 6–10 bullets, stack and app types, commands, overrides, convention counts by status with the conflicts, golden files, open questions.
