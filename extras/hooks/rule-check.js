#!/usr/bin/env node
// bdt-kit hook "rule-check" (UserPromptSubmit): every N prompts, adds a short self-audit reminder to the context.
// It never blocks the prompt. N = BDT_AUDIT_EVERY (default 12).
const { readInput, isOff, readState, writeState } = require('./lib');

if (isOff('rule-check')) process.exit(0);
const input = readInput();
const every = Math.max(1, Number(process.env.BDT_AUDIT_EVERY || 12));
const key = `prompts-${input.session_id || 'default'}`;
const count = (readState(key, 0) || 0) + 1;
writeState(key, count);
if (count % every !== 0) process.exit(0);

process.stdout.write(
  [
    `bdt-kit rule check (prompt ${count}): before answering, check your recent work against the rules, briefly and only in your reasoning unless something failed.`,
    '- Project rules (AGENTS.md / CLAUDE.md / .claude/skills) and the bdt-kit kernel: anything skipped?',
    '- Plan approved before multi-step edits? Stop-and-confirm items asked, not assumed?',
    '- Every "done" backed by a check you actually ran? Nothing mutating sent to shared environments?',
    '- Lesson entry for each bug fixed? Debug output, dead code, unused imports left?',
    'If something failed, tell the user in one line and fix it. For a full audit, use the kit-audit skill.',
  ].join('\n'),
);
process.exit(0);
