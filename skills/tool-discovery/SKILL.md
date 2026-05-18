
---
name: tool-discovery
description: >-
  Scout for tools that expand capabilities — existing MCP servers, APIs worth wrapping,
  and software worth adopting for its API. Use when building or improving skills/agents,
  exploring what integrations could transform a workflow, or when a task would benefit
  from external tools. Finds existing MCP servers, identifies APIs that could be wrapped,
  and discovers software worth installing specifically for its programmable interface.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Skill
---

# Tool Discovery

The right tool changes what's possible. Scout for it before building without it.

<HARD-GATE>
Don't just search for tools that match what the user already does. Search broadly — the highest-value discoveries are often systems nobody has heard of yet, adopted specifically because they have a great API. Super Productivity wasn't adopted for task management. It was adopted because it has a local REST API that could be wrapped in an MCP server. Think like that.
</HARD-GATE>

## Method Selection

| Situation | Approach | Depth |
|-----------|----------|-------|
| Building a new skill/agent | Full discovery: all three search layers | Deep — this shapes the skill's capability ceiling |
| Improving an existing skill | Gap analysis: what's the skill struggling with that a tool could solve? | Medium — targeted search for specific gaps |
| User asks "what tools for X?" | Focused search: MCP registries + API directories | Medium — present options with trade-offs |
| Exploring a domain | Broad scouting: what exists in this space? | Wide — cast a broad net, then narrow |
| Evaluating a specific tool | Single-tool deep dive: docs, API quality, maturity | Deep but narrow |

## The Three Search Layers

Tool discovery works in layers, from easiest to most creative:

### Layer 1: Existing MCP Servers (ready to install)

These are tools someone has already built. Search for them first.

**Where to search** (see `references/search-strategies.md` for concrete URLs and commands):
- MCP registries (PulseMCP, Official Registry, Glama, Smithery, etc.)
- npm (`npm search "mcp <domain>"`)
- GitHub topics (`mcp-server`, `mcp-servers`)
- Claude Code plugins marketplace
- Awesome-MCP curated lists

**What to look for:**
- Does a server exist for this exact domain?
- Is it maintained? (last commit, open issues, stars)
- Does it cover the specific tools/capabilities needed?
- Is it stdio (local) or HTTP (remote)? Does that matter for this use case?

### Layer 2: APIs Worth Wrapping (needs mcp-builder)

Many services have APIs but no MCP server yet. These are opportunities.

**Where to search:**
- "best `<domain>` tools with API" — find software with REST/GraphQL APIs
- "`<service name>` API documentation" — check if a known service has an API
- API directories (RapidAPI, APIs.guru, ProgrammableWeb)
- Developer docs of popular tools in the domain

**What to look for:**
- REST or GraphQL API (easiest to wrap)
- Good API documentation (reduces build effort)
- Authentication simplicity (API key > OAuth for MCP wrappers)
- Rate limits and pricing (free tier? reasonable limits?)
- The API surface matches what the skill/agent needs

**Evaluation shortcut:** If the API has a well-documented REST endpoint and you can test it with curl, it's wrappable. If it requires complex OAuth flows, SDK-only access, or webhook-based patterns, the wrapper will be harder.

### Layer 3: Software Worth Adopting (the creative leap)

This is where the real value is. Some software is worth installing *because* of its API, even if the user doesn't currently use it.

**The question to ask:** "If I needed `<capability>` and also needed it to be programmable, what software exists that was built API-first?"

**Search strategies:**
- "open source `<domain>` with REST API" — find self-hosted tools with APIs
- "self-hosted `<domain>` alternative" — self-hosted tools often have APIs for automation
- "`<domain>` software local API" — find desktop/local tools with APIs
- "headless `<domain>` tool" — headless tools are inherently API-driven
- Product Hunt / AlternativeTo / awesome-selfhosted — browse by category

**Examples of this pattern:**
- **Super Productivity** — adopted for task management because it runs locally with a REST API. Now wrapped in a custom MCP server for kanban management.
- **Obsidian** — note-taking app with a local REST API plugin. Could be wrapped for knowledge management.
- **Home Assistant** — home automation with a REST API. Could give agents control over physical devices.
- **n8n / Activepieces** — workflow automation with APIs. Could let agents trigger complex workflows.

