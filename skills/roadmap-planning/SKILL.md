---
name: roadmap-planning
description: Create and maintain product roadmaps — strategic planning artifacts that connect vision to execution. Produces Now/Next/Later or outcome-based roadmaps with initiative prioritization, confidence levels, and audience-specific views. Use when building a new roadmap, updating an existing one, running quarterly planning, preparing a roadmap for stakeholder presentation, or deciding what to build next at the strategic level. This skill plans WHICH initiatives to pursue and WHEN — use product-definition to scope HOW a specific initiative works.
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
argument-hint: "[topic, product name, or path to existing roadmap]"
---

# Roadmap Planning

A roadmap communicates strategic intent — it anchors every initiative to an outcome and uses confidence levels that decrease with time horizon. It is NOT a feature list, a delivery schedule, or a commitment contract.

<HARD-GATE>
Every roadmap item MUST be anchored to a measurable outcome. "Build X" is not a roadmap item — "Reduce Y by Z% through X" is. Feature-only items without outcomes produce feature factory roadmaps, the most common PM failure mode.
</HARD-GATE>

## Method Selection

| Situation | Approach | Why |
|---|---|---|
| **No roadmap exists** | Full creation flow (Steps 1-9) | Need to establish vision, themes, and initiative set |
| **Existing roadmap, quarterly review** | Review Protocol → Steps 3-8 | Vision/themes likely stable; initiatives need re-evaluation |
| **Adding specific initiatives** | Steps 4-6, 8 only | Structure exists; just placing new items |
| **Audience-specific view needed** | Step 7 only | Roadmap exists; need a different lens on it |
| **AI/agent product** | Full flow + AI supplement (Step 6) | Standard flow plus AI-specific initiative categories |

## Input Resolution

1. If `$ARGUMENTS` is a file path, read that as the existing roadmap
2. If `$ARGUMENTS` is a topic/product name, search `docs/plans/` for `*-roadmap.md` files
3. Search `docs/plans/` for business cases, opportunity scores, and product definitions — these are raw material for roadmap items
4. If no artifacts exist, start from scratch with the user

## Process

### Step 1: Establish Strategic Context

Pull from existing artifacts or establish with user:

```
PRODUCT VISION: [Where this product is going in 2-3 years — one paragraph]

NORTH STAR METRIC: [The single metric that defines product success]
  Current: [baseline]
  Target: [goal + timeframe]

STRATEGIC CONSTRAINTS:
  - [Resource limits, team size, budget]
  - [Regulatory or compliance deadlines]
  - [Platform or technical constraints]
  - [Market timing pressures]
```

Confirm with user: "This is the strategic frame. Does this still hold?"

### Step 2: Define Strategic Themes

Themes are the 3-5 focus areas that organize the roadmap. Each answers "why are we investing here?"

```
THEME 1: [Name] — [One sentence: what outcome this theme drives]
  Rationale: [Why this matters now — market signal, customer pain, strategic bet]
  North star connection: [How this theme moves the north star metric]

THEME 2: [Name] — [One sentence]
  ...
```

**Guideline:** 3 themes is focused. 5 is the max. More than 5 means you haven't prioritized.

**CHECKPOINT: Do NOT skip this step.**

"Here are the themes I'm seeing. These determine what makes it onto the roadmap and what doesn't. Right?"

### Step 3: Inventory Candidate Initiatives

Gather all potential roadmap items from:
- Scored opportunities (`docs/plans/*-score.md`)
- Business cases (`docs/plans/*-business-case.md`)
- Product definitions (`docs/plans/*-product-def.md`)
- User feedback and discovery findings
- Technical debt and infrastructure needs
- Compliance or regulatory requirements
- User's direct input

For each candidate:

```
INITIATIVE: [Name]
  Outcome: [What measurable result this produces]
  Theme: [Which strategic theme this serves]
  Source: [Where this came from — artifact, user input, market signal]
  Evidence: [What validates this is worth doing — score, customer signal, data]
  Size: [S/M/L — rough effort, not story points]
```

Scan all sources above before asking the user. Present what you found, then ask: "These are the candidates I found in your artifacts. What's missing?"

