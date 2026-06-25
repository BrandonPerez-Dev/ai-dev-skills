# Autonomous GitHub Flow

> Date: 2026-06-24
> Status: Draft

## Problem

The current skill pipeline (engineering → slicing → grill → test-planning → test-writer → build → refactor) assumes real-time interactive conversation. Every step with user involvement — grill, slicing constraint discovery, test-planning contract validation — blocks on synchronous back-and-forth.

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

### Phase 1: Investigate + Plan + Grill (one pass)

**What the agent does:**
1. Reads `context/`, in-scope `spec/`, and codebase
2. Investigates unknowns (web research, codebase exploration)
3. Produces the plan (`changes/NNN-<topic>/plan.md`) with spec changes declared
4. Grills its own plan using the three lenses:
   - Tensions & structure (cardinality, deletion semantics, state transitions, idempotency)
   - Terminology collisions (plan language vs `context/` language)
   - Prior-decision conflicts (existing specs/context the plan contradicts)
5. Self-answers grill questions at each confidence level (see Confidence Model below)
6. Creates `changes/NNN-<topic>/open-questions.md` with anything medium or low confidence

**What the agent pushes:**
- Creates branch (`agent/<topic>`)
- Pushes: plan.md, open-questions.md, any context/ updates
- Opens **draft PR**
- PR description = summary of the plan + current status
- Low-confidence questions → PR comments on the relevant lines in plan.md or spec files, labeled with severity

**What the human does:**
- Reviews plan + open questions
- Leaves line-level comments on plan.md, spec files, or open-questions.md
- Can also use a separate Claude Code chat to read the PR and ask clarifying questions in a different context
- Doesn't need to answer everything — agent proceeds on assumptions

**When the agent proceeds:**
- Immediately after posting, without waiting for human review
- Starts working on slices that are NOT blocked by low-confidence open questions
- Checks for human responses periodically (see Polling below)

### Phase 2: Test Planning (per slice, autonomous)

**What the agent does:**
1. For each unblocked slice in dependency order:
   - Writes or extends the integration test contract in `spec/<name>.md`
   - Decides mock boundaries based on `context/` (doesn't need to ask — context/ should document which systems have test modes)
   - Classifies contract confidence

**What the agent pushes:**
- Commits updated spec files to the branch
- High-confidence contracts → pushed with FYI comment ("contracts ready for `<slice>`, proceeding to test writing")
- Medium-confidence contracts → pushed with assumption comment ("assumed X for `<slice>`, will build against this unless corrected")
- Low-confidence contracts → pushed with blocking comment, slice paused

**What the human does:**
- Reviews spec file changes in the PR
- Line-level comments to correct contracts
- Approval = silence (agent proceeds after a reasonable window)

### Phase 3: Test Writing (per slice, autonomous)

**What the agent does:**
1. For each slice with a high/medium-confidence contract:
   - Translates contracts to executable tests (AAA structure)
   - Confirms each test fails for the right reason
   - Updates spec `## Tests` section with pointers
   - Commits test files + spec updates

**What the agent pushes:**
- Per-slice test commits
- If a test can't be written (infrastructure missing, contract unclear) → PR comment explaining what's blocked

### Phase 4: Build (per slice, autonomous)

**What the agent does:**
1. For each slice with committed red tests:
   - Implements against locked tests (red → green → refactor)
   - Full-suite gate after each slice
   - Marks spec `status: built`
   - Invokes refactor on just-committed changes

**What the agent pushes:**
- Per-slice implementation commits
- Per-slice refactor commits (if refactor finds improvements)
- If stuck after 2 attempts → PR comment explaining the failure, moves to next unblocked slice

### Phase 5: Completion

**When all buildable slices are done:**
- Agent updates PR description with final status
- If blocked slices remain → posts summary of what's blocked and why
- If all slices done → marks PR ready for review, requests review
- Removes `in-progress` label, adds `ready-for-review`

**When human approves:**
- Agent does NOT self-merge (protected branches / human-only merge)
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
`agent/<topic>` (e.g., `agent/credential-refresh-flow`)

### PR lifecycle
1. Opened as **draft** immediately after plan is pushed
2. Updated with commits as work progresses
3. PR description updated at each phase transition
4. Marked **ready for review** when all buildable slices are done
5. Never self-merged

### Labels (the state machine)
- `agent-in-progress` — agent is actively working
- `needs-answer` — agent is blocked on human input
- `ready-for-review` — all work done, awaiting human review
- `changes-requested` — human left review comments, agent addressing them

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

The supervisor (running on the always-on box) manages timing:

### Triggers that start a new cycle
- **Issue created** with agent label/assignee → new plan+grill pass
- **PR comment from human** → agent reads, updates, continues
- **PR review submitted** → agent addresses review comments
- **Heartbeat timer** (configurable, default ~2-4 hours) → agent checks for unanswered items that got answered, stale PRs

### What the agent does on each wake
1. Check for new human comments on active PRs
2. Map comments to open questions / change requests
3. Update open-questions.md with answers
4. Unblock slices whose questions are now answered
5. Continue building unblocked slices
6. Post status update if state changed

### What the agent does NOT do
- Poll more than every ~1 hour (respects subscription caps)
- Work on blocked slices without answers
- Self-merge any PR
- Push to main/master directly
- Delete branches without human approval

## Skill Changes Needed

Each skill needs an **autonomous adapter** — a thin wrapper that translates its interactive communication into GitHub artifacts. The core logic stays the same.

### Plan + Grill (merged from engineering + slicing + grill)
- **Remove:** one-at-a-time Q&A pacing, interactive constraint discovery
- **Add:** bulk grill with confidence classification, self-answering, open-questions.md generation
- **Add:** GitHub artifact generation (branch, draft PR, labeled comments)
- **Keep:** three grill lenses, context/ loading, spec change declaration, plan format

### Test Planning
- **Remove:** interactive checkpoint validation ("present one at a time, wait")
- **Add:** autonomous contract writing with confidence classification
- **Add:** PR comments for medium/low-confidence contracts
- **Keep:** contract format, mock boundary decisions, spec file structure

### Test Writer
- **Remove:** nothing significant — already mostly autonomous
- **Add:** git push per slice, PR comment on infrastructure issues
- **Keep:** everything — AAA, confirm red, locked artifacts, spec pointer updates

### Build
- **Remove:** nothing significant — already mostly autonomous
- **Add:** git push per slice, PR comment on stuck-points, skip-and-continue for blocked slices
- **Keep:** everything — TDD loop, full-suite gate, refactor invocation, spec status updates

### Refactor
- **No changes.** Already fully autonomous. Just commits to the branch.

### New: GitHub Adapter (infrastructure, not a skill)
- Branch management (create, push, never force-push)
- PR lifecycle (open draft, update description, add/remove labels, request review)
- Comment reading and parsing (map human comments to open questions)
- Comment writing (labeled with 🔴/🟡/🟢/📋 prefixes)
- Polling logic (check for new comments, map to state changes)

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
