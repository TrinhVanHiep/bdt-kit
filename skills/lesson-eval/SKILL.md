---
name: lesson-eval
description: After a bug fix or a review comment, decide whether the lesson is worth keeping (Save, Improve, Absorb, Drop), write it in the project's lessons file in a fixed format, and promote lessons that repeat across projects into kit or project rules. Use after fixing a bug, after a reviewer finds a defect, or when the user asks to "ghi lesson", "rút kinh nghiệm".
---

# lesson-eval

**Input:** a fixed bug or a review finding.
**Output:** a verdict (Save / Improve / Absorb / Drop), the entry in the lessons file, the same pattern searched across the repo, promotion proposals.

## 1. Find the home
The project's own lessons file first (for example `LESSON-LEARNED.md`), else `.bdt/LESSONS.md`. Read it fully before writing.

## 2. Verdict
- **Save:** new, specific, would have prevented a real defect.
- **Improve:** an existing entry covers it but misses this case; extend that entry.
- **Absorb:** it is really a rule; add it to the project rules or a lint rule/type instead (ask first when the rule file is shared).
- **Drop:** generic advice ("be careful with X"), a one-off typo, or already covered.

## 3. Entry format
```
## <symptom in plain words> (<YYYY-MM-DD>)
- Symptom: what the user or reviewer saw.
- Root cause: one sentence, the real cause, with evidence.
- Fix: what changed and at which layer.
- Prevention: the check that would catch it next time (grep, lint rule, type, review question).
```

## 4. Same pattern elsewhere
Grep for the pattern across the repo; fix every occurrence or list them. When a tool can catch it (lint rule, type), propose adding that too.

## 5. Promote
When the same lesson appears in two or more projects, propose a line for the kit kernel or a kit skill. The user approves every promotion. Keep the kernel short: a promotion that does not replace or sharpen an existing line probably belongs in a skill.
