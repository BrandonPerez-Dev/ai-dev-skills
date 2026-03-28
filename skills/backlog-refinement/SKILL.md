---
name: backlog-refinement
description: Refine and maintain product backlogs — make stories sprint-ready through acceptance criteria, vertical splitting, and backlog hygiene. Produces refined stories with testable criteria, split epics, and backlog health assessments. Use when asked to refine the backlog, groom stories, split an epic, write acceptance criteria, define or write user stories, prioritize or order the backlog, check backlog health, assess if stories are sprint-ready, clean up the backlog, or prepare stories for sprint planning. This skill PREPARES stories to be sprint-ready — use sprint-planning to SELECT which ready stories go into a sprint. Use decompose-tasks to break technical designs into implementation tasks. Use write-spec to formalize requirements into a PM-reviewable specification document.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - Skill
  - AskUserQuestion
argument-hint: "[story/epic to refine, or 'health check']"
---

# Backlog Refinement

Refinement makes stories sprint-ready — it's the ongoing practice that prevents sprint planning from becoming a 3-hour chaos session. The output is stories the team can confidently pull, not a perfectly detailed backlog.

<HARD-GATE>
Stories entering a sprint MUST have acceptance criteria (3+ testable criteria). Title-only stories break sprints. If a story has no acceptance criteria, it is not ready — full stop.
</HARD-GATE>

<HARD-GATE>
Split vertically, not horizontally. A story must deliver end-to-end value — "build the database schema" is a task, not a story. "User can save a draft quote" is a story. If a story has no user-facing outcome, it's a component task masquerading as a story.
</HARD-GATE>

## Method Selection

| Situation | Approach | Why |
|---|---|---|
| **Regular refinement session** | Ceremony flow (Steps 1-7) | Full backlog pass — triage, refine, estimate, rank |
| **Epic needs splitting** | Story splitting flow | Large item needs vertical decomposition |
| **Backlog health check** | Health assessment | Diagnose backlog problems before they hit sprints |
| **Story needs acceptance criteria** | AC writing flow (Step 3) | Individual story needs testable criteria |
| **Backlog is too large (>200 items)** | Pruning flow | Zombie backlog needs aggressive cleanup |

## Input Resolution

1. If `$ARGUMENTS` is a file path, read that as the backlog or story to refine
2. If `$ARGUMENTS` is "health check", run the health assessment
3. Search `docs/plans/` for backlog files, sprint artifacts, or story documents
4. If no artifacts exist, ask the user to provide the backlog or stories to refine

## Process

### Step 1: Review Backlog Health Metrics

Assess the current state before doing any refinement work:

```
BACKLOG HEALTH:
  Ready item ratio (top 2 sprints meeting DoR): [X]%
    Healthy: >80%  |  Warning: <50%
  Backlog depth: [X] sprints of ready stories
    Healthy: 2-3 sprints  |  Warning: <1 or >5
  Item age: [X]% older than 6 months
    Healthy: <10%  |  Warning: >10%
  Sprint carryover rate: [X]%
    Healthy: <10%  |  Warning: >25%
  Work type balance:
    Features: [X]%  (~65%)
    Bugs: [X]%  (~15%)
    Tech debt: [X]%  (~15%)
    Spikes: [X]%  (~5%)
```

If health data isn't available, flag it — "we can't assess backlog health without visibility into these metrics" is a finding.

### Step 2: Triage New Items

For each new or unrefined item, decide:

- **Accept** — belongs in the backlog, needs refinement
- **Defer** — valid idea, not now — park with a revisit trigger
- **Delete** — duplicates, stale ideas, items with no strategic connection

**Not everything belongs in the backlog.** The backlog is not a wish list. Items without a connection to current themes or roadmap priorities should be deferred or deleted.

### Step 3: Write/Refine Acceptance Criteria

For top-priority items, write testable acceptance criteria using Given/When/Then:

```
STORY: [User story in standard format]
  As a [persona], I want to [action] so that [outcome]

ACCEPTANCE CRITERIA:
  AC1: Given [precondition]
       When [action]
       Then [observable outcome]

  AC2: Given [precondition]
       When [action]
       Then [observable outcome]

  AC3: Given [precondition]
       When [action]
       Then [observable outcome]
```

**AC quality checks — apply to every criterion:**
- Is it testable? Can someone write a test case from this? If not, sharpen.
- Is it observable? Can the user or tester see the result? If not, rewrite.
- Is it independent? Does it test one thing? If it uses "and," split it.
- Does it include the unhappy path? At least one AC should cover error/edge cases.

### Step 4: Split Oversized Stories

Use the 7 splitting patterns (detail in `references/splitting-patterns.md`):

1. **Workflow Steps** — build the minimal path first, add branches later
2. **Operations (CRUD)** — separate create/read/update/delete
3. **Business Rule Variations** — flat rate first, then weight-based, then promo codes
4. **Data Variations** — start simple, add complexity
5. **Simple/Complex** — ship the simple version, defer edge cases
6. **Defer Performance** — "make it work" before "make it fast"
7. **Break Out a Spike** — time-box investigation when unknowns are too large

**Splitting test:** After splitting, does each resulting story deliver end-to-end value a user could validate? If not, you've sliced horizontally — try again.

### Step 5: Checkpoint — Present Refined Stories

**CHECKPOINT: Do NOT skip this step.**

Present the refined stories with their acceptance criteria:

