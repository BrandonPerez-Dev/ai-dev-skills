
---
name: innovation-status
description: Auto-generate portfolio status reports by scanning existing artifacts. Produces weekly team updates, monthly portfolio reviews, gate presentations, and executive summaries. Use when you need a snapshot of where things stand across all opportunities.
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
argument-hint: "[report type: weekly | monthly | gate | executive] or [specific opportunity]"
---

# Innovation Status

A status report that doesn't surface decisions is just a comfort blanket. Every report answers "what do we need to decide?" — not just "where are we?"

<HARD-GATE>
Status reports reflect what artifacts say, not what you think the status is. If there's no artifact, the status is "no evidence" — not "probably fine." Optimistic status reporting is how innovation teams die.
</HARD-GATE>

## When to Use

- Weekly standup or team sync needs a progress snapshot
- Monthly portfolio review with leadership
- Gate review (GO/KILL/PIVOT decision) for a specific opportunity
- Executive wants a one-pager on the innovation portfolio
- You need to quickly understand "where are we on everything?"

## Input Resolution

1. If $ARGUMENTS specifies a report type, use that format
2. If $ARGUMENTS names a specific opportunity, generate status for just that one
3. If no arguments, default to weekly team update
4. Scan `specs/` and `docs/plans/` for all artifacts to build the picture

## Process

### Step 1: Scan the Artifact Landscape

Search `specs/` and `docs/plans/` for all innovation artifacts:

```
ARTIFACT SCAN:
  Opportunities found: [list with dates]
  Discovery artifacts: [which opportunities have them]
  Market analyses: [which opportunities have them]
  Experiment packages: [which, with results status]
  Business cases: [which opportunities have them]
  Scorecards: [which opportunities have them]
  Product definitions: [which opportunities have them]
```

For each opportunity, determine its **stage** based on what artifacts exist:

| Stage | Artifacts Present | Meaning |
|-------|-------------------|---------|
| **Ideation** | Opportunity brief only | Just identified, not researched |
| **Discovery** | + Customer discovery and/or market analysis | Actively researching |
| **Validation** | + Experiment package (with results) | Testing assumptions |
| **Business Case** | + Business case and/or scorecard | Building the investment case |
| **Scoping** | + Product definition | Defining what to build |
| **Handoff** | + write-spec or technical artifacts | Moving to engineering |

### Step 2: Assess Health per Opportunity

For each active opportunity, pull key signals:

```
[Opportunity Name]
  Stage: [Current stage]
  Last activity: [Date of most recent artifact]
  Verdict/Score: [From most recent evaluation]
  Momentum: [Active / Stalled / Blocked]
  Key signal: [Most important recent finding]
  Next action: [What should happen next]
```

**Momentum rules:**
- **Active:** New artifact within last 2 weeks
- **Stalled:** No new artifact in 2-4 weeks
- **Blocked:** No new artifact in 4+ weeks OR explicitly blocked in an artifact

### Step 3: Choose Report Format

Based on the requested report type:

---

#### WEEKLY TEAM UPDATE

For the PM + Engineer pair. Quick, actionable, forward-looking.

```
INNOVATION WEEKLY — [Date]

ACTIVE OPPORTUNITIES: [count]

[For each active opportunity:]
▸ [Name] — [Stage] — [Momentum emoji: 🟢 Active / 🟡 Stalled / 🔴 Blocked]
  Last week: [What happened — one line]
  This week: [What should happen — one line]
  Signal: [Key insight or concern — one line]

PORTFOLIO HEALTH:
  [X] in Discovery | [Y] in Validation | [Z] in Business Case | [W] in Scoping
  Stalled: [list any stalled opportunities]

THIS WEEK'S PRIORITIES:
  1. [Most important action across all opportunities]
  2. [Second priority]
  3. [Third priority]
```

---

#### MONTHLY PORTFOLIO REVIEW

For leadership. Strategic view, progress trends, resource allocation.

```
INNOVATION PORTFOLIO — [Month Year]

EXECUTIVE SUMMARY:
[2-3 sentences on portfolio health and key developments]

PORTFOLIO OVERVIEW:
| Opportunity | Stage | Score | Horizon | Momentum | Key Development |
|-------------|-------|-------|---------|----------|-----------------|
| [Name]      | [Stage] | [X/3] | H[N] | [Status] | [One line]    |

PORTFOLIO BALANCE:
  H1 (Core): [N] opportunities — [X]% of portfolio
  H2 (Adjacent): [N] opportunities — [X]% of portfolio
  H3 (Transformational): [N] opportunities — [X]% of portfolio
  Assessment: [Balanced / Too conservative / Too risky]

MONTH IN REVIEW:
  Opportunities added: [list]
  Opportunities advanced: [list with from→to stage]
  Opportunities killed/paused: [list with reason]
  Key evidence gathered: [top 2-3 findings across portfolio]

DECISIONS NEEDED:
  1. [Decision] — context: [why now]
  2. [Decision] — context: [why now]

NEXT MONTH FOCUS:
  [Top 3 priorities for the coming month]
```

---

#### GATE REVIEW