Flag any candidates that don't map to a theme — they're either misaligned or reveal a missing theme.

### Step 4: Prioritize

For each candidate, score using RICE:

```
INITIATIVE: [Name]
  Reach: [How many users/customers affected per quarter] — [1-3 scale]
  Impact: [How much does it move the outcome metric] — [0.25/0.5/1/2/3]
  Confidence: [How sure are we about reach and impact] — [10%/25%/50%/80%/100%]
  Effort: [Person-months] — [estimated]
  RICE Score: (Reach × Impact × Confidence) / Effort = [score]
```

**Rank by RICE within each theme** — don't just rank globally. Each theme has its own stack rank; the user decides theme allocation.

If an initiative has a score from **opportunity-score**, use as additional signal:
- Score 2.5+: Strong candidate for Now/Next
- Score 1.5-2.4: Candidate for Next/Later
- Score <1.5: Needs more evidence — invoke **opportunity-score** or **experiment-design** before roadmapping

**CHECKPOINT: Do NOT skip this step.**

"Here's how the initiatives rank. The top [N] by RICE are [list]. Does the ranking feel right before I place them?"

### Step 5: Place on the Roadmap

Use Now/Next/Later as the default framework:

**NOW — Committed (this quarter)**
- Fully scoped or actively being scoped
- Confidence: High — we know what we're building and why
- These items should have (or be getting) product definitions

**NEXT — Planned (next 1-2 quarters)**
- Direction is clear, discovery underway or planned
- Confidence: Medium — we know the outcome but not the exact solution

**LATER — Exploratory (3+ quarters out)**
- Strategic intent only — may never be built as currently described
- Confidence: Low — we believe this matters but haven't validated it

```
NOW — [Quarter or "Current"]
  ▸ [Initiative] — [Outcome target] — [Size] — [Owner if known]
    Status: [Not started / Discovery / In progress / Shipped]
    Dependencies: [What this needs from other teams or systems]

---

NEXT — [Quarter range]
  ▸ [Initiative] — [Outcome hypothesis] — [Size estimate]
    Needs before promotion: [What must be true to move this to Now]

---

LATER — [Directional]
  ▸ [Initiative] — [Strategic intent]
    Open questions: [What we'd need to learn first]
    Kill criteria: [What would cause us to remove this]

---

PARKING LOT — Evaluated and deferred
  ▸ [Initiative] — [Why deferred] — [Revisit trigger]
```

**Placement rules:**
- **Now: 2-4 items max.** If you have 8, you haven't prioritized.
- **Next: 3-6 items.** Enough pipeline, not so many that everything looks planned.
- **Later:** Longer is OK — it's strategic intent, not commitment.
- **Parking Lot:** Prevents zombie initiatives from resurfacing every cycle.

### Step 6: AI/Agent Product Supplement

If the product involves AI, agents, or ML, read `references/ai-product-roadmap.md` for categories that belong as first-class initiatives (eval frameworks, data pipelines, trust features, guardrails). Only include what's relevant to this product's stage.

### Step 7: Generate Audience-Specific Views

Read `references/audience-views.md` for templates. Generate the appropriate view(s):
- **Strategic** (executives): outcomes, themes, risks — no implementation detail
- **Tactical** (PM + engineering): epics, dependencies, spec status, promotion criteria
- **External** (customers/sales): capabilities in user language — no internal details

### Step 8: Dependencies and Risks

```
DEPENDENCIES:
  [Initiative A] → blocks → [Initiative B]
    Risk: [What happens if A slips]
    Mitigation: [How to reduce coupling]

  [Initiative C] → requires → [External team/system]
    Status: [Confirmed / Requested / Unknown]

RISKS TO THE PLAN:
  1. [Risk] — Impact: [H/M/L] — Likelihood: [H/M/L]
     Mitigation: [Action]
```

### Step 9: Produce and Save

**CHECKPOINT: Do NOT skip this step.**

Present the roadmap and surface the key decisions:

"Here's the roadmap. The key decisions embedded in it:
1. [Most significant prioritization choice]
2. [What was deferred and why]
3. [Biggest risk or dependency]

Does this reflect your strategic intent?"

