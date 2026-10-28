// Shared helpers for bdt-kit hooks. Hooks never throw: any unexpected error lets the action through.
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

function readInput() {
  try {
    return JSON.parse(fs.readFileSync(0, 'utf8') || '{}');
  } catch {
    return {};
  }
}

function git(cwd, args) {
  try {
    return execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], timeout: 5000 }).trim();
  } catch {
    return '';
  }
}

function isOff(id) {
  if (process.env.BDT_HOOKS === 'off') return true;
  return (process.env.BDT_DISABLED_HOOKS || '').split(',').map(s => s.trim()).includes(id);
}

// Per-machine state (counters, "already reminded"), outside the repo.
function statePath(name) {
  const dir = path.join(os.homedir(), '.bdt-kit-state');
  fs.mkdirSync(dir, { recursive: true });
  return path.join(dir, name.replace(/[^A-Za-z0-9_.-]/g, '_'));
}

function readState(name, fallback) {
  try {
    return JSON.parse(fs.readFileSync(statePath(name), 'utf8'));
  } catch {
    return fallback;
  }
}

function writeState(name, value) {
  try {
    fs.writeFileSync(statePath(name), JSON.stringify(value));
  } catch {
    // State is a convenience: a hook still works without it, it only repeats itself.
  }
}

function latestWorkDir(root) {
  const work = path.join(root, '.bdt', 'work');
  try {
    return fs
      .readdirSync(work)
      .map(name => ({ name, mtime: fs.statSync(path.join(work, name)).mtimeMs }))
      .sort((a, b) => b.mtime - a.mtime)[0]?.name;
  } catch {
    return undefined;
  }
}

module.exports = { readInput, git, isOff, readState, writeState, latestWorkDir };
