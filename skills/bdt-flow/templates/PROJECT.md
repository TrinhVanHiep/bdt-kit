# Project profile (bdt-kit)

<!-- Written by project-onboard. Local only: .bdt/ is listed in .git/info/exclude. Edit freely. -->

## Links
- Ticket system: <!-- e.g. https://pms.example.com/project-detail/ABC -->
- Requirements (URD/PRD): <!-- doc link or path; note the screen ID scheme, e.g. SC-01… -->
- Design brief / spec doc: <!-- the doc with the screen table and per-screen requirements; it is often newer than the URD -->
- Ticket structure: <!-- e.g. story with FE/BE sub-tasks; where BE posts handoff docs -->
- Design: <!-- Figma file link; note which pages are "ready" -->
- API docs: <!-- Swagger UI and JSON URL; base path -->
- Environments: <!-- dev / staging / prod URLs; which are shared -->
- Repo: <!-- remote, default branch, PR target branch -->
- Coding conventions / architecture: <!-- doc links or paths, with version; dev-profile reads them -->

## Dev profile
- Stack and app types: <!-- one line, e.g. "Laravel 11 API + Next.js 15 web UI"; details in .bdt/dev/STACK.md -->
- Conventions: `.bdt/dev/CONVENTIONS.md` <!-- written by dev-profile; the project's own rule files still win -->

## Commands
- Install:
- Dev server / run:
- Lint:
- Format:
- Typecheck:
- Build:
- Tests: <!-- all, and one file; "none" is a valid answer -->
- Migrations / codegen: <!-- or "none" -->

## Verification
- Breakpoints (web UI): 375, 768, 1440
- Supported browsers and devices: <!-- from the client or the contract, e.g. Chrome and Edge latest 2, Safari iOS 16+, Chrome Android 12+; what is not listed is not promised -->
- Local mock: <!-- how to run one, or "none" -->
- Test accounts: <!-- where they are defined (seed file), never the values here -->
- Test data: <!-- seed or fixture files, how to reset them; no real personal data -->
- Test environments: <!-- where test runs may change data, after the user's go-ahead for each run; never production -->

## Testing
- Test-case sheet: <!-- link or path, sheet name, ID column, result words (e.g. OK / NG / Pending) -->
- Bug tracker: <!-- e.g. Backlog project ABC; required fields; title format -->
- Severity / priority scale: <!-- the project's own; the default is in templates/bug.md -->
- Release criteria: <!-- e.g. no open Critical or Major bug, every smoke row passed; or "the team decides" -->

## People and tone
- Report language: <!-- e.g. Vietnamese -->
- Ticket / PR comment language and tone: <!-- e.g. Vietnamese, reviewer "anh", author "em", no greeting, one idea per comment -->
- Owners: BA <!-- name -->, PO/PM <!-- name -->, BE <!-- name -->, Design <!-- name -->, QA <!-- name -->
- Third parties and integrations: <!-- e.g. payment provider, video platform, client's internal system: who answers for each -->
- Decides conflicts: <!-- who settles a disagreement between sources; default BA for business rules and copy, PO for scope and priority -->

## Project rules that override the kit
<!-- e.g. "no test suite: do not add tests", "tokens in localStorage on purpose", "no middleware/proxy on purpose" -->
