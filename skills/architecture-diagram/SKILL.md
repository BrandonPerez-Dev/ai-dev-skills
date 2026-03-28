---
name: architecture-diagram
description: >-
  Generate interactive, presentation-quality architecture diagrams rendered in the browser.
  Use when the user asks to visualize system architecture, show how components connect,
  create a diagram for a demo or stakeholder meeting, or display an agent/MCP/service topology.
  Also use when asked to "draw", "diagram", or "visualize" a system. Produces standalone HTML
  with React Flow + custom icon nodes, opens in Chrome for visual verification, and supports
  iterative refinement via screenshot feedback.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Agent
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__new_page
  - mcp__chrome-devtools__list_pages
  - mcp__chrome-devtools__resize_page
  - mcp__chrome-devtools__list_console_messages
---

# Architecture Diagram

Render the system so people can see it. Diagrams are code — generate, view, iterate.

<HARD-GATE>
Do NOT deliver a diagram without viewing it in the browser first. Every diagram must be
screenshot-verified before presenting to the user. Unverified diagrams have layout bugs,
overlapping labels, and broken edges that destroy credibility in a presentation.
</HARD-GATE>

## When to Use

| Situation | Approach |
|-----------|----------|
| User describes a system verbally | Extract components and connections, generate diagram |
| User says "visualize the architecture" | Read relevant code/config to discover the topology, generate diagram |
| User wants to update an existing diagram | Read the current HTML, modify the elements/styles, re-render |
| User asks for a demo-ready visual | Generate diagram with extra polish — title, legend, clean spacing |

## Process

### 1. Gather the Architecture

Identify what to diagram. Sources (in priority order):

- **User's description** — they told you the components and connections
- **Code analysis** — read config files, agent definitions, MCP server registrations, route definitions
- **Existing diagrams** — read a prior HTML diagram and modify it

Extract three things:
- **Nodes**: services, agents, MCP servers, databases, external APIs, UI components
- **Edges**: data flow, API calls, delegations, event streams — with labels
- **Groups**: logical containers (e.g., "Agent Platform" containing subagents, "External Services" containing Twilio/Google)

Assign each node a **type** for color coding and an **icon**. Common types:
- `agent` — AI agents and subagents (indigo, icon: `agent` or `subagent`)
- `mcp` — MCP servers (cyan, icon: `server`)
- `external` — third-party services (emerald, icon: `cloud`)
- `ui` — frontend components (violet, icon: `chat`)
- `data` — databases, storage (red, icon: `database` or `key`)
- `gateway` — routing layers, proxies (orange, icon: `gateway`)

### 2. Generate the HTML

Read `references/reactflow-patterns.md` for the complete template, component patterns, icon library, and CDN URLs.

Generate a standalone HTML file using React Flow + htm (JSX-free React):
- Use esm.sh import maps for React 18, @xyflow/react, and htm
- Define custom `ArchNode` (icon card) and `GroupNode` (dashed container) components
- Position nodes manually in a top-to-bottom hierarchy
- Include a header (title + subtitle) and a color-coded legend
- Use Inter font from Google Fonts for clean presentation

Write the file to `/tmp/architecture-diagram/diagram.html` (or user-specified path).

**Key rules:**
- Every node needs `id`, `type` ('arch' or 'group'), `position`, and `data` with `label`, `icon`, `nodeType`
- Group children use `parentId: 'group-id'` with positions relative to the group
- Groups need explicit `style: { width, height }` — React Flow doesn't auto-size groups
- Edge labels should be short (2-4 words): "API calls", "voice + sms", "OAuth tokens"
- Use invisible handles (transparent, 1px) for clean presentation

### 3. Serve and View

Start a local HTTP server and open the diagram in Chrome:

```bash
# Start server (background, specific port to avoid conflicts)
npx -y serve /tmp/architecture-diagram -p 8789 --no-clipboard &
```

Then use the Chrome DevTools MCP tools:
1. `mcp__chrome-devtools__navigate_page` to `http://localhost:8789/diagram.html`
2. `mcp__chrome-devtools__take_screenshot` to capture the render

If Chrome doesn't have a page open, use `mcp__chrome-devtools__new_page` first, or `mcp__chrome-devtools__list_pages` to find an existing tab.

**If the page is blank**, check `mcp__chrome-devtools__list_console_messages` for errors. Common issues:
- Missing `react-dom` in import map (must include both `react-dom` and `react-dom/client`)
- esm.sh timeout on first load — reload the page

### 4. Verify and Iterate

**CHECKPOINT: Always show the screenshot to the user.**

Look at the screenshot yourself and check:
- Are labels readable and not overlapping?
- Are groups visually containing their children?
- Are edges routing cleanly (no crossing through nodes)?
- Is the layout balanced (not all bunched to one side)?
- Is the legend accurate?
- Are icon boxes rendering with the right colors?

If there are issues, fix them:
- **Overlapping nodes**: Adjust `position` coordinates, increase group `width`/`height`
- **Groups too tight**: Increase group dimensions and child spacing
- **Edge clutter**: Reduce to representative edges, use a single labeled edge per relationship type
- **Missing connections**: Add edges to the initialEdges array

For quick tweaks, use `mcp__chrome-devtools__evaluate_script`:
```js
// React Flow instance isn't globally accessible by default,
// so for structural changes, update the HTML file and reload.
```

For structural changes, update the HTML file and reload.

Re-screenshot after every change. Present the updated screenshot to the user.

### 5. Deliver

When the user approves:
- The HTML file is already saved (shareable, opens in any browser)
- Offer to take a final high-res screenshot for slides
- Offer to move the file to a permanent location if it's in `/tmp/`

## Iterative Refinement

When the user asks for changes ("make MCP servers blue", "add a connection from X to Y", "remove the legend"):

1. Read the current HTML file
2. Make the requested changes
3. Write the updated file
4. Reload the page (`navigate_page` to the same URL)
5. Screenshot and present

## Output Format

Each iteration produces:
1. **The HTML file** at the specified path
2. **A screenshot** shown to the user
3. **A brief description** of what's shown ("Here's your agent platform architecture — the base agent delegates to 3 subagents, each connected to MCP servers through LiteLLM")

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do Instead |
|--------------|-------------|------------|
| Generating HTML without viewing it | Layout bugs are invisible in code | Always screenshot before presenting |
| Too many nodes (30+) | Becomes unreadable | Split into multiple focused diagrams |
| Deep nesting (3+ levels) | Groups overlap, positions break | Max 2 levels of grouping |
| Long edge labels | Overlap and clutter | Keep to 2-4 words |
| No legend | Viewer can't decode the color system | Always include a legend |
| Guessing the architecture | Wrong diagram is worse than no diagram | Read code/config or ask the user |
| Auto-layout expectations | React Flow needs manual positions | Position nodes explicitly in a grid |

## Guidelines

- **Presentation-first.** These diagrams are for demos and meetings, not debugging. Prioritize clarity and visual appeal over completeness.
- **Less is more.** Show the important connections, not every possible one. A clean diagram with 8-12 nodes communicates better than a comprehensive one with 30.
- **Icons add meaning.** Use the icon library to make node types immediately recognizable — servers, clouds, databases, not just colored rectangles.
- **Color means something.** Every color maps to a node type. Don't use color decoratively.
- **Screenshot is truth.** The code might look right but render wrong. Trust the screenshot, not the code.
- **Iterate fast.** Edit the HTML file and reload for all changes. Don't rewrite the whole file to tweak a position.

Follow the communication-protocol skill for all user-facing output and interaction.
