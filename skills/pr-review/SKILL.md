---
name: pr-review
description: Review a pull request or your own diff as a tech lead — gate on CI and merge state, review in separate lanes, report only findings with proof, and draft comments in the team's tone. Use when the user shares a PR link or asks "review PR này", "soạn comment review", or before opening your own PR (self mode).
---

# pr-review

**Input:** a PR link or a local diff, the project rules.
**Output:** findings with proof and a verdict, one comment draft per finding in the team's tone (posted only on request).

Report-only. Never push, approve, request changes or post comments without the user's go-ahead.

## 0. Gate
- PR mode: read the PR description, linked ticket, CI status and merge state. If CI is red or the branch conflicts, report that first.
- Run the project's lint / typecheck / build on the branch when it is available locally (worktree or checkout). Red checks are findings.
- Read the project rules, the lessons file and the domain glossary. Project rules decide what is a defect.

## 1. Read whole files, not only hunks
For each changed file read the full file and the callers of anything whose signature or behaviour changed.

## 2. Lanes (review each separately; in large PRs, one subagent per lane)
Agents: `bdt-code-reviewer` (correctness, contract, risk), `bdt-react-reviewer` (framework, UX and a11y), `bdt-silent-failure-hunter` (swallowed errors). Give each the diff range, the project rules and the PR description; verify every finding they return before reporting it.
- **Correctness:** states (loading, error, empty, permission), double submit, races, null fields, error codes vs the API spec, redirects.
- **Contract:** types and payloads match the API spec; enums; nullable fields; removed fields really removed everywhere.
- **Framework:** server/client boundary, effects and cleanup, hydration, keys, conditional rendering, env exposure.
- **Conventions:** the project's own rules (folder placement, naming, i18n, tokens, constants, imports).
- **UX and a11y:** labels, names, keyboard, 375px, copy matches the design.
- **Risk:** auth, tokens, payments, personal data, destructive actions.

## 3. Proof bar (drop anything that fails)
Before reporting a finding answer all four: exact file:line? concrete failure scenario (input → wrong result)? surrounding code read (is it already handled by the caller, a guard, a wrapper)? severity defensible? HIGH and CRITICAL also need the snippet and why existing guards miss it. Zero findings is a valid result.

Common false positives: "add error handling" when the caller handles it; style the formatter owns; a pattern the project rules allow on purpose; speculative performance; asking for tests in a repo without a suite.

## 4. Output
Per finding: `[CRITICAL|HIGH|MEDIUM|LOW] title` · `file:line` · issue · failure scenario · fix. Then a count by severity and a verdict: Approve · Approve with comments · Request changes · Block.

## 5. Comment drafts
One comment per finding, anchored to its line, in the language and tone from `.bdt/PROJECT.md` (for example reviewer "anh", author "em", no greeting, no filler). State the problem, the scenario and a concrete fix. Offer to post them; post only after the user says so, and only the ones they pick.

## Self mode
Same lanes and proof bar on your own diff before Gate 2; fix the findings, list the ones you chose not to fix and why.

## High-risk diffs
For auth, payment, token or release changes, run two independent reviewers (subagents with no shared context, same rubric). Both must pass; fix and re-review up to 3 rounds, then escalate to the user.
