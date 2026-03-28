---
name: frontend-build
description: Implement UI designs with visual verification. Takes ui-ux-design output and produces working, visually-verified frontend components. Uses MCP servers for design context (Figma, shadcn/ui) and screenshot-based iteration (Chrome DevTools, Playwright). Constraints over adjectives, verification over hope.
allowed-tools:
  # Core tools
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - WebSearch
  - WebFetch
  # Chrome DevTools MCP — visual verification loop (server name: chrome-devtools)
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__resize_page
  - mcp__chrome-devtools__list_console_messages
  - mcp__chrome-devtools__get_console_message
  - mcp__chrome-devtools__lighthouse_audit
  - mcp__chrome-devtools__hover
  - mcp__chrome-devtools__click
  - mcp__chrome-devtools__fill
  - mcp__chrome-devtools__fill_form
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__emulate
  - mcp__chrome-devtools__wait_for
  - mcp__chrome-devtools__new_page
  - mcp__chrome-devtools__close_page
  - mcp__chrome-devtools__list_pages
  - mcp__chrome-devtools__select_page
  # Playwright MCP — browser automation and accessibility snapshots (server name: playwright)
  - mcp__playwright__Playwright_navigate
  - mcp__playwright__Playwright_screenshot
  - mcp__playwright__Playwright_resize
  - mcp__playwright__Playwright_click
  - mcp__playwright__Playwright_hover
  - mcp__playwright__Playwright_fill
  - mcp__playwright__Playwright_select
  - mcp__playwright__Playwright_evaluate
  - mcp__playwright__Playwright_console_logs
  - mcp__playwright__Playwright_close
  - mcp__playwright__playwright_get_visible_text
  - mcp__playwright__playwright_get_visible_html
  # Figma MCP — design tokens and visual reference (server name: figma)
  - mcp__figma__get_variable_defs
  - mcp__figma__get_design_context
  - mcp__figma__get_screenshot
  - mcp__figma__get_code_connect_map
  - mcp__figma__add_code_connect_map
  - mcp__figma__generate_figma_design
  - mcp__figma__create_design_system_rules
  - mcp__figma__get_metadata
  - mcp__figma__get_code_connect_suggestions
  - mcp__figma__send_code_connect_mappings
  # shadcn/ui MCP — component registry (server name: shadcn)
  - mcp__shadcn__list-components
  - mcp__shadcn__get-component-docs
  - mcp__shadcn__install-component
  - mcp__shadcn__list-blocks
  - mcp__shadcn__get-block-docs
  - mcp__shadcn__install-blocks
  # Storybook MCP — component patterns and documentation (server name: storybook)
  - mcp__storybook__get_ui_building_instructions
  - mcp__storybook__get_story_urls
---

# Frontend Build

Faithfully implement UI designs with visual verification. This skill takes the design spec produced by ui-ux-design and turns it into working, production-quality components — then verifies they actually look right.

**This is an implementation skill, not a design skill.** Design decisions (visual direction, interaction patterns, component choices) come from ui-ux-design. This skill implements them with fidelity.

## When to Use

- Implementing UI components from a design spec or ui-ux-design output
- Building pages or layouts that need to match a visual reference
- During the build skill's execution of frontend slices
- Any frontend work where visual quality matters

## What This Skill Is NOT

- Not a design skill — ui-ux-design handles visual decisions
- Not a creativity prompt — no "be bold" or "pick an extreme"
- Not subjective — quality gates are measurable
- Does not invent colors, fonts, spacing, or component props

---

## Phase 1: Gather Design Context

Before writing any code, collect concrete constraints. Query available sources in priority order:

### Source 1: MCP Servers (Best)

Check what's available and use it:

**Figma MCP** — Design tokens and visual reference
- `get_variable_defs` → color palette, spacing scale, typography, border radius
- `get_design_context` → component styling and layout (returns React + Tailwind by default)
- `get_screenshot` → visual reference for layout verification
- `get_code_connect_map` → maps Figma components to codebase implementations

**shadcn/ui MCP** — Live component specs (prevents prop hallucination)
- Browse available components and blocks
- Search by functionality
- Get actual prop signatures — never guess component APIs

**Storybook MCP** — Pattern documentation
- Component states (default, hover, loading, error, disabled)
- Composition examples
- Usage patterns from existing codebase

### Source 2: UI/UX Design Spec (Good)

If no design MCP servers are available, extract tokens from the ui-ux-design output's **Visual Treatment** section:

```markdown
## Visual Treatment
- **Typography:** [Font, sizes, weights] → extract into type scale
- **Color:** [Palette, accent strategy] → extract hex values
- **Depth:** [Glass, shadows, borders] → extract shadow/border tokens
```

### Source 3: Existing Codebase (Baseline)

Always check regardless of other sources:
- `tailwind.config.*` or `@theme` block in CSS — existing design tokens
- `components/ui/` — existing component patterns
- `globals.css` or theme files — CSS variables already defined

### Phase 1 Output

A concrete token set. Not adjectives — values:

