# Autonomous GitHub Flow

> Date: 2026-06-24
> Status: Draft

## Problem

The current skill pipeline (engineering → grill → slicing → test-planning → test-writer → build → refactor) assumes real-time interactive conversation. Every step with user involvement — grill, slicing constraint discovery, test-planning contract validation — blocks on synchronous back-and-forth.

The goal is an autonomous agent that lives on a repo and communicates with the human via GitHub (PRs, comments, labels). The human acts as a staff engineer giving direction, not a pair programmer.

## Operating Model

**Interactive mode (current):** Agent and human share a conversation. Agent asks one question, human answers, agent proceeds. Round-trip: seconds.

**Autonomous mode (new):** Agent works independently, surfaces questions and artifacts via GitHub. Human reviews asynchronously. Agent proceeds on assumptions where confident, blocks only when truly stuck. Round-trip: minutes to hours.

The pipeline steps don't change. The *pacing and communication channel* change.

## Kickoff

Work starts from one of:
- **GitHub issue** with enough detail (what to build, key constraints, anything non-obvious)
- **Manual trigger** with a task description
- **Agent self-identifies work** from existing specs/plan (e.g., a `planned` spec with no implementation)

The kickoff replaces the "understand what we're building" conversation. The agent should NOT need to interview the human to start — it has the issue body + `context/` + `spec/` + codebase. If the kickoff is too vague to produce a plan, the agent posts clarifying questions and waits before starting.

Minimum viable kickoff: 2-3 sentences of what and why. Constraints and non-goals are bonus. The agent infers the rest from context/ and the codebase.

## The Flow

### Phase 0: Investigate (if needed)

**What the agent does:**
1. Reads `context/`, in-scope `spec/`, and codebase
2. Investigates unknowns (web research, codebase exploration)
3. Records findings in `changes/NNN-<topic>/research.md`
4. Promotes system-level findings to `context/` (marked as agent-proposed)

This phase is skipped if the kickoff + context/ provide enough information to plan.

### Phase 1: Grill (horizontals first)

Grill comes BEFORE slicing. The grill validates the approach at the horizontal level — cross-cutting concerns, architectural tensions, terminology, prior-decision conflicts — before the agent commits to how it cuts the work into verticals.

**What the agent does:**
1. Drafts a high-level approach (what, why, key constraints, proposed architecture)
2. Grills the approach using three lenses:
   - Tensions & structure (cardinality, deletion semantics, state transitions, idempotency)
   - Terminology collisions (approach language vs `context/` language)
   - Prior-decision conflicts (existing specs/context the approach contradicts)
3. Self-answers at each confidence level (see Confidence Model below)
4. Records each grill finding as an **ADR (Architecture Decision Record)** in the plan

**Grill output format — ADRs, not a flat list:**

Each grill finding becomes a lightweight ADR in `changes/NNN-<topic>/plan.md`:

```markdown
### ADR: [Decision Title]
- **Status:** accepted | proposed | blocked
- **Context:** [What tension/collision/conflict was found]
- **Decision:** [What we decided]
- **Confidence:** high | medium | low
- **Consequences:** [What this means for the design]
- **Alternatives considered:** [What else we could have done]
```

High-confidence ADRs are `accepted`. Medium-confidence are `proposed` (assumption — proceeding unless corrected). Low-confidence are `blocked` (posted as PR question).

**What the agent pushes:**
- Creates branch (`agent/<topic>`)
- Pushes: plan.md with ADRs, open-questions.md, any context/ updates
- Opens **draft PR** (this is the "plan PR" — one per change, not per slice)
- PR description = summary of the approach + current status
- Low-confidence ADRs → PR comments on the relevant lines, labeled with severity

**What the human does:**
- Reviews approach + ADRs
- Leaves line-level comments on plan.md or ADR entries
- Can use a separate Claude Code chat to read the PR and ask clarifying questions in a different context
- Doesn't need to answer everything — agent proceeds on assumptions

### Phase 2: Slicing (verticals from grilled approach)