**What makes software worth adopting for its API:**
- Runs locally (no cloud dependency, no latency, no cost)
- Has a REST API (not just a CLI or GUI)
- Solves a real capability gap (not just "nice to have")
- Is actively maintained
- The API covers the operations the skill/agent would need

## Process

### 1. Define the Capability Gap

Before searching, articulate what you're looking for:
- What would this skill/agent do if it had the perfect tool?
- What's currently impossible or painful without a tool?
- What domain does this operate in?

Frame it as: "I need a tool that can `<verb>` `<noun>` with `<constraints>`."

### 2. Audit What's Already Installed

Don't suggest what the user already has.

```bash
# Check Claude Code MCP servers
claude mcp list

# Check global MCP config
cat ~/.mcp.json

# Check project-level MCP config
cat .mcp.json

# Check Claude Code plugins
# Look at ~/.claude/settings.json → enabledPlugins

# Check what MCP tools are available in current session
# (the available-deferred-tools list in conversation context)
```

### 3. Search All Three Layers

Run searches across all three layers in parallel when possible. See `references/search-strategies.md` for concrete search commands and registry URLs.

**For each candidate found, capture:**
- Name and source (registry URL, npm package, GitHub repo)
- What it does (1-2 sentences)
- Install method (npm, GitHub clone, manual setup)
- Layer (existing MCP / API to wrap / software to adopt)
- Maturity signal (stars, last update, docs quality)

### 4. Evaluate Candidates

Score each candidate on:

| Dimension | Question |
|-----------|----------|
| **Capability match** | Does it actually do what the skill/agent needs? |
| **Setup effort** | How hard is it to install and configure? |
| **Maintenance burden** | Is it actively maintained? Will it break? |
| **API quality** | Good docs? Consistent responses? Error handling? |
| **Value-add** | How much does it expand what's possible? |

**Kill criteria** (skip if any are true):
- Last commit > 12 months ago with open issues
- No documentation for the API
- Requires enterprise license for API access
- The capability can be achieved with existing built-in tools

### 5. Present Recommendations

Group findings by action required:

```markdown
## Ready to Install
[MCP servers that exist and can be installed now]
- **tool-name** — what it does. Install: `claude mcp add ...` or `npm install ...`

## Worth Building (route to mcp-builder)
[APIs that exist but have no MCP server]
- **service-name** — has a REST API at [url]. Could wrap for [capability].
  Effort: [low/medium/high]. Value: [description].

## Worth Adopting
[Software to install specifically for its API]
- **software-name** — [what it is]. Has a [type] API that could be wrapped for [capability].
  Why: [what makes it worth adopting].

## Not Recommended
[Things considered but rejected, with reasons]
```

### 6. Act on Recommendations

After presenting recommendations, ask the user what to pursue:
- **Ready to install** → offer to install it right now
- **Worth building** → invoke the **mcp-builder** skill
- **Worth adopting** → explain what the user needs to download/install, then offer to build the wrapper

## Communication Pattern

When you find something worth recommending, use `AskUserQuestion` to confirm before acting:

"I found [tool] that would give this skill [capability]. It's [ready to install / would need an MCP wrapper / is software worth adopting for its API].

Want me to [install it / build a wrapper / explain the setup]?"

Don't silently add tools. Tool installation affects the user's environment — always confirm.

## Bias Guards

| Trap | Antidote |
|------|----------|
| **Only searching Layer 1** | Force yourself through all three layers. The best finds are often in Layer 3. |
| **Familiarity bias** | Don't recommend tools you've heard of. Search for tools you haven't. |
| **Complexity bias** | Simple tools with good APIs beat complex platforms. A local REST API > a cloud service with OAuth. |
| **Sunk cost** | Don't recommend building a wrapper when an existing MCP server does 80% of what's needed. |
| **Tool hoarding** | More tools != better. Only recommend tools that solve a real capability gap. Agents degrade above ~15 tools. |

## Guidelines

- **Layer 3 is the differentiator.** Anyone can search npm for MCP servers. Finding software worth adopting for its API — that's the creative leap that gives you capabilities nobody else has.
- **API quality > feature count.** A tool with 5 well-documented endpoints beats one with 50 undocumented ones.
- **Local > cloud for MCP.** Local APIs have no latency, no cost, no auth complexity. Prefer self-hosted and local tools when they exist.
- **Always audit first.** Suggesting a tool the user already has wastes credibility and time.
- **Confirm before installing.** Tool installation changes the user's environment. Present options, let the user choose.
