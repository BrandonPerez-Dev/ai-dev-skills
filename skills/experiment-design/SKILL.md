
---
name: experiment-design
description: Design experiments to test the riskiest assumptions behind an opportunity. Maps assumptions, formulates hypotheses, and creates experiment cards with pre-committed success criteria. Use when you need to validate before building.
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
argument-hint: "[opportunity topic or path to opportunity/market brief]"
---

# Experiment Design

Identify what could kill your opportunity, then design the cheapest possible test to find out.

<HARD-GATE>
Every experiment MUST have pre-committed success criteria defined BEFORE running the experiment. "See what happens" is not an experiment — it's a waste of time.
</HARD-GATE>

## When to Use

- You have an opportunity rated YELLOW and need to validate before investing
- You want to de-risk an opportunity before building an MVP
- Leadership is asking "what proof do you have that this will work?"
- You need to design a validation sprint (2-4 weeks of focused testing)
- You want to track evidence across multiple experiments over time

## Input Resolution

1. If $ARGUMENTS is a file path, read that brief as context
2. If $ARGUMENTS is a topic, search `docs/plans/` for matching `*-opportunity.md`, `*-market.md`, or `*-discovery.md`
3. If no arguments, ask what opportunity we're testing

## Process

### Step 1: Identify All Assumptions

Every opportunity rests on assumptions. Brainstorm them with the user across three categories:

**Desirability** — "Do they want it?"
- Is the problem real and painful enough?
- Will they pay to solve it?
- Will they change their behavior to use our solution?
- Will they choose us over alternatives?

**Viability** — "Can we make money?"
- Do unit economics work at our expected price?
- Can we acquire customers cheaply enough?
- Will customers retain long enough?
- Is the revenue model sustainable?

**Feasibility** — "Can we build it?"
- Is the technology proven enough?
- Can we integrate with required systems?
- Do we have the team/skills?
- Are there regulatory blockers?

Guide the user: "Let's brainstorm every assumption that must be true for this to work. Don't filter yet — we'll prioritize after."

Aim for 10-20 assumptions.

### Step 2: Map Assumptions by Risk

Plot each assumption on two axes:

**Importance:** If this is wrong, does it kill the opportunity?
**Knowledge:** Do we know this is true, or are we guessing?

```
              IMPORTANT
                 ↑
    KNOWN +      │      + UNKNOWN
    IMPORTANT    │      IMPORTANT
    (Confirm)    │      (TEST FIRST)
                 │
   ─────────────────────────────→ UNKNOWN
                 │
    KNOWN +      │      + UNKNOWN
    UNIMPORTANT  │      UNIMPORTANT
    (Ignore)     │      (Explore later)
                 │
```

**"Leap of faith" assumptions** = top-right quadrant = test first.

### Step 3: Check In — "Here are your riskiest assumptions"

**CHECKPOINT: Do NOT skip this step.**

"Based on what we've discussed, the riskiest assumptions are:
1. [Assumption] — if wrong, [consequence]
2. [Assumption] — if wrong, [consequence]
3. [Assumption] — if wrong, [consequence]

These are the ones I'd test first. Do you agree, or do you see a different risk hierarchy?"

### Step 4: Write Hypotheses

For each risky assumption, write a testable hypothesis:

**Format:**
```
If we [action/intervention]
for [specific customer segment],
then [measurable outcome]
because [underlying logic].
```

**Quality checklist:**
- [ ] Falsifiable — could be proven wrong
- [ ] Specific — names exact customer and outcome
- [ ] Measurable — outcome is observable
- [ ] Time-bounded — includes timeframe

**Example:**
```
If we show HVAC contractors (5-15 techs) an AI-generated dispatch plan,
then 60%+ will follow the AI recommendation without manual overrides
because it visibly reduces their morning planning from 2 hours to 15 minutes.
```

### Step 5: Design Experiments

Match experiment type to assumption type:

| Assumption Type | Cheapest Test | Medium Test | Expensive Test |
|-----------------|---------------|-------------|----------------|
| "Is the problem real?" | 5 customer interviews | Survey (50+) | Usage data analysis |
| "Will they pay?" | Pricing question in interviews | Landing page with pricing | Smoke test (real payment) |
| "Will they use it?" | Prototype walkthrough | Wizard of Oz (manual backend) | Beta with 5-10 users |
| "Can we build it?" | Architecture review | Technical spike (1 week) | POC (2-4 weeks) |
| "Can we acquire them?" | 100 cold emails | Paid ads ($500 budget) | Sales pilot (1 month) |

**Always start with the cheapest test that gives clear signal.**

For each experiment, create an experiment card:

```
EXPERIMENT: [Name]

ASSUMPTION: [What we're testing]
HYPOTHESIS: [If/then/because statement]

TYPE: [Interview / Survey / Landing page / Prototype / Wizard of Oz / Spike / Pilot]

DESIGN:
  Participants: [Who, how many, from where]
  Procedure: [Step by step, what happens]
  Duration: [How long]
  Cost: [Budget needed]

SUCCESS CRITERIA (pre-committed):
  ✓ STRONG SIGNAL: [Specific threshold that means GO]
  ⚠ MIXED SIGNAL: [Range that means ITERATE]
  ✗ WEAK SIGNAL: [Threshold that means PIVOT or KILL]

METRICS:
  Primary: [One key metric]
  Secondary: [Supporting metrics]

OWNER: [Who runs this]
TIMELINE: [Start → End → Decision date]
```

### Step 6: Prioritize the Experiment Backlog

Rank experiments by: **Risk reduction × Speed**

Best experiments are fast AND address high-risk assumptions. Deprioritize slow experiments that test low-risk assumptions.

```
PRIORITY | EXPERIMENT              | ASSUMPTION RISK | SPEED  | COST
P0       | 5 discovery interviews  | HIGH            | 2 wks  | $500
P0       | Pricing survey          | HIGH            | 1 wk   | $200
P1       | Wizard of Oz pilot      | MEDIUM          | 4 wks  | $5K
P1       | Technical spike         | MEDIUM          | 1 wk   | $0
P2       | Paid acquisition test   | MEDIUM          | 4 wks  | $2K
P3       | Full beta pilot         | LOW (premature) | 8 wks  | $15K
```

### Step 7: Set Up Evidence Tracking

Create a running evidence log that persists across experiments:

```
EVIDENCE LOG: [Opportunity Name]

ASSUMPTION          | EVIDENCE           | QUALITY    | STATUS
"Problem is real"   | 8/10 interviews    | Pattern    | VALIDATED ✓
                    | confirmed pain     |            |
"Will pay $400/mo"  | 6/8 said "yes"     | Anecdote   | NEEDS MORE DATA
                    | (self-reported)    |            |
"Can integrate w/   | API docs reviewed, | Anecdote   | NEEDS SPIKE
 Jobber"            | no blockers found  |            |
"CAC < $2K"         | No data yet        | None       | UNTESTED
```

**Evidence quality levels (consistent across all innovation skills):**
- Level 0 — No evidence
- Level 1 — Anecdote (1-2 data points)
- Level 2 — Pattern (4-7 data points, 40%+ consistency)
- Level 3 — Validated (8+ data points, 60%+ consistency, quantified)

### Step 8: Define Kill Criteria

Pre-agree on what would cause you to STOP pursuing this opportunity. This is hard but essential.

```
KILL CRITERIA (pre-agreed):
- If fewer than 30% of interviewees see this as a real problem → KILL
- If willingness to pay is below $200/mo across segments → KILL
- If technical spike reveals >6 engineer-months needed → PIVOT to simpler version
- If competitive response eliminates our differentiation → KILL
```

### Step 9: Produce the Experiment Package

**Layer 1 — Experiment Brief:**

```
OPPORTUNITY: [Name]

RISKIEST ASSUMPTIONS:
1. [Assumption] — [current evidence level]
2. [Assumption] — [current evidence level]
3. [Assumption] — [current evidence level]

EXPERIMENT PLAN:
  Sprint 1 (weeks 1-2): [What we test]
  Sprint 2 (weeks 3-4): [What we test next, depends on Sprint 1]

TOTAL COST: $[X] | DURATION: [Y] weeks
KILL CRITERIA: [Top 2 that would stop us]

DECISION POINT: [Date] — review evidence, decide GO/PIVOT/KILL
```

**Layer 2 — Full Package:**

- Complete assumption map (all assumptions, categorized, prioritized)
- Individual experiment cards (one per experiment)
- Prioritized experiment backlog
- Evidence log template
- Kill criteria with thresholds
- Decision framework (what evidence triggers what decision)

### Step 10: Save the Artifact

- Get today's date: !`date +%Y-%m-%d`
- Derive topic from opportunity
- Save to: `docs/plans/YYYY-MM-DD-<topic>-experiments.md`

After saving, present Layer 1 and ask:

"Experiment package saved to [path]. Want to:
(a) Refine any experiment card?
(b) Adjust the prioritization?
(c) Run customer-discovery to execute the interview experiments?
(d) Move on?"

## Guidelines

- **Test the assumption that could kill you first.** Not the one that's easiest to test.
- **Pre-commit success criteria.** Deciding after you see the data is called "confirmation bias."
- **Cheapest test wins.** 5 interviews beats a 3-month beta for testing desirability.
- **One assumption per experiment.** Testing 3 things at once means learning nothing clearly.
- **Kill criteria are mandatory.** If you can't define what would make you stop, you're not being honest about risks.
- **Evidence accumulates.** Update the evidence log after every experiment. Confidence builds over time.
