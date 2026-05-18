---
name: plan
description: >-
  Lightweight iterative planning — discover constraints through conversation,
  decide which spec files this change adds, modifies, or supersedes, and hand
  off to test-planning + build. The plan captures rationale for a specific
  change; the slices themselves live as files in spec/.
when_to_use: >-
  Before building any non-trivial feature, when invoked by the design skill, or
  when aligning with a teammate on approach before coding. Skip for single-line
  fixes with obvious scope — just build those.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Skill
argument-hint: "[topic or path/to/existing-plan.md]"
effort: high
---

# Plan

Discover what matters through conversation, decide which spec files change, hand off to test-planning and build. Planning a medium feature should take 10–15 minutes, not hours.

## The Model

There are three persistent directories at the project root:

- **`context/`** — architectural truth. Tech choices, integration patterns, infrastructure commitments. Loaded by every planning session.
- **`spec/`** — behavioral specs. Each file describes one slice of behavior with its integration test contract in plain text. Specs are the source of truth for *what work has been committed to* and *what proves it done*. A spec file with an integration test contract is what build implements against.
- **`changes/NNN-<topic>/`** — narrative for a single change. Captures *why* this change is happening, what decisions were made, and which specs are added/modified/superseded.

**Specs are persistent. Plans are transient.** A plan tells the story of one change. Specs accumulate and evolve over many changes. Each spec carries its own status (`planned | in-progress | built | superseded`) and its own change log.

<HARD-GATE>
Read the codebase before planning. Planning against an imagined architecture leads to constraints that the code can't satisfy and slices that don't fit existing seams.
</HARD-GATE>

## Process

### 1. Ground in Reality (2 min)

Read what's relevant:
- All files in `context/` — these are hot memory, always read before planning
- All files in `spec/` that the change might touch, plus `spec/README.md` if present
- Project structure, tech stack, existing patterns, existing tests for style

Don't read everything. Read what matters for this change.

### 2. Understand What We're Building (2–3 min)

Ask what's being built and why. Propose understanding back as 2–3 sentences; let the user correct.

> "So we're building X to solve Y. The main risk is Z."

Get confirmation before continuing.

### 3. Discover Constraints (5–10 min, iterative)

Surface architectural decisions as proposals, not open-ended questions:

> "For auth, QuickBooks requires OAuth 2.0 — no API key option. I'll use their Node SDK for the token flow. Sound right?"

Each confirmed decision becomes a constraint line in the plan. **System-level decisions** (technology choices, integration patterns, infrastructure commitments beyond this change) also get written to `context/` — feature-specific decisions stay in the plan only.

Cover the decisions that matter for *this* change:
- Transport & protocol
- Framework & patterns
- Auth & security
- Data — schemas, storage, external APIs
- Scope boundaries — what's in, what's explicitly out

Skip categories that are obvious. Spend time where a wrong default wastes hours.

Present constraints in groups of 2–3, confirm each group before moving on.

If a constraint involves component boundaries, data flow between services, or API contract design, invoke **architecture** for that specific question. If there's a UI component, invoke **ui-ux-design**.

### 4. Decide Which Specs Change

Walk through the existing `spec/` files and decide for each one whether this change:
- **Adds** a new spec (new slice of behavior not yet committed to)
- **Modifies** an existing spec (extends done-criteria, adds test cases, updates invariants)
- **Supersedes** an existing spec (the old slice is being replaced or removed)

A new spec gets created when this change introduces a slice that doesn't already exist. An existing spec gets modified when the change extends or refines work that's already committed to. This is the design choice that separates good planning from bad planning — **default to modifying existing specs over creating new ones** unless the slice is genuinely new behavior.

The actual spec content (intent, integration test contract, error cases, invariants) is written by **test-planning** in collaboration with the user, not by this skill. The plan only declares *which* specs change and *why*.

### 5. Identify the First Slice + Walking Skeleton

