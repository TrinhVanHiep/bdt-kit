#!/usr/bin/env node
// bdt-kit CLI: npx runs from a temporary cache, so the kit is first copied to a stable folder
// and install.sh runs from there (its links point at that folder).
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const PKG_DIR = path.resolve(__dirname, '..');
const KIT_HOME = path.resolve(process.env.BDT_KIT_HOME || path.join(os.homedir(), '.bdt-kit'));
const PARTS = ['bin', 'skills', 'agents', 'kernel', 'extras', '.claude-plugin', 'install.sh', 'package.json', 'README.md', 'LICENSE', 'CHANGELOG.md'];
const VERSION = require(path.join(PKG_DIR, 'package.json')).version;
const FLAGS = { install: ['--dry-run', '--with-hooks'], uninstall: ['--dry-run'] };

const USAGE = `bdt-kit ${VERSION}

  npx bdt-kit install [--dry-run] [--with-hooks]   copy the kit to ${KIT_HOME} and link it into ~/.claude
  npx bdt-kit uninstall [--dry-run]                remove the links, the kernel block and the hooks
  npx bdt-kit --version

BDT_KIT_HOME sets another folder. Needs bash (macOS, Linux, WSL).`;

function fail(message) {
  console.error(`bdt-kit: ${message}`);
  process.exit(1);
}

// The folder is ours only when it is new, empty, or a copy this CLI made; a git clone is never touched.
function checkHome() {
  if (!fs.existsSync(KIT_HOME)) return;
  if (fs.existsSync(path.join(KIT_HOME, '.git'))) {
    fail(`${KIT_HOME} is a git clone. Update it with "git -C ${KIT_HOME} pull" and run its install.sh, or set BDT_KIT_HOME.`);
  }
  const manifest = path.join(KIT_HOME, 'package.json');
  const ours = fs.existsSync(manifest) && JSON.parse(fs.readFileSync(manifest, 'utf8')).name === 'bdt-kit';
  if (!ours && fs.readdirSync(KIT_HOME).length > 0) {
    fail(`${KIT_HOME} exists and is not a bdt-kit copy. Move it or set BDT_KIT_HOME.`);
  }
}

function bash(script, args, options = {}) {
  const result = spawnSync('bash', [script, ...args], { stdio: options.capture ? 'pipe' : 'inherit', encoding: 'utf8' });
  if (result.error) fail(`could not run bash: ${result.error.message}`);
  return result;
}

function install(flags) {
  checkHome();
  if (flags.includes('--dry-run')) {
    // Preview from the package, shown with the paths the links will really have.
    console.log(`Dry run: would copy bdt-kit ${VERSION} to ${KIT_HOME}`);
    const result = bash(path.join(PKG_DIR, 'install.sh'), flags, { capture: true });
    const show = text => text.split(PKG_DIR).join(KIT_HOME).split('\n').filter(line => !line.startsWith('Dry run')).join('\n');
    process.stdout.write(show(result.stdout));
    process.stderr.write(show(result.stderr));
    console.log('Dry run only: nothing was copied or installed. Run "npx bdt-kit install" to install.');
    process.exit(result.status);
  }
  if (PKG_DIR !== KIT_HOME) {
    fs.mkdirSync(KIT_HOME, { recursive: true });
    for (const part of PARTS) {
      const target = path.join(KIT_HOME, part);
      fs.rmSync(target, { recursive: true, force: true });
      if (fs.existsSync(path.join(PKG_DIR, part))) fs.cpSync(path.join(PKG_DIR, part), target, { recursive: true });
    }
    console.log(`Copied bdt-kit ${VERSION} to ${KIT_HOME}`);
  }
  process.exit(bash(path.join(KIT_HOME, 'install.sh'), flags).status);
}

function uninstall(flags) {
  const script = path.join(KIT_HOME, 'install.sh');
  if (!fs.existsSync(script)) fail(`nothing to uninstall: ${script} not found.`);
  const status = bash(script, ['--uninstall', ...flags]).status;
  if (status === 0 && !flags.includes('--dry-run')) console.log(`The kit files stay in ${KIT_HOME}; delete that folder if you no longer need it.`);
  process.exit(status);
}

const [command, ...flags] = process.argv.slice(2);
if (command === '--version' || command === '-v') {
  console.log(VERSION);
} else if (FLAGS[command]) {
  const unknown = flags.filter(flag => !FLAGS[command].includes(flag));
  if (unknown.length) fail(`unknown option for ${command}: ${unknown.join(' ')}\n\n${USAGE}`);
  (command === 'install' ? install : uninstall)(flags);
} else {
  console.log(USAGE);
  process.exit(command && command !== 'help' && command !== '--help' ? 1 : 0);
}
