#!/usr/bin/env node
// bdt-kit hook "compact-save" (PreCompact): writes .bdt/session-state.md so the work survives a context compaction.
// The matching SessionStart hook (compact-restore.js) puts it back into the context right after.
const fs = require('node:fs');
const path = require('node:path');
const { readInput, git, isOff, latestWorkDir } = require('./lib');

if (isOff('compact-save')) process.exit(0);
const input = readInput();
const cwd = input.cwd || process.cwd();
const root = git(cwd, ['rev-parse', '--show-toplevel']) || cwd;
if (!fs.existsSync(path.join(root, '.bdt'))) process.exit(0);

const ticket = latestWorkDir(root);
const files = ticket
  ? fs.readdirSync(path.join(root, '.bdt', 'work', ticket)).filter(f => f.endsWith('.md')).map(f => `.bdt/work/${ticket}/${f}`)
  : [];
const lines = [
  '# Session state (written by bdt-kit before a context compaction)',
  '',
  `- Time: ${new Date().toISOString()}`,
  `- Trigger: ${input.trigger || 'unknown'}`,
  `- Branch: ${git(root, ['branch', '--show-current']) || '(detached)'}`,
  `- Last commit: ${git(root, ['log', '-1', '--format=%h %s'])}`,
  `- Active work folder: ${ticket ? `.bdt/work/${ticket}/` : 'none'}`,
  '',
  '## Files to re-read before continuing',
  ...(files.length ? files.map(f => `- ${f}`) : ['- (no work folder: re-read the plan or the user\'s last request)']),
  '',
  '## Uncommitted changes',
  '```',
  git(root, ['status', '--short']).slice(0, 4000) || '(clean)',
  '```',
];
try {
  fs.writeFileSync(path.join(root, '.bdt', 'session-state.md'), lines.join('\n') + '\n');
} catch {
  // Never block a compaction.
}
process.exit(0);
