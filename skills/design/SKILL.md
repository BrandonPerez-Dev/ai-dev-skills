---
name: design
description: Collaborative design phase — research the landscape, plan constraints and verticals, define test contracts, then transition to build. Lightweight orchestrator for non-trivial features. Invokes research, plan, architecture, test-planning, and ui-ux-design as needed.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Task
  - Skill
---

# Design

Lightweight orchestrator for the design phase. Research what you need to know, plan what you're building, start building as soon as the first verticals are ready.

<HARD-GATE>
Do NOT write implementation code during design. The output is a plan, not code.
</HARD-GATE>

<HARD-GATE>
Do NOT invoke build until at least one vertical has done criteria AND a test contract validated by test-planning. Confirm with the user before transitioning.
</HARD-GATE>

<HARD-GATE>
Do NOT skip test-planning. Every vertical needs user-validated integration test contracts with explicit mock boundaries before it is "ready." Verticals without test contracts are headlines, not ready verticals.
</HARD-GATE>

## When to Use

Use when 2 or more of these apply:

- Uncertainty about the right approach warrants investigation
- Work touches multiple layers, repos, or services
- Cross-cutting concerns (security, performance, accessibility) need consideration
- Integration with unfamiliar systems or APIs
- Teammate alignment is needed before coding

**Skip design** if the solution is obvious — go directly to build. Skip to **plan** if you already understand the landscape and just need to define the work.

## Scale the Effort

| Complexity | Design Effort | Example |
|---|---|---|
| **Small** | Skip design, go to plan or build directly | Add a new API field, simple CLI command |
| **Medium** | Quick research → plan | New endpoint with service logic, API integration |
| **Large** | Full research → architecture → plan | Multi-service integration, new system |

Default to **medium**. Escalate if you discover unexpected complexity.

## Flow

### 1. Research (if needed)

Invoke the **research** skill when you need to understand:
- Existing codebase patterns and conventions
- External libraries, APIs, or services involved
- Similar implementations for reference
- Technical feasibility of an approach

**For agent/MCP systems:** also invoke **tool-discovery** to find existing MCP servers or APIs worth wrapping.

Present findings as:
1. **Decision-relevant facts** (what changes our approach)
2. **Risks or unknowns** discovered
3. **Recommendation** with rationale

**Check in:** "Here's what I found — does this change our approach?"

### 2. Plan

Invoke the **plan** skill to produce the feature plan:
- Discovers architectural constraints through conversation
- Defines verticals with done criteria
- Saves to `specs/NNN-<topic>/plan.md`

During planning, invoke utility skills as needed:
- **architecture** — for complex structural decisions, API contracts, data flow
- **ui-ux-design** — for visual direction and interaction patterns
- **ai-agent-building** — for agent orchestration, tool design, model selection

Invoke these *during* the plan conversation only when a specific question needs deeper thinking. Do NOT run them as mandatory separate phases.

### 3. Test Planning (mandatory)

Invoke the **test-planning** skill after verticals are defined. This is NOT optional — verticals are not ready without validated test contracts.

Test-planning will:
- Define integration test contracts for each vertical (setup, action, input, expected output, side effects, error cases)
- Establish mock boundaries (controlled deps = real, uncontrolled deps = mock at adapter)
- Validate contracts with the user at checkpoints
- Produce the test plan that feeds into **test-writer**

A vertical without a user-validated test contract is a headline, not a ready vertical.

### 4. Test Writing

Invoke the **test-writer** skill to translate validated contracts into executable test code. test-writer will:
- Write integration tests from each contract using AAA structure
- Confirm every test fails for the right reason (red)
- Commit tests as locked artifacts that build implements against

Tests can be written per-vertical as contracts are validated — you don't need all contracts before starting.

### 5. Review (optional)

If the user wants teammate review:
- Invoke **commit-and-pr** to push the plan and create a PR
- Wait for approval before building

For solo projects: skip to build.

### 6. Transition to Build

**You don't wait for the complete plan.** When the first verticals are ready:
- Confirm with the user
- Invoke **build** with the plan path
- Continue detailing later verticals if needed (plan stays a living document)

## Collaboration Style

- **Be concise.** Keep each response under 200 words unless presenting structured research or a plan.
- **Lead with decisions.** "We should use X because Y" — not "Here's everything about X."
- **One question at a time.**
- **Flag uncertainty.** Present 2-3 options with tradeoffs. Never silently pick an approach when alternatives exist.
- **Check in at transitions.** After research, before planning. After planning, before building.

## Boundaries

Include in every plan:
- **Non-goals:** What this explicitly does NOT do
- **Constraints:** Decisions that bound the solution space
- **Open questions:** What's unresolved and might affect later verticals

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Running all utility skills as separate phases** | Invoke only when a specific question needs deeper thinking |
| **Research without a question** | State what you need to learn before invoking research |
| **Designing what you already know** | Skip to plan if the landscape is clear |
| **Dumping research findings without interpretation** | Lead with the decision, not the data |
| **Transitioning to build without user confirmation** | Always confirm before invoking build |

## Example: Medium Feature (API Integration)

User: "Add Stripe payment processing to the checkout flow"

1. **Research** (invoke research): Stripe API capabilities, existing payment patterns in codebase
   - Finding: Codebase uses repository pattern. Stripe Node SDK supports Payment Intents.
   - Check-in: "Stripe Payment Intents is the right fit — it handles SCA and 3DS. Sound right?"

2. **Plan** (invoke plan): Constraints discovered, 4 verticals defined
   - V0: Walking skeleton (Stripe SDK init + test mode charge)
   - V1: Payment intent creation from cart
   - V2-V3: Headlines for webhook handling and refunds

3. **Transition**: V0 and V1 have done criteria → invoke build

## After Design

The terminal state of design is invoking **build** (or the user starting a build session).

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **Ask when stuck, don't spin.** If research or planning stalls for 2+ iterations on the same question, escalate to the user.