For a specific opportunity's GO/KILL/PIVOT decision. Evidence-focused.

```
GATE REVIEW: [Opportunity Name]
Date: [Date]
Stage: [Current] → Proposed: [Next stage or KILL]

INVESTMENT THESIS:
[From business case, or summarized from available artifacts]

EVIDENCE SUMMARY:
  Desirability: [Score]/3 — [key evidence]
  Viability: [Score]/3 — [key evidence]
  Feasibility: [Score]/3 — [key evidence]
  Adaptability: [Score]/3 — [key evidence]
  Overall: [Score]/3

WHAT WE'VE LEARNED:
  Validated: [Assumptions confirmed with evidence]
  Invalidated: [Assumptions disproven]
  Unknown: [Still untested]

KILL CRITERIA CHECK:
  [For each pre-defined kill criterion:]
  - [Criterion]: [Met / Not met / Approaching] — [evidence]

FINANCIAL PICTURE:
  [From business case if available, or flag as missing]

RECOMMENDATION: [GO / CONDITIONAL GO / EXPLORE / HOLD / KILL]
  Rationale: [2-3 sentences grounded in evidence]
  If GO: Next phase is [X], requiring [resources]
  If CONDITIONAL: Must resolve [specific gaps] by [date]
  If KILL: [Timing issue vs fundamental issue]
```

---

#### EXECUTIVE SUMMARY

For senior leadership. One page. No jargon. Focus on portfolio value and decisions.

```
INNOVATION PORTFOLIO — EXECUTIVE SUMMARY
[Date]

BOTTOM LINE:
[2-3 sentences: what's the portfolio worth, what's working, what needs attention]

PORTFOLIO AT A GLANCE:
  Total opportunities: [N]
  Pipeline value (base case): $[X]M over [Y] years
  Highest-conviction bet: [Name] — [one line why]
  Biggest risk: [Name or theme] — [one line why]

TOP OPPORTUNITIES:
  1. [Name] — [Stage] — [Score]/3
     [One sentence on why this matters and where it stands]

  2. [Name] — [Stage] — [Score]/3
     [One sentence]

  3. [Name] — [Stage] — [Score]/3
     [One sentence]

DECISIONS FOR YOUR ATTENTION:
  [Only include if there are actual decisions needed]
  1. [Decision needed] — recommended: [action]

TEAM CAPACITY:
  Current allocation: [How the 2 PM+Engineer pairs are deployed]
  Bottleneck: [What's limiting throughput]
```

---

### Step 4: Check In — "Here's the status picture"

**CHECKPOINT: Do NOT skip this step.**

"Here's what the artifacts tell me about [scope]. The key things that stand out:
1. [Most important signal]
2. [Second signal]
3. [Concern or gap]

Does this match your sense of where things are? Anything I'm missing that isn't captured in artifacts?"

### Step 5: Identify Gaps and Stale Data

Flag anything concerning:

```
HEALTH FLAGS:
  ⚠ [Opportunity] has no activity in [X] weeks — stalled or intentional?
  ⚠ [Opportunity] scored [X]/3 but no experiment plan exists — should we test or kill?
  ⚠ [Opportunity] business case is [X] months old — market data may be stale
  ⚠ Portfolio has [X]% H1 and [Y]% H3 — [balance assessment]
  ⚠ No scored opportunities exist — consider running opportunity-score
```

### Step 6: Save the Report

- Get today's date: !`date +%Y-%m-%d`
- Save based on report type:
  - Weekly: `docs/reports/YYYY-MM-DD-innovation-weekly.md`
  - Monthly: `docs/reports/YYYY-MM-DD-innovation-monthly.md`
  - Gate: `docs/reports/YYYY-MM-DD-<opportunity>-gate-review.md`
  - Executive: `docs/reports/YYYY-MM-DD-innovation-executive.md`

After saving, ask:

"Status report saved to [path]. Want to:
(a) Dig into any specific opportunity?
(b) Run opportunity-score on an unscored opportunity?
(c) Generate a different report type?
(d) Move on?"

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Optimistic inference** | "Probably on track" with no artifact evidence | If there's no artifact, say "no evidence" |
| **Activity = progress** | Lots of commits but no stage advancement | Track stage transitions, not busyness |
| **Stale comfort** | Report looks green but data is 6 weeks old | Flag staleness prominently |
| **Decision-free report** | Status update with no "what should we do?" | Every report needs a decisions/priorities section |

## Guidelines

- **Artifacts are the source of truth.** Don't infer status from memory or assumptions. If no artifact exists, the status is unknown.
- **Stale data is worse than no data.** Flag when artifacts are old enough that the information may have changed.
- **Match the audience.** Weekly is for the team (tactical). Monthly is for leadership (strategic). Executive is for senior leaders (portfolio value). Don't mix levels.
- **Surface decisions, not just information.** Every report should answer "what do we need to decide?" not just "where are we?"
- **Momentum matters.** A high-scoring opportunity that hasn't been touched in 6 weeks is a problem. Surface it.
- **Portfolio balance is a finding.** If everything is H1, say so. If there's no pipeline behind the current bets, say so.
