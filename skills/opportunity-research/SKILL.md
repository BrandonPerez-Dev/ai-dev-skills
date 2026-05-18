
---
name: opportunity-research
description: Evaluate a new opportunity from any starting point — customer problem, technical capability, or market signal. Produces a decision brief with GO/YELLOW/RED recommendation. Use when exploring whether an idea is worth pursuing.
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
argument-hint: "[opportunity description or topic]"
---

# Opportunity Research

Evaluate whether an opportunity is worth pursuing. Produces a decision brief with an opinion, not a report.

<HARD-GATE>
Do NOT produce a neutral "further research needed" conclusion. Every brief MUST have a GO/YELLOW/RED verdict with a named riskiest assumption and a specific next move.
</HARD-GATE>

## When to Use

- Someone says "what about X?" and you need to figure out if it's real
- You discover a new AI capability and want to find who it helps
- You see a market trend, competitor move, or customer signal worth investigating
- You need to prepare an opportunity assessment for your PM or leadership

## Entry Points

This skill handles three starting situations:

**From a customer problem:** "Contractors are spending 2 hours a day on manual scheduling"
→ Research whether this problem is widespread, sizeable, and solvable

**From a technical capability:** "AI can now do real-time route optimization with 95% accuracy"
→ Find who has a problem this solves, validate the problem exists

**From a market signal:** "ServiceTitan just raised $500M" or "EV fleet adoption is at 25%"
→ Figure out what the underlying opportunity is and whether we can play

## Process

### Step 1: Understand the Starting Point

Ask the user what they're exploring. Determine which entry point they're coming from. Ask concise clarifying questions — one at a time:

- What's the opportunity in one sentence?
- Where did this idea come from? (customer interview, tech trend, competitor, article, hunch?)
- Who do you think benefits? (specific segment, or still figuring that out?)
- Any initial sense of how this connects to what WEX does? (customer access, data, integrations, or potentially standalone?)

If the user already provided context in $ARGUMENTS, don't re-ask what they've already answered.

### Step 2: Research the Landscape

Run web research in parallel across these dimensions. Use the Task tool to parallelize:

**Market research:**
- Industry size and growth trends
- Key players and recent funding/M&A activity
- Adoption signals (are people already buying solutions?)

**Competition:**
- Direct competitors (same solution, same customer)
- Indirect alternatives (how customers solve this today)
- White space (what nobody is doing well)

**Customer context:**
- Target segment size (how many potential customers?)
- Known pain points in this space
- Willingness to pay signals

**Technical feasibility (if starting from tech capability):**
- What's now possible that wasn't 12 months ago?
- Who else is building with this capability?
- How mature is the technology?

### Step 3: Check In — "Here's what I'm finding"

**CHECKPOINT: Do NOT skip this step.**

Present initial findings as a quick take — not a full report. Structure it as:

"Here's what I'm seeing so far:
- Market looks [bigger/smaller/different] than expected because [reason]
- Main competition is [X, Y, Z] — the gap seems to be [gap]
- [Surprising finding or contradiction]

Does this match your intuition, or should I adjust my focus?"

Wait for user input before proceeding. They may redirect you based on what they know that the web doesn't.

### Step 4: Assess the WEX Advantage

Evaluate honestly — don't force a connection where there isn't one.

**Trust & market access:**
- Does WEX have existing relationships with the target customer segment?
- Can we reach these customers with lower acquisition cost than a startup?
- Does the WEX brand add credibility for this use case?

**Integration proximity:**
- Can this plug into existing WEX systems (fleet, payments, benefits)?
- Does connecting to WEX data create a capability competitors can't easily replicate?
- Would this be a natural add-on to something customers already buy from WEX?

**Standalone case:**
- If WEX advantage is thin, is the opportunity compelling enough on its own?
- Could we build a moat through execution, data accumulation, or network effects?
- Be explicit: "WEX advantage is limited here. The case rests on [X]."

### Step 5: Identify the Riskiest Assumption

Every opportunity has a "if this isn't true, nothing else matters" assumption. Name it.

Common categories:
- **Desirability risk:** "Will customers actually pay to solve this?"
- **Feasibility risk:** "Can we actually build this with current technology?"
- **Viability risk:** "Can we make money at this price point?"
- **Adoption risk:** "Will users change their workflow to use this?"
- **Competitive risk:** "Will [incumbent] just add this feature?"

### Step 6: Check In — Draft Verdict

**CHECKPOINT: Do NOT skip this step.**

Present the draft decision brief to the user before finalizing:

"Here's where I'm landing:
- VERDICT: [GREEN/YELLOW/RED]
- Riskiest assumption: [specific]
- Next move: [specific action]

Does this feel right? Anything I'm missing or overweighting?"

### Step 7: Produce the Decision Brief

Write the final artifact. Two layers:

**Layer 1 — Decision Brief** (this is what people actually read):

```
OPPORTUNITY: [One-line description]

MARKET: [SAM estimate] | [growth rate] | [target customer count]
        [confidence: rough / directional / validated]

COMPETITION: [Who's here, what's the gap]

WEX EDGE: [Specific advantage, or "Limited — standalone case is X"]

VERDICT: [GREEN / YELLOW / RED]
         Riskiest assumption: [specific, testable statement]

NEXT MOVE: [Specific action with who/what/how-many]
           Success criteria: [What would upgrade or downgrade the verdict]
```

**Layer 2 — Evidence Locker** (reference material, structured for skimming):

- Market sizing (data sources, methodology, confidence ranges)
- Competitive landscape (table format: player, offering, pricing, gap)
- JTBD analysis (if starting from customer problem)
- Technical feasibility notes (if starting from tech capability)
- WEX advantage deep dive
- Risk assessment table (risk, likelihood, impact, mitigation)
- Sources cited

### Step 8: Save the Artifact

- Get today's date: !`date +%Y-%m-%d`
- Derive topic from the opportunity (e.g., "ai-job-costing" or "ev-fleet-analytics")
- Ensure directory: `mkdir -p docs/plans`
- Save to: `docs/plans/YYYY-MM-DD-<topic>-opportunity.md`

After saving, present the decision brief (Layer 1 only) and ask:

"Brief saved to [path]. Want to:
(a) Dig into any section of the evidence locker?
(b) Run market-analysis for detailed sizing?
(c) Run customer-discovery to validate with interviews?
(d) Move on to something else?"

## Verdict Criteria

**GREEN — Pursue aggressively:**
- Market is real and large enough
- WEX has clear advantage OR standalone case is compelling
- Riskiest assumption is testable within 2-4 weeks
- No obvious fatal risks

**YELLOW — Promising but unproven:**
- Market looks real but sizing is uncertain
- WEX advantage exists but isn't dominant
- Key assumptions need validation before committing resources
- Most opportunities start here

**RED — Hold or kill:**
- Market too small, too crowded, or too speculative
- No clear WEX advantage and standalone case is weak
- Fatal risks identified (regulatory, competitive, technical)
- Or: timing is wrong (revisit in 6-12 months)

## Guidelines

- **Have an opinion.** "Further research needed" is not a verdict. Pick a color and defend it.
- **Name the riskiest assumption.** If you can't name it, you haven't thought hard enough.
- **Be specific on next move.** "Do 5 interviews with HVAC contractors about X" not "validate with customers."
- **Don't inflate WEX advantage.** If the connection is thin, say so. A strong standalone idea beats a weak WEX-adjacent one.
- **Confidence ranges, not point estimates.** "$50-150M SAM" is honest. "$97.3M SAM" is false precision.
- **Check in at every checkpoint.** The user shapes the research direction — don't disappear for 10 minutes and return with a finished product.
