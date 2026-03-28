---
name: metrics-review
description: Run recurring and ad-hoc product metrics reviews — weekly business reviews, monthly performance reviews, and diagnostic investigations when a metric moves unexpectedly. Use when you need a metrics review, dashboard review, weekly business review, monthly review, KPI review, product analytics, business performance, funnel analysis, or when a specific metric dropped, retention is declining, churn spiked, signups are down, or you want to know why a metric moved. This skill analyzes DATA and TRENDS — use innovation-status for portfolio progress snapshots, use okr-setting to score or set OKRs rather than investigate underlying metric data.
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
  - Skill
  - AskUserQuestion
argument-hint: "[review type: weekly | monthly | diagnostic | okr-check] or [specific metric to investigate]"
---

# Metrics Review

A metrics review that doesn't produce decisions is reporting theater. Every review answers "what should we do differently?" — not just "what happened?"

<HARD-GATE>
Never draw conclusions from aggregate metrics without segmenting first. A 5% DAU drop could be entirely in one country, one cohort, or one device type. Aggregate metrics reliably hide the signal. Segment before concluding.
</HARD-GATE>

## Method Selection

| Situation | Approach | Why |
|---|---|---|
| **Weekly business review (WBR)** | Recurring ceremony format (Steps 1-7) | Regular cadence, focus on aberrations only |
| **Monthly deep dive** | Analytical deep dive (Steps 1-8, extended) | Broader analysis, trend identification, strategic implications |
| **Metric moved unexpectedly** | Diagnostic investigation (5-Factor RCA) | Root cause analysis, hypothesis generation |
| **Setting up metrics for a new product** | Framework selection + metric catalog | Choose framework, define metric hierarchy |
| **OKR progress check** | KR tracking format | Pull KRs, assess trajectory, flag at-risk |
| **AI/agent product metrics** | Standard flow + AI supplement | Standard review plus AI-specific metrics from `references/` |

## Input Resolution

1. If `$ARGUMENTS` specifies a review type, use that format
2. If `$ARGUMENTS` names a specific metric, run diagnostic investigation
3. Search `docs/reports/` for prior metrics reviews to establish baselines and trends
4. Search `docs/plans/` for roadmap artifacts — shipped initiatives are the input metrics
5. If no prior reviews exist, start with framework selection

## Process

### Step 1: Determine Review Type and Select Framework

Based on `$ARGUMENTS` or user context, confirm the review type and select the appropriate metrics framework:

| Use Case | Framework | What It Does |
|---|---|---|
| Early stage, where's the leak? | AARRR | Acquisition → Activation → Retention → Revenue → Referral funnel |
| Improving UX quality | HEART | Goal-Signal-Metric process (Happiness, Engagement, Adoption, Retention, Task success) |
| Team alignment, single focus | North Star + Input metrics | One outcome metric + 3-5 levers that drive it |
| Diagnosing why something moved | Input/Output metric tree | Decompose the output metric into upstream inputs |
| Quarterly planning | Combine all four | Cross-reference frameworks for blind spots |

Confirm with user: "I'll run a [type] review using [framework]. Right context?"

### Step 2: Pull Current Metrics

Gather metrics from dashboards, artifacts, or user input:

```
METRICS SNAPSHOT — [Date]
Framework: [Selected framework]
Period: [This week / This month / Custom range]

[For each metric in the framework:]
  [Metric]: [Current value] — [vs. prior period: +/-X%] — [vs. target: on/off track]
```

If metrics aren't available as data, ask the user to provide them. Flag any metric that has no source: "No data available for [metric] — this is a blind spot, not a green light."

### Step 3: Identify Aberrations

<HARD-GATE>
Skip green metrics entirely. A review that walks through every metric is a status meeting, not a metrics review. Focus exclusively on metrics that deviate from trend, miss targets, or moved unexpectedly.
</HARD-GATE>

```
ABERRATIONS:
  ▸ [Metric] — [Direction] [Magnitude] vs. [baseline]
    First observed: [When]
    Trend: [Accelerating / Decelerating / Step change]
```

If no aberrations exist, say so — "All metrics are within expected range. No action items from this review." A clean review is a valid outcome.

### Step 4: Segment and Investigate Each Aberration

For each aberration, apply the **5-Factor Root Cause Analysis** in sequence:

1. **Temporal variance** — Seasonal? Same time last year? Coincides with a recent product change or deploy?
2. **Component drift** — Which sub-metric is driving the aggregate change?
3. **Influence drift** — Did an upstream input metric change? (Trace the metric tree upward)
4. **Dimension shift** — Specific to one segment? (Country, cohort, device, plan tier, channel)
5. **External events** — Launch, campaign, competitor move, macro event, API/platform change?

```
INVESTIGATION — [Metric Name]
SIGNAL: [What moved, by how much, since when]
SEGMENTATION: [Which segments affected — or "affects all segments uniformly"]
ROOT CAUSE (5-Factor):
  1. Temporal: [Finding]
  2. Component: [Finding]
  3. Influence: [Finding]
  4. Dimension: [Finding]
  5. External: [Finding]
HYPOTHESIS: [What we think happened]
CONFIDENCE: [H/M/L]
```

For AI/agent products, also read `references/ai-product-metrics.md` for supplemental metrics to check.

### Step 5: Present Findings

**CHECKPOINT: Do NOT skip this step.**