After the approach is grilled, the agent decomposes into vertical slices.

**What the agent does:**
1. Declares which specs are added, modified, or superseded
2. Identifies the dependency graph (which slices depend on which)
3. Identifies the first slice (entry point, fewest dependencies)
4. Creates spec stubs for new slices
5. Updates plan.md with slice order and dependency graph

**What the agent pushes:**
- Updates the plan PR with spec stubs and slice order
- Each independent slice will get its own PR in the next phases (see PR-per-Slice below)

### Phase 3: Test Planning + Test Writing + Build (per slice)

Each slice follows the full pipeline: test-plan → test-write → build → refactor.

**PR-per-slice model:** Each slice gets its own PR branched from the appropriate base. This makes reviews atomic — each PR has one test contract, one test suite, one implementation. The human reviews one focused change at a time instead of a monolithic diff.

**Branching strategy — stacked PRs + worktrees:**

The agent builds a dependency DAG from spec `depends_on` frontmatter, then:
- **Independent slices** branch from `main`, can be built in parallel using separate git worktrees
- **Dependent slices** use **stacked branches** via `gh stack` (GitHub native, shipped April 2026): slice B branches from slice A's branch, PR targets A's branch
- When slice A merges to main, `gh stack sync` cascading-rebases the chain and retargets PRs to main automatically
- `gh stack push` uses `--force-with-lease --atomic` — safe (rejects if remote has unexpected changes) and atomic (all branches update or none do). This is inherent to stacked workflows where rebase rewrites history.
- **Fallback** if `gh stack` unavailable: Graphite `gt` CLI with `--no-interactive`, or plain `git` + `gh pr create --base <parent-branch>` with agent-managed dependency tracking

**Parallel worktree pattern:**
```bash
# Independent slices get their own worktrees
git worktree add ../repo-slice-d agent/<topic>/slice-d
git worktree add ../repo-slice-e agent/<topic>/slice-e
# Each worktree = own agent session, own branch, merge back after green
# Cleanup after merge: git worktree remove <path>
```

**Per-slice flow:**
1. **Test planning:** Write integration test contract in `spec/<name>.md`, classify confidence
2. **Test writing:** Translate contract to executable tests, confirm red, commit as locked artifacts
3. **Build:** Implement against locked tests (red → green), full-suite gate, invoke refactor
4. **Push:** Open a slice PR (`agent/<topic>/<slice-name>`), request review

**Per-slice PR conventions:**
- Title: `[Agent] <slice-name>: <one-line description>`
- Base: `main` for independent slices, parent slice branch for dependent slices
- Body: spec contract, test pointers, implementation summary
- Label: `agent-slice`

**What the human does per slice PR:**
- Reviews the test contract (is this what "done" looks like?)
- Reviews the implementation
- Can override a locked test via PR comment (one-time permission, not a general unlock)
- Approves or requests changes

### Phase 4: Completion

