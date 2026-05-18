
---
name: business-case
description: Build an evidence-based investment case for an opportunity. Pulls together market analysis, customer discovery, and experiment results into a revenue model, unit economics, GTM strategy, and financial projections. The artifact leadership uses to make funding decisions.
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
argument-hint: "[opportunity topic or path to existing briefs]"
---

# Business Case

Produce the investment case. This is the artifact that gets an opportunity funded or killed.

<HARD-GATE>
Every financial projection MUST include sensitivity analysis. Single-scenario projections are fiction. Show what happens when key assumptions are wrong.
</HARD-GATE>

## When to Use

- An opportunity has been researched and validated enough to warrant a business case
- Leadership is asking "should we invest in this?"
- You need to model the revenue potential and unit economics
- You want to compare the financial viability of two opportunities
- An opportunity is moving from YELLOW to potential GREEN

## Input Resolution

Look for existing artifacts to pull from (don't start from scratch if research exists):

1. Search `docs/plans/` for matching opportunity, market, discovery, and experiment files
2. If found, read them and summarize what's available: "I found [X artifacts]. I'll pull from these."
3. If nothing exists, note the gaps: "No market sizing found — estimates will be rough."

## Process

### Step 1: Gather Existing Evidence

Read all available artifacts for this opportunity:
- `*-opportunity.md` → problem, WEX advantage, verdict
- `*-market.md` → TAM/SAM/SOM, competitive landscape
- `*-discovery.md` → customer evidence, JTBD, pain quantification
- `*-experiments.md` → validated/invalidated assumptions, evidence levels

Present a quick inventory: "Here's what I'm working with:
- Market sizing: [available/missing] — confidence: [level]
- Customer evidence: [N interviews / surveys / none]
- Experiment results: [what's validated, what's not]
- Gaps I'll need to estimate: [list]"

### Step 2: Build the Investment Thesis

Write a 35-40 word thesis that captures the core bet:

"[WEX should / could] build [solution] for [target customer] to solve [problem], generating [$X]M in [timeframe] by leveraging [WEX advantage]. Key risk: [riskiest assumption]."

Check with user: "Does this thesis capture the bet we're making?"

### Step 3: Revenue Model

Build the model based on the likely revenue type:

**For Subscription/SaaS:**
```
Customers × ARPA × Retention = Revenue
Year 1: [X] customers × $[Y]/yr × [Z]% retention
Year 2: Y1 retained + new customers × ARPA
Year 3-5: Growth rate applied, retention compounding
```

**For Transaction-Based:**
```
Transaction Volume × Take Rate = Revenue
Year 1: [X] transactions × [Y]% rate
Growth: Volume growth + rate optimization
```

**For Platform/Hybrid:**
```
Platform fee + Transaction revenue + Premium tiers
Model each stream separately, then combine
```

### Step 4: Unit Economics

Calculate and present:

```
UNIT ECONOMICS:
  Customer Acquisition Cost (CAC): $[X]
    Basis: [how we'd acquire customers — channel, cost per]

  Average Revenue Per Account (ARPA): $[X]/year
    Basis: [pricing model, tier mix]

  Gross Margin: [X]%
    Basis: [COGS breakdown — infrastructure, support, payment processing]

  Lifetime Value (LTV): $[X]
    Formula: (ARPA × Gross Margin) / Annual Churn Rate

  LTV:CAC Ratio: [X]:1
    Target: >3:1 for healthy B2B SaaS

  Payback Period: [X] months
    Formula: CAC / (Monthly ARPA × Gross Margin)
    Target: <18 months for B2B
```

### Step 5: Check In — "Here's the financial picture"

**CHECKPOINT: Do NOT skip this step.**

"The unit economics look like this:
- We'd need to charge ~$[X]/month to make this work
- CAC estimate is $[Y] (based on [channel])
- LTV:CAC is [Z]:1 — [healthy/tight/concerning]
- Payback is [N] months

The model is most sensitive to [key driver — usually churn or CAC].
Does this feel realistic based on what you know?"

### Step 6: Go-to-Market Strategy

Define how we'd actually sell this:

**Distribution channels** (ranked by fit):
- Embedded in existing WEX products (lowest CAC)
- Direct sales to existing WEX customers (warm channel)
- Inside sales to new customers
- Channel partners
- Self-serve / product-led growth

**Sales motion:**
- Who buys? (persona, title, budget authority)
- Sales cycle length
- Deal size range
- Required sales resources

**Phased approach:**
- Phase 1 (months 1-6): [How we start — usually pilots with existing customers]
- Phase 2 (months 7-12): [How we scale — usually add sales capacity]
- Phase 3 (year 2+): [How we grow — channels, self-serve, expansion]

### Step 7: Risk Assessment

Categorize and assess:

```
| Risk | Category | Likelihood | Impact | Mitigation |
|------|----------|-----------|--------|------------|
| [Risk 1] | Market | H/M/L | H/M/L | [Action] |
| [Risk 2] | Competitive | H/M/L | H/M/L | [Action] |
| [Risk 3] | Technical | H/M/L | H/M/L | [Action] |
| [Risk 4] | Regulatory | H/M/L | H/M/L | [Action] |
| [Risk 5] | Execution | H/M/L | H/M/L | [Action] |
```

### Step 8: Financial Projections (3-5 Year)

Build three scenarios:

**Conservative (floor):** Slow growth, higher churn, lower ARPA
**Base case (likely):** Expected trajectory
**Optimistic (ceiling):** Strong product-market fit, faster growth

For each scenario, show:
- Revenue by year
- Customer count by year
- Key margins (gross, operating)
- Investment required
- Break-even point

### Step 9: Sensitivity Analysis

Model what happens when key assumptions are wrong:

```
SENSITIVITY: What if [assumption] changes?

If CAC increases 50%:
  → LTV:CAC drops from 3.5:1 to 2.3:1
  → Payback extends from 10 to 15 months
  → Impact: MODERATE — still viable but tighter

If churn doubles (3% → 6%):
  → LTV drops 50%
  → LTV:CAC drops below 2:1
  → Impact: SEVERE — need to solve retention before scaling

If ARPA is 30% lower:
  → Break-even pushes back 18 months
  → Impact: MODERATE — viable if CAC also lower
```

### Step 10: Resource Requirements

What does this take to execute?

```
PHASE 1 (Discovery + MVP): Months 1-6
  Team: [X] engineers, [Y] PM, [Z] design
  Budget: $[X]
  Key milestone: [What proves it's working]

PHASE 2 (Pilot + Scale): Months 7-12
  Additional: [Sales, customer success, etc.]
  Budget: $[X]
  Key milestone: [Revenue/customer target]

PHASE 3 (Growth): Year 2+
  Full team: [Size and composition]
  Budget: $[X]
  Key milestone: [Revenue/scale target]
```

### Step 11: Produce the Business Case

**Layer 1 — Investment Brief:**

```
INVESTMENT THESIS: [35-40 words]

MARKET: $[X-Y]M SAM | [growth]% CAGR
REVENUE MODEL: [Type] | ARPA: $[X]/yr | LTV:CAC: [X]:1

3-YEAR PROJECTION:
  Y1: $[X] revenue | [N] customers
  Y2: $[X] revenue | [N] customers
  Y3: $[X] revenue | [N] customers
  Break-even: Year [X]

INVESTMENT REQUIRED:
  Phase 1: $[X] over [Y] months
  Total 3-year: $[X]

WEX ADVANTAGE: [One line]

TOP RISK: [Named, with mitigation]

RECOMMENDATION: [FUND / CONDITIONAL FUND / HOLD / KILL]
  Condition (if applicable): [What must be true before Phase 2]
```

**Layer 2 — Full Business Case:**

- Investment thesis narrative
- Problem statement with customer evidence
- Solution overview
- Market opportunity (from market-analysis or estimated)
- Revenue model detail with assumptions
- Unit economics breakdown
- Competitive positioning
- WEX strategic advantage
- Go-to-market strategy
- Risk assessment table
- Financial projections (3 scenarios)
- Sensitivity analysis
- Resource requirements and timeline
- Lean Canvas (one-page business model summary)
- Evidence inventory (what's validated, what's not)

### Step 12: Save the Artifact

- Get today's date: !`date +%Y-%m-%d`
- Save to: `docs/plans/YYYY-MM-DD-<topic>-business-case.md`

After saving, present Layer 1 and ask:

"Business case saved to [path]. Want to:
(a) Stress-test any assumption in the financial model?
(b) Run opportunity-score to compare this against other opportunities?
(c) Run product-definition to start scoping what we'd build?
(d) Move on?"

## Guidelines

- **Evidence over estimates.** Pull from existing artifacts. Flag what's validated vs assumed.
- **Sensitivity analysis is mandatory.** Single-scenario projections are fantasy.
- **Three scenarios, not one.** Conservative, base, optimistic — leadership needs to see the range.
- **Unit economics must work.** If LTV:CAC < 2:1, the business model needs fixing before anything else.
- **GTM is not "build it and they will come."** Specify channel, cost, timeline.
- **Resource requirements are honest.** Don't low-ball to get approval — it backfires.
- **Check in on the financial picture.** The user may know things about pricing or costs that change the model.
