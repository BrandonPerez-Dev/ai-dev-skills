# Audience-Specific Roadmap Views

The same roadmap needs different presentations. Generate from the canonical Now/Next/Later source — never maintain separate roadmaps.

## Strategic View (Executives)

Focus: outcomes, themes, risks, resource needs. No implementation detail.

```
PRODUCT ROADMAP — [Product Name] — [Date]

VISION: [One sentence]
NORTH STAR: [Metric] — [current] → [target]

THEMES THIS [YEAR/HALF]:
  1. [Theme] — [Outcome target]
  2. [Theme] — [Outcome target]
  3. [Theme] — [Outcome target]

NOW: [2-4 initiatives, outcome-focused, no implementation detail]
NEXT: [3-6 initiatives, directional]
LATER: [Strategic bets]

KEY RISKS: [Top 2-3 risks to the plan]
RESOURCE ASK: [What's needed from leadership]
```

## Tactical View (PM + Engineering)

Focus: epics, dependencies, spec status, promotion criteria. This is what the team works from.

```
PRODUCT ROADMAP — [Product Name] — [Date]

NOW — [Quarter]
  [For each initiative:]
  ▸ [Name] — [Outcome] — [Size] — [Owner]
    Epics: [High-level breakdown]
    Dependencies: [Cross-team, infrastructure, external]
    Key decisions: [Open questions needing resolution]
    Spec status: [Not started / In progress / Approved]

NEXT — [Quarter range]
  [For each initiative:]
  ▸ [Name] — [Outcome hypothesis] — [Size estimate]
    Discovery needed: [What we need to learn]
    Promotion criteria: [What must be true to move to Now]

LATER
  [Initiatives with open questions]

TECH DEBT / INFRASTRUCTURE: [Items with standing allocation]
```

## External View (Customers / Sales)

Focus: capabilities and benefits in user language. No internal details, no dates, no sizes.

```
PRODUCT ROADMAP — [Product Name] — [Date]

COMING SOON:
  ▸ [Capability in user language] — [Benefit]

ON OUR RADAR:
  ▸ [Capability] — [Benefit]

EXPLORING:
  ▸ [Direction] — [What problem it addresses]

Note: Timelines are directional. Priorities may shift based on customer feedback.
```

## When to Use Each View

| Audience | View | Cadence | Channel |
|---|---|---|---|
| Board / C-suite | Strategic | Quarterly | Board deck, exec review |
| VP Engineering / PM Lead | Tactical | Monthly or per-sprint | Planning doc, wiki |
| Sales / CS team | External | Per-release or quarterly | Sales enablement brief |
| Customers / Prospects | External | Per-release | Product update email, changelog |
| Investors | Strategic (trimmed) | Quarterly | Investor update |