```
Colors:    --primary: #1a1a2e, --accent: #e94560, --surface: #16213e
Typography: Display: Inter Display 600/2rem, Body: Inter 400/1rem, Mono: JetBrains Mono 400/0.875rem
Spacing:   4px grid → 4, 8, 12, 16, 24, 32, 48, 64
Radius:    --radius-sm: 4px, --radius-md: 8px, --radius-lg: 12px
Components: Button, Card, Input, Dialog (from shadcn/ui — verified via MCP)
```

If you can't produce this token set, you don't have enough context. Ask the user or query more sources before proceeding.

---

## Phase 2: Implement

Build with constraints, not creativity. Every visual decision references a token.

### Tech Stack

- **React 19+** with functional components and hooks
- **TypeScript** with strict types
- **Tailwind CSS v4** with `@theme` directive for design tokens
- **shadcn/ui** for base components (query MCP for actual props)
- **Motion** (Framer Motion) for animations per design spec
- **Radix UI** for accessibility primitives

### Rules

**Colors** — Only use colors from the token set. If you need a shade, derive it from a token (e.g., `primary/80` for 80% opacity). Never pick a random hex value.

**Spacing** — Only use values from the spacing scale. No `p-[13px]` or `mt-[7px]`. Stick to the grid: `p-2` (8px), `p-3` (12px), `p-4` (16px).

**Typography** — Only use the type scale from the token set. Don't invent font sizes or weights.

**Components** — If using shadcn/ui, query the MCP server for actual prop signatures. If no MCP available, read the component source in `components/ui/`. Never assume props exist — verify.

**Interaction States** — Every interactive element needs: default, hover, focus, active, disabled. If the design spec includes loading states, implement those too.

**Animations** — Implement exactly what the ui-ux-design spec says. Typical defaults:
- Hover: `scale(1.02)`, spring 200ms
- Enter: `opacity 0→1, y 20→0`, spring 300ms
- List: stagger 50ms per item
- Always wrap in `prefers-reduced-motion` check

**Responsive** — Mobile-first. Breakpoints: `sm:640px`, `md:768px`, `lg:1024px`, `xl:1280px`. Test at minimum 3 widths: 375px, 768px, 1280px.

### Component Template

```typescript
import { cn } from '@/lib/utils';

interface ComponentProps {
  className?: string;
  // typed props — never `any`
}

export function Component({ className, ...props }: ComponentProps) {
  return (
    <div className={cn(
      // Base styles using design tokens
      'bg-surface text-foreground rounded-md p-4',
      // Interaction states
      'hover:bg-surface/80 focus-visible:ring-2 focus-visible:ring-accent',
      // Responsive
      'w-full md:w-auto',
      className
    )}>
      {/* content */}
    </div>
  );
}
```

---

## Phase 3: Visual Verification Loop

**This is what makes this skill work.** After implementing, you MUST see what you built.

### Prerequisites

Check for available browser MCP tools:
- **Chrome DevTools MCP**: `take_screenshot`, `navigate_page`, `resize_page`, `list_console_messages`, `lighthouse_audit`, `hover`, `evaluate_script`
- **Playwright MCP**: `Playwright_screenshot`, `Playwright_navigate`, `Playwright_resize`, `Playwright_console_logs`, `playwright_get_visible_text`

> **Note on MCP tool names:** The full tool name follows the pattern `mcp__<server-name>__<tool-name>`. The server names above assume you followed the naming in `mcp-setup.md`. If you named your servers differently, the tool prefix changes accordingly.

If neither is available, fall back to the **webapp-testing skill** patterns: write a Playwright Python script using `scripts/with_server.py` to manage the dev server and take screenshots.

If no browser tools at all: warn the user that visual verification is skipped. Rely on code review only.

### The Loop

```
1. Ensure dev server is running
   - Check if already running (curl localhost:PORT)
   - If not, start via `npm run dev` or framework equivalent
   - Wait for ready (HMR/hot reload enabled)

2. Navigate to the page/component
   - Chrome DevTools: navigate_page → URL
   - Playwright: browser_navigate → URL
   - Wait for networkidle / load complete

3. Take screenshot at desktop width (1280px)
   - Chrome DevTools: resize_page(1280, 800) → take_screenshot
   - Playwright: browser_resize → browser_take_screenshot

4. Evaluate against quality gates (see below)
   - Check each gate
   - Note specific failures

5. If failures found:
   - Fix the specific issue in code
   - Dev server hot-reloads
   - Return to step 3

6. Take responsive screenshots
   - Mobile (375px): resize → screenshot → evaluate
   - Tablet (768px): resize → screenshot → evaluate

7. Check console and accessibility
   - Chrome DevTools: list_console_messages → check for errors
   - Chrome DevTools: lighthouse_audit → accessibility score
   - Fix any issues found

8. When all gates pass → done
```

**Max iterations: 5.** If you can't pass quality gates in 5 visual iterations, stop and show the user what you have. Something deeper is wrong.

### Quality Gates