"Here are the refined stories. Each has 3+ testable acceptance criteria and delivers end-to-end value. The key decisions:
1. [Stories that were split and why]
2. [Items triaged out and why]
3. [Open questions or dependencies surfaced]

Do these look sprint-ready?"

### Step 6: Estimate (If Needed)

Use story points or t-shirt sizing — estimation's value is the discussion, not the number.

```
ESTIMATES:
  [Story 1]: [Size] — [Key sizing factor]
  [Story 2]: [Size] — [Key sizing factor]
  [Story 3]: [Size] — [Key sizing factor]
```

**Estimation is optional.** If the team has a flow-based system or doesn't estimate, skip this step. The refinement discussion itself surfaces complexity — the number is a side effect.

### Step 7: Stack Rank the Refined Backlog

Order items by priority. Present the top of the backlog:

```
REFINED BACKLOG (top items):
  1. [Story] — [Size] — [Ready status]
  2. [Story] — [Size] — [Ready status]
  3. [Story] — [Size] — [Ready status]
  ...
```

After ranking, offer next steps:

"Backlog refined. Want to:
(a) Refine additional stories?
(b) Invoke **sprint-planning** to select stories for the next sprint?
(c) Run a full backlog health check?
(d) Split a specific epic further?
(e) Move on?"

---

## Definition of Ready Checklist

Guidance for assessing whether a story is sprint-ready:

- [ ] Written in user story format
- [ ] 3+ acceptance criteria defined (Given/When/Then)
- [ ] Dependencies identified and unblocked
- [ ] Estimated by the team
- [ ] No blocking open questions

This is guidance, not a hard gate — teams can pull stories that are close, but stories missing acceptance criteria should not enter a sprint.

---

## Health Assessment Flow

When running a standalone health check:

1. Collect the metrics from Step 1
2. Flag anti-patterns found in the backlog:
   - **Zombie items** — older than 6 months without deliberate hold
   - **Title-only stories** — no acceptance criteria
   - **Epic-sized items** — same item deferred 5+ sprints, never split
   - **Priority inflation** — everything marked high priority
   - **Horizontal slices** — component stories with no user value
   - **No triage** — backlog used as a dumping ground
   - **Over-detailed future items** — wireframes for items 8 sprints away
3. Recommend specific actions for each finding
4. If backlog exceeds 200 items, recommend the pruning flow

---

## Pruning Flow (>200 Items)

1. Delete duplicates and items that have been superseded
2. Archive items older than 6 months with no deliberate hold reason
3. Merge related items into single stories or epics
4. Re-triage what remains using Step 2 criteria
5. Target: backlog should be 2-3 sprints of ready items plus a prioritized pipeline

---

## Bias Guards

| Thought | Reality | Do Instead |
|---|---|---|
| "This story is ready enough" | Does it have 3+ testable acceptance criteria? If not, it's not ready. | Apply the DoR checklist. "Ready enough" is how sprints derail. |
| "We'll figure it out during the sprint" | That's how sprints derail. Refine now. | Write the acceptance criteria. Surface the unknowns. |
| "This epic is too complex to split" | Use a spike. If it can't be split, it's a project, not a story. | Time-box a spike to learn enough to split it. |
| "Let's keep this in the backlog just in case" | Items older than 6 months without deliberate hold should be deleted. | Delete it. If it matters, it'll come back. |
| "Everything is high priority" | If everything is high, nothing is. Priorities require ordering. | Force-rank. The team can only pull N items per sprint. |
| "We need all the details before we can start" | Over-refinement is waste. Refine just enough for the next 2-3 sprints. | Refine top items deeply. Leave later items at epic level. |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Zombie backlog** | >200 items, stuff older than 6 months | Run pruning flow. Delete aggressively. |
| **Stories without acceptance criteria** | Team can't verify done. Sprint goal is ambiguous. | Write 3+ Given/When/Then criteria per story. |
| **Epic-sized stories that never get split** | Same item deferred 5+ sprints. Too big to pull. | Apply splitting patterns. Break out a spike if needed. |
| **Everything is high priority** | No differentiation. Team can't decide what to pull. | Force-rank the backlog. One stack, one order. |
| **Horizontal slicing** | Component stories with no user value. | Split vertically — every story delivers end-to-end value. |
| **Backlog as dumping ground** | No triage, no gatekeeping. Anyone adds anything. | Step 2 triage on every new item. Accept, defer, or delete. |
| **Over-detailed items far out** | Wireframes for items 8 sprints away. Wasted effort. | Only deeply refine the next 2-3 sprints of work. |

## Guidelines

- **Refinement is ongoing, not a one-time event.** The backlog should always have 2-3 sprints of ready stories. If sprint planning regularly surfaces unrefined stories, refinement cadence is broken.
- **Acceptance criteria are non-negotiable.** 3+ testable criteria per story. This is the single most impactful backlog quality practice.
- **Split vertically, always.** Every story delivers end-to-end value. "Build the API" is not a story. "User can submit a quote request" is.
- **The backlog is not a wish list.** Triage ruthlessly. Items without strategic connection should be deferred or deleted.
- **Estimation's value is the discussion.** Whether you use points or t-shirts, the conversation about complexity matters more than the number.
- **Pruning is healthy.** Deleting items is not losing ideas — it's maintaining focus. If an item matters, it'll resurface.
- **Refine just in time.** Deep refinement for the next 2-3 sprints. Light refinement for the pipeline. No refinement for items 6+ sprints out.

Follow the communication-protocol skill for all user-facing output and interaction.
