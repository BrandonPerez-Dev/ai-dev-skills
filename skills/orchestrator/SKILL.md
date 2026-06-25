
---
name: orchestrator
description: Skill routing and workflow guidance. Invoke when unsure which skill to use, or for detailed guidance on skill sequencing, tiers, and red flags.
---

# Orchestrator

Route to the right skill for each situation. Process skills are mandatory. Domain skills are recommended. Utility skills are available on demand.

## When to Use

- Unsure which skill applies to the current task
- Need guidance on skill sequencing (what comes after what)
- Want to check you're following the right workflow
- Starting a new type of work you haven't done before

## Skill Tiers

### Tier 1: Process Skills — Mandatory When Triggered

These define HOW to approach work. When their trigger condition is met, invoke them. They prevent wasted work downstream.

| Skill | Trigger | What It Does |
|-------|---------|-------------|
| **design** | Non-trivial feature work | Orchestrates research → architecture → test-planning → ui-ux-design. Produces a design doc. |
| **systematic-debugging** | Any bug, test failure, unexpected behavior | 5-phase root-cause-first investigation. No fixes without Phase 1. |
| **research** | Need evidence before a decision | Systematic investigation across codebase, docs, and web. Triangulated findings. |

**These are non-negotiable.** If you're building a feature, use design. If you're fixing a bug, use systematic-debugging. If you need to understand something, use research.

### Tier 2: Domain Skills — Recommended

Orchestrated by process skills or invoked directly for focused work.

| Skill | When |
|-------|------|
| **architecture** | Defining system structure, components, data flow, API contracts |
| **test-planning** | Design-phase: defining vertical slices, integration test contracts, mock boundaries (user validates) |
| **tdd** | Build-phase: red-green-refactor loop, executing against the approved test plan |
| **eval-driven-dev** | Eval suites for AI agents: grader selection, statistical confidence, transcript review |
| **ui-ux-design** | Visual design decisions, interaction patterns, agentic UX |
| **frontend-build** | Implementing UI designs with visual verification. Design decisions → ui-ux-design, implementation → frontend-build. Integrates with browser MCP servers for screenshot-based iteration. |
| **ai-agent-building** | Designing or building AI agent systems |
| **tool-discovery** | Finding MCP servers, APIs worth wrapping, software worth adopting for its API |
| **mcp-builder** | Creating MCP server integrations |
| **boilerplate-cicd** | Project scaffolding, CI/CD setup |
| **code-review** | Reviewing code for correctness, security, performance |
| **receiving-code-review** | Handling code review feedback with technical rigor |
| **prompt-engineering** | Writing effective system prompts, tool descriptions, skill descriptions, and structured context for AI models |
| **skill-creator** | Creating new skills (always research first) |
| **skill-eval** | Testing and validating skills — blind A/B comparison, baseline testing, grading |
| **skill-maintenance** | Evolving existing skills based on learnings |

### Tier 3: Utility Skills — Available on Demand

Reference libraries and format tools. Use when the task calls for them.

| Skill | When |
|-------|------|
| **commit-and-pr** | Staging, committing, pushing, creating PRs |
| **parallel-agents** | Dispatching multiple agents for independent problems |
| **git-worktrees** | Creating isolated workspaces |
| **verification** | Before ANY claim of completion (always) |
| **communication-protocol** | Referenced by other skills — not invoked directly |
| **docx, xlsx** | Working with specific file formats |
| **decompose-tasks** | Breaking designs into actionable tasks |
| **kanban-breakdown** | Structuring task lists into kanban cards |

### Product & Business Skills

| Skill | When |
|-------|------|
| **write-spec** | Formalizing requirements into a product spec |
| **product-definition** | Personas, user stories, MVP scope |
| **technical-breakdown** | Converting product spec to technical architecture |
| **opportunity-research** | Evaluating whether an idea is worth pursuing |
| **opportunity-score** | Scoring opportunities against a framework |
| **market-analysis** | TAM/SAM/SOM and competitive landscape |
| **business-case** | Building an investment case |
| **customer-discovery** | Synthesizing customer research |
| **experiment-design** | Designing experiments to test assumptions |
| **innovation-status** | Portfolio status reports |

## Pipelines

Skills connect in natural sequences. Don't skip steps.

### Feature Development
```
design → build → ship → commit-and-pr
```
Design orchestrates research, architecture, test-planning, and ui-ux-design internally. Build executes the design using tdd. Ship delivers it.

### Bug Investigation
```
systematic-debugging → [fix] → verification
```
If the code is unfamiliar, systematic-debugging's Phase 0 will direct you to use research. After fixing, always verify.

### Skill Creation
```
research → tool-discovery → prompt-engineering + skill-creator
```
Research the problem space first. Discover tools that could expand the skill's capabilities. Use prompt-engineering for writing effective descriptions and instructions. Use skill-creator for structure, methodology, and quality evaluation.

### Product to Engineering
```
product-definition → design → (write-spec → PR review → technical-breakdown → PR review) → decompose-tasks → build
```
The engineering skill orchestrates slicing and test-planning with review gates between them. Slice specs go in `spec/`.

### Opportunity Evaluation
```
opportunity-research → market-analysis → customer-discovery → experiment-design → business-case → opportunity-score
```

## Red Flags

If you catch yourself thinking any of these, stop and route to the right skill:

| Thought | Reality | Route To |
|---------|---------|----------|
| "This is a simple feature, skip design" | Design catches hidden complexity. If there is none, design finishes fast. | **design** |
| "I know how to fix this bug" | Knowing symptoms ≠ understanding root cause. | **systematic-debugging** |
| "Let me just write the code" | Process skills prevent rework. Use them. | **design** or **research** |
| "Quick fix, no need for investigation" | Quick fixes mask root causes and create tech debt. | **systematic-debugging** |
| "I'll review it later" | Review is cheaper than debugging. Do it now. | **code-review** |
| "It should work now" | "Should" is not evidence. Run verification. | **verification** |
| "I remember how this works" | Systems evolve. Verify your assumptions. | **research** |
| "I'll just commit this" | Follow the ship process. Tests, review, clean history. | **ship** |
| "Let me create this skill quickly" | Research the problem space first. Better input = better skill. | **research** → **skill-creator** |

## Process-First Principle

When multiple skills could apply, process skills run first:

1. **Process skills** (design, systematic-debugging, research) — determine HOW to approach the task
2. **Domain skills** (architecture, test-planning, tdd, ui-ux-design) — guide specific aspects of execution
3. **Utility skills** (commit-and-pr, file tools) — provide tools for specific operations

"Let's build X" → design first, then domain skills during build.
"Fix this bug" → systematic-debugging first, then fix.
"I need to understand Y" → research first, then decide next steps.

## Skill Types

**Rigid** (systematic-debugging, verification, tdd): Follow the process exactly. The discipline IS the value. Don't adapt away the rigor.

**Flexible** (research, architecture, design): Adapt the depth to the complexity. A simple question gets a quick lookup. A complex system gets a full investigation.

**Orchestrating** (design, build): These invoke other skills internally. Let them manage the sub-skill sequencing.

## Guidelines

- **Route, don't guess.** Use the routing table above. If unsure, invoke this skill.
- **Process skills are mandatory.** They prevent wasted work. Invoke them even when the task seems simple.
- **Let orchestrating skills manage sub-skills.** Design invokes research and architecture internally — you don't need to invoke them separately when using design.
- **Verify before claiming done.** Every time. No exceptions.
