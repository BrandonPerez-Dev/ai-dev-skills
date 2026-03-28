---
name: sprint-planning
description: Plan sprints by defining a sprint goal, calculating capacity, and selecting stories that serve the goal — not the reverse. Produces sprint plans with goal, capacity math, story selection, dependencies, and risks. Use when asked to plan a sprint, start a new sprint, set a sprint goal, figure out what fits in this sprint, scope a sprint, do capacity planning, determine how much the team can take on, handle sprint carryovers, or run sprint planning. This skill SELECTS and COMMITS stories for a sprint — use backlog-refinement to PREPARE stories before they're sprint-ready. Use roadmap-planning for quarterly or strategic planning decisions. Use decompose-tasks to break committed stories into implementation tasks.
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
argument-hint: "[sprint number or date range]"
---

# Sprint Planning

Sprint planning starts with a goal, not a backlog. The sprint goal defines the "why" — story selection follows from it, not the reverse. A sprint without a goal is a task queue, not a purposeful iteration.

<HARD-GATE>
Every sprint MUST have a sprint goal — a single sentence describing the outcome, not a list of tickets. "Complete stories 34, 35, and 41" is not a goal. If you can't articulate a goal, the sprint lacks purpose and planning should not proceed until one exists.
</HARD-GATE>

<HARD-GATE>
Never plan to 100% capacity. Teams with 15-20% buffer have 40% higher sprint success rates. Plan at 80-85% of adjusted capacity. If planned work exceeds 85%, move stories to the stretch list or cut scope.
</HARD-GATE>

## Method Selection

| Situation | Approach | Why |
|---|---|---|
| **Standard sprint planning** | Full flow (Steps 1-8) | Need carryover triage, capacity, goal, selection, dependencies |
| **Quick planning (experienced team, refined stories)** | Abbreviated flow (Steps 1, 3, 5-7) | Team knows velocity; stories are sprint-ready |
| **Capacity calculation needed** | Step 2 deep dive | New team, changed composition, or unusual sprint |
| **Sprint carries over stories** | Triage carryovers first (Step 1b) | Don't auto-carry; re-evaluate each story |
| **Remote/distributed team** | Async pre-work + abbreviated sync | Pre-work on Steps 1-3; sync on Steps 4-7 |

## Input Resolution

1. If `$ARGUMENTS` is a sprint number, use that as the target sprint
2. If `$ARGUMENTS` is a date range, use that as the sprint window
3. Search `docs/sprints/` for previous sprint plans — velocity history and carryover data
4. Search `docs/plans/` for `*-roadmap.md` and `*-okrs.md` — strategic context for goal-setting
5. If no artifacts exist, start from scratch with the user

## Process

### Step 1: Review Previous Sprint

Pull previous sprint results or ask the user:

```
PREVIOUS SPRINT: [Sprint N-1]
  Goal: [What was the goal]
  Result: [Met / Partially met / Missed]
  Velocity: [Points or stories completed]
  Carryovers: [Stories not completed]
```

#### Step 1b: Carryover Triage

Do NOT auto-carry incomplete stories. For each carryover:

```
CARRYOVER: [Story]
  Why incomplete: [Blocked / Underestimated / Deprioritized / Started late]
  Still top priority? [Yes → carry forward / No → return to backlog]
  Estimate still valid? [Yes / No → re-estimate]
```

**CHECKPOINT:** "These are the carryover candidates. Should any go back to the backlog instead of forward into this sprint?"

### Step 2: Calculate Capacity

```
SPRINT DURATION: [N days]

TEAM CAPACITY:
  [Name]: [Sprint days] − [PTO] − [holidays] = [available days] × [4-6 productive hrs/day] = [hours]
  ...
  Total team capacity: [sum of productive hours]

VELOCITY BASELINE: average of last 3 sprints = [X points/stories]
PLANNED CAPACITY: min(velocity baseline, team capacity) × 0.85 = [Y]
BUFFER: [15-20%] reserved for unplanned work
```

Productive hours per day = 4-6h after overhead (standups, ceremonies, reviews, context-switching). Use 5h as default unless the team specifies otherwise.

### Step 3: Propose Sprint Goal

Draft a single-sentence, outcome-oriented goal that connects to an OKR or roadmap theme.

```
PROPOSED SPRINT GOAL: [Single sentence — what outcome, not what tasks]
OKR CONNECTION: [Which KR this moves]
ROADMAP CONNECTION: [Which theme or initiative this serves]
```

**Goal quality check — apply every time:**
- Does it describe an outcome, not a task list?
- Is it singular (one objective, not "X and Y and Z")?
- Is it achievable within the sprint?
- If we completed the goal but dropped one story, would the sprint still feel successful?

### Step 4: Confirm Sprint Goal

**CHECKPOINT: Do NOT skip this step.**

"This is the proposed sprint goal. Does it capture what we're trying to achieve this sprint?"

Wait for confirmation before selecting stories. The goal shapes selection — changing it after selection inverts the process.

### Step 5: Select Stories

From the refined backlog, select stories that support the sprint goal. Balance work types:

| Work type | Suggested allocation |
|---|---|
| Feature work | 60-70% |
| Tech debt / refactoring | 15-20% |
| Bugs | 10-15% |
| Operational / support | 5-10% |

