---
name: okr-setting
description: Create and manage OKRs (Objectives and Key Results) — translate strategy into measurable outcomes by defining what success looks like each quarter or year. Produces OKR sets with scored key results, confidence tracking, and health metrics. Use when asked to set OKRs, write OKRs, define objectives, update key results, score or grade OKRs, run an OKR review or check-in, track progress against objectives, define success criteria, set team or company goals, or run quarterly or annual OKR planning. This skill is about MEASUREMENT and GOAL-SETTING — use roadmap-planning instead when deciding which initiatives to pursue, even if that happens during quarterly planning.
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
argument-hint: "[quarter, team name, or path to existing OKRs]"
---

# OKR Setting

OKRs bridge strategy to measurable outcomes — they answer "what does success look like this quarter?" not "what are we building?" Objectives inspire direction, Key Results prove progress.

<HARD-GATE>
Key Results MUST be outcomes, not tasks. "Launch newsletter" is a task. "Grow email subscribers by 20%" is a Key Result. If you can complete a KR by just doing work (regardless of impact), it's a task masquerading as a KR. Reject it and rewrite.
</HARD-GATE>

## Method Selection

| Situation | Approach | Why |
|---|---|---|
| **New OKRs from scratch** | Full creation flow (Steps 1-8) | Need strategic context, objectives, and key results |
| **Deriving team OKRs from company OKRs** | Alignment flow (Steps 1-2, then 3-8) | Company direction exists; team needs to connect to it |
| **Quarterly review/scoring** | Scoring flow (Step 9) | OKRs exist; need end-of-quarter evaluation |
| **Mid-quarter check-in** | Confidence update flow (Step 10) | OKRs exist; need progress pulse |
| **Connecting OKRs to existing roadmap** | Alignment flow (Steps 1-2, 6, 8) | Both artifacts exist; need explicit linkage |

## Input Resolution

1. If `$ARGUMENTS` is a file path, read that as the existing OKR document
2. If `$ARGUMENTS` is a quarter (e.g., "Q3 2026"), use that as the target period
3. Search `docs/plans/` for `*-okrs.md` files — existing OKR documents
4. Search `docs/plans/` for `*-roadmap.md` files — strategic themes to anchor to
5. If no artifacts exist, start from scratch with the user

## Process

### Step 1: Establish Strategic Context

Pull from existing artifacts or establish with user. Invoke **roadmap-planning** output if a roadmap exists.

```
QUARTER: [Target quarter]
TEAM/SCOPE: [Who these OKRs are for]

COMPANY OKRs (if they exist):
  O1: [Company objective]
    KR1: [Company key result]
    ...

STRATEGIC THEMES (from roadmap):
  - [Theme 1] — [What outcome it drives]
  - [Theme 2] — [What outcome it drives]

CONSTRAINTS:
  - [Resource limits, team transitions]
  - [Carryover commitments from last quarter]
  - [External dependencies or deadlines]
```

Confirm with user: "This is the strategic frame for the quarter. Does this hold?"

### Step 2: Review Previous Quarter (if OKRs exist)

<HARD-GATE>
Before setting new OKRs, score the previous quarter's OKRs first. Setting new goals without reviewing old ones means you're planning without learning. If previous OKRs exist but outcomes aren't measured, flag it — "we set these goals but have no data on whether we hit them" is a finding.
</HARD-GATE>

Use the Scoring Protocol (Step 9) on previous OKRs. Carry forward learnings:
- Which KRs were hit? What drove success?
- Which KRs were missed? Was the target wrong or the approach wrong?
- Any KRs that should carry over vs. be retired?

### Step 3: Draft Objectives

Objectives are qualitative, inspiring, and directional. They are NOT metric targets.

```
O1: [Objective — describes the desired state, not a number]
  Type: [Committed / Aspirational]
  Theme connection: [Which roadmap theme or company OKR this serves]
  Why now: [What makes this the right quarter for this objective]
```

**Rules:**
- **3-5 objectives max.** More means you haven't prioritized.
- Each objective connects to a strategic theme or company OKR.
- Committed = operationally required, failure has consequences. Aspirational = stretching toward a future state.
- If you can put a number in the objective, it's a KR pretending to be an objective.

