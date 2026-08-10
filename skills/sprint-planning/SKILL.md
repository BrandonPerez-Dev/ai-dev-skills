
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

Sprint planning starts with a goal, not a backlog. Two rules carry the method, stated once with the reason each holds:

- **Every sprint has a single-sentence outcome goal, and story selection follows from it.** "Complete stories 34, 35, and 41" is a task queue, not a goal — without a goal every story looks equally important and the team optimizes for throughput over outcome. If you can't articulate a goal, planning shouldn't proceed until one exists.
- **Never plan to 100% capacity.** Plan to 80-85% of adjusted capacity; the 15-20% buffer is structural, not slack — teams that keep it have ~40% higher sprint success rates. Work over 85% goes to the stretch list or gets cut.

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

Don't auto-carry incomplete stories — context has changed, and an almost-done story may no longer be top priority. For each carryover:

```
CARRYOVER: [Story]
  Why incomplete: [Blocked / Underestimated / Deprioritized / Started late]
  Still top priority? [Yes → carry forward / No → return to backlog]
  Estimate still valid? [Yes / No → re-estimate]
```

Then confirm: "These are the carryover candidates. Should any go back to the backlog instead of forward into this sprint?"

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

Productive hours per day = 4-6h after overhead (standups, ceremonies, reviews, context-switching). Use 5h as default unless the team specifies otherwise — teams that plan on 8h/day carry over every sprint.

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

The goal shapes selection, so confirm it before selecting stories — changing it afterward inverts the process:

"This is the proposed sprint goal. Does it capture what we're trying to achieve this sprint?"

### Step 5: Select Stories

From the refined backlog, select stories that support the sprint goal. Balance work types:

| Work type | Suggested allocation |
|---|---|
| Feature work | 60-70% |
| Tech debt / refactoring | 15-20% |
| Bugs | 10-15% |
| Operational / support | 5-10% |

The 15-20% tech-debt allocation is intentional every sprint — "we'll do it next sprint" said every sprint is how the debt spiral starts.

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

Name stretch stories explicitly — they are the first to drop when unplanned work arrives, and naming them now avoids mid-sprint negotiation.

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

Present the full sprint plan for the team to commit to:

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

The rationalizations that derail sprint planning mid-session, and the counter-move for each:

| Thought | Do instead |
|---|---|
| "We can fit one more story" | Check the math — at 85% or 100%? Over 85% goes to stretch; the buffer isn't optional. |
| "We almost finished it, just carry it over" | Triage every carryover: still top priority? estimate still valid? Almost-done isn't automatically next. |
| "We don't need a goal, we know what to build" | The goal is for focus, not for you. Write it; if you can't, the sprint lacks coherence. |
| "We'll handle tech debt next sprint" | Said every sprint, it never happens. Allocate a fixed 15-20% now — structural, not aspirational. |
| "Let's just auto-carry everything forward" | Priorities shift between sprints. Triage each; return to backlog if priority moved. |
