# MCP Server Setup for Frontend Build

Install and configure the MCP servers that power the frontend-build skill's visual verification loop and design system integration.

## Priority Order

Install in this order — each level adds capability:

1. **Browser MCP** (enables visual verification loop) — highest impact
2. **shadcn/ui MCP** (prevents component hallucination) — high impact
3. **Figma MCP** (design tokens from source of truth) — high impact if using Figma
4. **Storybook MCP** (pattern documentation) — nice to have

---

## 1. Chrome DevTools MCP

**What it does:** 29 tools for browser automation, screenshots, console inspection, Lighthouse audits, viewport resizing, and performance profiling.

**Why it matters:** This gives the agent eyes. It can take screenshots of its work, check the console for errors, run accessibility audits, and test responsive layouts.

### Install (Claude Code)

```bash
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest
```

### Install (settings.json)

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### All 29 Tools

**Input automation (9):** `click`, `drag`, `fill`, `fill_form`, `handle_dialog`, `hover`, `press_key`, `type_text`, `upload_file`

**Navigation (6):** `close_page`, `list_pages`, `navigate_page`, `new_page`, `select_page`, `wait_for`

**Emulation (2):** `emulate`, `resize_page`

**Performance (4):** `performance_analyze_insight`, `performance_start_trace`, `performance_stop_trace`, `take_memory_snapshot`

**Network (2):** `get_network_request`, `list_network_requests`

**Debugging (6):** `evaluate_script`, `get_console_message`, `lighthouse_audit`, `list_console_messages`, `take_screenshot`, `take_snapshot`

### Most Used by Frontend-Build

| Tool | Purpose |
|------|---------|
| `navigate_page` | Open the dev server URL |
| `take_screenshot` | Capture current page state |
| `resize_page` | Test responsive breakpoints (375, 768, 1280) |
| `list_console_messages` | Check for runtime errors |
| `lighthouse_audit` | Accessibility and performance scoring |
| `hover` | Verify hover states render correctly |
| `evaluate_script` | Run JS assertions on the rendered DOM |
| `take_snapshot` | Get DOM snapshot for structural verification |
| `emulate` | Simulate device presets (iPhone, iPad, etc.) |

---

## 2. Playwright MCP (Alternative to Chrome DevTools)

**What it does:** Browser automation with accessibility-first approach. Default mode uses structured accessibility snapshots (cheaper, faster than screenshots).

**Why it matters:** Cross-browser testing (Chrome, Firefox, WebKit). Accessibility snapshots tell you what a screen reader sees — excellent for a11y verification.

### Install (Claude Code)

```bash
claude mcp add playwright -- npx @playwright/mcp@latest
```

### Install (settings.json)

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

### Options

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--image-responses", "allow"
      ]
    }
  }
}
```

- `--image-responses allow` — Include screenshot images in responses (uses more tokens)
- Default mode returns accessibility snapshots (structured JSON, token-efficient)

### Key Tools

| Tool | Purpose |
|------|---------|
| `Playwright_navigate` | Open URL |
| `Playwright_screenshot` | Capture page as image |
| `Playwright_resize` | Change viewport dimensions |
| `Playwright_click` | Interact with elements |
| `Playwright_hover` | Trigger hover states |
| `Playwright_fill` | Fill form inputs |
| `Playwright_evaluate` | Run JS in browser context |
| `Playwright_console_logs` | Read console output |
| `playwright_get_visible_text` | Get rendered text content |
| `playwright_get_visible_html` | Get rendered HTML |

> **Note:** Microsoft's official `@playwright/mcp` may expose ~70 tools with different naming. The names above are from the ExecuteAutomation implementation. Check your actual server's tool list with `claude mcp list` after installation.

---

## 3. shadcn/ui MCP

**What it does:** Live component registry access. Browse, search, and inspect actual component props and available blocks.

**Why it matters:** Prevents the #1 AI frontend failure: hallucinating component props that don't exist.

### Install (Claude Code)

```bash
npx shadcn@latest mcp init --client claude
```

### Install (settings.json)

```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

