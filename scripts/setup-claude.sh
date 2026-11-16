#!/bin/bash
# Setup Claude Code with skills, agents, and plugins from this config repo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")"
CLAUDE_DIR="$HOME/.claude"

echo "Setting up Claude Code configuration..."

# Create Claude directories if they don't exist
mkdir -p "$CLAUDE_DIR/skills"
mkdir -p "$CLAUDE_DIR/agents"
mkdir -p "$CLAUDE_DIR/hooks"

# A skill whose SKILL.md frontmatter says `scope: cadre` belongs to the cadres
# that list it: a cadre runner links it into its own runs' folders, so it is
# not linked here, where every session on the machine would load it.
cadre_only() {
  [ -f "$1/SKILL.md" ] &&
    awk '/^---$/ { n++; next } n == 1' "$1/SKILL.md" | grep -qE '^[[:space:]]+scope:[[:space:]]*cadre[[:space:]]*$'
}

# Symlink skills
echo ""
echo "Linking skills..."
for skill_dir in "$CONFIG_DIR/skills"/*; do
  if [ -d "$skill_dir" ]; then
    skill_name=$(basename "$skill_dir")
    target="$CLAUDE_DIR/skills/$skill_name"

    if cadre_only "$skill_dir"; then
      [ -L "$target" ] && rm "$target"
      echo "  Cadre only: $skill_name (a cadre runner links it into its own runs)"
      continue
    fi

    if [ -L "$target" ]; then
      rm "$target"
    elif [ -d "$target" ]; then
      echo "  Skipping $skill_name (already exists as directory)"
      continue
    fi

    ln -s "$skill_dir" "$target"
    echo "  Linked: $skill_name"
  fi
done

# Symlink agents
echo ""
echo "Linking agents..."
for agent_file in "$CONFIG_DIR/agents"/*.md; do
  if [ -f "$agent_file" ]; then
    agent_name=$(basename "$agent_file")
    target="$CLAUDE_DIR/agents/$agent_name"

    if [ -L "$target" ]; then
      rm "$target"
    elif [ -f "$target" ]; then
      echo "  Skipping $agent_name (already exists)"
      continue
    fi

    ln -s "$agent_file" "$target"
    echo "  Linked: $agent_name"
  fi
done

# Symlink hooks
echo ""
echo "Linking hooks..."
for hook_file in "$CONFIG_DIR/hooks"/*.sh; do
  if [ -f "$hook_file" ]; then
    hook_name=$(basename "$hook_file")
    target="$CLAUDE_DIR/hooks/$hook_name"

    if [ -L "$target" ]; then
      rm "$target"
    elif [ -f "$target" ]; then
      echo "  Skipping $hook_name (already exists)"
      continue
    fi

    ln -s "$hook_file" "$target"
    chmod +x "$target"
    echo "  Linked: $hook_name"
  fi
done

# Configure hooks in settings.json if not already present
if [ -f "$CLAUDE_DIR/settings.json" ]; then
  if command -v jq &> /dev/null; then
    # Check if hooks are already configured
    has_hooks=$(jq -r '.hooks // empty' "$CLAUDE_DIR/settings.json")
    if [ -z "$has_hooks" ]; then
      echo "  Adding hook configuration to settings.json..."
      jq '.hooks = {
        "SessionStart": [{
          "matcher": "",
          "hooks": [{"type": "command", "command": "'"$CLAUDE_DIR/hooks/session-start.sh"'"}]
        }],
        "UserPromptSubmit": [{
          "matcher": "",
          "hooks": [{"type": "command", "command": "'"$CLAUDE_DIR/hooks/skill-router.sh"'"}]
        }]
      }' "$CLAUDE_DIR/settings.json" > "$CLAUDE_DIR/settings.json.tmp" && \
        mv "$CLAUDE_DIR/settings.json.tmp" "$CLAUDE_DIR/settings.json"
      echo "  Hooks configured in settings.json"
    else
      echo "  Hooks already configured in settings.json"
    fi
  fi
fi

# Install plugins from marketplace
echo ""
echo "Installing plugins..."
PLUGINS_FILE="$CONFIG_DIR/plugins/plugins.json"

if [ -f "$PLUGINS_FILE" ] && command -v claude &> /dev/null; then
  # Check if jq is available for JSON parsing
  if command -v jq &> /dev/null; then
    # First, add the superpowers marketplace if not already added
    echo "  Adding marketplaces..."
    jq -r '.marketplaces[] | "\(.name) \(.url)"' "$PLUGINS_FILE" | while read -r name url; do
      if [ "$name" != "claude-plugins-official" ]; then
        claude plugins add-marketplace "$url" 2>/dev/null || true
      fi
    done

    # Install each plugin
    echo "  Installing plugins..."
    jq -r '.plugins[] | "\(.name)@\(.marketplace)"' "$PLUGINS_FILE" | while read -r plugin; do
      echo "    Installing: $plugin"
      claude plugins install "$plugin" 2>/dev/null || echo "      (already installed or failed)"
    done
  else
    echo "  Warning: jq not installed, skipping plugin installation"
    echo "  Run: brew install jq"
    echo "  Then manually install plugins with: claude plugins install <plugin>@<marketplace>"
  fi
else
  if ! command -v claude &> /dev/null; then
    echo "  Warning: claude CLI not found, skipping plugin installation"
  else
    echo "  Warning: plugins.json not found"
  fi
fi

# Apply settings template if no settings exist
echo ""
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
SETTINGS_TEMPLATE="$CONFIG_DIR/plugins/settings.template.json"

if [ -f "$SETTINGS_TEMPLATE" ]; then
  if [ ! -f "$SETTINGS_FILE" ]; then
    cp "$SETTINGS_TEMPLATE" "$SETTINGS_FILE"
    echo "Applied settings template"
  else
    echo "Settings already exist (not overwriting)"
    echo "  To apply template: cp $SETTINGS_TEMPLATE $SETTINGS_FILE"
  fi
fi

echo ""
echo "Claude Code setup complete!"
echo ""
echo "Skills available:"
ls -1 "$CLAUDE_DIR/skills" 2>/dev/null || echo "  (none)"
echo ""
echo "Agents available:"
ls -1 "$CLAUDE_DIR/agents" 2>/dev/null || echo "  (none)"
echo ""
echo "Hooks installed:"
ls -1 "$CLAUDE_DIR/hooks" 2>/dev/null || echo "  (none)"
echo ""
echo "Use /code-review, /commit-and-pr, etc. to invoke skills"
echo "Agents will be used automatically based on their descriptions"
echo ""
echo "NOTE: The skill router hook requires Ollama with nomic-embed-text."
echo "  Install: https://ollama.com → ollama pull nomic-embed-text"
echo "  Build graph: cd $(dirname "$SCRIPT_DIR")/skill-router && npm install && npm run build && npm run build-graph"
