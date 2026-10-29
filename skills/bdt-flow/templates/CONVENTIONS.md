# Conventions (bdt-kit dev profile)

<!-- Written by dev-profile. One rule per block; IDs are never reused. The project's AGENTS.md / CLAUDE.md / lint config still win: link to them, do not restate them.
Status: confirmed (a document, the project rules or the user) · observed (code only, needs confirmation) · conflict (needs a decision) · legacy (allowed in old code, not in new code) · retired (reason kept).
Last reviewed: <YYYY-MM-DD> -->

Sources: <!-- documents with version and date; project rule files; user decisions with date -->

## Summary
| Area | Confirmed | Observed | Conflict | Legacy | Checked by lint in CI | Checked by grep |
| ---- | --------- | -------- | -------- | ------ | --------------------- | --------------- |

<!-- Areas in this order, only those with rules: Structure (STRUCT) · Naming (NAME) · Code style (STYLE) · Types (TYPE) · State and data flow (STATE) · API and data access (API) · Errors and logging (ERR) · Security (SEC) · i18n and copy (I18N) · Styling and UI (UI) · Tests (TEST) · Performance (PERF) · Git (GIT) -->

## Structure
### CONV-STRUCT-001 <rule in a few words>
- Rule: <one checkable statement> (MUST | SHOULD; add "level inferred" when the wording has neither)
- Applies to: <paths or globs; for legacy, where new code starts>
- Source: <document §section | AGENTS.md:line | user, YYYY-MM-DD>
- Golden files: `path/a`, `path/b`
- Violations today: <count, files> (`<command>`; say when it is grep instead of the project's tool)
- Check: <tool `rule` | grep `pattern` | review question>
- Status: confirmed
- Example: ✅ `<good>` ❌ `<bad>`

## Conflicts and open questions
| Rule | Document says | Code does (evidence) | Proposed default | Owner | Answer (who, date) |
| ---- | ------------- | -------------------- | ---------------- | ----- | ------------------ |

## Lint candidates
<!-- MUST rules caught only by a review question. Proposals: changing lint config is stop-and-confirm. -->

## Dropped from the documents
<!-- prose with nothing checkable, with the section reference, so nothing is lost silently -->
