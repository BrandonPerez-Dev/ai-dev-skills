---
name: retrospective
description: Run sprint retrospectives, post-incident reviews, team health checks, and milestone reflections that produce real change. Use when you need to run a retro, sprint retrospective, project retrospective, what went well, what should we improve, team health check, post-mortem, after-action review, lessons learned, blameless review, futurespective, pre-mortem, or start/stop/continue. This skill improves PROCESS and TEAM dynamics — use systematic-debugging for technical root-cause analysis of a specific bug or outage, use metrics-review for product data analysis, use sprint-planning to add retro actions to the backlog.
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
argument-hint: "[sprint number, format preference, or 'health-check']"
---

# Retrospective

A retrospective that doesn't produce action items is an expensive venting session. The output is 1-2 SMART commitments with named owners — not a list of complaints.

<HARD-GATE>
Open every retro by reviewing previous action items FIRST. Teams that skip this complete only 40-50% of retro actions. The follow-through loop is the entire point. If no prior retro exists, acknowledge it and move on — but never skip this step when history exists.
</HARD-GATE>

<HARD-GATE>
No line managers or stakeholders unless the team explicitly invites them by consensus. Manager presence is the single most reliable predictor of psychological safety collapse. If a manager is present, confirm the team consented before proceeding.
</HARD-GATE>

## Method Selection

| Context | Format | Why |
|---|---|---|
| Regular sprint retro | Ceremony flow (Steps 1-10) | Full process with format selection |
| Difficult sprint / incident | Mad/Sad/Glad or blameless postmortem | Surfaces emotions before solutions |
| Milestone / release boundary | 4Ls (Liked/Learned/Lacked/Longed For) | Captures growth, not just process |
| New team / quick session | Start/Stop/Continue | Zero learning curve |
| Team health assessment | Spotify Health Check (quarterly) | Systematic assessment across dimensions |
| Forward-looking / new project | Futurespective / Pre-mortem | Surfaces risks optimism hides |
| Stuck in repetitive complaints | Sailboat | Visual metaphor breaks the pattern |
| Process refinement | Starfish (Keep/More/Less/Stop/Start) | More granular than Start/Stop/Continue |

For detailed format templates and facilitation notes, see `references/retro-formats.md`.

## Input Resolution

1. If `$ARGUMENTS` is a sprint number, search `docs/retros/` for the most recent retro to pull prior action items
2. If `$ARGUMENTS` is a format name, use that format directly
3. If `$ARGUMENTS` is `health-check`, use Spotify Health Check format
4. Search `docs/retros/` for prior retro files to establish the follow-through loop
5. If no prior retros exist, start fresh — but note the gap

## Process

### Step 1: Read the Prime Directive

Start every retro with Kerth's Prime Directive:

> "Regardless of what we discover, we understand and truly believe that everyone did the best job they could, given what they knew at the time, their skills and abilities, the resources available, and the situation at hand."

This is not a platitude — it redirects blame from individuals to systems.

### Step 2: Review Previous Action Items

**This step is non-negotiable when prior retros exist.**

Pull action items from the most recent retro artifact (`docs/retros/`):

```
PREVIOUS ACTION ITEMS:
  ▸ [Action] — Owner: [Name] — Status: Done / Not done / Dropped
    [If not done: Why? Blocked? Deprioritized? Forgotten?]
```

Track the completion rate. If <50% are completed across multiple retros, the team has an action-item accountability problem — that IS the retro topic.

### Step 3: Safety Check

Anonymous 1-5 rating: "How safe do you feel sharing honestly in this retro?"

| Average | Interpretation | Adapt |
|---|---|---|
| 4-5 | Safe — proceed normally | Standard format |
| 3-3.9 | Cautious — some holding back | Use anonymous input; avoid naming individuals |
| <3 | Unsafe — address directly | Switch to anonymous-only; consider why safety is low |

### Step 4: Select Format

Based on `$ARGUMENTS`, context, or user preference. Default to Start/Stop/Continue for new teams. See method selection table above and `references/retro-formats.md` for templates.

Confirm with user: "I'll run a [format] retro for Sprint [N]. Right context?"

### Step 5: Silent Brainstorming (5-8 min)

Everyone writes before anyone speaks. This prevents anchoring bias — whoever speaks first shapes what everyone else says.

Prompt the team with the selected format's categories and let them write independently.

### Step 6: Group and Dot-Vote

Cluster similar items into themes. Each person gets 3-5 votes on what matters most.

```
THEMES (ranked by votes):
  1. [Theme] — [N votes] — [Summary of clustered items]
  2. [Theme] — [N votes]
  3. [Theme] — [N votes]
```

### Step 7: Discuss Top 2-3 Themes (20 min)

Dig into root causes, not just symptoms. Use these redirects:

- **Blame to systems:** "What in our process allowed this?" not "Who did this?"
- **Symptoms to causes:** "Why did that happen? And why did that happen?" (5 Whys)
- **Vague to specific:** "Can you give a concrete example from this sprint?"

