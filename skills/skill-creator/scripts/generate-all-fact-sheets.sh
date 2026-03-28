#!/bin/bash
# Generate fact sheets for all skills (or a subset)
# Usage: ./generate-all-fact-sheets.sh [skill1 skill2 ...]
# If no skills specified, generates for all.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="${SKILLS_DIR:-$(cd "$(dirname "$0")/../../.." && pwd)/skills}"

if [ $# -gt 0 ]; then
  SKILLS=("$@")
else
  SKILLS=()
  for d in "$SKILLS_DIR"/*/; do
    [ -f "$d/SKILL.md" ] && SKILLS+=("$(basename "$d")")
  done
fi

for skill in "${SKILLS[@]}"; do
  echo "========================================"
  bash "$SCRIPT_DIR/generate-fact-sheet.sh" "$skill" "$SKILLS_DIR"
  echo ""
done
