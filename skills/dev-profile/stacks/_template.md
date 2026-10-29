# Stack pack: <name> (<versions covered>)

<!-- A pack is reusable knowledge about one technology, shared by every project that uses it. Project rules never go here: they belong in the project's .bdt/dev/CONVENTIONS.md.
Every line has a source (the official docs for the version, a kit lesson, or the project it came from); a line without one is labelled "assumption". Keep each item a concrete failure or check, not a style preference. -->

Applies when: <manifest signal, e.g. `laravel/framework` in composer.json>
App types: <web UI | API/backend | mobile | CLI/library | worker>
Version-correct docs: <where to read the docs for the installed version>
Reviewer: <agent that runs the review checklist; `bdt-stack-reviewer` when there is no dedicated one>
Sources: <links>

## Plan gotchas
<!-- traps to check when planning a change in this stack: lifecycles, boundaries, generated code, migrations, caches -->
-

## Implement
- Debug leftovers to remove: <patterns>
- Forbidden ways to silence a check: <type escapes, ignore comments, rule disables, skipped hooks>
- Idioms: <the stack's own way for common tasks, with a doc link each>

## Verify
- Static: <usual lint, type and build tools; the real commands come from the project's PROJECT.md>
- Runtime: <how to exercise a change locally for this app type>
- Cases specific to this stack: <e.g. hydration warnings, N+1 queries, migration rollback, app resume>

## Review checklist
<!-- what the reviewer checks in the stack lane; each item: the failure it catches -->
-

## Security
<!-- stack-specific risks: injection, mass assignment, secrets in client bundles, unsafe deserialisation, debug mode in production -->
-
