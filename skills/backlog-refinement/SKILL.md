
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

Refinement makes stories sprint-ready — the ongoing practice that keeps sprint planning from becoming a 3-hour chaos session. The output is stories the team can confidently pull, not a perfectly detailed backlog.

Two non-negotiables carry most of the value; the reason is why they hold, so they're stated once here and assumed throughout:

- **3+ testable acceptance criteria per story.** A title-only story gives the team nothing to verify "done" against — the sprint goal turns ambiguous and work derails mid-sprint. No acceptance criteria → not ready.
- **Vertical slices, not horizontal.** A story delivers end-to-end value a user can observe. "Build the database schema" is a task; "user can save a draft quote" is a story. A component with no user-facing outcome is a task masquerading as a story — split it a different way.

Everything below is in service of reaching that bar *just in time* — deeply for the next 2-3 sprints, lightly for the pipeline, not at all for work 6+ sprints out. Over-refinement is waste.

## Method Selection

| Situation | Approach | Why |
|---|---|---|
| **Regular refinement session** | Ceremony flow (Steps 1-7) | Full backlog pass — triage, refine, estimate, rank |
| **Epic needs splitting** | Story splitting flow (Step 4) | Large item needs vertical decomposition |
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

If health data isn't available, flag it — "we can't assess backlog health without visibility into these metrics" is itself a finding.

### Step 2: Triage New Items

For each new or unrefined item, decide **Accept / Defer / Delete**:

- **Accept** — belongs in the backlog, needs refinement
- **Defer** — valid idea, not now — park with a revisit trigger
- **Delete** — duplicates, stale ideas, items with no strategic connection

The backlog is not a wish list. Items without a connection to current themes or roadmap priorities should be deferred or deleted — otherwise the backlog becomes a dumping ground no one can prioritize.

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

Apply four quality checks to every criterion:
- **Testable** — can someone write a test case from this? If not, sharpen it.
- **Observable** — can the user or tester see the result? If not, rewrite it.
- **Independent** — does it test one thing? If it uses "and," split it.
- **Covers the unhappy path** — at least one AC should cover an error or edge case.

### Step 4: Split Oversized Stories

Use the 7 splitting patterns (detail in `references/splitting-patterns.md`):

1. **Workflow Steps** — build the minimal path first, add branches later
2. **Operations (CRUD)** — separate create/read/update/delete
3. **Business Rule Variations** — flat rate first, then weight-based, then promo codes
4. **Data Variations** — start simple, add complexity
5. **Simple/Complex** — ship the simple version, defer edge cases
6. **Defer Performance** — "make it work" before "make it fast"
7. **Break Out a Spike** — time-box investigation when unknowns are too large

**Splitting test:** after splitting, does each resulting story deliver end-to-end value a user could validate? If not, you've sliced horizontally — try again.

### Step 5: Checkpoint — Present Refined Stories

Present the refined stories with their acceptance criteria before treating them as ready — an AI declaring its own refinement "done" is exactly how unrefined stories slip into a sprint:

"Here are the refined stories. Each has 3+ testable acceptance criteria and delivers end-to-end value. The key decisions:
1. [Stories that were split and why]
2. [Items triaged out and why]
3. [Open questions or dependencies surfaced]

Do these look sprint-ready?"

### Step 6: Estimate (If Needed)

Use story points or t-shirt sizing — estimation's value is the discussion that surfaces complexity, not the number.

```
ESTIMATES:
  [Story 1]: [Size] — [Key sizing factor]
  [Story 2]: [Size] — [Key sizing factor]
  [Story 3]: [Size] — [Key sizing factor]
```

Optional: if the team runs a flow-based system or doesn't estimate, skip it.

### Step 7: Stack Rank the Refined Backlog

Order items into one prioritized stack. If everything is "high priority," nothing is — force-rank, because the team can only pull N items per sprint.

```
REFINED BACKLOG (top items):
  1. [Story] — [Size] — [Ready status]
  2. [Story] — [Size] — [Ready status]
  3. [Story] — [Size] — [Ready status]
  ...
```

Then offer next steps:

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

Guidance, not a hard gate — teams can pull stories that are close, but a story missing acceptance criteria should not enter a sprint.

---

## Health Assessment Flow

When running a standalone health check:

1. Collect the metrics from Step 1.
2. Flag the anti-patterns found in the backlog:
   - **Zombie items** — older than 6 months without a deliberate hold
   - **Title-only stories** — no acceptance criteria
   - **Epic-sized items** — same item deferred 5+ sprints, never split
   - **Priority inflation** — everything marked high priority
   - **Horizontal slices** — component stories with no user value
   - **No triage** — backlog used as a dumping ground
   - **Over-detailed future items** — wireframes for items 8 sprints away
3. Recommend specific actions for each finding.
4. If the backlog exceeds 200 items, recommend the pruning flow.

---

## Pruning Flow (>200 Items)

1. Delete duplicates and superseded items.
2. Archive items older than 6 months with no deliberate hold reason.
3. Merge related items into single stories or epics.
4. Re-triage what remains using Step 2 criteria.
5. Target: 2-3 sprints of ready items plus a prioritized pipeline. Deleting is maintaining focus, not losing ideas — anything that matters resurfaces.

---

## Bias Guards

The rationalizations that derail refinement mid-session, and the counter-move for each:

| Thought | Do instead |
|---|---|
| "This story is ready enough" | Run the DoR checklist. No 3+ testable AC → not ready; "ready enough" is how sprints derail. |
| "We'll figure it out during the sprint" | Write the acceptance criteria now and surface the unknowns — that *is* the refinement. |
| "This epic is too complex to split" | Time-box a spike to learn enough to split it. If it truly can't be split, it's a project, not a story. |
| "Everything is high priority" | Force-rank into one stack. The team pulls N per sprint regardless. |
| "We need all the details before we start" | Refine top items deeply, leave later items at epic level. Over-refinement is waste. |
