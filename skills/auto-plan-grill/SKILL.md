---
name: auto-plan-grill
description: >-
  Autonomous planning + grill for GitHub-driven development. Reads context/spec/codebase,
  lands scope as spec stubs and decisions in context/ (ADR-style, agent-proposed),
  self-grills using three lenses, classifies confidence on every decision, pushes
  to a branch, opens a draft PR whose description carries the plan narrative, and
  posts open questions as PR comments. Proceeds on medium-confidence assumptions.
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

Autonomous planning with built-in self-grilling. Read the project, land the scope in the durable layers, poke holes in it, push to GitHub, and let the human review asynchronously. No interactive conversation — GitHub is the communication channel.

## The Model

Two persistent layers at the project root (same as the interactive pipeline):

- **`context/`** — architectural truth. Always loaded. Decisions are ADR-style: chosen, rationale, and rejected alternatives with the why-not. `context/research/` holds dated research references.
- **`spec/`** — behavioral specs. One file per slice, with integration test contracts, `status` frontmatter (`planned | in-progress | built | superseded`), `depends_on`, `## Notes`, and a `## Changes` log.

Git + GitHub carry the change narrative: the branch diff shows what the planning changed, the **draft PR description is the plan document** the human reads, and PR comments are the question channel. Scope-in-flight = which specs are `planned`/`in-progress`.

This skill's job: go from "kickoff description" to "scope landed in spec/ + context/, PR open, questions posted, ready for downstream skills to build unblocked slices."

<HARD-GATE>
Do not write implementation code. Do not write tests. Do not write test contracts. Output is spec stubs, context/ updates, a pushed branch with a draft PR, and open questions posted as PR comments. Downstream skills (auto-test-planning, auto-build) handle everything after.
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

**`context/` — always loaded.** Read all files. These are architectural constraints — including standing rejections — that inform every decision.

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

Research autonomously. Save dated, sourced findings to `context/research/<topic>.md` and cite them from the relevant topic file. Promote system-level conclusions to `context/` marked "Proposed by agent — not yet human-confirmed."

### 2. Plan

Derive the scope. This merges what the interactive pipeline does across slicing steps 2–7.

