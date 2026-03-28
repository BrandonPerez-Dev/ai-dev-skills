#!/bin/bash
# Generate structural fact sheet for a skill
# Usage: ./generate-fact-sheet.sh <skill-name> [skills-dir]
#
# Produces an objective fact sheet that feeds into subjective scoring.
# This eliminates false negatives by making structural markers impossible to miss.

set -euo pipefail

SKILL_NAME="${1:?Usage: $0 <skill-name> [skills-dir]}"
SKILLS_DIR="${2:-$(cd "$(dirname "$0")/../../.." && pwd)/skills}"
SKILL_DIR="$SKILLS_DIR/$SKILL_NAME"
FILE="$SKILL_DIR/SKILL.md"

if [ ! -f "$FILE" ]; then
  echo "ERROR: $FILE not found" >&2
  exit 1
fi

LINES=$(wc -l < "$FILE" | tr -d ' ')

# Extract frontmatter (between first and second ---)
FRONTMATTER=$(awk '/^---$/{n++; next} n==1' "$FILE")

# Allowed tools
ALLOWED_TOOLS=$(echo "$FRONTMATTER" | awk '/allowed-tools:/{found=1; next} found && /^ *-/{sub(/^ *- /,""); printf "%s, ", $0; next} found{exit}' | sed 's/, $//')
HAS_SKILL_TOOL="no"
if echo "$ALLOWED_TOOLS" | grep -q 'Skill'; then
  HAS_SKILL_TOOL="yes"
fi

# Name from frontmatter
SKILL_DISPLAY_NAME=$(echo "$FRONTMATTER" | grep '^name:' | sed 's/^name: //' || echo "$SKILL_NAME")

# Description (handle multi-line)
DESCRIPTION=$(awk '/^---$/{n++; next} n==1' "$FILE" | awk '/^description:/{found=1; sub(/^description: *>?-? */, ""); print; next} found && /^  /{sub(/^  */, ""); print; next} found{exit}' | tr '\n' ' ' | sed 's/  */ /g; s/^ *//; s/ *$//')

# Hard gates
HARDGATE_COUNT=$(rg -c '<HARD-GATE>' "$FILE" 2>/dev/null || echo 0)
HARDGATE_TEXTS=""
if [ "$HARDGATE_COUNT" -gt 0 ]; then
  HARDGATE_TEXTS=$(awk '/<HARD-GATE>/{found=1; next} /<\/HARD-GATE>/{found=0} found{print}' "$FILE" | sed 's/^/    /')
fi

# Anti-patterns
HAS_ANTIPATTERNS="no"
ANTIPATTERN_COUNT=0
if rg -qi 'anti.pattern' "$FILE" 2>/dev/null; then
  HAS_ANTIPATTERNS="yes"
  # Count rows in anti-pattern tables (bold entries)
  ANTIPATTERN_COUNT=$(awk '/[Aa]nti.[Pp]attern/{found=1; next} found && /^## /{exit} found{print}' "$FILE" | rg -c '^\| \*\*' 2>/dev/null || echo 0)
fi

# Guidelines
HAS_GUIDELINES="no"
GUIDELINE_COUNT=0
if rg -q '^## Guidelines' "$FILE" 2>/dev/null; then
  HAS_GUIDELINES="yes"
  GUIDELINE_COUNT=$(awk '/^## Guidelines/{found=1; next} found && /^## /{exit} found{print}' "$FILE" | rg -c '^- \*\*' 2>/dev/null || echo 0)
fi

# When to Use
HAS_WHEN_TO_USE="no"
if rg -q '^## When to Use' "$FILE" 2>/dev/null; then
  HAS_WHEN_TO_USE="yes"
fi

# Decision tables (rows with pipe delimiters, excluding separator rows)
DECISION_TABLE_ROWS=$(rg -c '^\| .+\|' "$FILE" 2>/dev/null || echo 0)

# Delegations
DELEGATION_LINES=$(rg -in '(invoke|delegates? to) \*\*' "$FILE" 2>/dev/null || true)

# Central thesis (first non-empty, non-tag line after H1)
OPENING_LINE=$(awk '/^# /{found=1; next} found && /^$/{next} found && !/^</{print; exit}' "$FILE")

# References directory
REFS_COUNT=0
REFS_FILES=""
if [ -d "$SKILL_DIR/references" ]; then
  REFS_COUNT=$(ls "$SKILL_DIR/references/" 2>/dev/null | wc -l | tr -d ' ')
  REFS_FILES=$(ls "$SKILL_DIR/references/" 2>/dev/null | sed 's/^/    - /')
fi

# All H2 sections
SECTIONS=$(rg '^## ' "$FILE" 2>/dev/null | sed 's/^/  - /')

# Communication protocol reference
HAS_COMM_PROTOCOL="no"
if rg -q 'communication-protocol' "$FILE" 2>/dev/null; then
  HAS_COMM_PROTOCOL="yes"
fi

# Output the fact sheet
echo "SKILL: $SKILL_NAME"
echo "LINES: $LINES"
echo ""
echo "FRONTMATTER:"
echo "  name: $SKILL_DISPLAY_NAME"
echo "  description: $DESCRIPTION"
echo "  allowed-tools: [$ALLOWED_TOOLS]"
echo ""
echo "STRUCTURAL MARKERS:"
echo "  hard-gates: $HARDGATE_COUNT"
if [ "$HARDGATE_COUNT" -gt 0 ]; then
  echo "  hard-gate-text:"
  echo "$HARDGATE_TEXTS"
fi
echo "  anti-patterns: $HAS_ANTIPATTERNS ($ANTIPATTERN_COUNT entries)"
echo "  guidelines: $HAS_GUIDELINES ($GUIDELINE_COUNT bullets)"
echo "  when-to-use: $HAS_WHEN_TO_USE"
echo "  decision-tables: $DECISION_TABLE_ROWS table rows"
echo "  references-dir: $REFS_COUNT files"
if [ "$REFS_COUNT" -gt 0 ]; then
  echo "$REFS_FILES"
fi
echo "  communication-protocol: $HAS_COMM_PROTOCOL"
echo ""
echo "DELEGATION:"
echo "  has-Skill-tool: $HAS_SKILL_TOOL"
if [ -n "$DELEGATION_LINES" ]; then
  echo "  explicit-invocations:"
  echo "$DELEGATION_LINES" | sed 's/^/    /'
else
  echo "  explicit-invocations: none"
fi
echo ""
echo "CENTRAL THESIS:"
echo "  opening-line: \"$OPENING_LINE\""
echo ""
echo "SECTIONS:"
echo "$SECTIONS"
