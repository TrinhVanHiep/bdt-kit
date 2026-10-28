#!/usr/bin/env node
// bdt-kit opt-in PreToolUse hook for Bash: blocks commands that destroy work or rewrite shared history.
// Exit 2 blocks the call and shows the reason to Claude; exit 0 lets it through. Prints nothing otherwise.
// Disable without editing settings: BDT_HOOKS=off

if (process.env.BDT_HOOKS === 'off') process.exit(0);

const BLOCKED = [
  { pattern: /\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|-[a-zA-Z]*f[a-zA-Z]*r)\b[^|;&\n]*(\s\/(\s|$)|\s~(\/|\s|$)|\s\$HOME)/, reason: 'recursive delete of a home or root path' },
  { pattern: /\bgit\s+push\b[^|;&\n]*\s(--force|-f)(\s|$)/, reason: 'force push (use --force-with-lease on your own branch)' },
  { pattern: /\bgit\s+reset\s+--hard\b/, reason: 'git reset --hard discards local work' },
  { pattern: /\bgit\s+clean\s+-[a-zA-Z]*f/, reason: 'git clean -f deletes untracked files' },
  { pattern: /\bgit\s+(checkout|restore)\s+(--\s+)?\.(\s|$)/, reason: 'discards every unstaged change' },
  { pattern: /--no-verify\b/, reason: '--no-verify skips the project hooks' },
  { pattern: /\bcurl\b[^|;&\n]*\s-X\s*(POST|PUT|PATCH|DELETE)\b[^|;&\n]*(dev|staging)\./i, reason: 'mutating request to a shared environment' },
];

let input = '';
process.stdin.on('data', chunk => (input += chunk));
process.stdin.on('end', () => {
  let command = '';
  try {
    command = JSON.parse(input).tool_input?.command ?? '';
  } catch {
    process.exit(0); // Not a Bash payload we understand: never block on a parse error.
  }
  const hit = BLOCKED.find(rule => rule.pattern.test(command));
  if (!hit) process.exit(0);
  process.stderr.write(`bdt-kit guard blocked this command: ${hit.reason}. Ask the user to run it, or to confirm explicitly.\n`);
  process.exit(2);
});
