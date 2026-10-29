# Stack pack: React / Next.js

<!-- Moved from kit 0.1–0.3 (bdt-react-reviewer, qa-click-path, dev-implement, stop-check), which came from the kit's trial projects. Project rules go in .bdt/dev/CONVENTIONS.md, not here. -->

Applies when: `react` or `next` in `package.json` dependencies
App types: web UI (Next.js route handlers and server actions are also API/backend)
Version-correct docs: the installed versions in the lockfile; the docs shipped in `node_modules` when present, else react.dev and nextjs.org for that major version
Reviewer: `bdt-react-reviewer`
Sources: kit 0.1–0.3 skills and agents named above

## Plan gotchas
- A new component that uses state, effects or browser APIs needs `'use client'`; keep the boundary as low in the tree as it can go.
- A new env var read in the browser needs the `NEXT_PUBLIC_` prefix, and anything secret must not have it.
- `useSearchParams` in a statically rendered page needs a Suspense boundary.
- Data from a query or props: derive it during render instead of copying it into state with an effect.
- An effect that sends a one-time request runs twice in StrictMode during development: plan the guard or move the call to the event handler.

## Implement
- Debug leftovers to remove: `console.log`, `debugger`.
- Forbidden ways to silence a check: `any`, `@ts-ignore` / `@ts-expect-error` without a reason, `eslint-disable` lines, `--no-verify`.
- Idioms: stable keys from data ids, not the array index; `cond ? <X/> : null` when `cond` can be `0` or `''`; cleanup for every timer, listener and subscription an effect creates.

## Verify
- Static: lint, `tsc --noEmit` or the project's typecheck script, `next build` (it catches server/client boundary errors that the dev server forgives).
- Runtime: the web UI recipe in `qa-verify` (browser at the breakpoints in PROJECT.md).
- Cases specific to this stack: hydration warnings in the console; requests sent twice in the network tab; a select or form library emitting an empty value while it registers options; reload and deep link on a client-only route.

## Review checklist
Run by `bdt-react-reviewer`; its lane is the checklist: server/client boundary, hooks and effects, rendering, forms, accessibility, navigation.

## Security
- Secrets in `NEXT_PUBLIC_*` or in client components.
- `dangerouslySetInnerHTML` with data that is not sanitised.
- Redirect targets taken from the URL without checking that they are internal.
