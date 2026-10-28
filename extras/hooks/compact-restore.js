#!/usr/bin/env node
// bdt-kit hook "compact-restore" (SessionStart, matcher "compact"): what it prints is added to the new context.
const fs = require('node:fs');
const path = require('node:path');
const { readInput, git, isOff } = require('./lib');

if (isOff('compact-restore')) process.exit(0);
const input = readInput();
const cwd = input.cwd || process.cwd();
const root = git(cwd, ['rev-parse', '--show-toplevel']) || cwd;
const file = path.join(root, '.bdt', 'session-state.md');
if (!fs.existsSync(file)) process.exit(0);

const MAX_CHARS = Number(process.env.BDT_RESTORE_MAX_CHARS || 6000);
const state = fs.readFileSync(file, 'utf8').slice(0, MAX_CHARS);
process.stdout.write(
  [
    'bdt-kit: the context was just compacted. Before doing anything else, re-read the files listed below',
    '(brief, plan, report, questions) and continue from them, not from memory of the summary.',
    'Recalled details that the files do not confirm are hints to verify.',
    '',
    state,
  ].join('\n'),
);
process.exit(0);
