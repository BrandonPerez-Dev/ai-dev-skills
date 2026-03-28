---
name: cli-builder
description: >-
  Build CLI tools optimized for AI agent consumption. Use when creating a new
  CLI that agents will call via Bash, wrapping a REST API as a CLI, or
  converting an existing MCP server to CLI. Covers command design, auth
  integration, output formatting, and agent-specific patterns backed by
  research. Routes to tool-discovery first.
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

# CLI Builder

Design CLIs that agents call via Bash. The agent's experience of your CLI IS the command surface, help text, output format, and error messages.

Research reference: `references/research.md` — benchmarks, papers, and evidence behind every design rule in this skill.

<HARD-GATE>
Before building a new CLI, check if one already exists. Invoke **tool-discovery** to search npm, GitHub, and official vendor CLIs. If an official CLI exists (like `gws` for Google, `twilio` for Twilio), use it — don't rebuild. Only build a custom CLI when the vendor has no CLI or the existing one is unsuitable for agent use.
</HARD-GATE>

## Why CLI Over MCP

Evidence-based (see research reference for full citations):
- **10-30x fewer tokens** per task vs MCP (Scalekit benchmark: 1,365–9,386 vs 32,279–82,835)
- **100% vs 72% success rate** in head-to-head benchmarks
- **No schema bloat** — agent only pays context cost for commands it actually runs
- **Flat flags: +18.4 pp accuracy** over nested JSON (NLT paper, 6,400 trials)
- **Agents are excellent at Bash** — no additional tooling needed

## Process

### 1. Check Existing CLIs

Invoke **tool-discovery**. Search for:
- Official vendor CLI (npm, homebrew, apt)
- Community CLIs wrapping the same API
- The API's own documentation quality (REST? SDK? OpenAPI spec?)

If a CLI exists, evaluate: does it output structured data? Can it accept auth via env var or config file? Is it agent-friendly?

### 2. Map the API Surface

Before designing commands, understand the API:
- What resources exist? (customers, invoices, files, etc.)
- What CRUD operations per resource?
- What's the auth mechanism? (OAuth, API key, bearer token)
- What are the API quirks? (pagination, rate limits, required fields, query language)

If converting from an existing MCP server, extract the API patterns from the tool handlers.

### 3. Design the Command Surface

**CHECKPOINT: Present command surface to user before implementing.**

```
<cli-name> <resource> <verb> [flags]

Examples:
  qbo customers search --name "Smith" --limit 10
  qbo customers get 12345
  qbo invoices create --customer 12345 --item 789 --qty 2 --price 100
  qbo invoices context 12345    # consolidated: invoice + customer + payments
```

#### Command Design Rules (Research-Backed)

**Flat flags over nested JSON (mandatory):**
- Nested JSON causes 17-37% accuracy degradation at 5+ levels (DeepJSONEval)
- Flat flags: +18.4 pp accuracy over JSON schema (NLT paper)
- Every common operation MUST have flat flag equivalents
- `--json` as escape hatch for complex edge cases only

**Consolidate operations:**
- Multi-step tool chains have significantly higher error rates (BFCL)
- Build `context` commands that return related data in one call
- `qbo customer context 123` > agent calling `get` + `list invoices` + `list payments` separately

**5-15 commands max per CLI:**
- More = agent confusion and selection errors
- Group by resource: `<cli> <resource> <verb>`
- Common verbs: `search`, `get`, `create`, `update`, `delete`, `context`

**Self-documenting:**
- `<cli> --help` — list resources
- `<cli> <resource> --help` — list verbs and flags
- `<cli> <resource> <verb> --help` — detailed usage with examples
- Agent can self-serve docs at runtime (zero upfront context cost)

### 4. Design Output Format

**Default: human-readable (mandatory):**
Research shows human-readable output is more accurate for agent reasoning:
- Markdown tables use 34-38% fewer tokens than JSON with higher accuracy
- JSON output reduces reasoning accuracy by up to 27.3 pp (Tam et al.)
- TSV uses 50% fewer tokens than JSON for tabular data

```
# Default (search results):
ID      Name          Email               Status
12345   Smith LLC     smith@example.com   Active
12346   Smith & Co    info@smithco.com    Active

# Default (single entity):
Customer: Smith LLC (ID: 12345)
Email: smith@example.com
Phone: (555) 123-4567
Status: Active
Balance: $2,100.00
Last Invoice: 2026-03-15

# With --json flag:
{"Id":"12345","DisplayName":"Smith LLC",...}

# With --raw flag (full API response):
{"QueryResponse":{"Customer":[...],"totalCount":2}}
```

**Output format rules:**
- Default to clean tables for lists, key-value for single entities
- `--json` for machine-readable (when agent needs to pipe data)
- `--raw` for unmodified API response (debugging)
- `--format <table|json|csv|raw>` for explicit control
- Cap list output at sensible defaults (25 rows), with `--limit` override
- For large responses, paginate — don't dump everything

**Error messages must be actionable:**
```
# Bad:
Error: 404

# Good:
Customer "Smithh" not found. Similar matches:
  - Smith LLC (ID: 12345)
  - Smith & Co (ID: 12346)
Use: qbo customers search --name "Smith"
```

