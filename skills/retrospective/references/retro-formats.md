# Retrospective Format Templates

Detailed templates for each retro format. The main skill selects the format — this file provides the facilitation structure.

## Start/Stop/Continue

Best for: new teams, quick sessions, general-purpose.

```
START — What should we begin doing?
  ▸ [Item]

STOP — What should we stop doing?
  ▸ [Item]

CONTINUE — What's working and should keep going?
  ▸ [Item]
```

**Facilitation notes:**
- Start with "Continue" to set a positive tone
- "Stop" items often reveal the most actionable insights
- If "Stop" is empty, the team may not feel safe — check the safety score

## Starfish (Keep/More/Less/Stop/Start)

Best for: process refinement when Start/Stop/Continue feels too coarse.

```
KEEP DOING — Working well, don't change
  ▸ [Item]

MORE OF — Good but we need to do it more consistently
  ▸ [Item]

LESS OF — Not bad, but we're overdoing it
  ▸ [Item]

STOP DOING — Not helping, actively harmful
  ▸ [Item]

START DOING — New practice we should adopt
  ▸ [Item]
```

**Facilitation notes:**
- "More of" and "Less of" are the differentiators from SSC — they capture nuance
- Often reveals that a practice is good in moderation but harmful at scale

## Mad/Sad/Glad

Best for: after a difficult sprint, incident, or emotional period.

```
MAD — What frustrated you this sprint?
  ▸ [Item]

SAD — What disappointed you?
  ▸ [Item]

GLAD — What made you happy?
  ▸ [Item]
```

**Facilitation notes:**
- Surfaces emotions before jumping to solutions
- Start with "Glad" — even hard sprints have bright spots
- "Mad" items need careful facilitation — redirect anger at people toward anger at systems
- Particularly useful when the team is visibly frustrated but hasn't articulated why

## 4Ls (Liked/Learned/Lacked/Longed For)

Best for: milestone retros, release boundaries, end-of-project reflections.

```
LIKED — What went well that we want to preserve?
  ▸ [Item]

LEARNED — What did we discover — about the product, tech, or ourselves?
  ▸ [Item]

LACKED — What was missing that would have helped?
  ▸ [Item]

LONGED FOR — What do we wish we had?
  ▸ [Item]
```

**Facilitation notes:**
- "Learned" captures growth — most formats miss this entirely
- "Lacked" vs "Longed For": Lacked = concrete gap; Longed For = aspirational improvement
- Strong format for teams transitioning between phases or wrapping up major work

## Sailboat

Best for: teams stuck in repetitive complaints, visual thinkers.

```
WIND (propelling us forward) — What's helping us move fast?
  ▸ [Item]

ANCHOR (holding us back) — What's slowing us down?
  ▸ [Item]

ROCKS (risks ahead) — What could sink us if we don't address it?
  ▸ [Item]

ISLAND (our goal) — Where are we trying to get to?
  ▸ [Item]
```

**Facilitation notes:**
- Draw the actual sailboat — visual metaphors break stuck patterns
- "Rocks" introduces forward-looking risk, which most retro formats lack
- Works well when teams keep listing the same anchors — "we've said this for 3 sprints, what's different now?"

## Futurespective / Pre-mortem

Best for: forward-looking sessions, new projects, major pivots.

```
IT'S [DATE 6 MONTHS FROM NOW] AND THE PROJECT SUCCEEDED:
  What did we do right?
  ▸ [Item]

IT'S [DATE 6 MONTHS FROM NOW] AND THE PROJECT FAILED:
  What went wrong?
  ▸ [Item]

WHAT SHOULD WE DO NOW TO PREVENT FAILURE / ENSURE SUCCESS?
  ▸ [Item]
```

**Facilitation notes:**
- Pre-mortem is Gary Klein's technique — imagining failure surfaces risks that optimism hides
- "Prospective hindsight" increases the ability to identify reasons for future outcomes by 30%
- Don't let "what we did right" dominate — the value is in the failure scenario

## Blameless Postmortem

Best for: after incidents, outages, or significant production issues.

```
INCIDENT SUMMARY:
  What happened: [Brief factual description]
  Impact: [Who was affected, for how long]
  Timeline: [Key events with timestamps]

CONTRIBUTING FACTORS (not "root cause" — incidents are multi-causal):
  1. [Factor] — [How it contributed]
  2. [Factor] — [How it contributed]

WHAT WENT WELL IN THE RESPONSE:
  ▸ [Item]

WHAT COULD HAVE GONE BETTER:
  ▸ [Item]

ACTION ITEMS:
  ▸ [Preventive action] — Owner: [Name] — Deadline: [Date]
  ▸ [Detective action — how we'll catch this sooner] — Owner: [Name]
```

**Facilitation notes:**
- "Contributing factors" not "root cause" — incidents rarely have a single cause
- Blameless means analyzing decisions in context: "given what they knew at the time, this was reasonable"
- Focus on system fixes: "how do we make it harder for this to happen?" not "who let this happen?"
- Include "what went well" — incident response often has heroes worth recognizing

## Spotify Health Check

Best for: quarterly team health assessment, new teams establishing baselines.

Rate each dimension green/yellow/red with trend arrows:

| Dimension | Rating | Trend | Notes |
|---|---|---|---|
| **Delivering value** | G/Y/R | Up/Down/Flat | Are we shipping things customers care about? |
| **Easy to release** | G/Y/R | Up/Down/Flat | Is our deployment process smooth? |
| **Health of codebase** | G/Y/R | Up/Down/Flat | Is the code clean and maintainable? |
| **Teamwork** | G/Y/R | Up/Down/Flat | Do we work well together? |
| **Fun** | G/Y/R | Up/Down/Flat | Do we enjoy coming to work? |
| **Learning** | G/Y/R | Up/Down/Flat | Are we getting better? |
| **Mission** | G/Y/R | Up/Down/Flat | Do we know WHY we're doing this? |
| **Pawns or players** | G/Y/R | Up/Down/Flat | Do we have control over what we build and how? |
| **Speed** | G/Y/R | Up/Down/Flat | Can we move fast when we need to? |
| **Suitable process** | G/Y/R | Up/Down/Flat | Does our process help or hinder? |
| **Support** | G/Y/R | Up/Down/Flat | Do we get the help we need? |

**Facilitation notes:**
- Each person rates independently, then discuss the spread — disagreement IS the insight
- Trends matter more than absolute ratings — a yellow trending up is better than a green trending down
- Compare across quarters to track improvement
- Don't try to fix everything — pick 1-2 red/yellow dimensions as focus areas