After confirmation:
- Get today's date: !`date +%Y-%m-%d`
- Save to: `docs/plans/YYYY-MM-DD-<topic>-roadmap.md`
- Include all generated views with clear section breaks

After saving, offer next steps:

"Roadmap saved to [path]. Want to:
(a) Adjust any initiative's placement or priority?
(b) Generate a standalone audience view?
(c) Invoke **product-definition** on a Now initiative to start scoping?
(d) Invoke **opportunity-score** on a candidate that needs evaluation?
(e) Move on?"

---

## Roadmap Review Protocol

<HARD-GATE>
Before updating an existing roadmap, check outcomes first. Did shipped Now items achieve their target metrics? A roadmap review that skips outcome checking just rotates items through horizons without learning. If metrics aren't available, flag it — "we shipped X but have no data on whether it worked" is a finding, not a failure.
</HARD-GATE>

For quarterly reviews:

1. **Check outcomes:** Did shipped Now items hit their targets? What does that tell us?
2. **Promote:** Move Next → Now for items with evidence gathered and resources available
3. **Demote or kill:** Move items to Parking Lot if they lost relevance, evidence, or priority
4. **Add:** New initiatives from recent discovery, market changes, or user feedback
5. **Rebalance themes:** Are we still investing in the right areas?
6. **Update confidence:** Has anything become more or less certain?

If outcomes are consistently missed, question the themes — not just the initiatives.

---

## Bias Guards

| Thought | Reality | Do Instead |
|---|---|---|
| "We should add this — it's easy" | Ease is not a prioritization criterion. Easy + low-impact = waste. | Score with RICE. Low impact = doesn't belong. |
| "We committed to this at the offsite" | Sunk cost. The offsite didn't have today's evidence. | Re-evaluate with current data. Park it if it doesn't score. |
| "The CEO mentioned this" | HiPPO is not evidence. | Note the request, score it, present honestly. |
| "Everything is a Must Have" | If everything is Now, nothing is prioritized. | Force-rank. If you can't cut, you haven't decided. |
| "Let's keep it on Later just in case" | Later is strategic intent, not a junk drawer. | No strategic rationale → remove. Parking Lot exists for a reason. |
| "We need dates for the roadmap" | Dates create commitment contracts, not plans. | Now/Next/Later. Date ranges only when asked, with confidence bands. |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Feature factory roadmap** | Features without outcomes. Assumes we know what to build. | Every item needs an outcome hypothesis. |
| **Date-driven commitments** | Strategic intent becomes delivery contract. | Now/Next/Later. Dates are estimates, not promises. |
| **Roadmap as backlog** | 47 items, no hierarchy. Everything equally important. | 2-4 Now, 3-6 Next. Can't cut = haven't decided. |
| **Single static view** | One view for all audiences. Execs see too much, engineers too little. | Audience-specific views from the same source. |
| **Never-updated roadmap** | Written once, drifts from reality in weeks. | Quarterly minimum. Monthly for fast-moving products. |
| **HiPPO-driven roadmap** | Reflects what leadership wants, not what evidence supports. | Score everything. Let evidence speak. |
| **No parking lot** | Deferred ideas resurface every planning cycle. | Explicit Parking Lot with revisit triggers. |
| **No outcome checking** | Items rotate through horizons without measuring impact. | Review Protocol requires outcome check before any update. |

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **Outcomes over outputs.** "Reduce churn by 15%" is a roadmap item. "Build notification system" is a solution hypothesis that belongs inside the initiative.
- **Confidence decreases with distance.** Now items are specific. Later items are directional. This is correct, not lazy.
- **The Parking Lot is a feature, not a bug.** Explicitly deferring items prevents zombie initiatives.
- **3-5 themes max.** More means you're listing, not choosing. Every theme connects to the north star.
- **Now is sacred.** Only 2-4 items. 8 simultaneous items = nothing gets done well.
- **Review is not optional.** Unreviewed roadmap = wish list.
- **Kill criteria belong on the roadmap.** For Later items, define what would trigger removal.
- **Outcome check before any update.** The Review Protocol gate is non-negotiable — rotating items without measuring impact is the second most common roadmap failure mode after feature factory.