Round-robin for initial reactions — prevents quiet participants from staying silent.

**CHECKPOINT: Do NOT skip this step.**

"Here are the themes the team surfaced. What's the one thing we must change before next sprint?"

### Step 8: Define 1-2 SMART Action Items

Every action item must pass the SMART test:

```
ACTION ITEM:
  What: [Specific action — not "improve communication"]
  Measure: [How we'll know it's done]
  Owner: [Single named person — not "the team"]
  Deadline: [By when — typically end of next sprint]
  Tracking: [Where this lives — Jira ticket, Linear issue]
```

**Quality bar:**
- Weak: "improve communication"
- Strong: "frontend and backend leads hold 20-min sync every Tuesday for next 2 sprints"

**Maximum 2 items per retro.** Pick fewer, complete them. Five action items means zero completed.

### Step 9: Add to Sprint Backlog

The top action item goes into the next sprint backlog as a first-class item — not buried in retro notes nobody reads.

Flag: "Invoke **sprint-planning** to add this action to the next sprint backlog."

### Step 10: Save the Retro Artifact

```
SPRINT [N] RETROSPECTIVE — [Date]
Team: [Team name]
Format: [Selected format]
Facilitator: [Name]
Safety score: [Average]

PREVIOUS ACTION ITEMS:
  ▸ [Action] — [Status]

THEMES DISCUSSED:
  1. [Theme] — [Key insights]
  2. [Theme] — [Key insights]

ACTION ITEMS:
  ▸ [Action] — Owner: [Name] — Deadline: [Date] — Tracking: [Link]

PARTICIPANTS: [Names]
```

Save to: `docs/retros/YYYY-MM-DD-sprint-N-retro.md`

After saving, offer next steps:

"Retro saved to [path]. Want to:
(a) Invoke **sprint-planning** to add action items to the backlog?
(b) Invoke **backlog-refinement** if a process issue needs story-level changes?
(c) Run another format for deeper exploration of a theme?
(d) Move on?"

---

## Facilitation Timing Guide

| Section | Duration | Notes |
|---|---|---|
| Setup + Prime Directive | 5 min | Read the directive; set expectations |
| Previous actions review | 5 min | Non-negotiable |
| Safety check | 2 min | Anonymous; adapt if <3 |
| Silent brainstorming | 7 min | No talking — writing only |
| Grouping + voting | 5 min | Cluster, then dot-vote |
| Discussion | 20 min | Top 2-3 themes; root causes |
| Action items | 10 min | SMART; single owner; max 2 |
| Wrap-up | 5 min | Recap actions; confirm owners |
| **Total** | **~60 min** | |

---

## Optional Metrics to Bring In

Pull from recent metrics reviews or dashboards to ground the retro in data:

- Velocity trend (last 3-5 sprints)
- Cycle time trend
- Sprint goal completion rate
- Escaped defects
- **Retro action completion rate** (meta but critical)

---

## Bias Guards

| Thought | Reality | Do Instead |
|---|---|---|
| "We don't need a retro, the sprint went fine" | Good sprints need retros to understand and reinforce what made them good | Run it — "what worked well?" is just as valuable |
| "Let's just quickly list the problems" | Whoever speaks first anchors everyone else | Silent brainstorming first. Always. |
| "We'll fix that next sprint" | Is there a named owner and a specific action? If not, it won't happen. | SMART action item or it doesn't count |
| "The real problem is [other team/management]" | What can WE change within our control this sprint? | Redirect to circle of influence |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **No action items** | Venting without commitment | Hard minimum: 1 SMART action item per retro |
| **Groundhog Day** | Same complaints every retro, nothing changes | Review prior actions first; if they're not done, THAT is the topic |
| **Blame sessions** | Individuals named instead of systems | Prime Directive + redirect: "what in our process allowed this?" |
| **Manager presence killing honesty** | Safety collapse | Hard gate: consensus invitation only |
| **Skipping "good" retros** | Missing reinforcement of what works | Good sprints are data — what made them good? |
| **Boiling the ocean** | 15 action items, none completed | Max 2. Pick fewer, complete them. |
| **Outside circle of influence** | Discussing things the team can't control | Redirect: what can WE change this sprint? |
| **Same format, 40 sprints** | Format fatigue, declining engagement | Rotate formats; match format to context |

## Guidelines

- **Follow-through is the point.** A retro without action review is a suggestion box. The hard gate on reviewing previous actions exists because completion rates drop to 40-50% without it.
- **Silent brainstorming is non-negotiable.** Anchoring bias is the single most reliable way to make a retro useless. Writing before speaking is the fix.
- **1-2 actions, not 10.** Teams that commit to fewer actions complete more. This is counterintuitive and consistently true.
- **Systems, not people.** The Prime Directive is not decoration — it's the mechanism that makes honest discussion possible.
- **Safety scores below 3 are the retro topic.** Nothing else matters if people can't speak honestly.
- **Good sprints need retros too.** Reinforcing what worked is as valuable as fixing what didn't.

Follow the communication-protocol skill for all user-facing output and interaction.
