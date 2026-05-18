
---
name: product-definition
description: Bridge the gap between a validated business case and an engineering-ready product spec. Defines personas, user stories, user flows, feature prioritization, and MVP scope. Use when an opportunity is approved and needs to be scoped for engineering.
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
argument-hint: "[opportunity topic or path to business case]"
---

# Product Definition

Turn a validated opportunity into something engineering can build. Defines WHAT we're building, for WHOM, and what's in/out of MVP.

<HARD-GATE>
Do NOT design the technical solution — that's what write-spec and technical-breakdown are for. This skill defines the product from the customer's perspective: who uses it, what they do with it, and how we know it's working.
</HARD-GATE>

## When to Use

- An opportunity has been scored GO or CONDITIONAL GO and needs scoping
- You need to define MVP scope before engineering begins
- You want to bridge from business case to write-spec
- You need to clarify "what are we actually building?" for the team

## Input Resolution

1. Search `docs/plans/` for business case, discovery, and market artifacts
2. Read everything available — this skill synthesizes prior work into product scope
3. If no prior artifacts exist, flag: "No business case found. Consider running business-case first."

## Process

### Step 1: Restate the Problem and Customer

Pull from existing artifacts. Don't re-research — synthesize:

```
PROBLEM: [One sentence from business case]
TARGET CUSTOMER: [From discovery — segment, size, characteristics]
VALUE PROPOSITION: [What we're offering and why it's better than alternatives]
```

Confirm with user: "This is who we're building for and why. Still accurate?"

### Step 2: Define User Personas

For B2B, you typically need 2-3 personas:

**P1 — Primary User** (the person who uses it daily)
```
Name/archetype: [e.g., "Dispatch Manager Dana"]
Role: [Job title and responsibilities]
Goal: [What they're trying to accomplish]
Current pain: [Their biggest frustration today]
Success looks like: [How they'd measure value]
Tech comfort: [Low/Medium/High]
```

**P2 — Decision Maker** (the person who approves the purchase)
```
Name/archetype: [e.g., "Owner-Operator Oscar"]
Role: [Title]
Cares about: [ROI, risk, competitive advantage]
Objections: [What would make them say no]
```

**P3 — Affected User** (if different from P1)
```
Name/archetype: [e.g., "Technician Tom"]
Role: [End user in the field]
Impact: [How this changes their day]
Adoption risk: [Will they resist?]
```

### Step 3: Map User Stories

Using JTBD from customer discovery, translate into user stories:

**Format:** "As a [persona], I want to [action] so that [outcome]"

Group by importance:
- **Must Have** — Without these, the product has no value
- **Should Have** — Important but product works without them
- **Could Have** — Nice to have, include if time permits
- **Won't Have (this version)** — Explicitly excluded from MVP

For each Must Have, define acceptance criteria:
```
STORY: As a dispatch manager, I want to see all technicians on a map
       so that I can assign the nearest available tech to a new job.

ACCEPTANCE CRITERIA:
- [ ] Map shows real-time location of all active technicians
- [ ] Technician status visible (available, on-job, en-route)
- [ ] Can assign job to technician directly from map
- [ ] Assignment triggers notification to technician
```

### Step 4: Check In — "Here's the scope I'm seeing"

**CHECKPOINT: Do NOT skip this step.**

"For MVP, I'm seeing [X] Must Have stories, [Y] Should Have, [Z] Could Have.