Each gate is pass/fail. No subjective judgment.

| Gate | How to Check | Pass Criteria |
|------|-------------|---------------|
| **Token fidelity** | Inspect screenshot colors/spacing against token set | All visible colors match tokens. Spacing follows grid. |
| **Visual hierarchy** | Screenshot shows clear heading/body/accent distinction | Primary content is immediately identifiable |
| **Responsive** | Screenshots at 375px, 768px, 1280px | No horizontal overflow. Content readable at all sizes. Layout adapts. |
| **Interaction states** | Use hover/focus tools or inspect CSS | Hover, focus, disabled states all defined and visible |
| **Console clean** | `list_console_messages` or equivalent | Zero errors. Warnings reviewed (not all must be fixed). |
| **Accessibility** | Lighthouse audit or manual check | Score ≥ 90. Proper ARIA labels. Keyboard navigable. Contrast ≥ 4.5:1. |
| **Design match** | Compare screenshot to Figma screenshot or design spec | Layout, spacing, typography match the reference |

### Webapp-Testing Fallback

If no browser MCP servers are available but Playwright is installed locally, use the webapp-testing skill's patterns:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1280, "height": 800})
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')

    # Desktop screenshot
    page.screenshot(path='/tmp/desktop.png', full_page=True)

    # Mobile screenshot
    page.set_viewport_size({"width": 375, "height": 812})
    page.screenshot(path='/tmp/mobile.png', full_page=True)

    # Tablet screenshot
    page.set_viewport_size({"width": 768, "height": 1024})
    page.screenshot(path='/tmp/tablet.png', full_page=True)

    browser.close()
```

Then read the screenshot files to visually evaluate them.

Use `scripts/with_server.py` if the dev server isn't already running:
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python screenshot_check.py
```

---

## Phase 4: Quality Gate

Before claiming this frontend work is done:

- [ ] All visual quality gates from Phase 3 pass
- [ ] Console has no errors
- [ ] Responsive at 375px, 768px, 1280px — verified with screenshots
- [ ] Accessibility audit ≥ 90 (if available)
- [ ] Component props match actual library API (verified via MCP or source)
- [ ] Animation respects `prefers-reduced-motion`
- [ ] Matches ui-ux-design spec's component recommendations
- [ ] All TypeScript types are strict (no `any`)

---

## Anti-Patterns

These are the specific failure modes this skill prevents:

| Anti-Pattern | What Happens | Prevention |
|--------------|-------------|------------|
| **Inventing colors** | Random hex values that don't match the design | Only use tokens from Phase 1 |
| **Hallucinating props** | `<Button loading={true}>` that doesn't exist | Query shadcn/ui MCP or read component source |
| **Skipping visual check** | Code "looks right" but renders wrong | Phase 3 is mandatory, not optional |
| **Random spacing** | `p-[13px]`, `mt-7`, inconsistent gaps | Only use spacing scale values |
| **Missing states** | Buttons with no hover, inputs with no focus ring | Interaction states checklist per element |
| **No responsive** | Looks great at 1280px, broken at 375px | Screenshot at 3 breakpoints minimum |
| **Creativity over fidelity** | "I made it more interesting" when spec said otherwise | Implement the spec. Creative decisions belong in ui-ux-design. |
| **Blind coding** | Writing 200 lines without seeing the result | Visual loop after every meaningful change |

---

## Integration with Build Skill

When the build skill encounters a frontend slice:

1. Build skill handles the full slice (route → service → data → UI)
2. For the UI layer, follow this skill's phases:
   - Phase 1: Gather tokens (may already be established from a prior slice)
   - Phase 2: Implement the component/page
   - Phase 3: Visual verification loop
   - Phase 4: Quality gate
3. Build skill continues with its own verification checklist

The design tokens from Phase 1 persist across slices — gather once, reuse throughout.

---

## MCP Server Reference

See `mcp-setup.md` for installation and configuration of recommended MCP servers.

**Graceful degradation order:**
1. **Full setup** (Figma + shadcn/ui + Chrome DevTools): Best quality — design tokens from source of truth, live component specs, full visual loop
2. **Partial setup** (shadcn/ui + Playwright): Good quality — component awareness, screenshot verification
3. **Minimal setup** (Playwright only): Adequate — visual verification without design system context
4. **No MCP**: Baseline — code review only, warn user that visual verification is skipped

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **Tokens, not adjectives.** Every visual choice references a concrete value.
- **Verify, don't assume.** Take screenshots. Read console output. Run audits. Evidence over confidence.
- **Implement the spec.** The ui-ux-design skill made the creative decisions. This skill executes them faithfully.
- **Query before guessing.** If an MCP server can tell you the actual prop signature, use it. Don't hallucinate APIs.
- **5 iterations max.** If the visual loop isn't converging, stop and show the user. Something structural is wrong.
- **Degrade gracefully.** Use whatever tools are available. More tools = better quality, but the skill works at every level.
- **Mobile first.** Build for 375px, enhance for larger screens. Don't bolt on responsiveness after the fact.
