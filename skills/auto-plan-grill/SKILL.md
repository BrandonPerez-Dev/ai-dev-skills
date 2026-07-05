---
name: auto-plan-grill
description: >-
  Autonomous plan + grill for GitHub-driven development. Reads context/spec/codebase,
  produces a plan with spec changes, self-grills using three lenses, classifies
  confidence on every decision, pushes to a branch, opens a draft PR, and posts
  open questions as PR comments. Proceeds on medium-confidence assumptions.
  Communicates with the human via GitHub, not interactive conversation.
when_to_use: >-
  Use when an autonomous agent needs to plan a change for a project and communicate
  via GitHub. Requires a kickoff (issue body, task description, or manual trigger)
  with enough detail to start planning without interviewing the human. Do NOT use
  for interactive planning — use engineering + slicing for that.
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
argument-hint: "[issue URL, task description, or path/to/kickoff.md]"
effort: high
---

# Auto Plan + Grill

Autonomous planning with built-in self-grilling. Read the project, produce a plan, poke holes in it, push to GitHub, and let the human review asynchronously. No interactive conversation — GitHub is the communication channel.

## The Model

Three persistent layers at the project root (same as interactive pipeline):

- **`context/`** — architectural truth. Always loaded.
- **`spec/`** — behavioral specs. One file per slice, with integration test contracts.
- **`changes/NNN-<topic>/`** — narrative for a single change. Plan + open questions + corrections log.

This skill's job: go from "kickoff description" to "plan pushed, PR open, questions posted, ready for downstream skills to build unblocked slices."

<HARD-GATE>
Do not write implementation code. Do not write tests. Do not write test contracts. Output is a plan, updated/new spec stubs, context/ updates, and open questions. Downstream skills (auto-test-planning, auto-build) handle everything after.
</HARD-GATE>

<HARD-GATE>
Do not proceed without reading the codebase. Planning against an imagined architecture produces constraints the code can't satisfy.
</HARD-GATE>

## Input

The kickoff. One of:
- **GitHub issue URL** — agent reads issue body via `gh issue view`
- **Task description** — plain text: what to build, why, any known constraints
- **Kickoff file** — path to a markdown file with the above

Minimum viable kickoff: 2–3 sentences of what and why. The agent infers constraints, non-goals, and scope from `context/`, `spec/`, and the codebase. If the kickoff is too vague to produce any plan, the agent posts clarifying questions to GitHub and stops.

## Process

### 0. Load Project Context

Read the project's knowledge layers before doing anything else.

**`context/` — always loaded.** Read all files. These are architectural constraints that inform every decision.

**`spec/` — loaded per change.**
1. Read `spec/README.md` if it exists.
2. Small project (≤10 specs): scan all.
3. Larger project: read specs likely to overlap with this change.

**Codebase — targeted read.** Project structure, tech stack, existing patterns, test conventions. Read what matters for this change; don't read everything.

**If neither `context/` nor `spec/` exists** — greenfield. Note it; spec/ will be bootstrapped when downstream skills write contracts.

### 1. Investigate (if needed)

If the kickoff references unfamiliar systems, libraries, or APIs, investigate first:
- Codebase patterns and conventions
- External libraries, APIs, or services
- Similar implementations for reference
- Technical feasibility