**When all slices are done:**
- Agent updates the plan PR description with final status
- Links to all slice PRs
- If blocked slices remain → posts summary of what's blocked and why
- Slice PRs merge independently as they're approved (in dependency order)
- Plan PR is closed (not merged — it's a coordination artifact, not code)

**When human approves a slice PR:**
- Agent does NOT self-merge (protected branches / human-only merge)
- Agent rebases dependent slice branches onto main after merge
- Agent may do final cleanup if review comments request changes → new commits → re-request review

## Confidence Model

Every decision the agent makes gets a confidence classification. This replaces the interactive confidence gates.

| Confidence | Agent behavior | GitHub artifact | Human action needed |
|---|---|---|---|
| **High** | Proceeds. Records decision in plan/spec. | No comment (or FYI if noteworthy) | None — silence = approval |
| **Medium** | Proceeds on assumption. Records assumption explicitly. | PR comment: "ASSUMPTION: [decision]. Building against this unless corrected." | Correct if wrong. Silence = accepted. |
| **Low / blocking** | Does NOT build against this. Works on other slices. | PR comment: "BLOCKING: [question]. Slices blocked: [list]. My best guess: [X]." | Must answer before blocked slices proceed. |

**What raises/lowers confidence:**
- `context/` has a clear answer → high
- Codebase patterns suggest an answer → high
- Multiple valid approaches, no clear signal → medium
- Contradicts existing spec/context, or no information at all → low
- Security/data-model/deletion-semantics decisions → bias toward low (expensive to get wrong)

## The GitHub Protocol

### Branch naming
- Plan branch: `agent/<topic>` (e.g., `agent/credential-refresh-flow`)
- Slice branches: `agent/<topic>/<slice-name>` (e.g., `agent/credential-refresh-flow/create-intent`)
- Stacked slices: branch from parent slice branch, not from `agent/<topic>`

### Two PR types
1. **Plan PR** — opened as draft after grill+plan. Contains plan.md, ADRs, open-questions.md, spec stubs, context/ updates. This is a coordination artifact — it's closed (not merged) when all slice PRs are done.
2. **Slice PRs** — one per slice. Contains the test contract, locked tests, implementation, and refactor. These are the PRs that get reviewed and merged.

### PR lifecycle (plan PR)
1. Opened as **draft** after grill+plan completes
2. Updated with status comments as slices progress
3. Links to all slice PRs in description
4. Closed when all slices are merged (or blocked slices documented)

### PR lifecycle (slice PRs)
1. Opened after test-write + build for that slice
2. Base: `main` for independent slices, parent slice branch for dependent slices
3. Marked **ready for review** immediately (each slice is self-contained)
4. Merged independently by the human in dependency order
5. After merge, agent runs `gh stack sync` to cascade-rebase dependent slices

### Labels (the state machine)
- `agent-in-progress` — agent is actively working
- `needs-answer` — agent is blocked on human input
- `ready-for-review` — all work done, awaiting human review
- `changes-requested` — human left review comments, agent addressing them
- `agent-slice` — marks a slice PR (vs the plan PR)
- `agent-plan` — marks the plan/coordination PR

### Comment conventions
Comments from the agent use a prefix to indicate type:

```
🔴 BLOCKING: [question]
   Slices blocked: [list]
   My best guess: [answer]

🟡 ASSUMPTION: [decision]
   Slices affected: [list]
   Rationale: [why this seems right]

🟢 FYI: [information]
   No action needed.

📋 STATUS: [phase update]
   Completed: [list]
   In progress: [list]
   Blocked: [list]
```

### Open questions file
`changes/NNN-<topic>/open-questions.md` — the index of all questions. Each entry:

```markdown
### [Question title]
- **Status:** open | answered | assumption-accepted
- **Confidence:** low | medium
- **Slices blocked:** [list, or "none — proceeding on assumption"]
- **My best guess:** [agent's answer]
- **Answer:** [human's answer, filled in when responded to]
- **Resolution:** [what changed as a result — spec update, context/ update, etc.]
```

The human can answer by:
- Leaving a line-level PR comment on the question → agent reads and updates the file
- Editing the file directly → agent reads on next poll
- Leaving a general PR comment → agent reads and maps to the relevant question

## Correction Feedback Loop

When the human corrects an assumption or answers a question, the fix goes into the **most durable appropriate layer**:

| Correction type | Where it lands | Why |
|---|---|---|
| Project architecture decision | `context/<topic>.md` | Prevents the same question on future changes |
| Behavioral expectation | `spec/<name>.md` | Becomes a locked contract |
| Agent behavior / approach preference | Skill memory or CLAUDE.md | Improves the agent's future judgment |
| One-off clarification | `changes/NNN/plan.md` only | Doesn't generalize |

The agent should explicitly state where it's recording the correction: "Recorded in `context/security-model.md` — won't ask again."

## Polling and Triggers

The supervisor (running on the always-on box) manages timing. Claude Code also supports native scheduling via `/schedule` and cloud Routines (see https://code.claude.com/docs/en/scheduled-tasks) — these can complement or replace self-hosted triggers.

### Triggers that start a new cycle
- **Issue created** with agent label/assignee → new grill+plan pass
- **PR comment from human** → agent reads, updates, continues
- **PR review submitted** → agent addresses review comments
- **Heartbeat timer** (configurable, default ~2-4 hours) → agent checks for unanswered items that got answered, stale PRs
- **Claude Code Routine** (cron ≥1h or GitHub webhook) → cloud-managed trigger, laptop-independent
- **Slice PR merged** → agent rebases dependent slices, continues building next slice

### What the agent does on each wake
1. Check for new human comments on active PRs (plan PR + all slice PRs)
2. Map comments to open questions / change requests
3. Update open-questions.md with answers
4. Unblock slices whose questions are now answered
5. Rebase dependent branches if parent slices merged
6. Continue building unblocked slices
7. Post status update if state changed

### What the agent does NOT do
- Poll more than every ~1 hour (respects subscription caps)
- Work on blocked slices without answers
- Self-merge any PR
- Push to main/master directly
- Force-push or delete branches without human approval

## Skill Changes Needed

Each skill interacts with GitHub differently. The GitHub interaction is skill-specific, not a generic adapter — the plan skill opens plan PRs and posts ADRs as comments; the build skill opens slice PRs and posts stuck-points; the refactor skill just commits to the slice branch.

### Grill (horizontal approach validation)
- **Remove:** one-at-a-time Q&A pacing
- **Add:** bulk grill with ADR output format, confidence classification, self-answering
- **GitHub role:** opens the plan PR (draft), posts blocking/assumption ADRs as line comments on plan.md, manages the `agent-plan` label
- **Keep:** three grill lenses, context/ loading

### Slicing (vertical decomposition)
- **Remove:** interactive constraint discovery conversation
- **Add:** dependency graph construction, spec stub generation, stacked branch planning
- **GitHub role:** updates the plan PR with slice order and spec stubs, creates branch structure for slices
- **Keep:** spec change declaration, plan format, first-slice identification

### Test Planning
- **Remove:** interactive checkpoint validation ("present one at a time, wait")
- **Add:** autonomous contract writing with confidence classification
- **GitHub role:** commits contracts to slice branches, posts assumption/blocking comments on spec files in slice PRs
- **Keep:** contract format, mock boundary decisions, spec file structure

### Test Writer
- **Remove:** nothing significant — already mostly autonomous
- **Add:** commits to slice branch, pushes
- **GitHub role:** minimal — test files committed to slice branch. Posts comment only if infrastructure issues block test writing.
- **Keep:** everything — AAA, confirm red, locked artifacts, spec pointer updates

### Build
- **Remove:** nothing significant — already mostly autonomous
- **Add:** commits to slice branch, pushes, opens slice PR when green
- **GitHub role:** opens slice PR (`agent-slice` label), posts stuck-points as comments, requests review when green
- **Keep:** everything — TDD loop, full-suite gate, refactor invocation, spec status updates

### Refactor
- **Minimal changes.** Commits to slice branch. No direct GitHub interaction beyond the commit.

### Checker / Validation Skills
Beyond refactor, additional validation skills may be needed:
- **Spec compliance checker** — does the implementation match the spec contract? (already exists as a step in build's subagent mode)
- **Security review** — does the change introduce security issues? (especially important for security-critical projects like Ostia)
- **Cross-slice regression checker** — do merged slices still work together? (runs after dependent slices rebase)
- **CI validator** — do CI checks pass? (reads GitHub Actions results)

These are future additions. Refactor + the locked-test full-suite gate are the day-one validation layer. Additional checkers layer on as we learn where the autonomous agent's blind spots are.

### GitHub Operations (shared infrastructure, not a skill)
Common operations used by multiple skills:
- Branch management (`gh stack`, worktrees, rebase after merge)
- PR lifecycle (create, update description, add/remove labels, request review)
- Comment reading and parsing (map human comments to open questions)
- Comment writing (labeled with 🔴/🟡/🟢/📋 prefixes)
- Polling logic (check for new comments, map to state changes)

These are bash/gh commands available to all skills, not a separate skill. Each skill calls them differently depending on its GitHub role.

## Eval Tasks for Skill Evolution (Phase: L1 Factory)

With this flow defined, eval tasks for GEPA optimization can be drawn from Ostia. For each skill in flow order:

### Plan + Grill evals
- **Input:** Issue body describing a feature for Ostia (e.g., "add network namespace isolation to sandbox profiles")
- **Grader:** Does the plan reference correct context/ files? Are grill questions substantive (not surface-level)? Do confidence classifications match what a senior engineer would assign? Does the open-questions file capture the genuinely uncertain items?
- **Feedback:** LLM judge comparing plan quality to expert-written plan for the same feature

### Test Planning evals
- **Input:** Plan + spec changes for an Ostia feature
- **Grader:** Do contracts cover happy path + error cases? Are mock boundaries correct per context/? Do contracts trace to plan constraints?
- **Feedback:** LLM judge on contract completeness and mock boundary correctness

### Build evals
- **Input:** Spec + locked red tests for an Ostia slice
- **Grader:** Do tests go green? Full suite still green? Implementation matches spec? No locked tests modified?
- **Feedback:** Code review judge on implementation quality

## Separation from Existing Skills

**These autonomous skills are a trial run — they do NOT replace the existing interactive pipeline.** The current skills (engineering, slicing, test-planning, test-writer, build, refactor) remain untouched and in active use.

Autonomous skills live in the same repo (`dev-config/ai-workflow-config/skills/`) as new directories alongside the existing ones (e.g., `skills/auto-plan-grill/`, `skills/auto-test-planning/`, `skills/auto-build/`). They share the same spec/context/changes model and file formats, but have different communication patterns (GitHub artifacts instead of interactive Q&A). The existing interactive skills are not modified — the auto-* skills are copies that diverge.

If the autonomous versions prove effective, selective migration later. If not, nothing lost — the interactive pipeline still works.

## Slice Dependency and Parallelism

The agent works on unblocked slices, but **within the dependency DAG**. Each spec's `depends_on` frontmatter defines the order. The agent:
- Builds the dependency graph from spec frontmatter
- Identifies independent slices (no shared dependencies among them)
- Builds dependent slices sequentially
- Independent slices MAY run in parallel (future: separate worktrees/branches per independent slice, merge back after green)

Day one: sequential build in dependency order, skipping blocked slices. Worktree parallelism is a later optimization once the basic loop is proven.

## Corrections as Eval Signal

Every human correction is a potential GEPA eval example:
- Agent assumed X → human corrected to Y → labeled training pair for reflective feedback
- Pattern of corrections in the same area → signal that the skill needs evolution in that dimension
- Corrections that land in context/ or spec/ improve the agent's raw inputs; corrections that land in skill memory or CLAUDE.md improve the agent's judgment

Track corrections in a lightweight log (`changes/NNN-<topic>/corrections.md`) so they can be harvested for eval tasks later. Format:

```markdown
### [Correction title]
- **Phase:** plan-grill | test-planning | build
- **What agent assumed:** [X]
- **What was correct:** [Y]
- **Where recorded:** context/<file>.md | spec/<file>.md | skill memory | plan only
- **Generalizable:** yes | no (would this help on a different project?)
```

## Migration Path

1. **Design the autonomous flow** (this document) ← we are here
2. **Write the merged plan+grill skill** as a new `auto-plan-grill` skill (separate from existing skills)
3. **Set up L1 eval harness** with 5-10 Ostia-derived tasks for plan+grill
4. **Evolve auto-plan-grill** via GEPA against those tasks
5. **Repeat for auto-test-planning, then auto-build** (test-writer and refactor are low-priority — already mostly autonomous)
6. **Build the GitHub adapter** and supervisor
7. **Pilot on Ostia** — full autonomous cycle on a real feature
8. **gskill later** — once Ostia has clean commit history from autonomous work, point gskill at it for further repo-specific optimization
