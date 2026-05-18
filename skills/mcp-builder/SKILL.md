
---
name: mcp-builder
description: >-
  Build MCP servers — from local productivity tools to production agent infrastructure.
  Use when wrapping an API, local app, or service as an MCP server. Covers the full
  lifecycle: check existing, design tool surface, choose pattern, implement, test, register.
  Routes to tool-discovery first. Scales rigor based on server type (local vs production).
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Skill
---

# MCP Builder

Design the tool surface before writing code. The agent's experience of your MCP server IS the tool descriptions.

<HARD-GATE>
Before building a new MCP server, check if one already exists. Invoke the **tool-discovery** skill to search MCP registries, npm, and GitHub. If a server exists that covers 80%+ of your needs, use it or fork it — don't rebuild from scratch. Only proceed to build when nothing suitable exists or the existing options have disqualifying issues (security, maintenance, wrong transport).
</HARD-GATE>

## Server Type Selection

Not every MCP server needs the same rigor. Choose the type first — it determines the pattern, testing, and infrastructure.

| Type | When | Example | Pattern |
|------|------|---------|---------|
| **Local utility** | Wrapping a local app or API for personal productivity | superproductivity-mcp | Direct implementation, stdio, minimal structure |
| **Production agent** | Part of the agent platform, serves end users through the agent | google-ads-mcp, banking-mcp | Full pattern: dual-mode, provider, auth, registry |
| **Shared team tool** | Used by team members but not customer-facing | internal dashboard MCP | Provider pattern, basic tests, .mcp.json |

**Ask the user which type if unclear.** This determines everything downstream.

### What Each Type Requires

| Concern | Local Utility | Shared Team | Production Agent |
|---------|--------------|-------------|-----------------|
| Dual-mode (mock/live) | No | Optional | **Required** |
| Provider pattern | No | Yes | **Required** |
| Result type | Optional | Yes | **Required** |
| Auth integration | No (local) | Token/env var | **credential-vault + gateway** |
| Testing | Manual / light | Unit tests | **Unit + integration** |
| Tool registry | No | .mcp.json | **LiteLLM + role-scoped** |
| Error mapping | Console errors fine | Basic codes | **Domain-specific codes** |
| Transport | Stdio | Stdio | **Stdio (dev) + HTTP (deployed)** |
| Mock data | Not needed | Optional | **Domain-specific, realistic** |

## Process

### 1. Check Existing Servers

Invoke **tool-discovery** skill. Search for:
- Official MCP servers for the service (npm, GitHub)
- Community implementations (PulseMCP, Glama, MCP Registry)
- The service's own API quality (REST? GraphQL? SDK?)

**If a server exists:** Evaluate it — does it cover the tools you need? Is it maintained? Is the code quality acceptable? Present findings to user with a recommendation: use as-is, fork, or build new.

**If nothing exists:** Proceed to step 2.

### 2. Design the Tool Surface

This is the most important step. The tool surface is how the agent experiences your server. Bad tool descriptions = unreliable agent behavior. Good descriptions = 40%+ reliability improvement.

For each tool, define:

```markdown
### Tool: [name]
**Purpose:** [What it does in one sentence]
**When the agent should use it:** [Trigger condition]
**Parameters:**
- `param_name` (type, required/optional): [Description with format example]
**Returns:** [Shape of the response]
**Errors:** [What can go wrong and what the error looks like]
```

**Tool description rules:**
- Lead with WHEN to use, not what it does technically
- Include format examples in parameter descriptions: `"date in YYYY-MM-DD format"`
- Document what the response looks like so the agent can parse it
- Add a `detail_level` parameter for tools that return large responses
- Keep tool count low — 5-10 tools is ideal. More = agent confusion.

**CHECKPOINT: Present the tool surface to the user.**

"Here are the tools I'm planning to expose:
1. **tool_name** — [purpose]
2. **tool_name** — [purpose]

Does this cover what the agent needs? Missing anything? Any tools that should be combined or split?"

### 3. Choose Transport

| Transport | Use When | Setup |
|-----------|----------|-------|
| **Stdio** | Local utility, local dev, single-user | Entry point calls `StdioServerTransport` |
| **HTTP** | Deployed, multi-tenant, behind gateway | Hono server, LiteLLM routes to it |

Most servers need stdio. Only add HTTP when deploying behind the agent platform's gateway.

### 4. Scaffold the Project

Use the **boilerplate-cicd** skill or scaffold manually:

```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript vitest @biomejs/biome tsx
```

Choose the file structure based on server type — see `references/patterns.md` for both structures.

### 5. Implement Mock First (Production/Shared Only)

For production and shared servers, build the mock adapter first:

