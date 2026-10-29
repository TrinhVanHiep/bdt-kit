---
name: ask-questions
description: Draft clear questions for BA, PO/PM, BE, Design or a third party — each with an ID, evidence with document versions, impact per answer, a proposed default, a blocking flag and a needed-by date — blocking first and ready to paste per owner; then track each one (Open / Answered / Default applied / Obsolete) and carry the answers into the brief, ACs, scenarios and test cases. Use when requirements are unclear or conflict, when the API differs from its docs, when the design is missing a state, when the user says "soạn câu hỏi gửi BA/BE/designer", or when answers come back ("BA trả lời rồi", "cập nhật câu trả lời").
---

# ask-questions

**Input:** open points from a brief, a review, a test run or a bug, with the evidence behind each; later, the answers.
**Output:** `questions.md` (one row per question, with an ID and a status), a paste-ready message per owner in the project's language and tone (the user sends it), and, as answers arrive, the updates they cause.

Template: `../bdt-flow/templates/questions.md`. If it is missing, use one table with the columns ID, Owner, Question, Evidence, Impact per answer, Proposed default, Blocking, Needed by, Status, Answer. Write to `.bdt/work/<TICKET-ID>/questions.md`.

## 0. Inputs
- No ticket ID: use the branch name for the work folder.
- No `.bdt/PROJECT.md`: write in the user's language, numbered, no greeting, neutral; ask the user once for the owners and who decides conflicts.

## A good question
- An **ID** (`Q-01`, `Q-02`…), unique in the work folder and never reused, so answers given together in a chat can be matched.
- One decision per question, answerable in one line (yes/no, A/B, a value).
- Says **what changes with each answer** (otherwise it is not worth asking).
- **Evidence** with the document's version or last-updated date: screen ID and section, Figma frame and its last edit, file:line, or for BE the request, the response and the `requestId`. Documents change; the version settles "it has been fixed since".
- A **proposed default**, whether work is **blocked** until it is answered, and **needed by** (the sprint milestone or test date that needs the answer).
- An **owner**, from the Owners in `.bdt/PROJECT.md`: BA (business rules, copy), PO/PM (scope, priority, release), BE (contract, data), Design (missing states, layout), or a third party or integrated system (their API, rules or data).
- **Neutral wording:** what was found and what is needed, never who missed it ("§3.2 does not cover the expired case. Which applies, A or B?", not "Why does the spec not cover…"). The same for a backend bug.

## Before asking, check it is not already answered
Read the whole requirements section, the ticket comments, the design comments and the API spec. A question the doc answers costs trust. Write in Evidence where you looked and what each place says, or that it says nothing, so the owner can point to the right place if it was missed.

## Conflicts between sources or owners
When two sources disagree (URD and Figma, BA and Design, spec and API), ask **one** question to the person who decides, quoting both sides with their versions. The decision owner is "Decides conflicts" in `.bdt/PROJECT.md`; without one, BA decides business rules and copy, PO decides scope and priority.

## Order and size
- Blocking questions first, then by needed-by date.
- Merge questions that the same decision answers.
- At most 10 questions per message. The rest wait for the next message; the record keeps them all.

## Defaults
- **Not blocking:** work may go on with the proposed default. Write it in the brief's Assumptions with the Q-ID; the question stays Open.
- **Blocking:** never apply the default on your own. Stop the work that depends on it (`bdt-flow` step 2) and do only what does not depend on the answer.
- A value the client owns (copy, price, limit, date) has no invented default: it stays a placeholder until answered.
- **Test cases:** the Expected result follows the confirmed answer or the default in force. The open part goes in the Note column with the Q-ID; "to be confirmed" or "cần xác nhận" never appears in Expected. A case whose expected result depends on an open blocking question is marked pending in Note with the Q-ID.

## Lifecycle
| Status | Meaning |
| ------ | ------- |
| Open | Asked, no answer yet |
| Answered | The answer is recorded: who, when, where (chat, ticket comment, meeting) |
| Default applied | Not blocking, and the needed-by date passed without an answer: the default is in force as an assumption |
| Obsolete | No longer needed (scope changed, the document was updated); the reason is written |

When answers arrive, often several in one chat message, match each one to its Q-ID and quote it in Answer. Then carry it through:
- the brief: the AC or constraint it settles, marked `[revised rN]` (never deleted), and the matching assumption removed;
- `CONTEXT.md`: the entry leaves Needs confirmation and becomes a term or rule with the answer as its source;
- scenarios and test cases written on the default: Expected rewritten, Note cleared;
- a plan or code already built on the default: list what has to change and tell the user before changing it.

An answer that raises a new point gets a new ID. An unclear answer is asked back once, with the reading you would take.

A non-blocking question past its needed-by date without an answer becomes Default applied: the assumption stays in the brief and the user hears about it in the next hand-off. A blocking question past its date goes back to the user, never to a default.

## For a backend bug
Report, do not work around: endpoint, request body (no tokens or personal data), status, `error.code`, response excerpt, `requestId`, what the spec says (with its version), what the frontend expects. Screenshots attached to any question have personal data and tokens masked.

## Output
- `questions.md`: the record of every question and its status.
- A paste-ready message per owner, numbered with the Q-IDs, blocking first, each with its needed-by date, in the language and tone from `.bdt/PROJECT.md`. Do not send it: the user sends it.
- Blocking questions copied into the brief's Questions table and `CONTEXT.md` → Needs confirmation, with the same IDs.