**Discover constraints autonomously.** Instead of asking the human about each constraint:
- Derive constraints from `context/`, the codebase, and research
- For each constraint, classify confidence (see Confidence Model below)
- High-confidence constraints land directly in their durable home (context/ for system-level, spec Notes for slice-level)
- Medium-confidence constraints land the same way, marked as assumptions
- Low-confidence constraints become blocking open questions (posted to the PR; noted in the affected spec's `## Notes`)

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
- Which slices depend on which (`depends_on` frontmatter)
- Which slices are independent (can be built without waiting for others)
- Which slices are blocked by open questions

**Suggest build skills:** Language/runtime, domain, infrastructure skills needed — note in the entry-point spec's `## Notes` if non-obvious.

### 3. Grill (bulk, in the same pass)

Immediately after deriving the scope — before pushing it — grill it. The planning pass builds the scope up; the grill tries to knock it down.

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
- Does the scope use a term that `context/` defines differently?
- Does it introduce a new term that overlaps with an existing one?
- Are there fuzzy terms that need sharpening before they enter a spec?

#### Lens 3: Prior-Decision Conflicts
Find existing spec contracts or `context/` decisions this scope contradicts:
- Name the conflict explicitly
- Propose resolution: keep the old decision, or supersede on purpose
- Never leave both implicitly in effect
- A superseded **locked contract** is flagged for auto-test-planning → auto-test-writer to re-lock; never edit locked artifacts here

#### Refutation Attempt
Close with one attempt to refute the scope:
- Is there a simpler version that accomplishes the same goal?
- Does an existing capability already cover this?
- Does it break an invariant it doesn't acknowledge?

Resolve the refutation (accept or reject). A rejected refutation is a rejected alternative — record it in the relevant `context/` topic file.

#### Self-Answering Grill Findings

For each grill finding, the agent does one of:

| Confidence | Action | Where it lands |
|---|---|---|
| **High** | Self-answers. | ADR entry in the relevant `context/` topic file (agent-proposed) or the affected spec's `## Notes`. |
| **Medium** | Self-answers tentatively. | Same as high, marked "Assumption"; 🟡 PR comment so the human can correct. |
| **Low** | Does NOT assume. | "Open (blocking): …" line in the affected spec's `## Notes`; 🔴 PR comment with the agent's best guess. |

#### ADR Format for Grill Entries

Each durable grill resolution is recorded as a lightweight Architecture Decision Record in the `context/` topic file it belongs to (or the spec's `## Notes` when slice-scoped):

```markdown
- **[Decision title]** — [the resolution]. Rationale: [why]. Rejected: [alternative] — [why not].
  (agent-proposed, confidence: high | assumption)
```

Challenges the design survived unchanged get one line in the planning commit message, not a context entry.

### 4. Build the Dependency Graph

From the scope, produce a dependency ordering:

1. Read `depends_on` frontmatter from existing specs
2. For new specs, infer dependencies from the constraints
3. Classify each slice:
   - **Unblocked** — no open low-confidence questions affect it, all dependencies are either already built or also unblocked
   - **Blocked** — depends on an unanswered low-confidence question, or depends on a blocked slice
4. Record blockers in each affected spec's `## Notes` ("BLOCKED by: [question]"); summarize the order in the PR description's Slice Order section

### 5. Land the Artifacts

#### Spec stubs (new specs) and spec updates (modified specs)

For each new spec, create a stub in `spec/<name>.md`:

```markdown
---
status: planned
depends_on: []
---

# [Slice Name]

## Does
[One sentence]

## Done when
- [Placeholder — auto-test-planning will fill this in]

## Integration test contract
[Placeholder — auto-test-planning will fill this in]

## Tests
No test exists yet — auto-test-planning will produce the contract, auto-test-writer will produce the test.

## Notes
- [Slice-level decisions and assumptions, with confidence markers]
- Out of scope: [non-goals]
- Open (blocking): [question] — see PR comment
- Created by auto-plan-grill from kickoff: [issue URL / one-line description]

## Changes
- YYYY-MM-DD — created (auto-plan-grill): [why this slice]
```

For each modified spec: set `status: in-progress`, append intent to `## Notes` and `## Changes`, name any supersession explicitly.

#### Context updates
System-level decisions, grill ADRs, and terminology land in `context/` topic files, marked "Proposed by agent — not yet human-confirmed." Dated research goes to `context/research/`.

### 6. Push to GitHub

1. **Create branch:** `agent/<topic>` from main/default branch
2. **Commit:** spec stubs/updates + context/ updates. The commit message carries the plan narrative (what & why, key decisions, named supersessions).
3. **Push branch**
4. **Open draft PR** — the PR description IS the plan document (see PR Description Format below)
5. **Add label:** `agent-in-progress`
6. **Post PR comments** for each open question:
   - 🔴 BLOCKING questions → comment on the relevant line in the affected spec or context file
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

**Confidence is per-decision, not per-plan.** A scope can have 10 high-confidence constraints and 2 low-confidence ones. The 2 low-confidence ones don't make the whole scope low-confidence — they make specific slices blocked.

## PR Description Format

The draft PR description is the plan document the human reviews:

```markdown
## Summary
[2–3 sentences: what this change accomplishes and why now]

## Scope
- `spec/<name>.md` (new, planned) — [what slice this describes]
- `spec/<name>.md` (modified, in-progress) — [what's changing]
- `spec/<name>.md` (superseded by `spec/<new-name>.md`) — [why]
- `context/<topic>.md` — [decisions added/changed, agent-proposed]

## Slice order
- `spec/<name>.md` — first (entry point, no dependencies)
- `spec/<name>.md` — depends on: <name>
- `spec/<name>.md` — 🔴 BLOCKED by: [open question title]

## Key decisions & assumptions
- [Decision — rationale] — confidence: high
- [Decision — rationale] — 🟡 ASSUMPTION: [what we're assuming]
- 🔴 [Open question] — blocks [slice list] — best guess: [answer]

## Non-Goals
- [What this change explicitly does NOT do]

## Grill summary
- [Challenge] → [resolution or "held — see context/<topic>.md"]
- Refutation: [strongest argument against] → [why we proceed / what changed]

## What's Next
- Downstream skills will begin test-planning + building on unblocked slices
- Answer 🔴 blocking comments to unblock remaining slices
- Leave line-level comments on spec/context files to discuss
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

Post comments on the specific lines in the spec or context files where the question arises — this enables line-level reply threads. When the human answers, record the resolution in the same durable file (spec `## Notes` / context entry) and drop the "agent-proposed" marker.

## Scaling

| Change Size | Constraints | Specs touched | Grill depth |
|---|---|---|---|
| **Small** | 3–5 bullets | 1–2 | 1–2 sanity checks |
| **Medium** | 5–10 bullets | 2–4 | Full three-lens pass |
| **Large** | 10–15 bullets | 4–8 | Full pass + deep refutation |

If the scope touches more than 8 specs, the change is too big — split into multiple changes.

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Asking the human before trying to answer** | Research first. Check context/ and codebase. Only post as open question if you genuinely can't determine the answer. |
| **Marking everything as blocking** | Most decisions can be assumed at medium confidence. Only mark as blocking when the wrong answer would require significant rework. |
| **Marking everything as high confidence** | Security, data-model, and deletion decisions should bias toward low/medium. When in doubt, flag it. |
| **Skipping the grill** | The grill is not optional. Scopes that skip it carry wrong assumptions into locked tests. |
| **Grilling surface-level questions** | "Should we use REST or GraphQL?" is a constraint, not a grill question. The grill interrogates structural assumptions, not technology choices. |
| **Planning without reading the codebase** | Hard gate. Planning against an imagined architecture is the #1 failure mode. |
| **Writing scope or rationale into a standalone planning doc** | Scope → spec stubs; decisions → context/; narrative → the commit message + PR description. |
| **Decisions without their rejected alternatives** | Record "Rejected: X — because Y" next to the decision in context/. |
| **Not recording grill resolutions** | Every grill challenge lands in context/, a spec's Notes, or the commit message. Unresolved challenges are open questions. |
| **Proceeding on low-confidence decisions** | Low confidence = blocked. Work on other slices instead. |

## Output

This skill produces:
1. Spec stubs/updates in `spec/` — statuses set, Notes carrying slice decisions, assumptions, blockers
2. `context/` updates (ADR-style, marked agent-proposed) + `context/research/` entries for dated findings
3. A pushed branch with a draft PR whose description is the plan document
4. PR comments for each open question, posted on the relevant lines

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
- **Corrections improve the system.** When the human corrects an assumption, record it in the most durable appropriate layer (context/, spec/, CLAUDE.md, skill memory) and drop the agent-proposed marker.
- **Specs are the source of truth.** Work commitments live in spec/; decisions live in context/; the PR tells the story.
- **The grill is the quality gate.** It's what separates a plan from a wish. Every scope gets grilled; the depth scales with the change size.
- **Proceed on unblocked work.** Don't wait for all questions to be answered. Build what you can while questions are outstanding.
