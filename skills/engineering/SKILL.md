---
name: engineering
description: >-
  The engineering-cycle orchestrator: loads project context, researches the
  landscape, runs slicing to land scope directly in spec/ and decisions in
  context/, runs test-planning to land integration test contracts inside those
  spec files, then hands off to build. ALWAYS invoke for non-trivial feature or
  system work; do not start multi-layer changes without it.
when_to_use: >-
  Use when work involves uncertainty about approach, touches multiple layers or
  services, has cross-cutting concerns (security, performance, accessibility),
  integrates with unfamiliar systems, or needs teammate alignment. Skip if the
  solution is obvious — go direct to slicing or build.
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

# Engineering

Lightweight orchestrator for the engineering cycle. Research what you need to know, land scope in spec/ and decisions in context/, land contracts in the in-scope specs, hand off to build as soon as the first slice spec has its test contract.

## The Model

Two persistent layers at the project root — together they are the **entire plain-text story of the codebase** (spec as source):

- **`context/`** — architectural truth. Always loaded. Decisions are ADR-style: what was chosen, why, and what was **rejected** and why not. `context/research/` holds dated research references (a cache — refresh when stale).
- **`spec/`** — behavioral specs. Each file describes one slice of behavior with its integration test contract in plain text, a `status` (`planned | in-progress | built | superseded`), and a `## Changes` log. Specs are the source of truth for what's committed and what proves done.

Git is the change record: diffs on `context/` + `spec/` show what changed; commit messages and PR descriptions carry the narrative. Scope-in-flight = which specs are `planned`/`in-progress`.

Engineering's job is to walk the user from "we want to build X" to "spec files updated with validated test contracts and build is starting." It doesn't write code. It doesn't write tests. It orchestrates the skills that do.

<HARD-GATE>
Do not write implementation code during design. The output is updated spec/ and context/ files. Implementation during design creates sunk costs that bias decisions — you'll shape the spec to justify the code instead of the other way around.
</HARD-GATE>

<HARD-GATE>
Do not invoke build until at least one slice spec has a user-validated integration test contract. Without that, the AI defines "done" — and AI agents always declare their own work correct.
</HARD-GATE>

## Scale the Effort

| Complexity | Effort | Example |
|---|---|---|
| **Small** | Skip orchestration, go to slicing or build directly | Add a new API field, simple CLI command |
| **Medium** | Quick research → slicing → test-planning | New endpoint with service logic, API integration |
| **Large** | Full research → architecture → slicing → test-planning | Multi-service integration, new system |

Default to **medium**. Escalate if you discover unexpected complexity.

## Confidence and Autonomy

Engineering has gates — points where you pause for user input. Not every gate needs a hard stop. **Declare confidence before each gate** and adjust behavior accordingly.

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
| Slicing constraints | Propose and proceed | Present in groups, confirm each | Stop — ask the user |
| Scope write-backs (spec stubs + context edits) | Propose and proceed | Present with recommendation | Stop — discuss |
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

**`context/` — always loaded.** Read all files. Architectural truth, technology choices, integration patterns, constraints, rationale — including what was rejected and why. Read before `spec/`.

Each `context/` topic file is flat, topic-scoped markdown holding current truth; git history is its changelog. Dated material lives only in `context/research/` (the research cache). A finding that applies beyond the current change belongs in `context/`; purely conversational detail belongs nowhere durable.

**`spec/` — loaded per change.**
1. Read `spec/README.md` if it exists (system intent + slice index).
2. Small project (≤10 specs): scan all `spec/*.md` files.
3. Larger project: read only specs likely to overlap with this change. Use the README to identify them. Load more as scope narrows.

**Exit action** — by the end of this step, you have four things ready to pass to downstream skills:
- **Architectural constraints** from `context/` (including standing rejections). Pass to slicing so it doesn't re-discover known decisions; pass to test-planning so mock boundaries reflect existing infrastructure.
- **In-scope specs** — which `spec/*.md` files are likely touched.
- **Existing invariants** that the change must not break. Pass to test-planning.
- **Related specs** the change extends or references. Pass to architecture so it doesn't re-design something already specified.

Do NOT redesign behavior that already exists in `spec/` without explicit user direction. Default is extend, not replace.

**If neither directory exists** — greenfield project. Skip this step. test-planning will bootstrap `spec/` during its own flow. `context/` gets seeded as architectural decisions emerge during slicing.

### 1. Investigate (if needed)

Invoke **investigating** when you need to understand:
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

**Promote to context/.** System-level findings get written to `context/` after user confirmation; dated sourced research goes to `context/research/<topic>.md` and is cited from the topic file.

### 2. Slice

