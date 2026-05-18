
---
name: opportunity-score
description: Score an opportunity against a standardized framework (Desirability/Viability/Feasibility/Adaptability) and compare it to other opportunities in the portfolio. Use when deciding what to pursue, kill, or prioritize.
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
argument-hint: "[opportunity topic or path to business case]"
---

# Opportunity Score

Standardized, evidence-based evaluation for portfolio comparison and GO/KILL/PIVOT decisions.

<HARD-GATE>
Scores MUST be based on evidence levels, not opinion. If evidence doesn't exist, the score reflects that (low), not what you think the answer would be. Opinion-based scoring is worse than no scoring.
</HARD-GATE>

## When to Use

- You need to compare multiple opportunities against each other
- Leadership needs a standardized view of the innovation portfolio
- You're preparing for a gate review (go/kill/pivot decision)
- You want to check if portfolio balance is healthy (H1/H2/H3 mix)
- An opportunity needs a formal recommendation

## Input Resolution

1. Search `docs/plans/` for all artifacts related to the opportunity topic
2. Read business case, market analysis, discovery synthesis, and experiment results
3. If minimal artifacts exist, note that scores will be low due to lack of evidence (this is correct behavior, not a problem)

## Process

### Step 1: Inventory Available Evidence

Before scoring, catalog what exists:

```
EVIDENCE INVENTORY for [Opportunity]:
  Opportunity brief: [exists/missing]
  Customer discovery: [N interviews / missing]
  Market analysis: [exists with confidence X / missing]
  Experiment results: [N experiments completed / missing]
  Business case: [exists / missing]
  Technical assessment: [exists / missing]
```

Present to user: "Here's what I have to score against. Gaps will show as lower scores — that's honest, not a problem."

### Step 2: Score on DVF+A Framework

**Desirability (0-3): "Do customers want this?"**

| Score | Evidence Required |
|-------|------------------|
| 0 | No customer evidence at all |
| 1 | 1-3 interviews mention the problem; no quantification |
| 2 | 8+ interviews validate problem; 40%+ would pay; pain quantified |
| 3 | 15+ interviews across segments; willingness to pay validated; behavioral evidence (not just stated preference) |

**Viability (0-3): "Can we make money?"**

| Score | Evidence Required |
|-------|------------------|
| 0 | No financial model; pricing untested |
| 1 | Initial model exists; ARPA estimated but not validated |
| 2 | Pricing tested with 5+ customers; unit economics modeled; LTV:CAC estimated |
| 3 | Pricing validated across segments; LTV:CAC >3:1 confirmed; retention data from pilot |

**Feasibility (0-3): "Can we build and deliver it?"**

| Score | Evidence Required |
|-------|------------------|
| 0 | No technical work done; architecture unclear |
| 1 | Architecture outlined; key risks identified |
| 2 | MVP built or prototyped; core integrations POC'd |
| 3 | MVP deployed to real users; integrations working; operations proven at small scale |

**Adaptability (0-3): "Does it fit our strategy and can we compete?"**

| Score | Evidence Required |
|-------|------------------|
| 0 | Misaligned with strategy or competitive position untenable |
| 1 | Loosely aligned; competitive response unclear |
| 2 | Aligned to strategy; competitive positioning identified; some capability gaps |
| 3 | Strongly aligned; sustainable advantage identified; organizational capabilities in place |

### Step 3: Three Horizons Classification

Categorize the opportunity:

**H1 — Core (0-2 years):** Enhances existing WEX products. Lower risk, shorter payback.
**H2 — Adjacent (2-4 years):** Extends into related markets or capabilities. Medium risk.
**H3 — Transformational (4+ years):** New market, new business model. High risk, high reward.

### Step 4: Check In — "Here's how it scores"

**CHECKPOINT: Do NOT skip this step.**

Present the scorecard:

```
[Opportunity Name]
  Desirability: [X]/3 — [one-line justification]
  Viability:    [X]/3 — [one-line justification]
  Feasibility:  [X]/3 — [one-line justification]
  Adaptability: [X]/3 — [one-line justification]
  Average:      [X]/3
  Horizon:      H[1/2/3]
```

