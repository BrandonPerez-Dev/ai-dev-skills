---
name: design
description: >-
  Collaborative design phase orchestrator. Loads project context, researches the
  landscape, runs plan to declare which spec files change, runs test-planning to
  land integration test contracts inside those spec files, then hands off to
  build. Promotes architectural decisions to context/ along the way.
when_to_use: >-
  Use when work involves uncertainty about approach, touches multiple layers or
  services, has cross-cutting concerns (security, performance, accessibility),
  integrates with unfamiliar systems, or needs teammate alignment. Skip if the
  solution is obvious — go direct to plan or build.
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
effort: high
---

# Design

Lightweight orchestrator for design. Research what you need to know, plan what changes, land contracts in spec/, hand off to build as soon as the first slice spec has its test contract.

## The Model

Three persistent layers at the project root:

- **`context/`** — architectural truth. Always loaded.
- **`spec/`** — behavioral specs. Each file describes one slice of behavior with its integration test contract in plain text. Specs are the source of truth for what's committed and what proves done.
- **`changes/NNN-<topic>/`** — narrative for a single change. Plan + research notes.

Design's job is to walk the user from "we want to build X" to "spec files updated with validated test contracts and build is starting." It doesn't write code. It doesn't write tests. It orchestrates the skills that do.

<HARD-GATE>
Do not write implementation code during design. The output is updated spec files and a plan. Implementation during design creates sunk costs that bias decisions — you'll shape the spec to justify the code instead of the other way around.
</HARD-GATE>

<HARD-GATE>
Do not invoke build until at least one slice spec has a user-validated integration test contract. Without that, the AI defines "done" — and AI agents always declare their own work correct.
</HARD-GATE>

## Scale the Effort

| Complexity | Design Effort | Example |
|---|---|---|
| **Small** | Skip design, go to plan or build directly | Add a new API field, simple CLI command |
| **Medium** | Quick research → plan → test-planning | New endpoint with service logic, API integration |
| **Large** | Full research → architecture → plan → test-planning | Multi-service integration, new system |

Default to **medium**. Escalate if you discover unexpected complexity.

## Confidence and Autonomy

Design has gates — points where you pause for user input. Not every gate needs a hard stop. **Declare confidence before each gate** and adjust behavior accordingly.

### Confidence Levels

- **High** — Vision is clear, research supports the approach, aligns with existing patterns. Proceed with an FYI the user can flag.
- **Medium** — Reasonable approach but trade-offs unclear. Present with a recommendation, wait briefly.
- **Low** — Uncertain about the right approach or implications you can't assess. Stop — research first, then ask if still unclear.

Confidence is per-decision, not per-session.

**When in doubt, research.** Research raises confidence from low to high without involving the user. The user's time is the most expensive resource — exhaust other options first.

### Gate Behavior

| Gate | High Confidence | Medium Confidence | Low Confidence |
|------|----------------|-------------------|----------------|
| Research check-in | FYI — "Found X, moving on" | Present findings with recommendation | Stop — present, ask for direction |
| Plan constraints | Propose and proceed | Present in groups, confirm each | Stop — ask the user |
| Spec changes (plan output) | Propose and proceed | Present with recommendation | Stop — discuss |
| Test contract validation (test-planning) | Present contracts, proceed unless flagged | Present one at a time, wait for confirmation | Stop — ask about each contract |
| Build transition | FYI — "First slice ready, moving to build" | "Ready to build. Proceeding?" | Stop — confirm |

**Always-stop gates** (regardless of confidence):
- Ship decisions (irreversible)
- Discard/destructive actions
- Pushing to remote

### User Sets the Floor

- "Run everything by me" → all gates become hard stops
- "Just go" / "low involvement" → only always-stop gates remain hard

## Flow

### 0. Load Project Context

Load the two knowledge layers at the project root before doing anything else.

**`context/` — always loaded.** Read all files. Architectural truth, technology choices, integration patterns, constraints, rationale. These tell you *why* the system is built the way it is. Read before `spec/`.

Each `context/` file is flat, topic-scoped markdown. No timestamps, no status fields — just current truth. Git history is the changelog. A finding that applies beyond this change belongs in `context/`; a finding specific to this change stays in `changes/`.

**`spec/` — loaded per change.**
1. Read `spec/README.md` if it exists (system intent + slice index).
2. Small project (≤10 specs): scan all `spec/*.md` files.
3. Larger project: read only specs likely to overlap with this change. Use the README to identify them. Load more as scope narrows.

**Exit action** — by the end of this step, you have four things ready to pass to downstream skills:
- **Architectural constraints** from `context/`. Pass to plan so it doesn't re-discover known decisions; pass to test-planning so mock boundaries reflect existing infrastructure.
- **In-scope specs** — which `spec/*.md` files are likely touched. Pass to plan.
- **Existing invariants** that the change must not break. Pass to test-planning.
- **Related specs** the change extends or references. Pass to architecture so it doesn't re-design something already specified.

Do NOT redesign behavior that already exists in `spec/` without explicit user direction. Default is extend, not replace.

**If neither directory exists** — greenfield project. Skip this step. test-planning will bootstrap `spec/` during its own flow. `context/` gets seeded as architectural decisions emerge during planning.

### 1. Research (if needed)