Invoke **slicing**. Its output lands directly in the durable layers:
- New/modified **spec stubs** with `status: planned`/`in-progress` — the scope declaration downstream skills read
- **context/** decision entries (ADR-style, rejected alternatives included)
- Slice-specific decisions, non-goals, and open questions in each spec's `## Notes`
- One planning commit whose message carries the change narrative

During slicing, invoke utility skills as specific questions need deeper thinking — **architecture**, **ui-ux-design**, **ai-agent-building** — not as separate mandatory phases.

### 3. Grill the Scope

Invoke **grill** on the sliced scope (the planned/in-progress specs + the new context entries). The slicing conversation builds the design up; this step tries to knock it down. Designs that skip the grill carry wrong assumptions into locked tests, where they're expensive.

Grill's findings write back into the layers themselves: sharpened terms and decisions (with the rejected alternative named) → `context/`; slice-scoped resolutions → the spec's `## Notes`. Scale it like everything else: small change → one sanity question; large change → a full session.

### 4. Test Planning (mandatory)

Invoke **test-planning** on the specs marked `planned`/`in-progress`. This is not optional — slice specs aren't ready without validated integration test contracts.

Test-planning will:
- Write or extend the integration test contract inside each in-scope `spec/*.md` (setup, action, input, expected output, side effects, error cases)
- Establish mock boundaries — controlled deps real, uncontrolled mocked at adapter
- Validate contracts with the user at checkpoints
- Bootstrap `spec/` on greenfield — create the initial slice spec files from the sliced scope

A slice spec without a user-validated test contract is an unfinished idea. Don't hand it to build.

### 5. Test Writing

Invoke **test-writer** to translate contracts into executable test code. test-writer:
- Reads contracts from the spec files (the source of truth)
- Writes integration tests using AAA structure
- Confirms every test fails for the right reason
- Writes back to each slice spec's `## Tests` section pointing at the committed `<test file>` § `"<test name>"`
- Commits the test files AND the spec edits together as locked artifacts that build implements against

Tests can be written per-slice as contracts validate — you don't need every spec finalized before starting on one.

### 6. Review (optional)

If teammate review is wanted: invoke **commit-and-pr** to push the spec/context updates, wait for approval. The PR description is where the change narrative gets told in full. For solo work: skip.

### 7. Transition to Build

**You don't wait for every spec to be finalized.** When the first slice spec has a validated test contract + committed red test:
- High confidence: notify the user and invoke **build**
- Medium/low: confirm before invoking build
- Continue detailing later specs as build proceeds

## Collaboration Style

- **Be concise.** Keep each response under 200 words unless presenting structured research or scope.
- **Lead with decisions.** "We should use X because Y" — not "Here's everything about X."
- **One question at a time.**
- **Flag uncertainty.** Present 2–3 options with tradeoffs. Don't silently pick when alternatives exist.
- **Check in at transitions.** After research, before slicing. During the grill (one question at a time). After test-planning, before building.

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Writing scope or rationale into a standalone planning doc | Scope → spec stubs; decisions → context/; narrative → commit messages + PR description |
| Running all utility skills as separate phases | Invoke only when a specific question needs deeper thinking |
| Research without a question | State what you need to learn before invoking investigating |
| Designing what's already known | Skip to slicing if the landscape is clear |
| Dumping research findings without interpretation | Lead with the decision, not the data |
| Transitioning to build with no signal | At minimum notify (FYI at high confidence, confirm at medium/low) |
| Recording the same fact in two layers | Single entry: system-level → context/; slice-level → spec Notes |
| Inventing new specs when an existing one fits | Default to modifying. Add only when the slice is genuinely new |

## Example: Medium Feature (Feature 2+ Flow)

User: "Add Stripe payment processing to the checkout flow"

1. **Load context** — `context/` shows no payment provider chosen, checkout uses SSR, orders use Postgres. `spec/` has `checkout`, `orders`, `users` specs; no `payments` slice yet.

2. **Research** — Stripe Payment Intents handles SCA/3DS. Codebase uses repository pattern. Check-in at high confidence: "Payment Intents is the right fit. Moving on."

3. **Slice** — Constraints confirmed and landed: `context/payments.md` gains the provider decision (with "Rejected: Braintree — no Payment-Intents-equivalent for SCA"); stubs created: `spec/payments-create-intent.md` (planned, first slice), `spec/payments-webhook.md` (planned); `spec/checkout.md` and `spec/orders.md` marked in-progress with intent noted. One planning commit.

4. **Grill** — Invoke **grill** on the scope. Surfaces: "Orders spec says an order is immutable after submission; the sliced scope adds a 'paid' state mutation. Supersede that invariant or model payment as a separate record?" → user picks separate `payment` record; `spec/orders.md` change shrinks; the rejected mutation approach is recorded in `context/payments.md`. Terminology sharpened ("checkout session" vs "cart") in `context/`.

5. **Test Planning** — Writes the integration test contract into `spec/payments-create-intent.md` (setup: cart with items; action: POST /api/payment-intents; expected: 200 + intent ID; side effects: Stripe API call with correct amount; error cases: empty cart, declined card, network error). Validates with user. Repeats for other in-scope specs.

6. **Test Writing** — Generates red integration tests from each spec's contract. Commits them.

7. **Transition** — First slice spec has contract + red test → invoke build.

## After Engineering

The terminal state of engineering is invoking **build** (or the user starting a build session).

### Build Loop

Each slice spec follows: **build → commit → refactor → next slice**. Build invokes refactor automatically after each commit. This prevents debt from accumulating across slices.

## Guidelines

- **Pass context downstream.** Every downstream skill needs the four items from Step 0's exit action. Don't assume they'll be rediscovered.
- **Spec + context are the source; git is the changelog.** If it matters durably, it lives in one of the two layers — exactly once.
- **A slice spec without an integration test contract is unfinished.** It cannot be handed to build.
