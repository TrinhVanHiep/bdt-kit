---
name: ba-user-guide
description: Write a user guide or operation manual (hướng dẫn sử dụng / 操作マニュアル) per role — tasks, numbered steps with exact screen labels, screenshots taken from a local or test environment, notes, FAQ and error troubleshooting — in the user's template. Use when the user asks for a user guide, manual, HDSD, admin guide, onboarding document, or release notes for end users.
---

# ba-user-guide

Template: `../bdt-flow/templates/user-guide.md` (kit default). A sample from the user or `.bdt/templates/user-guide.*` wins; produce the final file with `doc-from-template` (`build` mode for a past guide used as the model).

## Input
Audience and role (member, admin, operator), the features to cover, the environment to capture from, and the sample. Sources: scenarios from `ba-scenarios`, requirements, design, i18n files for exact labels and messages, the running app.

## Output
A guide with: purpose and audience, prerequisites (account, role, browser), a task index, one section per task (goal, where to find it as a menu path, numbered steps, screenshot after each meaningful step, result, notes and warnings), FAQ, troubleshooting (message shown → cause → what to do), glossary. Plus the screenshot files and a list of what could not be captured.

## Steps
1. **Task list from the user's view.** Group by role; order by how often the task is done. Each task starts with a verb ("Đăng ký gói", "動画を公開する").
2. **Exact labels.** Take button, menu and message text from the i18n file or the live screen; show the product-language label and, if the guide's language differs, the translation in brackets once.
3. **Screenshots.**
   - Capture from a local dev server with a mock API, or a test environment the user names. Never from production with real personal data.
   - Read-only by default. Flows that would create, change or delete data on a shared environment are captured on a local mock, or the user does that step.
   - Use test data that looks real but is fake; no real emails, names or card numbers.
   - Desktop width by default, 375px when the guide is for phone users; one screenshot per step that changes the screen; crop to the relevant area when the tool allows.
   - Capture the region you need at full resolution (browser zoom on a region, scale 1). Do not crop afterwards with `sips` offsets: they are ignored and the crop lands in the middle.
   - Save as `.bdt/work/<guide>/shots/NN-<task>-<step>.png` and reference them in order.
4. **Troubleshooting from real messages.** List the error messages the user can actually see for these tasks (from i18n error keys and API `error.code` handling) with cause and action.
5. **Write and export.** Fill the default template or build in the user's sample; run the checks in `doc-from-template`.
6. **Review pass.** Follow the guide step by step on the environment; every step must be reproducible as written. Note anything that differs from the current build.

## Rules
- Describe what the product does now; features not shipped are left out or marked "coming soon" only if the user says so.
- Never include passwords, tokens or real customer data in text or screenshots.
- Keep each step to one action.