1. Define the provider interface (one interface, all methods return `Promise<Result<T>>`)
2. Implement `MockAdapter` with realistic fixture data
3. Wire up tool handlers that delegate to the provider
4. Register tools in `server.ts` with the descriptions from step 2
5. Test manually — can the agent call the tools and get sensible responses?

**Mock adapter must be complete** — every method, every tool works. This is your development environment and your demo environment.

For local utility servers, skip the provider pattern — tool handlers can call the API/service directly.

### 6. Implement Live Adapter (Production/Shared Only)

1. Build the API client (constructor-injected, testable)
2. Implement `LiveAdapter` — same interface as mock
3. Add response mapper (`mapper.ts`) — transform API responses to domain types
4. Map all API errors to domain-specific error codes via `fail()`
5. Add `createProvider()` factory that switches on `MODE` env var

**Never expose raw API errors to the agent.** Always map to domain codes: `ITEM_NOT_FOUND`, `AUTH_EXPIRED`, `RATE_LIMITED`, not `HTTP 404`.

### 7. Test

Testing strategy scales with server type:

**Local utility:** Manual testing. Does it work when you call it? Good enough.

**Shared team:**
- Unit tests for any non-trivial logic
- Smoke test: can a client call each tool and get a valid response?

**Production agent:**
- Unit tests for provider methods (mock and live adapters separately)
- Unit tests for response mappers
- Integration tests: tool handler → provider → mock data (end-to-end through the MCP layer)
- Test error paths: what happens when the API returns errors?

```typescript
// Example: integration test for a tool
describe('get_campaigns tool', () => {
  it('returns campaigns through mock provider', async () => {
    const provider = new MockAdapter();
    const server = createMcpServer(provider);
    // Call the tool through the MCP server
    // Assert response shape matches tool description
  });
});
```

### 8. Register and Configure

**Local utility:**
```json
// ~/.mcp.json
{
  "mcpServers": {
    "my-tool": {
      "command": "npx",
      "args": ["tsx", "/path/to/src/index.ts"]
    }
  }
}
```

**Production agent:**
- Add to tool registry (`registry.json`) with tier, auth_provider, transport
- Configure role-scoped access (`roles.json`)
- Register in LiteLLM MCP gateway config
- Add credential-vault provider entry if auth needed

## Tool Description Quality Checklist

Run this checklist on every tool before shipping. Tool descriptions are the #1 lever for agent reliability.

- [ ] Description starts with WHEN to use, not implementation details
- [ ] Every parameter has a type, required/optional flag, and format example
- [ ] Response shape is documented or inferable from the description
- [ ] Error cases are mentioned ("Returns error if X")
- [ ] No jargon the agent won't understand — write for a smart non-expert
- [ ] Name is verb_noun format: `get_campaigns`, `create_task`, `list_accounts`
- [ ] If response can be large, there's a `detail_level` or `limit` parameter

## Anti-Patterns

| Anti-Pattern | What Happens | Instead |
|--------------|-------------|---------|
| Building without checking existing | Weeks of work duplicating an official server | tool-discovery first, always |
| Vague tool descriptions | Agent calls the wrong tool or passes wrong params | Format examples, trigger conditions, response shapes |
| Business logic in tool handlers | Untestable, unmockable, duplicated between tools | Thin handlers → delegate to provider |
| Skipping mock adapter | Can't develop or demo without live credentials | Mock first, live second |
| Too many tools | Agent gets confused, picks wrong tool | 5-10 tools max. Combine related operations. |
| Raw API errors to agent | Agent can't interpret HTTP 422 or stack traces | Domain error codes: `ITEM_NOT_FOUND`, `RATE_LIMITED` |
| In-memory substitutes in tests | SQLite for Postgres, fake Redis | Test against real dependencies or mock at adapter boundary |
| Over-engineering local utilities | Provider pattern for a personal productivity wrapper | Match rigor to server type |

## Recommended Tools

**Ready now (no account needed):**
- **Semgrep MCP** — security scan your MCP server code before shipping
- **@djankies/vitest-mcp** — test runner with coverage for your MCP server tests

**When available:**
- **GitHub MCP** — PR workflow for MCP server repos

## Guidelines

- **Check existing before building.** The hard gate is not optional. tool-discovery runs first.
- **Tool descriptions are the product.** The agent never sees your code — it sees your tool names, descriptions, and parameter schemas. Invest the most time here.
- **Match rigor to server type.** Local utility = just make it work. Production agent = full pattern. Don't over-engineer personal tools. Don't under-engineer production ones.
- **Mock first, live second.** For production servers, the mock adapter is your dev environment, your demo environment, and your test fixture. Build it first.
- **Thin tool handlers.** Validate args, call provider, format response. That's it. Business logic lives in the provider.
- **Domain error codes.** The agent understands `CAMPAIGN_NOT_FOUND`. It doesn't understand `AxiosError: Request failed with status code 404`.
