---
name: ticket-brief
description: Turn a ticket plus requirements, design and API docs into a brief with observable acceptance criteria (AC-NNN), facts vs business constraints vs assumptions, applicable edge cases and open questions. Use when starting a ticket, when the user asks "task này cần làm gì / test gì", or when requirements, design and API seem to disagree.
---

# ticket-brief

**Input:** ticket link or ID; the requirements doc, design brief, design file, API spec and repo named in `.bdt/PROJECT.md`; anything the user pastes.
**Output:** `brief.md` (goal, scope, facts / constraints / assumptions, AC-NNN, edge cases, questions, verification plan, source table), status READY or BLOCKED.

Template: `../bdt-flow/templates/brief.md`. Write to `.bdt/work/<TICKET-ID>/brief.md`.

## Gather (read everything relevant before writing)
1. **Ticket:** title, description, every comment (newest last wins only if it says so), attachments (open images: flows and mockups often carry the real rules), linked tickets, status, assignee. Comments from BE or BA often change the scope: quote the deciding comment. **An empty description means the scope lives in the parent story**: read the parent and its sibling tickets (the FE/BE split tells you whether the API side is done).
2. **Requirements:** read the whole relevant section of the URD/PRD and the design brief or spec doc listed in `.bdt/PROJECT.md`, not a keyword search. Read the screen table (status, designer link). Note the screen ID and check that the IDs match between documents and the design file; a mismatch is a question.
3. **Design:** the frame for each screen and state; note what is "ready" vs "in progress" and what has no frame at all. Read comments in the design file. If the design connector is not authorised, open the file in the browser, select the frame and zoom to it.
4. **API docs:** the real paths, request and response schemas, enums, nullable fields, error codes. Prefer the JSON spec over the UI, and read every environment's spec (dev and staging can differ). **Readiness check:** list each capability the ACs need (list, create, change, preview, status field) and mark it present or missing in the spec. Missing ones block the ticket and go to BE as one contract question.
5. **Code:** what exists today (routes, hooks, types, i18n keys) with file:line. Check open branches and PRs for the same ticket. **Consistency scan:** grep the business values the ticket touches (prices, plan names, limits, dates) across constants, i18n and components; two screens showing different values for the same thing is a live bug to report.
6. **Live behaviour:** read-only calls or the browser if the ticket is a bug.

## Write
- **Facts** cite their source (file:line, endpoint, comment). **Business constraints** come only from requirements, ticket or client. Never derive a business rule from code. Everything else is an **Assumption** and, if it changes behaviour, also a question.
- **Acceptance criteria:** each one observable: Scenario, Action, Expected, Must not, Verify by. Use Required / Important / Optional. Banned without evidence: "correctly", "properly", "secure", "fast", "user-friendly".
- **States and edge cases:** walk the list in the template; keep only the ones that apply; map each to an AC or a question.
- **Disagreement** between ticket, requirements, design and API is a question with all sources quoted, never a silent choice.
- A business number, price, limit or copy that does not exist yet stays a placeholder and is listed as a question.

## Revise, never drop
If an AC proves impossible or wrong later, mark it `[revised rN]`, add a revision log line and tell the user. Do not delete it.

## Hand-off
Show the user: goal, ACs (one line each), blocking questions, and a source table (ticket, parent, requirements, design, API spec, code) with what each one says on the disputed points. If any blocking question is open, mark the brief **BLOCKED**, stop here and run `ask-questions`.
