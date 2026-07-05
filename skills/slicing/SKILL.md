---
name: slicing
description: >-
  Lightweight iterative planning — discover constraints through conversation,
  land them directly in spec/ (slice stubs) and context/ (decisions), and hand
  off to test-planning + build. Spec + context are the source; git history is
  the change record.
when_to_use: >-
  Before building any non-trivial feature, when invoked by the engineering skill, or
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
argument-hint: "[topic]"
effort: high
---

# Slicing

Discover what matters through conversation, land it directly in the durable layers, hand off to test-planning and build. Planning a medium feature should take 10–15 minutes, not hours.

## The Model

There are two persistent directories at the project root — together they tell the **entire plain-text story of the codebase** (spec as source):

- **`context/`** — architectural truth. Tech choices, integration patterns, infrastructure commitments, and **decisions ADR-style**: what was chosen, why, and what was *rejected* and why not. `context/research/` holds dated research references (a cache — refresh when stale).
- **`spec/`** — behavioral specs. Each file describes one slice of behavior with its integration test contract in plain text, a `status` (`planned | in-progress | built | superseded`), and its own `## Changes` log. Specs are the source of truth for *what work has been committed to* and *what proves it done*.

The change record is git: diffs on `context/` and `spec/` show *what* changed; commit messages and the PR description carry the per-change narrative; rejected alternatives live in `context/` where the decision lives. Scope-in-flight is visible as which specs carry `status: planned` or `in-progress`.

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

Each confirmed decision lands **directly where it lives**:
- **System-level decisions** (technology choices, integration patterns, commitments beyond this change) → the relevant `context/<topic>.md`, ADR-style: the decision, its rationale, and any **rejected alternative with the why-not** ("Rejected: X — because Y"). Rejected alternatives are first-class — they prevent re-litigating settled questions.
- **Slice-specific decisions and non-goals** → the affected spec's `## Notes` (created in step 4 if the spec is new).

Cover the decisions that matter for *this* change:
- Transport & protocol
- Framework & patterns
- Auth & security
- Data — schemas, storage, external APIs
- Scope boundaries — what's in, what's explicitly out

Skip categories that are obvious. Spend time where a wrong default wastes hours.

Present constraints in groups of 2–3, confirm each group before moving on.

If a constraint involves component boundaries, data flow between services, or API contract design, invoke **architecture** for that specific question. If there's a UI component, invoke **ui-ux-design**. If research produced dated, sourced findings worth keeping, save them to `context/research/<topic>.md` (a dated cache) and cite them from the topic file.

### 4. Land the Scope in spec/

Walk through the existing `spec/` files and decide for each one whether this change:
- **Adds** a new spec — create the **stub now**: frontmatter (`status: planned`, `depends_on`), `## Does` (one sentence), a skeletal `## Done when`, `## Notes` (slice-specific decisions, non-goals, open questions), and a `## Changes` entry naming the why. test-planning fills in the contract.
- **Modifies** an existing spec — mark it `in-progress`, append the intent to its `## Notes` and `## Changes` (what's changing and why; what's being **superseded** gets named explicitly).
- **Supersedes** an existing spec — set its status, point at the successor.

The set of specs now marked `planned`/`in-progress` **is** the scope declaration — downstream skills (test-planning, test-writer, build) read it from spec statuses, not from a plan file.

Default to **modifying existing specs over creating new ones** unless the slice is genuinely new behavior. Contract content (test contract, error cases) is written by **test-planning** with the user, not by this skill.

### 5. Identify the First Slice + Walking Skeleton

For greenfield projects (no `spec/` yet), the first slice spec is the **walking skeleton** — thinnest end-to-end path proving the infrastructure works. Build handles the V0a/V0b split internally.

For changes to existing projects, identify which in-scope spec is the entry point — usually the most foundational, fewest dependencies. Note it in that spec's `## Notes` ("entry point for this change"). Build starts there.

### 6. Suggest Build Skills

Suggest which skills the build phase will need (language/runtime, domain, infrastructure). User confirms. Record in the entry-point spec's `## Notes` if non-obvious.

### 7. Commit the Planning Write-Backs

Commit the spec stubs + context edits as one planning commit. The commit message carries the change narrative (what & why, key decisions, named supersessions) — it is the durable "plan" record, alongside the diff itself.

## Hand Off

Either the user moves to **test-planning** to land contracts in the `planned`/`in-progress` specs, or you invoke it directly. After contracts land, **test-writer** translates them into locked tests, and **build** implements until green.

You don't need every spec finalized before build starts — once one spec has its test contract landed, build can start on that slice while later specs get detailed.

## Spec Stub Format (what slicing creates)

```markdown
---
status: planned
depends_on: []
---

# [Slice Name]

## Does
[One sentence — what this slice accomplishes for the user]

## Done when
- [Observable outcome — skeletal; test-planning refines]

## Notes
- [Slice-specific decisions, with rejected alternatives where they were real choices]
- Out of scope: [non-goals for this slice, with where they land instead]
- Open: [unresolved questions that might affect later slices]

## Changes
- YYYY-MM-DD — created (sliced): [why this slice, in one line]
```

## Scaling

| Change Size | Constraints | Specs touched | Planning Time |
|---|---|---|---|
| **Small** | 3–5 bullets | 1–2 (often modify, not add) | 5 min |
| **Medium** | 5–10 bullets | 2–4 | 10–15 min |
| **Large** | 10–15 bullets | 4–8, often with new specs | 15–20 min |

If planning takes more than 20 minutes, the change is too big — split it into separate changes that touch different specs.

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Writing scope or rationale into a standalone planning doc** | Constraints → context/ and spec Notes; narrative → the planning commit message + PR description. |
| **Inventing new specs when an existing one fits** | Default to modifying. Only add when the slice is genuinely new behavior. |
| **Decisions without their rejected alternatives** | A bare decision re-litigates itself later. Record "Rejected: X — because Y" next to it in context/. |
| **Planning without reading `spec/` and `context/`** | Hard gate — without these you'll re-discover known constraints. |
| **Skipping non-goals** | Non-goals prevent scope creep. They live in the spec's Notes (slice-level) or context/ (durable boundaries). |
| **Duplicating the same fact in context AND spec Notes** | Single entry: system-level → context/; slice-level → spec Notes. Never both. |
| **Detailing every spec change upfront** | Stub the first 2–3 slices fully; later specs get fleshed out as build approaches them. |

## Guidelines

- **Spec + context are the source.** If it matters beyond this conversation, it lands in one of them — exactly once.
- **Git is the changelog.** Diffs show what changed; commit messages say why; the PR description tells the story of the change.
- **Constraints prevent wrong turns.** This is where planning time pays off — not prose descriptions.
- **Every slice spec needs an integration test contract** before build. test-planning enforces this; a spec without one is an unfinished idea.
