---
name: presentation
description: >-
  Design and build browser-rendered scrollable presentations for demos, meetings,
  and stakeholder updates. Produces a single-page HTML/CSS layout with styled sections,
  embedded diagrams (via architecture-diagram skill), and syntax-highlighted code blocks.
  Use when the user needs to present, demo, or walk through something visually — whether
  for engineers (dark theme) or business audiences (light theme).
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Skill
  - Agent
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_screenshot
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__new_page
  - mcp__chrome-devtools__list_pages
  - mcp__chrome-devtools__resize_page
  - mcp__chrome-devtools__list_console_messages
---

# Presentation

Design the page. Let the content breathe. Scroll down to present.

<HARD-GATE>
Do NOT deliver a presentation without viewing it in the browser first. Every page must be
screenshot-verified before presenting to the user. Unverified pages have broken layouts,
unreadable code blocks, and styling bugs that destroy credibility in front of an audience.
</HARD-GATE>

## When to Use

| Situation | Approach |
|-----------|----------|
| Technical demo for engineers | Dark theme, code-heavy, real project code, diagrams |
| Executive update or business audience | Light theme, narrative-heavy, minimal code, more visuals |
| Show-and-tell / ways of working | Mix of narrative, diagrams, and illustrative code |
| Meeting walkthrough | Structured sections with clear progression |

## Theme Selection

The first decision. Get this wrong and the audience tunes out before you start.

| Audience | Theme | Why |
|----------|-------|-----|
| Engineers, technical ICs | Dark | Familiar environment, code reads naturally, less eye strain |
| Business stakeholders, executives | Light | Professional, readable in bright rooms, no "hacker" vibes |
| Mixed audience | Light | Default to the less technical audience's preference |

## Section Types

Every presentation is a sequence of sections. Each section type has a job. Use the right one.

| Type | Job | When |
|------|-----|------|
| **Hero** | Set context — title, subtitle, one sentence | Opening. Sometimes mid-deck to introduce a new act. |
| **Narrative** | Explain something — headline + short paragraphs | Connective tissue between visuals. Keep paragraphs to 2-3 sentences. |
| **Diagram** | Show architecture or flow | Delegate to `architecture-diagram` skill. Embed as `<img>` with caption. |
| **Code** | Show real code with syntax highlighting | When illustrating how something works. Title explains what to look at. 15 lines max. |
| **Comparison** | Side-by-side contrast | Showing trade-offs, before/after, or two approaches |
| **Callout** | Emphasize a key insight or quote | Sparingly — one per 4-5 sections. Visually distinct from narrative. |

### Section Pacing

- Open with a Hero
- Alternate between narrative and visual sections (diagram, code, comparison)
- Never stack two narrative sections — put a visual between them
- Never stack two diagrams — put narrative context between them
- End with a clear "what's next" narrative section
- Callouts break rhythm intentionally — use for the one thing you want remembered

## Process

### 1. Understand the Presentation

Before writing HTML, answer:
- **Who is the audience?** (determines theme, code density, jargon level)
- **What's the one thing they should remember?** (this becomes the callout)
- **How long do you have?** (determines section count — roughly 1-2 min per section)
- **What do they need to see vs. hear?** (diagrams and code go on screen, explanation is verbal)

### 2. Outline the Sections

Draft a section list with types. Present it to the user for validation before building.

```
1. Hero — title, context
2. Narrative — the problem / why this matters
3. Diagram — system overview (architecture-diagram skill)
4. Narrative — how it works (bridge to code)
5. Code — illustrative snippet
6. Callout — the key insight
7. Narrative — what's next
```

**CHECKPOINT:** Present the outline. "Here's the flow I'm thinking. Does this match your talk track?"

### 3. Generate Diagrams

For any diagram sections, invoke the `architecture-diagram` skill to produce React Flow diagrams. Take screenshots and save them as images to embed in the presentation.

Diagrams are separate artifacts. The presentation embeds them as `<img>` tags with appropriate sizing and captions.

### 4. Build the HTML

Read `references/scrollable-template.md` for the complete HTML/CSS template.

Generate a standalone HTML file with:
- CSS variables for theme (swap between dark and light)
- Inter font from Google Fonts
- Styled sections using the section type patterns
- Syntax-highlighted code blocks (highlight.js from CDN for code sections)
- Responsive layout (readable on laptop screens and projectors)

Write to `/tmp/presentation/deck.html` (or user-specified path).

**Key layout rules:**
- Max content width: 800px, centered (readable line length)
- Section spacing: generous — 80-120px between sections
- Code blocks: slightly different background from page, monospace font, 16-18px size
- Diagrams: full content width, with caption below
- Typography: 3:1 ratio headers to body (e.g., 36px / 12px or 42px / 14px)

### 5. Serve and View

```bash
npx -y serve /tmp/presentation -p 8790 --no-clipboard &
```

Use Chrome DevTools MCP:
1. `mcp__chrome-devtools__navigate_page` to `http://localhost:8790/deck.html`
2. `mcp__chrome-devtools__take_screenshot` to verify
3. Scroll through sections using `evaluate_script`:
   ```js
   window.scrollTo({ top: document.querySelector('#section-3').offsetTop, behavior: 'smooth' })
   ```

### 6. Verify and Iterate

Screenshot the page at multiple scroll positions. Check:
- Is text readable at presentation distance?
- Do code blocks have proper syntax highlighting?
- Are diagram images loading and sized correctly?
- Is section spacing consistent?
- Does the theme feel right for the audience?

Fix issues by editing the HTML and reloading.

## Orchestration

The presentation skill designs the page. Other skills produce components:

| Component | Skill | How |
|-----------|-------|-----|
| Architecture diagrams | `architecture-diagram` | Invoke skill → get screenshot → embed as `<img>` |
| Content research | `research` | Invoke when building content from unfamiliar material |
| Code selection | Direct file reads | Read from the actual project codebase |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do Instead |
|---|---|---|
| Wall of text in a section | Audience stops reading | 2-3 sentences per paragraph, max 2 paragraphs per narrative section |
| Code dump (30+ lines) | Nobody reads it on screen | Show the interesting 10-15 lines, explain the rest verbally |
| Diagram without context | Audience doesn't know what they're looking at | Narrative section before every diagram explaining what to notice |
| Dark theme for business audience | "Looks like a hacker tool" complaints | Light theme for non-technical audiences, always |
| Stacking same section types | Monotonous rhythm | Alternate between narrative and visual sections |
| No "what's next" ending | Presentation just stops | Always end with direction and next steps |
| Skipping browser verification | Broken layout in front of audience | Screenshot-verify every time |

## Guidelines

- **The scroll is the pacing.** Each section is a beat. The presenter scrolls to advance. This gives natural pausing and lets the audience absorb.
- **Less text, more visual.** If you can show it in a diagram or code block, don't describe it in a paragraph.
- **Real code from the real project.** Don't write example code for presentations. Pull actual snippets from the codebase and highlight the interesting part.
- **One idea per section.** If you're explaining two things, make two sections.
- **Diagrams are first-class.** Don't treat them as decoration. Each diagram should teach the audience something specific.
- **The presenter carries the detail.** The page shows the structure; the human fills in the nuance. Don't try to put everything on screen.

Follow the communication-protocol skill for all user-facing output and interaction.
