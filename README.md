# AI Workflow Config

Personal AI coding assistant configuration - skills, agents, MCP servers, plugins, and IDE-agnostic instructions.

## Quick Start

```bash
# 1. Clone this repo
git clone https://github.com/BrandonPerez-Dev/ai-dev-skills.git ~/ai-workflow-config

# 2. Install MCP servers
./scripts/install-mcps.sh

# 3. Setup Claude Code (symlinks skills, installs plugins)
./scripts/setup-claude.sh

# 4. Sync instructions to a project
./scripts/sync-to-project.sh /path/to/your/project react-agent
```

## Skill Router (RAG-based)

The skill router uses local Ollama embeddings to match user prompts to the right skill via a graph-based routing system. It runs as a Claude Code `UserPromptSubmit` hook.

### Prerequisites

1. **Install Ollama** — https://ollama.com
2. **Pull the embedding model:**
   ```bash
   ollama pull nomic-embed-text
   ```
3. **Ensure Ollama is running** (it starts automatically on macOS, or run `ollama serve`)

### Setup

```bash
cd skill-router

# Install dependencies
npm install

# Build TypeScript
npm run build

# Generate the skill graph with embeddings (requires Ollama running)
npm run build-graph
```

### How it works

The router maintains a skill graph (`skill-graph.json`) where each skill node has a pre-computed embedding vector. When a user submits a prompt:

1. The prompt is embedded via Ollama's `nomic-embed-text` model
2. Cosine similarity is computed against all skill nodes
3. Top matches above the threshold are returned with graph context (prerequisites, references, macro category)
4. The result is injected as `additionalContext` into Claude Code's hook system

### Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model name |
| `ROUTE_THRESHOLD` | `0.45` | Minimum cosine similarity to match |
| `ROUTE_TOP_K` | `2` | Max number of skill matches returned |

### Rebuilding the graph

Re-run `npm run build-graph` after adding or modifying skills in `src/skill-graph.ts`.

## Structure

```
ai-workflow-config/
├── skills/                 # Reusable skills (~40 skill definitions)
├── skill-router/           # RAG-based skill router (Ollama + graph embeddings)
│   ├── src/                # TypeScript source
│   └── skill-graph.json    # Pre-computed graph with embeddings
│
├── instructions/           # IDE-agnostic canonical instructions
│   ├── base.md             # Core instructions for all projects
│   ├── coding-standards.md # Shared coding standards
│   └── project-types/      # Project-specific additions
│       └── react-agent.md
│
├── agents/                 # Subagent definitions
│   ├── code-reviewer.md
│   ├── researcher.md
│   └── test-runner.md
│
├── plugins/                # Claude Code plugin configuration
│   ├── plugins.json        # Plugins to install from marketplaces
│   └── settings.template.json
│
├── mcp/                    # MCP server configurations
│   ├── servers.json
│   └── setup-guides/
│
├── docs/plans/             # Design documents
│
└── scripts/                # Setup and sync scripts
    ├── install-mcps.sh
    ├── setup-claude.sh
    └── sync-to-project.sh
```

## Skills

40 skills organized into macro categories by the skill router:

| Category | Skills |
|----------|--------|
| **Software Design** | design, architecture, build, ship, tdd, test-planning, ui-ux-design, frontend-build, frontend-design, simplify |
| **Quality** | systematic-debugging, code-review, receiving-code-review, verification |
| **Product** | write-spec, product-definition, technical-breakdown, decompose-tasks |
| **Business** | opportunity-research, opportunity-score, market-analysis, business-case, customer-discovery, experiment-design, innovation-status |
| **AI Engineering** | ai-agent-building, eval-driven-dev, prompt-engineering, tool-discovery, mcp-builder |
| **Infrastructure** | boilerplate-cicd, cloud-infrastructure, git-worktrees |
| **Meta** | skill-creator, skill-eval, skill-maintenance, orchestrator |
| **Delivery** | commit-and-pr, parallel-agents, sp-kanban, kanban-breakdown, docx, xlsx, pdf, pptx, mermaid, presentation, architecture-diagram |
| **Cross-cutting** | research, coding-standards, communication-protocol |

## Plugins

Marketplace plugins installed by `setup-claude.sh`:

| Plugin | Marketplace | Description |
|--------|-------------|-------------|
| `frontend-design` | claude-plugins-official | Production-ready React UI components |
| `context7` | claude-plugins-official | Library documentation lookup |
| `github` | claude-plugins-official | GitHub MCP integration |
| `atlassian` | claude-plugins-official | Jira + Confluence skills |
| `superpowers` | claude-plugins-official | TDD, debugging, code review, planning |
| `superpowers-lab` | superpowers-marketplace | Slack, tmux, MCP CLI, duplicate finder |

## Agents

Subagents for specialized tasks with persistent memory:

| Agent | Description | Memory |
|-------|-------------|--------|
| `code-reviewer` | Reviews code changes, tracks patterns | project |
| `researcher` | Deep codebase exploration | user |
| `test-runner` | Runs tests, analyzes failures | project |

## MCP Servers

Priority order for installation:

1. **shadcn/ui** - Component library integration
2. **Atlassian** - Jira + Confluence
3. **Google Workspace** - Gmail, Drive, Docs, Sheets
4. **GitHub** - Enhanced repo operations
5. **Context7** - Library documentation
6. **Sequential Thinking** - Enhanced reasoning
7. **Document Parser** - PDF/DOCX parsing

## IDE Support

| IDE | Config Location | Sync Command |
|-----|-----------------|--------------|
| Claude Code | `.claude/CLAUDE.md` | `sync-to-project.sh path claude` |
| Cursor | `.cursorrules` | `sync-to-project.sh path cursor` |
| Gemini CLI | `GEMINI.md` + `conductor/` | `sync-to-project.sh path gemini` |
| Codex | `AGENTS.md` | `sync-to-project.sh path codex` |

## Portability

To set up on a new machine:

```bash
# Clone your config
git clone https://github.com/BrandonPerez-Dev/ai-dev-skills.git ~/ai-workflow-config

# Run setup (installs everything)
cd ~/ai-workflow-config
./scripts/setup-claude.sh
./scripts/install-mcps.sh

# Set up skill router
cd skill-router
npm install && npm run build && npm run build-graph
```

This will:
- Symlink all skills to `~/.claude/skills/`
- Symlink all agents to `~/.claude/agents/`
- Install marketplace plugins (requires `jq`)
- Apply settings template if no settings exist
- Build the skill routing graph (requires Ollama)

## License

MIT