For greenfield projects (no `spec/` yet), the first slice spec is the **walking skeleton** — thinnest end-to-end path proving the infrastructure works. Build handles the V0a (boundary scaffold) / V0b (walking skeleton wiring) split internally; the plan only declares the slice's scope.

For changes to existing projects, identify which spec is the entry point — usually the most foundational, the one with the fewest dependencies on other in-scope specs. Build will start there.

### 6. Suggest Build Skills

Suggest which skills the build phase will need:
- Language/runtime — `rust-quality`, `frontend-build`, etc.
- Domain — `ai-agent-building`, `mcp-builder` if relevant
- Infrastructure — `boilerplate-cicd` if the project lacks CI/linting

Present suggestions. User confirms. Record in the plan's "Build skills" section.

### 7. Save the Plan

Save to `changes/NNN-<topic>/plan.md`:
- `changes/` at project root (`mkdir -p changes` if needed)
- Find highest existing `NNN-*` prefix, increment by 1. Start at `001` if empty.
- All rationale, research, and notes for this change go in the same directory.

Today's date for the plan header: !`date +%Y-%m-%d`

### 8. Hand Off

Either the user moves to **test-planning** to land contracts in the affected spec files, or you invoke it directly. After test-planning lands integration test contracts in the specs, **test-writer** translates them into executable tests, and **build** implements until green.

You don't need every spec finalized before build starts — once one spec has its test contract landed, build can start on that slice while later specs get detailed.

## Plan Format

```markdown
# Plan: [Change Name]

> Date: YYYY-MM-DD
> Status: planning | building | complete

## What & Why
[2–3 sentences: what this change accomplishes and why now]

## Spec changes
- `spec/<name>.md` — modified — [what's changing: new test cases, extended done-criteria, etc.]
- `spec/<name>.md` (new) — [what slice this describes]
- `spec/<name>.md` (superseded by `spec/<new-name>.md`) — [why]

## Context changes
- `context/<topic>.md` — [what's changing or being added]
- [omit this section if no context/ changes needed]

## Constraints
- [Decision: rationale]
- [Decision: rationale]

## Non-Goals
- [What this change explicitly does NOT do]

## Build skills
- [skill-name — why it's needed]

## First slice
- `spec/<name>.md` — [why this is the entry point]

## Open Questions
- [Anything unresolved that might affect later slices]
```

The plan is the narrative for *this change*. It does not duplicate spec content — it points at the specs being touched and explains why. Spec files carry the test contracts, done criteria, and historical change log.

## Scaling

| Change Size | Constraints | Specs touched | Planning Time |
|---|---|---|---|
| **Small** | 3–5 bullets | 1–2 (often modify, not add) | 5 min |
| **Medium** | 5–10 bullets | 2–4 | 10–15 min |
| **Large** | 10–15 bullets | 4–8, often with new specs | 15–20 min |

If planning takes more than 20 minutes, the change is too big — split it into multiple changes that touch different specs.

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Inventing new specs when an existing one fits** | Default to modifying. Only add when the slice is genuinely new behavior. |
| **Duplicating spec content in the plan** | Plans point at specs; specs hold the contracts. Don't restate. |
| **Planning without reading `spec/` and `context/`** | Hard gate — without these you'll re-discover known constraints. |
| **Skipping non-goals** | Non-goals prevent scope creep. Always include them. |
| **Writing prose constraints** | Constraints are bullets, not paragraphs. |
| **Detailing every spec change upfront** | Only detail the first 2–3 slices fully. Later specs get fleshed out as build approaches them. |
| **Planning > 20 minutes** | Change is too big — split, or you're over-specifying. |

## Guidelines

- **Specs are the source of truth.** The plan is a pointer to a change. The work commitments live in `spec/`.
- **Constraints prevent wrong turns.** This is where planning time pays off — not prose descriptions.
- **Every slice spec needs an integration test contract.** test-planning enforces this. The plan's job is to declare which specs are in scope; test-planning fills in the contract.
- **A spec without a test contract is an unfinished idea.** Don't hand it to build.
