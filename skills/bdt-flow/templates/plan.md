# Plan: <TICKET-ID> <title>

Brief: ./brief.md (revision N) · Branch: <type>/<slug> from <base>

## Must read first
| File | Why |
| ---- | --- |

## Patterns to mirror
<!-- Real code only, with file:line. Never invent a pattern. -->
- <what> → `path/to/file.ts:42`

## Impact (before coding)
- Code: <!-- importers of each shared thing you touch (grep evidence) -->
- Data and interfaces: <!-- request/response shapes, query params, storage keys, routes, i18n keys -->
- Shared ground touched: <!-- if yes, this is a stop-and-confirm item -->
- Docs and release: <!-- env vars, lessons file, changelog -->
- Unverified: <!-- anything not proven by a grep or read -->

## Not building
-

## Tasks
### T1 <name>
- Action: CREATE | UPDATE | DELETE `path`
- Implement:
- Mirror: `file:line`
- Gotcha:
- Validate: <!-- command or check right after this task -->
- Covers: AC-00x

## Validation
- Static: <!-- lint, typecheck -->
- Build:
- Browser: <!-- pages, breakpoints, states to exercise -->
- Edge cases: <!-- from the brief -->

## Confidence
<!-- 1–10 that someone new to the repo could ship this from the plan alone, and what would raise it. -->