"Does this feel right? Any dimension where you have evidence I'm not capturing?"

### Step 5: Portfolio Comparison (if other scored opportunities exist)

Search `docs/plans/` for other `*-score.md` files. If found, create comparison:

```
PORTFOLIO VIEW:

| Opportunity       | D | V | F | A | Avg  | Horizon | Status    |
|-------------------|---|---|---|---|------|---------|-----------|
| [Opportunity 1]   | 2 | 2 | 2 | 3 | 2.25 | H2      | Phase 2   |
| [Opportunity 2]   | 3 | 2 | 3 | 2 | 2.50 | H1      | Building  |
| [This one]        | 1 | 0 | 0 | 2 | 0.75 | H3      | Discovery |
```

Check portfolio balance:
- What % of opportunities are H1 / H2 / H3?
- Is the portfolio balanced? (Guideline: ~70% H1, 20% H2, 10% H3)
- Are there resource conflicts between opportunities?

### Step 6: Evidence Gaps and Next Steps

Identify what's missing to improve the score:

```
EVIDENCE GAPS:
  Desirability: Score would improve from 1→2 if we [run 5 more interviews]
  Viability: Score would improve from 0→1 if we [build initial financial model]
  Feasibility: Score would improve from 0→1 if we [do architecture review]
```

### Step 7: Recommendation

Based on score + horizon + portfolio context:

**Score 2.5+:** GO — invest in next phase
**Score 2.0-2.4:** CONDITIONAL GO — proceed if specific evidence gaps are closed by [date]
**Score 1.5-1.9:** EXPLORE — small investment to reduce uncertainty; not ready for commitment
**Score <1.5:** HOLD or KILL — not enough evidence to justify resources

If KILL, check: is it a timing issue (revisit in 6-12 months) or a fundamental issue (walk away)?

### Step 8: Produce the Scorecard

**Layer 1 — Score Brief:**

```
OPPORTUNITY: [Name]
HORIZON: H[1/2/3] — [one-line rationale]

SCORECARD:
  Desirability:  [X]/3 [██░░░░] — [one-line]
  Viability:     [X]/3 [██░░░░] — [one-line]
  Feasibility:   [X]/3 [██░░░░] — [one-line]
  Adaptability:  [X]/3 [██░░░░] — [one-line]
  OVERALL:       [X]/3

PORTFOLIO FIT: [How this fits with other opportunities]

RECOMMENDATION: [GO / CONDITIONAL GO / EXPLORE / HOLD / KILL]
  [One-line rationale]

TO IMPROVE SCORE: [Top 2 evidence gaps to close]
```

**Layer 2 — Full Scorecard:**

- Evidence inventory (what exists, what's missing)
- Detailed scoring rationale per dimension
- Portfolio comparison table
- Portfolio balance analysis
- Evidence gap analysis with recommended actions
- Kill criteria (what would trigger stopping)
- Historical score progression (if re-scoring)

### Step 9: Save the Artifact

- Get today's date: !`date +%Y-%m-%d`
- Save to: `docs/plans/YYYY-MM-DD-<topic>-score.md`

After saving, present Layer 1 and ask:

"Scorecard saved to [path]. Want to:
(a) Challenge any dimension's score?
(b) See the portfolio comparison in detail?
(c) Run experiment-design to close evidence gaps?
(d) Run product-definition if this is a GO?
(e) Move on?"

## Guidelines

- **Evidence, not opinion.** A score of 0 for "no evidence" is MORE useful than a score of 2 based on "I think customers would like it."
- **Low scores are informative, not bad.** A score of 0.75 for a new idea means "we're early" not "this is a bad idea."
- **Portfolio balance matters.** Five H1 opportunities and zero H3 means we're not taking enough risk. All H3 means we're being reckless.
- **Re-score periodically.** Scores should improve as evidence accumulates. If they don't, ask why.
- **Kill criteria are pre-agreed.** Don't move the goalposts when a favorite project scores low.
