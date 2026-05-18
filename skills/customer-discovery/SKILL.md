
---
name: customer-discovery
description: Synthesize customer research — interview transcripts, surveys, support tickets — into structured insights using JTBD, empathy mapping, and opportunity solution trees. Use when you have customer data to analyze or need to prepare for interviews.
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
argument-hint: "[path to transcript/data or research topic]"
---

# Customer Discovery

Turn raw customer data into structured, evidence-based insights. Extracts jobs-to-be-done, pain points, and gains — then identifies what you still don't know.

<HARD-GATE>
Every insight MUST cite its source (interview #, survey response, ticket ID). No unsourced claims. Confidence levels are required — don't present anecdotes as patterns.
</HARD-GATE>

## When to Use

- You have interview transcripts (from Gemini, manual notes, recordings) to analyze
- You have survey responses, support tickets, or feedback to synthesize
- You need to identify patterns across multiple customer conversations
- You want to generate an interview guide for upcoming discovery interviews
- You need to build customer personas or journey maps from research data

## Modes

**Synthesis mode** — "Here are 5 interview transcripts, what did we learn?"
→ Analyze data, extract themes, produce discovery synthesis

**Prep mode** — "We're interviewing contractors about dispatching next week"
→ Generate interview guide based on what we know and what we need to learn

**Gap analysis mode** — "What don't we know yet?"
→ Review existing research, identify blind spots, recommend next research

## Process

### Step 1: Understand What We're Working With

Ask the user:

- What data do you have? (transcripts, surveys, tickets, notes, or nothing yet?)
- What research question are we trying to answer?
- How many data points? (this determines confidence expectations)
- What customer segment? (trade, size, geography, business model?)

If the user provides file paths or data in $ARGUMENTS, read and assess before asking questions. Don't ask what you can infer.

**Confidence expectations by sample size:**
- 1-3 interviews: Anecdotes only. Flag everything as low confidence.
- 4-7 interviews: Patterns may emerge. Medium confidence if consistent.
- 8-15 interviews: Patterns are reliable. High confidence if 60%+ consistency.
- 15+: Strong signal. Can segment by sub-groups.

### Step 2: Process the Data

For each data source, extract:

**Jobs to Be Done (JTBD):**
- Functional jobs: What task are they trying to accomplish?
- Emotional jobs: How do they want to feel?
- Social jobs: How do they want to be perceived?
- Format: "When [situation], I want to [action], so I can [outcome]"

**Pains:**
- What obstacles do they face?
- What frustrates them about current solutions?
- What are they afraid of?
- Rate intensity: how much does this pain cost them? (time, money, stress)

**Gains:**
- What outcomes do they desire beyond solving the problem?
- What would delight them?
- What would make them switch from their current solution?

**Direct quotes:**
- Pull the most vivid, specific quotes that illustrate each finding
- Tag with source (e.g., "Interview #3, HVAC owner, 8 techs, Atlanta")

**Behavioral observations:**
- What do they actually DO vs what they SAY they do?
- What workarounds have they built?
- Where do they spend time/money that suggests unmet needs?

### Step 3: Check In — "Here's what's emerging"

**CHECKPOINT: Do NOT skip this step.**

Present initial themes before doing full analysis:

"From the [N] data points, here's what's jumping out:
- Theme 1: [pain/job] — mentioned by X/N (frequency)
- Theme 2: [pain/job] — mentioned by X/N
- Surprise: [something unexpected]
- Contradiction: [where data points disagree]

Does this match what you heard in the interviews? Anything I should weight differently?"

Wait for user direction. They were in the room — they have context you don't.

### Step 4: Cluster and Score

Group findings into themes with evidence scoring:

```
THEME: [Name]
├─ Frequency: X/N interviews (XX%)
├─ Intensity: HIGH/MEDIUM/LOW
├─ Confidence: HIGH/MEDIUM/LOW (based on sample size + consistency)
├─ Segments affected: [which customer types]
├─ Key quotes:
│  ├─ "[Quote 1]" — Source
│  └─ "[Quote 2]" — Source
└─ Revenue/cost impact: [quantified if possible]
```

**Scoring rules:**
- Frequency alone isn't enough — one passionate pain point beats five mild mentions
- Contradictions between interviews are flagged, not hidden
- Segment differences are called out (solo operators vs 20-person shops may have different pains)

### Step 5: Build the Opportunity Solution Tree

Connect findings to potential opportunities using Teresa Torres' OST framework:

```
DESIRED OUTCOME: [Business metric we want to improve]
├─ Opportunity 1: [Unmet need, scored by importance × satisfaction gap]
│  ├─ Potential solution A
│  ├─ Potential solution B
│  └─ Potential solution C
├─ Opportunity 2: [Unmet need]
│  ├─ Potential solution A
│  └─ Potential solution B
└─ Opportunity 3: [Unmet need]
   └─ Potential solution A
```

For each opportunity, calculate an opportunity score:
`Opportunity Score = Importance + (Importance - Current Satisfaction)`

Higher score = bigger gap between what matters and what exists.

### Step 6: Identify Gaps

What DON'T we know yet? This is often more valuable than what we do know.

**Common gaps to check for:**
- Pricing sensitivity (how much would they pay?)
- Decision-maker mapping (who approves the purchase?)
- Adoption barriers (what would prevent them from switching?)
- Segment variations (does this apply to all trades or just HVAC?)
- Competitive awareness (do they know about alternatives?)

### Step 7: Generate Interview Guide (if gaps exist)

For each identified gap, generate specific interview questions:

```
GAP: Pricing sensitivity
QUESTION: "If we could save you [specific benefit from research],
           what would that be worth to your business? Would $X/month
           be reasonable?"
WHY: We have strong problem validation but zero pricing data.
```

Structure the guide for a 45-60 minute conversation:
1. Context/rapport (5 min)
2. Current workflow deep-dive (15 min) — "Walk me through last Tuesday"
3. Pain exploration (10 min) — dig into specific themes from research
4. Gap-filling questions (10 min) — pricing, decision-making, adoption
5. Solution reaction (5 min) — only if appropriate, show concept/mockup
6. Wrap-up (5 min) — "What should I have asked you?"

### Step 8: Produce the Discovery Synthesis

**Layer 1 — Discovery Brief:**

```
RESEARCH QUESTION: [What we set out to learn]

DATA: [N] interviews | [segment description] | [date range]

TOP FINDINGS:
1. [Finding] — [frequency], [confidence level]
   "[Best quote]" — Source
2. [Finding] — [frequency], [confidence level]
   "[Best quote]" — Source
3. [Finding] — [frequency], [confidence level]

SURPRISE: [What we didn't expect]

CONFIDENCE: [Overall X/10] — [What drives the rating up/down]

GAPS: [Top 2-3 things we still don't know]

NEXT MOVE: [Specific: "5 more interviews focused on pricing"
           or "ready for market-analysis"]
```

**Layer 2 — Full Synthesis:**

- Complete JTBD framework (all jobs, pains, gains with evidence)
- Empathy map (Says/Thinks/Feels/Does quadrants)
- Opportunity Solution Tree
- Theme clusters with all quotes and sources
- Customer segment profiles / personas
- Interview guide for next round
- Evidence quality assessment per finding

### Step 9: Save the Artifact

- Get today's date: !`date +%Y-%m-%d`
- Derive topic from research question
- Save to: `docs/plans/YYYY-MM-DD-<topic>-discovery.md`

After saving, present Layer 1 and ask:

"Discovery synthesis saved to [path]. Want to:
(a) Dig into any theme or persona?
(b) See the generated interview guide for next round?
(c) Run opportunity-research on the top opportunity?
(d) Run market-analysis to size the opportunity?
(e) Move on?"

## Evidence Levels (Consistent Across All Innovation Skills)

| Level | Description | Based On |
|-------|-------------|----------|
| 0 — No evidence | Assumption only | Nothing |
| 1 — Anecdote | Single source mentioned it | 1-2 data points |
| 2 — Pattern | Multiple sources independently confirm | 4-7 data points, 40%+ consistency |
| 3 — Validated | Strong signal across segments | 8+ data points, 60%+ consistency, quantified impact |

## Guidelines

- **Cite everything.** Every finding traces back to a specific source.
- **Confidence levels are mandatory.** Don't present a single interview quote as a validated pattern.
- **Contradictions are gold.** When interviews disagree, dig in — the truth is usually more nuanced than either side.
- **Behavioral > stated preference.** What customers DO matters more than what they SAY they'd do.
- **Segment differences matter.** A 3-person shop and a 50-person shop may have completely different problems.
- **Check in before finalizing.** The user was in the room for interviews — they have context the transcript doesn't capture.
- **Always identify gaps.** The most valuable output is often "here's what we still need to learn."
