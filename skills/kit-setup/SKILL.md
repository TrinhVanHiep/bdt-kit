---
name: kit-setup
description: Install, update or check the bdt-kit on this machine — merge the kernel into ~/.claude/CLAUDE.md with a diff, check that skills and agents are linked, and optionally enable the opt-in hooks. Use when the user asks to install, update, uninstall or check bdt-kit, or when kit skills seem missing.
---

# kit-setup

**Input:** this kit folder and the user's `~/.claude`.
**Output:** a dry-run report, then linked skills and agents, the kernel block, and hooks only when asked.

Pattern: inventory → choices → dry run → one confirmation → apply → verify. Never change user settings without showing the diff first.

## Inventory
- Kit location (the folder that contains `kernel/`, `skills/`, `agents/`) and its version in `.claude-plugin/plugin.json`.
- `~/.claude/CLAUDE.md`: missing, has an older `bdt-kit kernel` block, or has other content.
- `~/.claude/skills/*` and `~/.claude/agents/*`: which kit entries are linked, missing or shadowed by a same-name folder.
- `~/.claude/settings.json`: any bdt-kit hooks already present.

## Choices
1. Install method: symlinks via `install.sh` (default), or plugin marketplace (when the `claude` CLI is available).
2. Kernel: insert or update the block between `<!-- bdt-kit:start -->` and `<!-- bdt-kit:end -->` in `~/.claude/CLAUDE.md`, keeping the user's other content.
3. Hooks: off by default. Offer `extras/hooks/guard-bash.js` (blocks destructive shell commands) only on request.

## Dry run
Print exactly what will be created, linked, or changed (with the CLAUDE.md diff). Wait for one "ok".

## Apply and verify
Run `install.sh` (or the plugin commands the user runs), then list the linked skills and agents and confirm that a new session will pick them up (skills load at session start).