"Here's what the metrics tell us. The key aberrations:
1. [Most significant finding + hypothesis]
2. [Second finding]
3. [Third finding, if any]

Does this match what you're seeing? Any context I'm missing — recent launches, campaigns, or external events?"

### Step 6: Connect to Roadmap and OKR Decisions

This is where metrics become decisions:

```
ROADMAP IMPLICATIONS:
  ▸ [Finding] suggests [initiative] should be [accelerated / deprioritized / investigated further]
  ▸ [Finding] validates [shipped initiative] — [outcome met / not met]

OKR IMPLICATIONS:
  ▸ KR: [Key Result] — [on track / at risk / off track]
    Action needed: [What changes to get back on track, or update the target]
```

If findings suggest priority changes, flag: "This finding may warrant a roadmap update — invoke **roadmap-planning** to reassess."

If KR progress needs updating, flag: "KR [X] trajectory has changed — invoke **okr-setting** to update."

If a hypothesis needs testing, flag: "This is a hypothesis, not a conclusion — invoke **experiment-design** to validate."

### Step 7: Assign Actions and Save

```
WEEKLY BUSINESS REVIEW — [Date]
ABERRATIONS:
  ▸ [Metric] — [Direction] [Magnitude] — [Hypothesis] — Owner: [Name] — Deadline: [Date]
ACTIONS FROM LAST WEEK:
  ▸ [Action] — [Status: Done / In progress / Dropped]
ROADMAP IMPLICATIONS:
  [Any priority changes based on what we're seeing]
NEXT REVIEW: [Date]
```

For diagnostic investigations, use this format instead:

```
METRIC INVESTIGATION — [Metric Name]
SIGNAL: [What moved, by how much, since when]
SEGMENTATION: [Which segments affected]
ROOT CAUSE: [5-factor analysis results]
HYPOTHESIS: [What we think happened]
CONFIDENCE: [H/M/L]
RECOMMENDED ACTION: [What to do]
OWNER: [Name] — DEADLINE: [Date]
```

Save to: `docs/reports/YYYY-MM-DD-<type>-metrics-review.md`

After saving, offer next steps:

"Review saved to [path]. Want to:
(a) Dig deeper into a specific aberration?
(b) Invoke **roadmap-planning** to adjust priorities based on findings?
(c) Invoke **experiment-design** to test a hypothesis?
(d) Invoke **okr-setting** to update KR trajectories?
(e) Move on?"

---

## Metrics Catalog

For detailed benchmarks by category (Acquisition, Activation, Engagement, Retention, Revenue, Performance), see `references/metrics-catalog.md`.

For AI/agent-specific metrics (hallucination rate, task completion, trust signals, eval infrastructure, cost efficiency), see `references/ai-product-metrics.md`.

---

## Bias Guards

| Thought | Reality | Do Instead |
|---|---|---|
| "This metric is fine, it's within normal range" | Define what "normal" is first; context-free numbers are uninterpretable | Set explicit thresholds before reviewing |
| "We need more data before deciding" | "More data" is often avoidance; set a decision deadline | Time-box the investigation; decide by [date] |
| "DAU is up, things are going well" | Which cohort? Which channel? What's retention? | Segment it before concluding |
| "The AI is working great, task completion is 85%" | What's the hallucination rate? The override rate? | Check supplemental AI metrics |
| "This drop is just noise" | Noise is a hypothesis, not a conclusion | Segment and check; if it's noise, segmentation will show it |
| "We shipped the feature, the metric will move" | Hope is not a tracking mechanism | Set a measurement window and check-in date |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Vanity metrics** | Total users, raw page views — inflatable without delivering value | Use rate metrics and cohort analysis |
| **Data without decisions** | Review produces no action items | Every review must end with actions or explicit "no action needed" |
| **Aggregate conclusions** | Not segmenting before drawing conclusions | Hard gate: segment before concluding |
| **Over-optimization** | Optimizing one metric at expense of others (Goodhart's Law) | Track counter-metrics alongside primary metric |
| **Analysis paralysis** | Endlessly investigating, never deciding | Time-box investigations; decide by deadline |
| **Survivorship bias** | Only analyzing retained users | Include churned/dropped-off users in analysis |
| **Dashboard without ceremony** | Dashboard exists but nobody reviews it on schedule | Dashboard is infrastructure; the review is the practice |

## Guidelines

- **Aberrations only.** A review that walks through every metric is a status meeting. Focus on what moved, what's off-track, and what's surprising. Green metrics get skipped.
- **Segment before you conclude.** The hard gate is non-negotiable. Aggregate metrics are averages of averages — they hide everything interesting.
- **Decisions are the output.** If a review produces no action items and no explicit "no action needed," it failed. Reporting without deciding is theater.
- **Connect metrics to the roadmap.** Metrics exist to evaluate whether initiatives worked. A metric review disconnected from the roadmap is navel-gazing.
- **Counter-metrics prevent Goodhart's Law.** When optimizing activation rate, track support load. When optimizing engagement, track churn. One metric in isolation lies.
- **Time-box investigations.** "We need more data" gets a deadline. Investigations without deadlines become permanent excuses to avoid deciding.
- **Clean reviews are valid.** If nothing moved, say "nothing moved" and move on. Not every review produces a crisis.

Follow the communication-protocol skill for all user-facing output and interaction.
