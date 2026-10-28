#!/usr/bin/env node
// bdt-kit hook "stop-check" (Stop): before Claude ends its turn, two cheap checks on the repo.
// 1. Leftovers in changed files: debug output, `debugger`, merge-conflict markers.
// 2. Lesson reminder: on a fix branch whose diff touches code, the lessons file is still unchanged.
// Exit 2 sends the reason back to Claude once; it never loops (stop_hook_active, and one reminder per state).
const fs = require('node:fs');
const path = require('node:path');
const { readInput, git, isOff, readState, writeState } = require('./lib');

if (isOff('stop-check')) process.exit(0);
const input = readInput();
if (input.stop_hook_active) process.exit(0);
const cwd = input.cwd || process.cwd();
const root = git(cwd, ['rev-parse', '--show-toplevel']);
if (!root) process.exit(0);

const CODE = /\.(m?[jt]sx?|vue|svelte|py|rb|go|php|java|kt|swift|cs)$/;
const LESSON_FILES = (process.env.BDT_LESSON_FILES || 'LESSON-LEARNED.md,LESSONS.md,.bdt/LESSONS.md').split(',');
const FIX_BRANCH = new RegExp(process.env.BDT_FIX_BRANCH || '^(fix|bugfix|hotfix)/');

const changed = [
  ...git(root, ['diff', '--name-only', 'HEAD']).split('\n'),
  ...git(root, ['ls-files', '--others', '--exclude-standard']).split('\n'),
].filter(Boolean);

const problems = [];
for (const file of changed.filter(f => CODE.test(f))) {
  let text = '';
  try {
    text = fs.readFileSync(path.join(root, file), 'utf8');
  } catch {
    continue;
  }
  // Only lines this change adds; an untracked file has no diff, so all of it counts.
  const diff = git(root, ['diff', '-U0', 'HEAD', '--', file]);
  const addedLines = diff
    ? diff.split('\n').filter(l => l.startsWith('+') && !l.startsWith('+++')).map(l => l.slice(1))
    : text.split('\n');
  if (addedLines.some(l => /\bconsole\.log\(|\bdebugger\b|\bbreakpoint\(\)|pdb\.set_trace\(/.test(l))) {
    problems.push(`${file}: debug output (console.log / debugger / breakpoint)`);
  }
  if (/^(<{7}|>{7}) /m.test(text)) problems.push(`${file}: merge-conflict markers`);
}

const branch = git(root, ['branch', '--show-current']);
const base = process.env.BDT_BASE || ['origin/develop', 'origin/main', 'main', 'master'].find(b => git(root, ['rev-parse', '--verify', '--quiet', b]));
if (FIX_BRANCH.test(branch) && base) {
  const mergeBase = git(root, ['merge-base', 'HEAD', base]);
  const branchFiles = mergeBase ? git(root, ['diff', '--name-only', mergeBase]).split('\n').filter(Boolean) : [];
  const touchesCode = [...branchFiles, ...changed].some(f => CODE.test(f));
  const lessonFile = LESSON_FILES.find(f => fs.existsSync(path.join(root, f)));
  const lessonTouched = [...branchFiles, ...changed].some(f => LESSON_FILES.includes(f));
  if (touchesCode && lessonFile && !lessonTouched) {
    problems.push(`branch ${branch} fixes code but ${lessonFile} is unchanged: run lesson-eval (Save / Improve / Absorb), or tell the user why it is a Drop`);
  }
}

// Each problem is raised once; after that it is Claude's call (and the user's) to keep it.
const seenKey = `stop-${root}`;
const seen = new Set(readState(seenKey, []));
const fresh = problems.filter(p => !seen.has(p));
if (!fresh.length) process.exit(0);
writeState(seenKey, [...seen, ...fresh].slice(-200));
process.stderr.write(`bdt-kit stop-check:\n- ${fresh.join('\n- ')}\nFix these or say why they are intended, then finish.\n`);
process.exit(2);