**CHECKPOINT: Do NOT skip this step.**

"Here are the draft objectives. These set the direction for the quarter — everything else flows from them. Do they capture the right ambitions?"

### Step 4: Define Key Results

For each objective, define 3-5 measurable outcomes scored 0-1.0.

```
O1: [Objective]
  KR1: [Measurable outcome with specific target]
    Baseline: [Current state]
    Target: [End-of-quarter target]
    Measurement: [How we'll measure this — source, frequency]
    Type: [Committed / Aspirational]

  KR2: [Measurable outcome]
    ...
```

**KR quality checks — apply to every KR:**
- Can someone complete this by just doing work, regardless of impact? → It's a task. Rewrite.
- Is the target specific enough to score unambiguously at end of quarter? → If not, sharpen.
- Do we have a baseline? → If not, first week of quarter is measurement setup.
- Is it within this team's influence? → If not, it's a dependency, not a KR.

### Step 5: Set Health Metrics

Health metrics are guardrails — things that must NOT degrade while pursuing OKRs.

```
HEALTH METRICS (must not degrade):
  - [Metric]: maintain above [threshold]
  - [Metric]: keep below [threshold]
  - [Metric]: no regression from [baseline]
```

If a health metric degrades, it's a signal to re-examine the OKR approach — the team may be achieving KRs at the cost of something important.

### Step 6: OKR-to-Roadmap Alignment

```
ALIGNMENT MAP:
  Roadmap Theme → OKR Objective → Key Initiatives (the "how")
  [Theme 1]     → O1             → [Initiative A, Initiative B]
  [Theme 2]     → O2             → [Initiative C]
  [Theme 3]     → [NO OKR]       → Flag: missing OKR or theme shouldn't be on roadmap
```

**Rules:**
- Each roadmap theme should map to an OKR objective.
- Roadmap initiatives are the "how" — they drive KR movement.
- If a theme has no OKR, either the OKR is missing or the theme shouldn't be on the roadmap.
- OKRs without roadmap themes may signal work that isn't strategically anchored.

### Step 7: Present Full OKR Set

**CHECKPOINT: Do NOT skip this step.**

Present the complete OKR set and surface the key decisions:

"Here's the full OKR set for [quarter]. The key decisions embedded in it:
1. [What's committed vs. aspirational and why]
2. [What's NOT an OKR this quarter — conscious omissions]
3. [Biggest risk to hitting these KRs]

Does this reflect what success looks like?"

### Step 8: Save Artifact

After confirmation:
- Get today's date: !`date +%Y-%m-%d`
- Save to: `docs/plans/YYYY-MM-DD-<topic>-okrs.md`
- Use the output template from `references/okr-template.md`

After saving, offer next steps:

"OKRs saved to [path]. Want to:
(a) Adjust any objective or key result?
(b) Invoke **roadmap-planning** to align the roadmap to these OKRs?
(c) Set up the weekly confidence tracking cadence?
(d) Score previous quarter's OKRs first?
(e) Move on?"

---

## Scoring Protocol (End-of-Quarter)

### Step 9: Score OKRs

For each KR, score 0.0-1.0 against the target:

```
O1: [Objective]
  KR1: [Key Result]
    Target: [what we aimed for]
    Actual: [what we achieved]
    Score: [0.0-1.0]
    Notes: [What drove this result]

  Objective Score: [average of KR scores]
  Grade: [Green/Yellow/Red per thresholds below]
```

**Scoring thresholds:**

| Type | Green | Yellow | Red |
|---|---|---|---|
| **Aspirational** | 0.7+ | 0.4-0.6 | <0.4 |
| **Committed** | 1.0 | 0.7-0.9 | <0.7 |

- **Committed KRs below 1.0** trigger root cause analysis — what broke?
- **Consistently 1.0 on aspirational** = goals too easy, increase ambition next quarter.
- **All red** = either targets were wrong, approach was wrong, or context changed. Diagnose which.

Invoke **metrics-review** to pull actuals for KR scoring where metrics dashboards exist.

**CHECKPOINT: Do NOT skip this step.**

"Here's how the quarter scored. The headline: [one-sentence summary]. Want to dig into any specific objective?"

---

## Confidence Update (Mid-Quarter)

### Step 10: Weekly Confidence Check

For each KR, update confidence on a 1-10 scale:

```
Week [N] Confidence Update:
  O1/KR1: [confidence 1-10] — [one-line reason]
  O1/KR2: [confidence 1-10] — [one-line reason]
  ...

Flags:
  - [Any KR where confidence dropped 3+ points since last check]
  - [Any KR stuck at low confidence for 2+ weeks]
```

Confidence below 4 for two consecutive weeks = trigger a conversation about whether the KR target needs adjustment or the approach needs to change.

---

## Bias Guards

| Thought | Reality | Do Instead |
|---|---|---|
| "We're already building X, let's write an OKR around it" | OKRs precede roadmap, not the reverse. Backlog-fitting is the second most common OKR failure. | Start from outcomes. What should be true by end of quarter? |
| "Let's make this committed so the team takes it seriously" | Committed means operationally required, not "important." | Reserve committed for KRs where missing the target has operational consequences. |
| "Everyone should have individual OKRs" | Team OKRs are sufficient. Individual OKRs create overhead and perverse incentives. | Set team-level OKRs. Individuals contribute to team KRs. |
| "We scored 1.0 on everything!" | Aspirational goals were too easy. You're sandbagging. | Increase ambition next quarter. Aspirational should hit ~0.7. |
| "This KR is hard to measure, so let's use a proxy" | Proxy metrics drift from real outcomes. | Find the real metric or change the KR to something measurable. |
| "Let's add one more objective — it's important" | More than 5 = no focus. Important is not the same as prioritized. | Force-rank. What gets cut? |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **KRs that are tasks** | "Launch X" can be done without impact. Completing work ≠ achieving outcomes. | Rewrite as outcome: what changes because X launched? |
| **Too many OKRs** | >5 objectives = everything is a priority = nothing is. | 3-5 objectives, 3-5 KRs each. Cut ruthlessly. |
| **Sandbagging** | Deliberately low targets to guarantee green scores. | Aspirational should be uncomfortable. 0.7 is the target, not 1.0. |
| **Backlog-fitting** | Writing OKRs to justify already-planned work. | OKRs define outcomes. Roadmap defines how to get there. |
| **Set and forget** | No weekly check-ins. OKRs decay into a forgotten doc. | Weekly confidence updates. Bi-weekly team discussion. |
| **OKRs as performance reviews** | Using OKR scores for individual evaluation destroys psychological safety. | OKRs measure team progress toward outcomes, not individual performance. |
| **Metric-only objectives** | "Grow revenue to $10M" — that's a KR, not an objective. | Objectives are qualitative and directional. Metrics live in KRs. |
| **No health metrics** | Achieving KRs at the cost of quality, morale, or stability. | Set guardrail metrics that must not degrade. |

## Guidelines

- **Outcomes over outputs.** "Reduce support tickets by 30%" is a KR. "Build help center" is a task. This is the single most important OKR principle and the most violated.
- **Committed vs. aspirational is a real distinction.** Committed = must hit, failure triggers action. Aspirational = stretch, 0.7 is success. Mislabeling creates either sandbagging or panic.
- **3-5 objectives is a hard ceiling.** If you can't cut to 5, you haven't made strategic choices. More objectives = less focus = worse outcomes.
- **Weekly confidence is non-negotiable.** OKRs without check-ins are wish lists. Confidence tracking catches problems early enough to course-correct.
- **Score honestly.** 0.3 on an aspirational OKR is information, not failure. Inflating scores destroys the system's value.
- **OKRs precede the roadmap.** The roadmap is how you achieve OKR outcomes. If OKRs are written to match the roadmap, you've inverted the relationship.
- **Health metrics protect the business.** Pursuing KRs at the expense of stability, quality, or team health is not success.
- **Kill sandbagging aggressively.** Consistently hitting 1.0 on aspirational OKRs means the bar is too low. Raise it.

Follow the communication-protocol skill for all user-facing output and interaction.
