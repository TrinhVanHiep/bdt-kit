---
name: ask-questions
description: Draft clear questions for BA, BE or the designer, grouped by owner, each with evidence, impact and a proposed default, ready to paste into chat or a ticket. Use when requirements are unclear or conflict, when the API differs from its docs, when the design is missing a state, or when the user says "soạn câu hỏi gửi BA/BE/designer".
---

# ask-questions

**Input:** open points from a brief, a review or a bug; the evidence behind each.
**Output:** `questions.md` grouped by owner, plus a paste-ready message per owner in the project's language and tone (the user sends it).

Template: `../bdt-flow/templates/questions.md`. Write to `.bdt/work/<TICKET-ID>/questions.md`, then give the user a paste-ready version.

## A good question
- One decision per question, answerable in one line (yes/no, A/B, a value).
- Says **what changes with each answer** (otherwise it is not worth asking).
- Carries **evidence**: screen ID and section, Figma frame, file:line, or for BE the request, the response and the `requestId`.
- Has a **proposed default** and says whether work is blocked until it is answered.
- Names the **owner** (BA for rules and copy, BE for contract and data, Design for missing states and layout).

## Before asking, check it is not already answered
Read the whole requirements section, the ticket comments, the design comments and the API spec. A question the doc answers costs trust.

## For a backend bug
Report, do not work around: endpoint, request body (no tokens or personal data), status, `error.code`, response excerpt, `requestId`, what the spec says, what the frontend expects.

## Output
- The table file for the record.
- A paste-ready message per owner in the language and tone from `.bdt/PROJECT.md` (for example Vietnamese, numbered, no greeting padding). Do not send it: the user sends it.
- Copy blocking questions into the brief's Questions table and `CONTEXT.md` → Needs confirmation.
