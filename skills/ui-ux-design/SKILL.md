
---
name: ui-ux-design
description: Modern UI/UX design principles for AI applications. Use when making visual design decisions, choosing interaction patterns, or defining the look and feel of a frontend. Focuses on cutting-edge design trends and agentic UX patterns. Design theory, not code generation.
allowed-tools:
  - Read
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Task
---

# UI/UX Design

Guide design decisions for modern AI application interfaces. Design theory, visual trends, interaction patterns, and design system decisions — not code generation.

**Always research current trends before recommending.** Visual design moves fast. Web search for what's current, don't rely on stale knowledge.

## When to Use

- Choosing the visual direction for a new UI
- Designing interaction patterns for AI-driven workflows
- Evaluating existing UI against modern standards
- Making animation, layout, typography, or color decisions
- Designing human-in-the-loop interfaces

## Agentic UX Patterns

AI interfaces require specific patterns that traditional UI doesn't. These six patterns cover the full interaction lifecycle:

### Pre-Action: Establishing Intent

**Intent Preview** — Before the agent acts, show a plain-language plan of what it will do. Offer "Proceed," "Edit Plan," or "Handle it Myself." Critical for irreversible actions.

**Autonomy Dial** — Let users calibrate agent independence per task type:
- Observe & Suggest → Plan & Propose → Act with Confirmation → Act Autonomously
- Trust is a spectrum, not a switch. Start supervised, earn autonomy.

### In-Action: Providing Context

**Explainable Rationale** — Link actions to user preferences: "Because you said X, I did Y." Ground decisions in stated rules, not opaque reasoning.

**Confidence Signal** — Surface uncertainty visually. Green for high confidence, yellow for low. Prevents automation bias — users need to know when to pay closer attention.

### Post-Action: Safety and Recovery

**Action Audit & Undo** — Chronological log of everything the agent did. Persistent undo buttons with clear time windows. The ability to reverse is the ultimate safety net.

**Escalation Pathway** — Agents don't guess in ambiguous situations. They escalate: request clarification, present options, or involve humans. A well-designed agent asks rather than assumes.

## Progressive Disclosure for AI

AI generates a lot. Don't show it all at once.

- **Summary first** — drill into details on demand
- **Streaming text** — word-by-word responses show the system is working and let users start processing before completion
- **Stage indicators** — "Researching..." "Reasoning..." "Generating..." reduces uncertainty
- **Expandable reasoning** — collapsible sections for agent logic and source attribution
- **Skeleton loading** — match final layout shape, not generic spinners

## Visual Design Direction

### The "Linear" Aesthetic

The dominant visual language for modern dev tools and AI apps. Key principles:

**Linearity** — Sequential, logical progression. No zig-zagging content. Single-dimension scrolling. Minimal choices per screen. Reduces cognitive load.

**Restraint** — Monochrome base (near-black/white) with very few bold accent colors. More content = simpler gradients. Every element justified, nothing decorative without purpose.

**Typography** — Bold display type for headings (Inter Display or equivalent), regular weight for body. Large headings, tight line-height. Monospace for data and code, proportional for prose.

**Dark mode first** — Not pure black. Use your brand color at 1-10% lightness for warmth. Improve contrast by making text and icons lighter than you think. Light mode as secondary.

### Depth & Dimension

**Dark glassmorphism** — frosted glass over ambient gradients:
- `backdrop-filter: blur(12px)` on semi-transparent backgrounds (`bg-white/[0.05]`)
- 1px border (`border-white/[0.1]`) as light-catcher
- Ambient gradient orbs behind UI (deep purples, neon blues) — never solid black backgrounds
- Fallback: `bg-gray-900/90` for browsers without backdrop-filter support

**Layered shadows** — at least two shadow layers (ambient + direct light). Combine borders with shadows for edge clarity.

### Motion & Animation

**Spring physics** over linear easing — feels natural, not mechanical.
- 150–250ms for micro UI changes (hover, toggle, badge)
- 250–400ms for context switches (modals, page transitions)
- Motion library (formerly Framer Motion) for React spring animations

**Stagger animations** for lists — items enter sequentially, not all at once.

**Shimmer/pulse loading** — not spinners. Match the shape of the content that's loading.

**Always respect `prefers-reduced-motion`** — skip or reduce animations for users who request it.

### Layout

- Card-based with generous whitespace
- Collapsible sidebar navigation
- Split-pane for detail views (list + detail)
- Responsive: cards reflow, not just stack

## Component Stack

The modern AI app component stack:
- **shadcn/ui** — copy-paste components you own, built on Radix primitives
- **Radix UI** — handles accessibility, keyboard nav, focus management, ARIA
- **Tailwind CSS** — utility-first styling with design token theming
- **Motion** (Framer Motion) — spring animations, layout transitions, gestures

shadcn/ui is AI-friendly because the source lives in your codebase — full context for modification.

## Reference Apps

Study these for current visual language:
- **Linear** — linearity, restraint, bold typography, dark glassmorphism
- **Vercel** — pure blacks/whites, layered shadows, functional minimalism
- **Cursor** — IDE-native AI integration, dual-pane layouts
- **ChatGPT** — streaming UX, conversation patterns, model switching
- **v0** — generative UI, code preview patterns

## Process

1. **Research** current trends — web search for AI app design patterns, check reference apps
2. **Check** project's existing design system and conventions
3. **Recommend** specific patterns with rationale and reference to research
4. **Be specific** — exact timing, exact colors, exact component names

## Output

```markdown
## Design Direction
[1-2 sentences on the visual approach and why]

## Agentic UX Patterns
- **Pattern** — Where to use, why it works for this feature

## Visual Treatment
- **Typography:** [Font, sizes, weights]
- **Color:** [Palette, accent strategy, dark mode approach]
- **Depth:** [Glass, shadows, borders]

## Component Recommendations
- **Component** — Visual treatment, interaction behavior

## Animation Notes
- [Specific: "Card hover: scale(1.02), spring 200ms. List enter: stagger 50ms delay per item."]

## Accessibility
- [Reduced motion handling, contrast ratios, keyboard nav]
```

## Guidelines

- **Research before recommending.** Web search for what's current. Trends shift fast.
- **Be specific.** "Spring animation on card hover, scale(1.02), 200ms" not "use animations."
- **Respect existing design system.** Enhance it, don't contradict it.
- **Dark mode first.** Light mode as secondary.
- **Performance matters.** CSS transforms over layout changes. GPU-composited animations. No jank.
- **Accessibility always.** `prefers-reduced-motion`, WCAG contrast ratios, keyboard nav, screen reader support.