For each selected story:

```
SELECTED STORIES:
  ▸ [Story] — [Size] — [Owner] — [Goal connection: direct/supporting/maintenance]
  ...

STRETCH STORIES (if capacity allows):
  ▸ [Story] — [Size]
  ...

Planned: [Y points/stories] of [Z] capacity (85%)
Remaining buffer: [15-20%]
```

Name stretch stories explicitly — they are the first to drop if unplanned work arrives.

### Step 6: Identify Dependencies

2-minute check per selected story:

```
DEPENDENCIES:
  ▸ [Story] depends on [Team/System] — Status: [Confirmed/Pending]
  ...
```

Any dependency with status "Pending" is a sprint risk. Flag it.

### Step 7: Surface Risks

```
RISKS:
  ▸ [Risk] — Mitigation: [Action]
  ...
```

Common sprint risks: pending dependencies, team member PTO mid-sprint, stories not fully refined, external integration timelines.

### Step 8: Produce Sprint Plan

**CHECKPOINT: Do NOT skip this step.**

Present the full sprint plan:

```
SPRINT PLAN — Sprint [N] — [Date range]
SPRINT GOAL: [Single sentence outcome]
OKR CONNECTION: [Which KR this goal moves]

SELECTED STORIES:
  ▸ [Story] — [Size] — [Owner] — [Dependencies if any]
  ...

STRETCH STORIES (if capacity allows):
  ▸ [Story] — [Size]

CAPACITY:
  Team availability: [X person-days]
  Planned: [Y story points / stories] (85% of [Z] velocity baseline)
  Buffer: [15-20%] for unplanned work

DEPENDENCIES:
  ▸ [Story] depends on [Team/System] — Status: [Confirmed/Pending]

RISKS:
  ▸ [Risk] — Mitigation: [Action]
```

"Here's the sprint plan. The key decisions:
1. [Sprint goal and why]
2. [What was left out and why]
3. [Biggest risk or dependency]

Does this plan reflect what the team should commit to?"

After confirmation, save to `docs/sprints/sprint-[N]-plan.md`.

After saving, offer next steps:

"Sprint plan saved to [path]. Want to:
(a) Adjust story selection or ownership?
(b) Invoke **backlog-refinement** on stories that aren't sprint-ready?
(c) Invoke **okr-setting** to check KR alignment?
(d) Move on?"

---

## Bias Guards

| Thought | Reality | Do Instead |
|---|---|---|
| "We can fit one more story" | Are you at 85% capacity or 100%? Buffer is not optional. | Check the math. If over 85%, move it to stretch. |
| "Let's carry this over, we almost finished it" | Re-evaluate: is it still the top priority? Does the estimate still hold? | Triage every carryover. Almost-done is not automatically next. |
| "We don't need a sprint goal, we know what to build" | The goal isn't for you, it's for focus. Without it, everything is equally important. | Write the goal. If you can't, the sprint lacks coherence. |
| "We'll handle tech debt next sprint" | If you say this every sprint, you'll never do it. | Allocate a fixed 15-20% now. Make it structural, not aspirational. |
| "Let's just auto-carry everything forward" | Incomplete stories may no longer be the top priority. Context has changed. | Triage each one. Return to backlog if priority shifted. |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **No sprint goal** | Task queue, not purposeful iteration. Team optimizes for throughput, not outcomes. | Goal first, stories second. Always. |
| **Over-commitment** | >25% carryover rate = systemic over-planning. Destroys team morale and predictability. | Plan at 85%. Track carryover rate across sprints. |
| **Cherry-picking easy stories** | No sprint goal → optimize for personal comfort, not team outcomes. | Sprint goal forces coherent selection. |
| **Auto-carryover** | Incomplete stories moved forward without triage. Backlog silently grows. | Re-evaluate each carryover: still top priority? Estimate still valid? |
| **Planning at 100% capacity** | No room for surprises. First interrupt derails the sprint. | 15-20% buffer is structural, not negotiable. |
| **Sprint planning as refinement** | Stories arrive unrefined → 3-hour meeting that mixes planning with discovery. | Refinement is a separate activity. Only sprint-ready stories enter planning. |
| **Retro actions never entering sprint backlog** | Process improvements discussed but never executed. | Review retro actions in Step 1. Add relevant ones to the sprint. |

## Guidelines

- **Goal first, stories second.** The sprint goal shapes story selection. Inverting this produces task queues, not purposeful sprints.
- **Buffer is structural, not aspirational.** 15-20% unplanned capacity is not slack — it's what separates predictable teams from perpetually behind ones.
- **Carryovers are not automatic.** Every incomplete story gets triaged. Priorities shift, estimates change, context evolves.
- **Stretch stories are named, not hoped for.** If capacity opens up, the team knows exactly what to pull. No mid-sprint negotiation.
- **Capacity math is honest.** 4-6 productive hours per day after overhead. Teams that plan on 8h/day carry over every sprint.
- **Work type balance is intentional.** 15-20% tech debt allocation every sprint prevents the "we'll do it next sprint" death spiral.
- **Dependencies are sprint risks.** Any story with a pending dependency is a risk. Flag it, mitigate it, or don't commit to it.

Follow the communication-protocol skill for all user-facing output and interaction.