### 5. Design Auth Integration

The CLI must work with the credential vault. Two patterns:

**Pattern A: Environment variable (recommended for our CLIs)**
```bash
# Vault injects before exec:
QBO_ACCESS_TOKEN=ya29... QBO_REALM_ID=123456 qbo invoices search
```
- CLI reads token from env var
- Vault handles refresh — CLI always gets a fresh token
- Simplest pattern, works everywhere

**Pattern B: Config file (for third-party CLIs)**
```bash
# Seed at container start:
# Write ~/.config/<cli>/credentials.json from vault
gws gmail users messages list --params '...'
```
- CLI manages own token refresh from config
- Only viable when CLI has built-in refresh (like `gws`)

**Auth check pattern:**
```typescript
function getAuth(): { token: string; realmId: string } {
  const token = process.env.QBO_ACCESS_TOKEN;
  const realmId = process.env.QBO_REALM_ID;
  if (!token || !realmId) {
    console.error(
      'Not authenticated. Set QBO_ACCESS_TOKEN and QBO_REALM_ID, ' +
      'or connect QuickBooks in the agent platform.'
    );
    process.exit(1);
  }
  return { token, realmId };
}
```

### 6. Scaffold the Project

```bash
mkdir <cli-name> && cd <cli-name>
npm init -y
npm install commander zod
npm install -D typescript vitest @biomejs/biome tsx
```

**File structure:**
```
src/
  index.ts          # CLI entry point (commander setup)
  commands/
    customers.ts    # customer subcommands
    invoices.ts     # invoice subcommands
    ...
  api/
    client.ts       # API client (auth, base URL, headers)
    types.ts        # API response types
  format/
    table.ts        # table formatter
    json.ts         # JSON output
  lib/
    auth.ts         # auth from env/config
    errors.ts       # error formatting
```

**Package.json bin entry:**
```json
{
  "bin": { "<cli-name>": "dist/index.js" }
}
```

### 7. Implement

**Order:**
1. Auth + API client (can you make an authenticated API call?)
2. One `search` command end-to-end (proves the full path)
3. One `get` command (single entity)
4. Output formatters (table, json)
5. Remaining CRUD commands
6. `context` consolidated commands
7. Error handling + actionable messages
8. `--help` text for every command

**API client pattern:**
```typescript
class ApiClient {
  constructor(
    private baseUrl: string,
    private token: string,
    private realmId: string,
  ) {}

  async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${this.baseUrl}/v3/company/${this.realmId}/${path}`);
    if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${this.token}`, Accept: 'application/json' },
    });
    if (!res.ok) throw new ApiError(res.status, await res.text());
    return res.json() as T;
  }

  async post<T>(path: string, body: unknown): Promise<T> { /* similar */ }
  async query<T>(sql: string): Promise<T> { /* for search */ }
}
```

### 8. Test

- **Unit tests:** API client, formatters, auth parsing
- **Integration tests:** Full command → mock API → formatted output
- **Agent smoke test:** Can the agent call `<cli> --help`, discover commands, and complete a task?

### 9. Register for Agent Use

Add to the agent's system prompt (in `prompts.ts` or equivalent):
```
QUICKBOOKS ACCESS:
You have the "qbo" CLI for QuickBooks Online. Use it via Bash.
Usage: qbo <resource> <verb> [flags]
Resources: customers, invoices, estimates, bills, vendors, employees, items
Run "qbo --help" for full usage.
```

Do NOT pre-load all command documentation — let the agent discover via `--help` at runtime.

## Anti-Patterns

| Anti-Pattern | What Happens | Instead |
|---|---|---|
| Nested JSON as primary input | 17-37% accuracy degradation | Flat flags, --json as escape hatch |
| JSON as default output | 2x tokens, lower reasoning accuracy | Human-readable tables, --json opt-in |
| Too many commands | Agent confusion, wrong command selection | 5-15 commands, consolidate with `context` |
| Pre-loading all docs in prompt | Wastes context, distractors degrade perf | `--help` at runtime, minimal prompt mention |
| Generic error messages | Agent can't self-correct | Actionable: suggest specific fix command |
| Building CLI for API that has one | Wasted effort | tool-discovery first, use official CLI |
| Refresh logic in CLI | Complexity, failure modes | Vault handles refresh, CLI gets fresh token via env |
| No --help per command | Agent can't self-serve documentation | Comprehensive --help with examples on every command |

## Quality Checklist

Before shipping, verify:

- [ ] Every common operation has flat flag equivalents (not just --json)
- [ ] Default output is human-readable (tables for lists, key-value for entities)
- [ ] --json flag available for machine-readable output
- [ ] --help on every command with usage examples
- [ ] Auth via environment variable (or config file for third-party CLIs)
- [ ] Errors are actionable with suggested fix commands
- [ ] `context` command consolidates related data for key resources
- [ ] List commands have sensible defaults and --limit flag
- [ ] Exit codes: 0 = success, 1 = error
- [ ] Agent smoke test: agent can discover and use the CLI without pre-loaded docs

Follow the **communication-protocol** skill for all user-facing output and interaction.