### Key Tools

| Tool | Purpose |
|------|---------|
| `list-components` | List all available shadcn/ui components |
| `get-component-docs` | Get component documentation, props, and usage |
| `install-component` | Install a component into your project |
| `list-blocks` | List available pre-built block patterns |
| `get-block-docs` | Get block documentation and composition examples |
| `install-blocks` | Install block patterns into your project |

### Usage Pattern

Before using any shadcn/ui component, query the MCP:
1. Search for the component by name
2. Read its actual prop signature
3. Use only the props that exist

**Never assume a prop exists.** If the MCP says Button has `variant`, `size`, and `asChild` — those are the only options.

---

## 4. Figma MCP

**What it does:** Extract design tokens, component specs, visual references, and code mappings directly from Figma files.

**Why it matters:** Design tokens from the source of truth. No guessing at colors, spacing, or typography. Visual reference screenshots for comparison.

### Install

The Figma MCP server has two connection modes:

**Remote (no Figma app required):**
```json
{
  "mcpServers": {
    "figma": {
      "url": "https://mcp.figma.com/v1"
    }
  }
}
```

**Desktop (through Figma app):**
Follow the setup at https://developers.figma.com/docs/figma-mcp-server/

### All 13 Tools

| Tool | Purpose |
|------|---------|
| `get_variable_defs` | Extract design tokens: colors, spacing, typography, radius |
| `get_design_context` | Component styling/layout (React + Tailwind by default) |
| `get_screenshot` | Visual reference from Figma for comparison |
| `get_code_connect_map` | Map Figma components → codebase implementations |
| `add_code_connect_map` | Add new component-to-code mappings |
| `generate_figma_design` | Capture live web UI and send to Figma |
| `create_design_system_rules` | Define design system constraints |
| `get_metadata` | File and project metadata |
| `get_figjam` | Access FigJam board content |
| `generate_diagram` | Create diagrams in Figma |
| `whoami` | Check authenticated user |
| `get_code_connect_suggestions` | Get suggested code mappings |
| `send_code_connect_mappings` | Push code mappings to Figma |

### Best Results from Figma

For the Figma MCP to produce the best output:
- Use Figma Variables for all styling decisions (primitives for colors, spacing, radius, typography)
- Use Auto Layout on all containers (maps to CSS flexbox)
- Name layers descriptively (hierarchical: `Group.Input.Label`)
- Set up Code Connect to link Figma components to your React components

---

## 5. Storybook MCP

**What it does:** Serve component documentation, states, and patterns to AI agents.

**Why it matters:** Shows how components are actually used in your project — states, composition, edge cases.

### Install

**As Storybook addon:**
```bash
npx storybook@latest add @storybook/addon-mcp
```

**Standalone:**
```json
{
  "mcpServers": {
    "storybook": {
      "command": "npx",
      "args": ["@storybook/mcp"]
    }
  }
}
```

### Key Tools

| Tool | Purpose |
|------|---------|
| `get_ui_building_instructions` | Get component documentation, patterns, and building guidelines |
| `get_story_urls` | Get URLs to view specific component stories |

---

## Recommended Configurations

### Full Setup (Best Quality)

All servers — design tokens from Figma, component specs from shadcn, visual verification from Chrome DevTools:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    },
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    },
    "figma": {
      "url": "https://mcp.figma.com/v1"
    },
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

### Minimal Setup (Visual Loop Only)

Just browser automation — the highest-impact single addition:

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": ["-y", "chrome-devtools-mcp@latest"]
    }
  }
}
```

### No MCP Fallback

If no MCP servers are configured, the frontend-build skill falls back to:
- Playwright Python scripts via the webapp-testing skill patterns
- Manual token extraction from ui-ux-design specs
- Code review only (no visual verification)

This works but produces lower quality. At minimum, install Chrome DevTools MCP.