Research autonomously. Record findings in `changes/NNN-<topic>/research.md`. Promote system-level findings to `context/` (with a note that these are agent-proposed; human hasn't confirmed).

### 2. Plan

Produce the plan. This merges what the interactive pipeline does across slicing steps 2–7.

**Discover constraints autonomously.** Instead of asking the human about each constraint:
- Derive constraints from `context/`, the codebase, and research
- For each constraint, classify confidence (see Confidence Model below)
- High-confidence constraints go directly into the plan
- Medium-confidence constraints go into the plan marked as assumptions
- Low-confidence constraints go into open-questions.md

**Constraint categories** (skip what's obvious, spend time where a wrong default wastes hours):
- Transport & protocol
- Framework & patterns
- Auth & security
- Data — schemas, storage, external APIs
- Scope boundaries — what's in, what's explicitly out

**Decide which specs change:**
- Walk through existing `spec/` files
- For each: does this change add, modify, or supersede it?
- Default to modifying existing specs over creating new ones
- New specs only when the slice is genuinely new behavior

**Identify the first slice:**
- Most foundational, fewest dependencies on other in-scope specs
- For greenfield: the walking skeleton (thinnest end-to-end path)

**Identify the dependency graph:**
- Which slices depend on which
- Which slices are independent (can be built without waiting for others)
- Which slices are blocked by open questions

**Suggest build skills:** Language/runtime, domain, infrastructure skills needed.

### 3. Grill (bulk, in the same pass)

Immediately after producing the plan — before saving it — grill it. The planning pass builds the plan up; the grill tries to knock it down.

Run **all three lenses** against `context/` and in-scope specs. Unlike the interactive version, raise ALL findings at once, not one at a time.

#### Lens 1: Tensions and Structure
Concrete, structural challenges:
- Relationships and cardinality ("does one X hold many Y?")
- Deletion and cascade semantics
- State transitions and who owns them
- Ordering and idempotency under retry
- Concurrency and locking
- Error propagation across boundaries

Prefer challenges whose answer changes a contract.

#### Lens 2: Terminology Collisions
Challenge every load-bearing term against the project's existing language in `context/`:
- Does the plan use a term that `context/` defines differently?
- Does the plan introduce a new term that overlaps with an existing one?
- Are there fuzzy terms that need sharpening before they enter a spec?

#### Lens 3: Prior-Decision Conflicts
Find existing spec contracts or `context/` decisions this plan contradicts:
- Name the conflict explicitly
- Propose resolution: keep the old decision, or supersede on purpose
- Never leave both implicitly in effect

#### Refutation Attempt
Close with one attempt to refute the plan:
- Is there a simpler version that accomplishes the same goal?
- Does an existing capability already cover this?
- Does the plan break an invariant it doesn't acknowledge?

Resolve the refutation (accept or reject) and record the resolution.

#### Self-Answering Grill Findings

For each grill finding, the agent does one of:

| Confidence | Action | Artifact |
|---|---|---|
| **High** | Self-answers. Records resolution as ADR in `## Grill` section. | No open question. |
| **Medium** | Self-answers tentatively. Records assumption as ADR in `## Grill` section. | Entry in open-questions.md marked "assumption — proceeding unless corrected." |
| **Low** | Does NOT assume. Records the question and its best guess as ADR. | Entry in open-questions.md marked "blocking" with affected slices listed. |

#### ADR Format for Grill Entries

Each grill finding is recorded as a lightweight Architecture Decision Record:

```markdown
### [Finding Title]
- **Status:** resolved | assumption | blocking
- **Context:** [What part of the plan this challenges]
- **Decision:** [The resolution or assumption]
- **Confidence:** high | medium | low
- **Consequences:** [What changes as a result — spec updates, new constraints, etc.]
- **Alternatives considered:** [Other options and why they were rejected]
```

### 4. Build the Dependency Graph

From the plan's spec changes, produce a dependency ordering:

1. Read `depends_on` frontmatter from existing specs
2. For new specs, infer dependencies from the plan's constraints
3. Classify each slice:
   - **Unblocked** — no open low-confidence questions affect it, all dependencies are either already built or also unblocked
   - **Blocked** — depends on an unanswered low-confidence question, or depends on a blocked slice
4. Record the graph in the plan under `## Slice Order`

### 5. Save Artifacts

#### Plan file
Save to `changes/NNN-<topic>/plan.md` using the format below. Increment NNN from the highest existing prefix; start at 001 if empty.

#### Open questions file
Save to `changes/NNN-<topic>/open-questions.md` with all medium and low-confidence items.

#### Spec stubs (new specs only)
For each new spec declared in the plan, create a minimal stub in `spec/<name>.md`:

```markdown
---
status: planned
depends_on: []
---

# [Slice Name]

## Does
[One sentence from the plan]

## Done when
- [Placeholder — test-planning will fill this in]

## Integration test contract
[Placeholder — test-planning will fill this in]

## Tests
No test exists yet — auto-test-planning will produce the contract, auto-test-writer will produce the test.

## Notes
- Created by auto-plan-grill from changes/NNN-<topic>/plan.md
```

#### Context updates
If the planning or grill pass produced findings that belong in `context/`, write them. Mark agent-proposed updates clearly: "Proposed by agent — not yet human-confirmed."

### 6. Push to GitHub

1. **Create branch:** `agent/<topic>` from main/default branch
2. **Commit:** plan.md, open-questions.md, spec stubs, context/ updates
3. **Push branch**
4. **Open draft PR** with:
   - Title: `[Agent] <change name>`
   - Body: plan summary + current status (see PR Description Format below)
5. **Add label:** `agent-in-progress`
6. **Post PR comments** for each open question:
   - 🔴 BLOCKING questions → comment on the relevant line in plan.md or spec file
   - 🟡 ASSUMPTION items → comment on the relevant line
7. If there are any blocking questions, also add label: `needs-answer`

## Confidence Model

Every decision gets a confidence classification.

**What raises confidence:**
- `context/` has a clear, unambiguous answer
- Codebase patterns strongly suggest an answer
- Research confirms a single viable approach
- The decision matches an existing spec's pattern

**What lowers confidence:**
- Multiple valid approaches with no clear signal from context/ or codebase
- Contradicts an existing spec or context/ decision
- No information available — pure guess
- Security, data-model, or deletion-semantics decisions (bias toward low — expensive to get wrong)
- The kickoff explicitly left this open or flagged uncertainty

**Confidence is per-decision, not per-plan.** A plan can have 10 high-confidence constraints and 2 low-confidence ones. The 2 low-confidence ones don't make the whole plan low-confidence — they make specific slices blocked.

## Plan Format

```markdown
# Plan: [Change Name]

> Date: YYYY-MM-DD
> Status: planning
> Branch: agent/<topic>
> PR: #NNN

## What & Why
[2–3 sentences: what this change accomplishes and why now]

## Spec changes
- `spec/<name>.md` — modified — [what's changing]
- `spec/<name>.md` (new) — [what slice this describes]
- `spec/<name>.md` (superseded by `spec/<new-name>.md`) — [why]

## Slice order
- `spec/<name>.md` — first (entry point, no dependencies)
- `spec/<name>.md` — depends on: <name>
- `spec/<name>.md` — BLOCKED by: [open question title]

## Context changes
- `context/<topic>.md` — [what's changing or being added]

## Constraints
- [Decision: rationale] — confidence: high
- [Decision: rationale] — confidence: medium (ASSUMPTION: [what we're assuming])
- [Decision: rationale] — confidence: low (see open-questions.md)

## Non-Goals
- [What this change explicitly does NOT do]

## Build skills
- [skill-name — why it's needed]

## Grill

Each finding below uses ADR format. Grill runs BEFORE slicing — horizontal validation before vertical decomposition.

### Tensions & Structure

#### [Challenge Title]
- **Status:** resolved
- **Context:** [What part of the plan this challenges]
- **Decision:** [The resolution]
- **Confidence:** high
- **Consequences:** [What changes]
- **Alternatives considered:** [Other options]

### Terminology

#### [Term Collision Title]
- **Status:** resolved
- **Context:** [Term usage in plan vs context/]
- **Decision:** [Standardized term. Written to context/: yes/no]
- **Confidence:** high
- **Consequences:** [Where the term is updated]
- **Alternatives considered:** [Other terms]

### Prior-Decision Conflicts

#### [Conflict Title]
- **Status:** resolved | assumption
- **Context:** [Which spec/context decision this contradicts]
- **Decision:** [Keep old / supersede on purpose]
- **Confidence:** high | medium
- **Consequences:** [What specs/context docs change]
- **Alternatives considered:** [Other resolutions]

### Refutation
- **Strongest argument against this plan:** [argument]
- **Resolution:** [why we proceed anyway / how we addressed it]

## Open Questions
See `changes/NNN-<topic>/open-questions.md` for full detail.
- 🔴 [Blocking question 1] — blocks: [slice list]
- 🟡 [Assumption 1] — affects: [slice list]
```

## Open Questions Format

```markdown
# Open Questions: [Change Name]

> Last updated: YYYY-MM-DD

## Blocking (agent cannot proceed on affected slices)

### [Question title]
- **Status:** open
- **Confidence:** low
- **Slices blocked:** [list]
- **My best guess:** [agent's answer if it has one]
- **Why this blocks:** [what changes depending on the answer]
- **Answer:** [filled by human]
- **Resolution:** [what changed — spec update, context/ update, etc.]

## Assumptions (agent proceeding unless corrected)

### [Assumption title]
- **Status:** assumption-accepted
- **Confidence:** medium
- **Slices affected:** [list]
- **What I'm assuming:** [the decision]
- **Rationale:** [why this seems right]
- **If wrong, impact:** [what would need to change]
- **Correction:** [filled by human if the assumption is wrong]
- **Resolution:** [what changed]
```

## PR Description Format

```markdown
## Summary
[2–3 sentences from the plan's What & Why]

## Status
- **Phase:** Planning complete, awaiting review
- **Slices:** [N] total, [M] unblocked, [K] blocked
- **Open questions:** [N] blocking, [M] assumptions

## Plan
See `changes/NNN-<topic>/plan.md`

## Open Questions
See `changes/NNN-<topic>/open-questions.md`

### Blocking (need your input)
- 🔴 [Question 1] — blocks [slice list]
- 🔴 [Question 2] — blocks [slice list]

### Assumptions (proceeding unless you correct)
- 🟡 [Assumption 1]
- 🟡 [Assumption 2]

## What's Next
- Downstream skills will begin test-planning + building on unblocked slices
- Answer blocking questions to unblock remaining slices
- Leave line-level comments on plan.md or spec files to discuss
```

## Comment Conventions

PR comments from this skill use labeled prefixes:

```
🔴 BLOCKING: [question]
   Slices blocked: [list]
   My best guess: [answer]

🟡 ASSUMPTION: [decision]
   Slices affected: [list]
   Rationale: [why this seems right]

🟢 FYI: [information]
   No action needed.
```

Post comments on the specific lines in plan.md or spec files where the question arises — this enables line-level reply threads.

## Scaling

| Change Size | Constraints | Specs touched | Grill depth |
|---|---|---|---|
| **Small** | 3–5 bullets | 1–2 | 1–2 sanity checks |
| **Medium** | 5–10 bullets | 2–4 | Full three-lens pass |
| **Large** | 10–15 bullets | 4–8 | Full pass + deep refutation |

If the plan touches more than 8 specs, the change is too big — split into multiple changes.

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Asking the human before trying to answer** | Research first. Check context/ and codebase. Only post as open question if you genuinely can't determine the answer. |
| **Marking everything as blocking** | Most decisions can be assumed at medium confidence. Only mark as blocking when the wrong answer would require significant rework. |
| **Marking everything as high confidence** | Security, data-model, and deletion decisions should bias toward low/medium. When in doubt, flag it. |
| **Skipping the grill** | The grill is not optional. Plans that skip it carry wrong assumptions into locked tests. |
| **Grilling surface-level questions** | "Should we use REST or GraphQL?" is a constraint, not a grill question. The grill interrogates the plan's structural assumptions, not its technology choices. |
| **Planning without reading the codebase** | Hard gate. Planning against an imagined architecture is the #1 failure mode. |
| **Duplicating spec content in the plan** | The plan points at specs. Specs hold contracts. Don't restate. |
| **Not recording grill resolutions** | Every grill challenge needs a resolution in the plan's `## Grill` section. Unresolved challenges are open questions. |
| **Proceeding on low-confidence decisions** | Low confidence = blocked. Work on other slices instead. |

## Output

This skill produces:
1. `changes/NNN-<topic>/plan.md` — the plan with grill section
2. `changes/NNN-<topic>/open-questions.md` — medium and low-confidence items
3. Spec stubs in `spec/` for new slices (minimal — test-planning fills them in)
4. Context/ updates (marked as agent-proposed)
5. A pushed branch with a draft PR
6. PR comments for each open question, posted on the relevant lines

The skill does NOT produce test contracts, test code, or implementation code. Downstream skills handle those phases.

## Handoff

After this skill completes:
- **auto-test-planning** picks up unblocked slices and writes integration test contracts
- **auto-test-writer** translates contracts to executable tests
- **auto-build** implements against locked tests
- The human reviews the PR asynchronously, answering questions and correcting assumptions
- As answers arrive, blocked slices become unblocked and the downstream skills continue

## Guidelines

- **GitHub is the communication channel.** Do not ask questions in conversation. Post them as PR comments.
- **Silence = approval.** For high and medium-confidence items, the human doesn't need to respond. The agent proceeds.
- **Corrections improve the system.** When the human corrects an assumption, record it in the most durable appropriate layer (context/, spec/, CLAUDE.md, skill memory).
- **Specs are the source of truth.** The plan is a pointer to a change. Work commitments live in spec/.
- **The grill is the quality gate.** It's what separates a plan from a wish. Every plan gets grilled; the depth scales with the change size.
- **Proceed on unblocked work.** Don't wait for all questions to be answered. Build what you can while questions are outstanding.
