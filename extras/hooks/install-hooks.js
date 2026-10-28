#!/usr/bin/env node
// Adds or removes the bdt-kit hooks in a Claude Code settings.json, keeping every other setting and hook.
// Usage: node install-hooks.js add|remove [settings.json] [--dry-run]
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const [, , action, target = path.join(os.homedir(), '.claude', 'settings.json'), flag] = process.argv;
const dryRun = flag === '--dry-run' || target === '--dry-run';
const settingsPath = target === '--dry-run' ? path.join(os.homedir(), '.claude', 'settings.json') : target;
const HOOKS_DIR = __dirname;
const OURS = /extras\/hooks\/(compact-save|compact-restore|rule-check|stop-check|guard-bash)\.js/;

const command = file => `node "${path.join(HOOKS_DIR, file)}"`;
const WANTED = {
  PreCompact: [{ matcher: '*', hooks: [{ type: 'command', command: command('compact-save.js'), timeout: 10 }] }],
  SessionStart: [{ matcher: 'compact', hooks: [{ type: 'command', command: command('compact-restore.js'), timeout: 10 }] }],
  UserPromptSubmit: [{ hooks: [{ type: 'command', command: command('rule-check.js'), timeout: 5 }] }],
  Stop: [{ hooks: [{ type: 'command', command: command('stop-check.js'), timeout: 20 }] }],
  PreToolUse: [{ matcher: 'Bash', hooks: [{ type: 'command', command: command('guard-bash.js'), timeout: 5 }] }],
};

if (!['add', 'remove'].includes(action)) {
  console.error('Usage: node install-hooks.js add|remove [settings.json] [--dry-run]');
  process.exit(1);
}

let settings = {};
if (fs.existsSync(settingsPath)) settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
const hooks = settings.hooks || {};

const isOurs = entry => (entry.hooks || []).some(h => OURS.test((h.command || '').replace(/\\/g, '/')));
for (const event of Object.keys(hooks)) {
  hooks[event] = hooks[event].filter(entry => !isOurs(entry));
  if (!hooks[event].length) delete hooks[event];
}
if (action === 'add') {
  for (const [event, entries] of Object.entries(WANTED)) hooks[event] = [...(hooks[event] || []), ...entries];
}
const next = { ...settings };
if (Object.keys(hooks).length) next.hooks = hooks;
else delete next.hooks;

const output = JSON.stringify(next, null, 2) + '\n';
if (dryRun) {
  process.stdout.write(`Would write ${settingsPath}:\n${output}`);
  process.exit(0);
}
fs.mkdirSync(path.dirname(settingsPath), { recursive: true });
if (fs.existsSync(settingsPath)) fs.copyFileSync(settingsPath, settingsPath + '.bak');
fs.writeFileSync(settingsPath, output);
console.log(`${action === 'add' ? 'Added' : 'Removed'} bdt-kit hooks in ${settingsPath} (backup: settings.json.bak)`);
