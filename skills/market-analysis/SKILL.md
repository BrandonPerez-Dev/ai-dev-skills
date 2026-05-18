
---
name: market-analysis
description: Rigorous market sizing (TAM/SAM/SOM) combined with competitive landscape analysis. Use when you need to answer "how big is this?" and "who's already doing it?" Produces confidence-ranged estimates, not false precision.
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
argument-hint: "[opportunity topic or path to opportunity brief]"
---

# Market Analysis

Size the market and map the competition. Produces defensible estimates with honest confidence levels.

<HARD-GATE>
NEVER produce a single point estimate. Every market size MUST be a range with a stated confidence level. "$97.3M" is false precision. "$50-150M (directional)" is honest.
</HARD-GATE>

## When to Use

- You've identified an opportunity and need to know if it's big enough
- Leadership is asking "how big is this market?"
- You need to understand the competitive landscape before committing resources
- You want to compare the relative size of two opportunities
- An opportunity-research brief needs detailed sizing

## Input Resolution

1. If $ARGUMENTS is a file path, read that opportunity brief as context
2. If $ARGUMENTS is a topic, search `docs/plans/` for `*-opportunity.md` matching that topic
3. If no arguments, ask the user what market to analyze

## Process

### Step 1: Define What We're Sizing

This matters more than people think. "Field service management" and "AI dispatching for HVAC contractors" are completely different markets.

Ask the user to confirm:
- What's the specific product/service concept?
- Who's the target customer? (segment, size, geography)
- What's the revenue model? (subscription, transaction-based, usage-based?)
- What price range are we assuming?

If an opportunity brief exists, pull these from it and confirm: "Based on the opportunity brief, I'm sizing [X] for [Y customers] at roughly [$Z/year]. Sound right?"

### Step 2: Top-Down Sizing

Start from published industry data and narrow down.

**Research (use web search):**
- Industry reports for the broader market (Gartner, Forrester, IBISWorld, Grand View Research, MarketsandMarkets)
- CAGR and growth projections
- Geographic and segment breakdowns

**Calculate:**
```
Total market (from reports): $[X]B
├─ Geography filter (US only? North America?): $[Y]B
├─ Segment filter (our target vertical): $[Z]B
├─ Use case filter (specific problem we solve): $[W]B
└─ TAM: $[W]B
    └─ SAM (realistic addressability): $[V]B
```

**Document your filters and sources.** Every step should cite where the number came from.

### Step 3: Bottom-Up Sizing

Build from unit economics upward — this is usually more defensible.

**Calculate:**
```
Number of target customers: [count]
├─ Source: [Census, LinkedIn, industry DB, SIC/NAICS codes]
├─ Segment: [specific criteria]
└─ Addressable subset: [filtered count]

× Average Revenue Per Account (ARPA): $[X]/year
├─ Source: [pricing research, competitor pricing, customer interviews]
└─ Model: [subscription, transaction, usage]

= Bottom-up SAM: [count] × $[ARPA] = $[X]M

× Realistic penetration (5-year): [X]%
├─ Basis: [comparable company data, market maturity]
└─ Conservative vs optimistic range

= SOM range: $[low]M - $[high]M
```

### Step 4: Reconcile Top-Down and Bottom-Up

They will almost never agree. The gap is informative.

**If top-down >> bottom-up:**
- Top-down probably includes adjacent segments you're not targeting
- Bottom-up may be underestimating customer count or ARPA
- Use bottom-up as conservative, top-down as ceiling

**If bottom-up >> top-down:**
- You may be overestimating addressable customers or ARPA
- Top-down reports may not capture a nascent market
- Investigate what's different

**Present the reconciliation:**
```
Top-down SAM: $[X]M (source: industry reports)
Bottom-up SAM: $[Y]M (source: customer count × ARPA)
Delta: [X vs Y, % difference]

Explanation: [Why they differ]
Best estimate: $[low]M - $[high]M [confidence level]
```

### Step 5: Check In — "Here's the sizing"

**CHECKPOINT: Do NOT skip this step.**

"The market sizes to roughly $[X-Y]M SAM. Here's how I got there:
- Top-down says $[A]M based on [source]
- Bottom-up says $[B]M based on [count] customers at $[ARPA]
- The gap is because [reason]
- Confidence is [rough/directional/validated]