Invoke **research** when you need to understand:
- Existing codebase patterns and conventions
- External libraries, APIs, or services
- Similar implementations for reference
- Technical feasibility of an approach

**For agent/MCP systems:** also invoke **tool-discovery** to find existing MCP servers or APIs worth wrapping.

Present findings as:
1. Decision-relevant facts (what changes the approach)
2. Risks or unknowns discovered
3. Recommendation with rationale

**Confidence-gated check-in.** High: FYI and move on. Medium/low: present and ask.

**Promote to context/.** System-level architectural findings get written to `context/` after user confirmation. Feature-specific details stay in `changes/`.

### 2. Plan

Invoke **plan**. The plan declares:
- Which specs are added, modified, or superseded
- Constraints and non-goals for this change
- The first slice spec (entry point for build)
- Build skills needed

The plan does NOT enumerate slice definitions — those live as files in `spec/`. The plan points at them.

During planning, invoke utility skills as specific questions need deeper thinking — **architecture**, **ui-ux-design**, **ai-agent-building** — not as separate mandatory phases.

### 3. Test Planning (mandatory)

Invoke **test-planning** after the plan declares which specs change. This is not optional — slice specs aren't ready without validated integration test contracts.

Test-planning will:
- Write or extend the integration test contract inside each in-scope `spec/*.md` (setup, action, input, expected output, side effects, error cases)
- Establish mock boundaries — controlled deps real, uncontrolled mocked at adapter
- Validate contracts with the user at checkpoints
- Bootstrap `spec/` on greenfield — create the initial slice spec files seeded from the plan's why and constraints

A slice spec without a user-validated test contract is an unfinished idea. Don't hand it to build.

### 4. Test Writing

Invoke **test-writer** to translate contracts into executable test code. test-writer:
- Reads contracts from the spec files (the source of truth)
- Writes integration tests using AAA structure
- Confirms every test fails for the right reason
- Writes back to each slice spec's `## Tests` section pointing at the committed `<test file>` § `"<test name>"` — gives the spec a forward link to the test that enforces it
- Commits the test files AND the spec edits together as locked artifacts that build implements against

Tests can be written per-slice as contracts validate — you don't need every spec finalized before starting on one.

### 5. Review (optional)

If teammate review is wanted: invoke **commit-and-pr** to push the plan and updated specs, wait for approval. For solo work: skip.

### 6. Transition to Build

**You don't wait for every spec to be finalized.** When the first slice spec has a validated test contract + committed red test:
- High confidence: notify the user and invoke **build**
- Medium/low: confirm before invoking build
- Continue detailing later specs (the plan stays a living document)

## Collaboration Style

- **Be concise.** Keep each response under 200 words unless presenting structured research or a plan.
- **Lead with decisions.** "We should use X because Y" — not "Here's everything about X."
- **One question at a time.**
- **Flag uncertainty.** Present 2–3 options with tradeoffs. Don't silently pick when alternatives exist.
- **Check in at transitions.** After research, before planning. After test-planning, before building.

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Running all utility skills as separate phases | Invoke only when a specific question needs deeper thinking |
| Research without a question | State what you need to learn before invoking research |
| Designing what's already known | Skip to plan if the landscape is clear |
| Dumping research findings without interpretation | Lead with the decision, not the data |
| Transitioning to build with no signal | At minimum notify (FYI at high confidence, confirm at medium/low) |
| Restating spec content in the plan | The plan points at specs; specs hold contracts |
| Inventing new specs when an existing one fits | Default to modifying. Add only when the slice is genuinely new |

## Example: Medium Feature (Feature 2+ Flow)

User: "Add Stripe payment processing to the checkout flow"

1. **Load context** — `context/` shows no payment provider chosen, checkout uses SSR, orders use Postgres. `spec/` has `checkout`, `orders`, `users` specs; no `payments` slice yet.

2. **Research** — Stripe Payment Intents handles SCA/3DS. Codebase uses repository pattern. Check-in at high confidence: "Payment Intents is the right fit. Moving on."

3. **Plan** — Constraints discovered. Plan declares:
   - `spec/payments-create-intent.md` (new) — first slice
   - `spec/payments-webhook.md` (new) — second slice
   - `spec/checkout.md` (modified) — adds payment intent step
   - `spec/orders.md` (modified) — adds "paid" state to lifecycle

4. **Test Planning** — Writes integration test contract into `spec/payments-create-intent.md` (setup: cart with items; action: POST /api/payment-intents; expected: 200 + intent ID; side effects: Stripe API call with correct amount; error cases: empty cart, declined card, network error). Validates with user. Repeats for other in-scope specs.

5. **Test Writing** — Generates red integration tests from each spec's contract. Commits them.

6. **Transition** — First slice spec has contract + red test → invoke build.

## After Design

The terminal state of design is invoking **build** (or the user starting a build session).

### Build Loop

Each slice spec follows: **build → commit → refactor → next slice**. Build invokes refactor automatically after each commit. This prevents debt from accumulating across slices.

## Guidelines

- **Pass context downstream.** Every downstream skill needs the four items from Step 0's exit action. Don't assume they'll be rediscovered.
- **Specs are persistent. Plans are transient.** A plan tells the story of one change. Specs accumulate across changes.
- **A slice spec without an integration test contract is unfinished.** It cannot be handed to build.