The Must Haves are:
1. [Story] — because [why it's essential]
2. [Story]
3. [Story]

The biggest scoping question is: [specific trade-off or ambiguity]

Does this feel like the right MVP boundary?"

### Step 5: Define the Happy Path

Map the primary user flow — the ideal scenario from start to finish:

```
HAPPY PATH: [Primary use case name]

1. [User action] → [System response]
2. [User action] → [System response]
3. [User action] → [System response]
...
N. [Outcome achieved]
```

Identify key decision points and what happens at each.

**Edge cases to note** (not design, just identify):
- What if [X fails]?
- What if [data is missing]?
- What if [user doesn't have permission]?

These get handled in write-spec, not here. But naming them now prevents surprises later.

### Step 6: Feature Prioritization

Apply MoSCoW to all identified features:

```
MUST HAVE (MVP — launch blocked without these):
- [Feature] — [Why essential]
- [Feature] — [Why essential]

SHOULD HAVE (Fast follow — next sprint after launch):
- [Feature] — [Why important]

COULD HAVE (Future — if we have time/signal):
- [Feature] — [What would trigger building this]

WON'T HAVE (Explicitly out of scope):
- [Feature] — [Why excluded — prevents scope creep]
```

If applicable, use Kano classification:
- **Must-be:** Expected, absence = failure
- **Performance:** More = better, linear satisfaction
- **Delighter:** Unexpected, creates disproportionate satisfaction

### Step 7: Define Success Metrics

How will we know this product is working?

```
SUCCESS METRICS (measure within 90 days of launch):

PRIMARY: [One metric that defines success]
  Target: [Specific threshold]
  Measurement: [How we track it]

SECONDARY:
  - [Metric] — target: [X]
  - [Metric] — target: [X]
  - [Metric] — target: [X]

LEADING INDICATORS (early signals):
  - [Metric] — watch for: [X]

FAILURE SIGNALS (things that mean it's not working):
  - [Metric below X] → investigate
  - [Metric below Y] → consider pivot
```

### Step 8: Technical Constraints

Note constraints that engineering needs to know (without designing the solution):

- Integration requirements (what systems must this connect to?)
- Data requirements (what data does it need access to?)
- Performance requirements (response time, availability)
- Compliance/security requirements
- Platform constraints (web, mobile, API-only?)

### Step 9: Produce the Product Definition

**Layer 1 — Product Brief:**

```
PRODUCT: [Name]
FOR: [Target persona] who needs to [core job]
UNLIKE: [Current alternative] which [limitation]
OUR PRODUCT: [Key differentiator]

MVP SCOPE: [N] Must Have features | [Estimated complexity: S/M/L]

PRIMARY USER FLOW:
[3-5 step happy path summary]

SUCCESS METRIC: [Primary metric] — target: [threshold]

READY FOR: write-spec → technical-breakdown → build
```

**Layer 2 — Full Product Definition:**

- Problem restatement with customer evidence
- Persona profiles (2-3)
- Complete user story map (MoSCoW categorized)
- Acceptance criteria for all Must Have stories
- Happy path flow (detailed)
- Edge cases identified (for write-spec to handle)
- Feature prioritization rationale
- Success metrics framework
- Technical constraints
- Assumptions and risks
- Glossary of domain terms (if relevant)

### Step 10: Save and Hand Off

- Get today's date: !`date +%Y-%m-%d`
- Save to: `docs/plans/YYYY-MM-DD-<topic>-product-def.md`

After saving, present Layer 1 and ask:

"Product definition saved to [path]. This is ready for the engineering pipeline. Want to:
(a) Refine any persona or user story?
(b) Adjust MVP scope?
(c) Hand off to write-spec to start the engineering pipeline?
(d) Move on?"

If the user chooses (c), invoke: `Skill: write-spec` with `Args: <path-to-product-def>`

## Guidelines

- **Customer perspective, not technical.** "User sees a map of technicians" not "React component renders MapBox tiles."
- **MVP is the smallest thing that tests the value proposition.** Not the smallest thing you can build.
- **Won't Have is as important as Must Have.** Explicitly excluding features prevents scope creep.
- **One primary metric.** If you can't pick one, you don't understand what success looks like.
- **Edge cases are identified, not solved.** Name them for write-spec. Don't design solutions here.
- **Acceptance criteria are testable.** "Works well" is not a criterion. "Shows location within 30 seconds" is.