Does this feel right given what you know about the space?"

### Step 6: Competitive Landscape

**Direct competitors** — same solution, same customer:
Research and tabulate:
| Player | What they offer | Pricing | Customers | Funding | Weakness/Gap |

**Indirect alternatives** — how customers solve this today:
(Often the real competition is Excel, phone calls, or "do nothing")

**Potential disruptors** — who could enter this market:
(Adjacent players, well-funded startups, big tech)

### Step 7: Porter's Five Forces

Apply practically, not academically. For each force, answer the strategic question:

**Competitive Rivalry** — How hard is it to win customers?
**Threat of New Entrants** — How easy is it for someone new to enter?
**Threat of Substitutes** — What else could customers use instead?
**Buyer Power** — Can customers negotiate us down or switch easily?
**Supplier Power** — Are we dependent on any key technology or partner?

Rate each: HIGH / MEDIUM / LOW with one-line justification.

### Step 8: Competitive Positioning Map

Pick two axes that meaningfully differentiate competitors in this market. Axes should be:
- Customer-relevant (not internal capabilities)
- Show visible variance across competitors (not all bunched in one corner)

Plot 5-8 players including "current solution" (e.g., spreadsheets/manual).

Identify the **white space** — positioning that nobody occupies but customers would value.

### Step 9: Check In — "Here's the competitive picture"

**CHECKPOINT: Do NOT skip this step.**

"The competitive landscape looks like [brief characterization]. Key findings:
- Leader: [X] with [positioning]
- Gap: Nobody is doing [specific thing]
- WEX could play: [positioning] because [advantage]
- Biggest competitive risk: [specific threat]

Does this match what you're seeing?"

### Step 10: Produce the Market Analysis

**Layer 1 — Market Brief:**

```
MARKET: [Opportunity name]

SIZING:
  TAM: $[X-Y]B [confidence]
  SAM: $[X-Y]M [confidence]
  SOM (5yr): $[X-Y]M [confidence]
  Growth: [X]% CAGR

COMPETITION:
  [X] direct competitors. Market leader: [name].
  White space: [what nobody is doing]
  Biggest threat: [specific]

POSITIONING OPPORTUNITY:
  [Where WEX could play and why]

BOTTOM LINE:
  Market is [attractive/moderate/limited] because [reason].
  [Confidence level] — [what would increase confidence]
```

**Layer 2 — Full Analysis:**

- Top-down sizing methodology and sources
- Bottom-up sizing methodology and sources
- Reconciliation analysis
- Competitor table (features, pricing, funding, gaps)
- Porter's Five Forces assessment
- Positioning map (visual or ASCII)
- WEX advantage assessment for this market
- Data sources and methodology notes

### Step 11: Save the Artifact

- Get today's date: !`date +%Y-%m-%d`
- Derive topic from opportunity
- Save to: `docs/plans/YYYY-MM-DD-<topic>-market.md`

After saving, present Layer 1 and ask:

"Market analysis saved to [path]. Want to:
(a) Dig into the competitive landscape?
(b) Challenge any of the sizing assumptions?
(c) Run business-case to build the financial model?
(d) Run experiment-design to test riskiest sizing assumptions?
(e) Move on?"

## Confidence Levels

| Level | Meaning | Basis |
|-------|---------|-------|
| **Rough** | Order of magnitude only | Single industry report, no bottom-up |
| **Directional** | Range is meaningful but wide | Top-down + bottom-up attempted, some reconciliation |
| **Validated** | Narrow range, defensible | Multiple sources agree, customer pricing data, bottom-up verified |

## Guidelines

- **Ranges, not points.** "$50-150M" not "$97.3M". False precision destroys credibility.
- **Source everything.** Every number traces to a report, database, or calculation.
- **Bottom-up is king.** Top-down gets you in the ballpark. Bottom-up is what you defend.
- **The gap between top-down and bottom-up is informative.** Don't hide it — explain it.
- **"Current solution" is a competitor.** Spreadsheets, phone calls, and gut feel are often the real competition.
- **Check in before finalizing.** The user may know things about the market that web research doesn't capture.
