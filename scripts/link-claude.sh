#!/bin/bash
# Symlink every skill and agent in this repo into ~/.claude, so Claude Code loads them.
# Links only: unlike setup-claude.sh it leaves hooks, settings and plugins alone.
#
#   scripts/link-claude.sh            link, and repoint links that go elsewhere
#   scripts/link-claude.sh --dry-run  print what would change, change nothing
#
# A skill folder without SKILL.md is skipped. A real file or directory already at the
# target is never touched. Links to skills or agents not in this repo are reported, not removed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"

dry_run=false
[ "${1:-}" = "--dry-run" ] && dry_run=true

run() {
  if $dry_run; then echo "    would run: $*"; else "$@"; fi
}

# link_one SOURCE TARGET: create, repoint or leave the link; prints what it did.
link_one() {
  local source="$1" target="$2" name
  name="$(basename "$target")"
  if [ -L "$target" ]; then
    if [ "$(readlink -f "$target")" = "$(readlink -f "$source")" ]; then
      unchanged=$((unchanged + 1)); return
    fi
    echo "  repoint:  $name  (was $(readlink "$target"))"
    run ln -sfn "$source" "$target"; repointed=$((repointed + 1))
  elif [ -e "$target" ]; then
    echo "  skip (real file or directory at target):  $name"; skipped=$((skipped + 1))
  else
    echo "  link:     $name"
    run ln -s "$source" "$target"; linked=$((linked + 1))
  fi
}

# report_foreign DIR SOURCE_DIR: list entries in DIR that this repo does not provide.
report_foreign() {
  local dir="$1" source_dir="$2" entry name
  for entry in "$dir"/*; do
    [ -e "$entry" ] || [ -L "$entry" ] || continue
    name="$(basename "$entry")"
    [ -e "$source_dir/$name" ] && continue
    echo "  not from this repo, left alone:  $name -> $(readlink "$entry" || echo 'real file or directory')"
  done
}

for kind in skills agents; do
  linked=0; repointed=0; unchanged=0; skipped=0
  mkdir -p "$CLAUDE_DIR/$kind"
  echo "$kind:"

  if [ "$kind" = skills ]; then
    for source in "$CONFIG_DIR/skills"/*/; do
      source="${source%/}"
      if [ ! -f "$source/SKILL.md" ]; then
        echo "  skip (no SKILL.md):  $(basename "$source")"; skipped=$((skipped + 1)); continue
      fi
      link_one "$source" "$CLAUDE_DIR/skills/$(basename "$source")"
    done
  else
    for source in "$CONFIG_DIR/agents"/*.md; do
      link_one "$source" "$CLAUDE_DIR/agents/$(basename "$source")"
    done
  fi

  echo "  linked $linked, repointed $repointed, already correct $unchanged, skipped $skipped"
  report_foreign "$CLAUDE_DIR/$kind" "$CONFIG_DIR/$kind"
done

$dry_run && echo "(dry run: nothing changed)"
exit 0
