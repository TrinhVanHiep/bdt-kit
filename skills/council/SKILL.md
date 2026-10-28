---
name: council
description: Decide between several valid options with real trade-offs by gathering four independent positions (architect, skeptic, pragmatist, user advocate) and returning one recommendation with the strongest dissent. Use when there are two or more reasonable fixes or designs, when a choice is costly to undo, or when the user asks "nên làm cách nào".
---

# council

**Input:** a decision with 2–4 options and its constraints.
**Output:** four positions, a recommendation, the strongest dissent, what would change the decision.

## Frame
Write the decision in one sentence, the options (2–4), the constraints (project rules, deadlines, what the client owns) and what "good" means here. Check the premise: is this really a choice, or does a project rule, the API spec or the design already decide it?

## Positions
Run four subagents **without the conversation history** (pass only the frame and the relevant file excerpts) so they are not anchored:
- **Architect:** long-term fit with the codebase and its patterns.
- **Skeptic:** what breaks, edge cases, hidden cost, what we would regret.
- **Pragmatist:** smallest change that meets the criteria now.
- **User advocate:** what the end user and the client see; copy, states, accessibility.
Each answers in under 150 words: preferred option, the one reason that matters most, the main risk.

For a small decision, write the four positions yourself instead of spawning agents, and say so.

## Verdict
- Recommendation and why (one paragraph).
- Strongest dissent, stated fairly.
- What would change the decision.
- If the choice belongs to BA, BE, the client or the user (copy, data shape, scope): hand it to them as a question with the recommendation, do not decide.
