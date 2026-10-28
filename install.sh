#!/usr/bin/env bash
# bdt-kit installer: links skills and agents into ~/.claude and merges the kernel into ~/.claude/CLAUDE.md.
# Usage: ./install.sh [--dry-run] [--uninstall] [--with-hooks]
set -euo pipefail

KIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
START='<!-- bdt-kit:start -->'
END='<!-- bdt-kit:end -->'
DRY_RUN=0
UNINSTALL=0
WITH_HOOKS=0

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --with-hooks) WITH_HOOKS=1 ;;
    *) echo "Unknown option: $arg" >&2; exit 1 ;;
  esac
done

run() {
  if [ "$DRY_RUN" -eq 1 ]; then echo "  would: $*"; else "$@"; fi
}

# Removes the kernel block, keeping everything else in the file.
strip_kernel() {
  awk -v s="$START" -v e="$END" '$0==s{skip=1;next} $0==e{skip=0;next} !skip' "$1"
}

link_items() {
  local kind="$1" pattern="$2"
  run mkdir -p "$CLAUDE_DIR/$kind"
  for source in "$KIT_DIR/$kind"/$pattern; do
    [ -e "$source" ] || continue
    local target="$CLAUDE_DIR/$kind/$(basename "$source")"
    if [ -L "$target" ]; then
      run ln -sfn "$source" "$target"
    elif [ -e "$target" ]; then
      echo "  skip $kind/$(basename "$source"): a file you own already has that name" >&2
    else
      run ln -s "$source" "$target"
    fi
  done
}

unlink_items() {
  local kind="$1"
  for target in "$CLAUDE_DIR/$kind"/*; do
    [ -L "$target" ] || continue
    case "$(readlink "$target")" in
      "$KIT_DIR"/*) run rm "$target" ;;
    esac
  done
}

if [ "$UNINSTALL" -eq 1 ]; then
  echo "Uninstalling bdt-kit from $CLAUDE_DIR"
  unlink_items skills
  unlink_items agents
  if [ -f "$CLAUDE_DIR/settings.json" ] && grep -Eq 'extras/hooks/(compact-save|compact-restore|rule-check|stop-check|guard-bash)\.js' "$CLAUDE_DIR/settings.json"; then
    if [ "$DRY_RUN" -eq 1 ]; then echo "  would: remove bdt-kit hooks from $CLAUDE_DIR/settings.json"; else
      node "$KIT_DIR/extras/hooks/install-hooks.js" remove "$CLAUDE_DIR/settings.json"
    fi
  fi
  if [ -f "$CLAUDE_MD" ] && grep -qF "$START" "$CLAUDE_MD"; then
    if [ "$DRY_RUN" -eq 1 ]; then echo "  would: remove the kernel block from $CLAUDE_MD"; else
      strip_kernel "$CLAUDE_MD" > "$CLAUDE_MD.tmp" && mv "$CLAUDE_MD.tmp" "$CLAUDE_MD"
    fi
  fi
  echo "Done."
  exit 0
fi

echo "Installing bdt-kit $(grep -o '"version": *"[^"]*"' "$KIT_DIR/.claude-plugin/plugin.json" | cut -d'"' -f4) into $CLAUDE_DIR"
link_items skills '*'
link_items agents '*.md'

KERNEL="$(printf '%s\n%s\n%s\n' "$START" "$(cat "$KIT_DIR/kernel/CLAUDE.md")" "$END")"
if [ "$DRY_RUN" -eq 1 ]; then
  echo "  would: write the kernel block into $CLAUDE_MD (other content is kept)"
else
  mkdir -p "$CLAUDE_DIR"
  touch "$CLAUDE_MD"
  [ -s "$CLAUDE_MD" ] && cp "$CLAUDE_MD" "$CLAUDE_MD.bak"
  { strip_kernel "$CLAUDE_MD"; printf '\n%s\n' "$KERNEL"; } > "$CLAUDE_MD.tmp"
  mv "$CLAUDE_MD.tmp" "$CLAUDE_MD"
fi

if [ "$WITH_HOOKS" -eq 1 ]; then
  if [ "$DRY_RUN" -eq 1 ]; then
    node "$KIT_DIR/extras/hooks/install-hooks.js" add "$CLAUDE_DIR/settings.json" --dry-run
  else
    node "$KIT_DIR/extras/hooks/install-hooks.js" add "$CLAUDE_DIR/settings.json"
  fi
fi

echo "Done. Start a new Claude Code session to load the skills."
[ "$WITH_HOOKS" -eq 1 ] || echo "Hooks are not installed: add --with-hooks (see extras/hooks/README.md)."
