# Opt-in hooks

Hooks run code on every matching event, so the kit installs them only when asked:

```bash
~/bdt-kit/install.sh --with-hooks --dry-run
```

```bash
~/bdt-kit/install.sh --with-hooks
```

`install-hooks.js` merges them into `~/.claude/settings.json`, keeps every other setting and hook, writes `settings.json.bak`, and is safe to run again. `install.sh --uninstall` removes them.

| Hook id | Event | What it does | Blocks? |
| ------- | ----- | ------------ | ------- |
| `compact-save` | PreCompact | writes `.bdt/session-state.md`: branch, last commit, active `.bdt/work/<id>/` and its files, uncommitted changes | never |
| `compact-restore` | SessionStart (`compact`) | puts that state back into the context after a compaction and tells Claude to re-read the brief, plan and report before continuing (capped at `BDT_RESTORE_MAX_CHARS`, default 6000) | never |
| `rule-check` | UserPromptSubmit | every `BDT_AUDIT_EVERY` prompts (default 12) adds a short self-audit checklist; the full audit is the `kit-audit` skill | never |
| `stop-check` | Stop | before Claude finishes: debug output or conflict markers in changed files; on a `fix/`, `bugfix/` or `hotfix/` branch that changes code, a lessons file that is still unchanged | once per problem (exit 2), never loops |
| `guard-bash` | PreToolUse (Bash) | blocks recursive deletes of home/root, `git push --force`, `git reset --hard`, `git clean -f`, `git checkout .`, `--no-verify`, `curl -X POST/PUT/PATCH/DELETE` to `dev.`/`staging.` hosts | yes (exit 2) |

## Switches (environment variables)
- `BDT_HOOKS=off`: all hooks do nothing for that session.
- `BDT_DISABLED_HOOKS=rule-check,stop-check`: turn off some by id.
- `BDT_AUDIT_EVERY=20`, `BDT_RESTORE_MAX_CHARS=4000`.
- `BDT_LESSON_FILES=LESSON-LEARNED.md,docs/lessons.md`, `BDT_FIX_BRANCH='^(fix|bug)/'`, `BDT_BASE=origin/develop`.

State (prompt counters, problems already raised) lives in `~/.bdt-kit-state/`, outside every repo. Delete it to reset.

## Test

```bash
echo '{"tool_input":{"command":"git push --force origin main"}}' | node extras/hooks/guard-bash.js; echo "exit $?"
```
