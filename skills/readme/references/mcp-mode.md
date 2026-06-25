# MCP Server README Patterns

Patterns derived from modelcontextprotocol reference servers (filesystem, fetch, memory, git, GitHub) and community MCP servers.

## What Makes MCP READMEs Different

MCP server READMEs serve two audiences simultaneously: **humans** choosing whether to deploy the server, and **agents** that will interact with its tools. The Tools listing is the core documentation — it's the equivalent of an API reference, but optimized for LLM consumption.

## Key Patterns

### Tools Listing as Core Documentation

Replace the "Features" section with a "Tools" section. This is the most important section in an MCP README:

**Simple format (for servers with <10 tools):**
```markdown
## Tools

- **read_file** — Read complete contents of a file from the allowed directories
  - `path` (string, required): Path to the file
- **write_file** — Create or overwrite a file
  - `path` (string, required): Path to the file
  - `content` (string, required): Content to write
- **search_files** — Recursively search for a regex pattern
  - `path` (string, required): Starting directory
  - `pattern` (string, required): Regex pattern to match
  - `excludePatterns` (string[], optional): Patterns to exclude
```

**Grouped format (for servers with 10+ tools):**
```markdown
## Tools

### File Operations
- **read_file** — Read complete contents of a file
- **write_file** — Create or overwrite a file
- **list_directory** — List directory contents

### Search
- **search_files** — Recursively search for a regex pattern
- **grep** — Search file contents with regex

<details>
<summary>Full tool reference with parameters</summary>

[Detailed parameter documentation here]

</details>
```

For servers with 20+ tools, use collapsible `<details>` blocks to keep the README scannable while providing full reference.

### Claude Desktop Config JSON

This is the "getting started" moment for MCP servers — the equivalent of `docker run`:

```markdown
## Quick Start

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

\```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@org/mcp-server-name", "/allowed/path"]
    }
  }
}
\```
```

Show the config block before any installation instructions. The reader needs to understand the integration point before committing.

For servers with authentication:
```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@org/mcp-server-name"],
      "env": {
        "API_TOKEN": "your-token-here"
      }
    }
  }
}
```

### Three-Way Installation

MCP servers should document three installation paths, ordered by speed:

```markdown
## Installation

### npx (no install required)
\```bash
npx -y @org/mcp-server-name
\```

### pip (Python servers)
\```bash
pip install mcp-server-name
python -m mcp_server_name
\```

### Docker
\```bash
docker run -i --rm org/mcp-server-name
\```
```

Key Docker conventions for MCP:
- **Always `-i`** (interactive) — MCP stdio transport requires stdin
- **Always `--rm`** — MCP servers are ephemeral by design
- **Never `-d`** — MCP servers run attached, not daemonized
- Mount volumes for any filesystem access: `-v /host/path:/container/path`

### VS Code / IDE Integration

If the server supports IDE integration, include one-click install badges or config snippets:

```markdown
## VS Code Integration

Install with one click: [Install in VS Code](vscode:...)

Or add to `.vscode/mcp.json`:
\```json
{
  "servers": {
    "my-server": {
      "command": "npx",
      "args": ["-y", "@org/mcp-server-name"]
    }
  }
}
\```
```

### Security Section (Mandatory)

Every MCP server that touches the network, filesystem, or credentials MUST have a security section:

```markdown
## Security

This server can access [what it accesses]. Consider the following:

- **Network access**: The fetch tool can access local/internal IP addresses
- **Filesystem scope**: Only directories passed as arguments are accessible
- **Credential handling**: API tokens are passed via environment variables, never logged
- **Read-only mode**: Use `--read-only` to prevent write operations

Report vulnerabilities to [security contact].
```

### Toolset Feature Flags

For servers with a large tool surface, document optional toolset selection:

```markdown
## Toolset Configuration

By default, all tools are enabled. Restrict to specific toolsets:

\```bash
npx -y @org/mcp-server --toolsets repos,issues
\```

Available toolsets: `repos`, `issues`, `pull_requests`, `actions`, `search`

Or via environment variable:
\```bash
export MCP_TOOLSETS=repos,issues
\```
```

### MCP Inspector for Debugging

Document the standard debugging tool:

```markdown
## Debugging

Use the MCP Inspector to test the server interactively:

\```bash
npx @modelcontextprotocol/inspector npx -y @org/mcp-server-name
\```
```

### Resources and Prompts (if applicable)

If the server exposes MCP resources or prompts in addition to tools, document them in separate sections:

```markdown
## Resources

- `file:///{path}` — File contents for allowed paths
- `memo://insights` — Accumulated knowledge graph

## Prompts

- **summarize** — Generate a summary of collected resources
  - `style` (enum): "brief" | "detailed"
```

## Section Order (MCP-Specific)

```
1. Logo + Badges (npm version, license)
2. Title + one-liner ("An MCP server that provides [capability]")
3. Quick Start (Claude Desktop config JSON)
4. Tools listing (the core section)
5. Installation (npx → pip → docker)
6. IDE Integration (VS Code, JetBrains)
7. Configuration (env vars, flags, toolsets)
8. Resources and Prompts (if applicable)
9. Security (mandatory for network/filesystem/credential access)
10. Debugging (MCP Inspector command)
11. Contributing
12. License
```

## MCP-Specific Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Tools listing without parameter types | Include type, required/optional, and description for every parameter |
| Docker example with `-d` flag | MCP stdio requires attached mode — use `-i --rm`, never `-d` |
| Missing security section | Mandatory for any server touching network, filesystem, or credentials |
| Config JSON without env vars for secrets | Never hardcode tokens in the config example — use `env` block |
| No debugging instructions | Include the MCP Inspector command |
| Generic "Features" section instead of Tools | MCP servers are defined by their tool surface — list tools, not features |
| Missing transport documentation | State which transports are supported (stdio, SSE, streamable-http) |
