---
name: startup-pitch
description: >-
  Create and refine startup pitch materials — elevator pitches, one-liners,
  positioning statements, cold email pitches, one-pagers, and full pitch decks.
  Builds from core narrative outward: nail the two-sentence pitch first, then
  expand into every format. Supports multiple deck frameworks (Kawasaki, Sequoia,
  YC, corporate innovation). Use when pitching a product to investors, preparing
  for demo day, explaining a startup in one sentence, writing a cold outreach
  email, creating an investor deck, building a one-pager, or pitching an internal
  initiative to executives.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Skill
  - mcp__searxng__searxng_web_search
  - mcp__searxng__web_url_read
argument-hint: "[product/company name or context]"
---

# Startup Pitch

Nail the core narrative before you touch a single slide.

Every pitch format — from a one-word tagline to a 20-slide deck — draws from the same underlying story. Get that story right first. Templates are scaffolding, not strategy.

<HARD-GATE>
Do NOT start with the pitch deck. Start with the 2-sentence pitch. If you can't explain the company in two clear sentences, no amount of slides will save you. The inside-out build order exists because clarity compounds — each shorter format forces sharper thinking that makes the longer formats better.
</HARD-GATE>

<HARD-GATE>
Do NOT fill in templates mechanically. Every blank in a template represents a strategic decision. Before writing content for any field, understand WHY that field exists and what it signals to the audience. April Dunford's critique: "Everyone uses the mad-libs template. Nobody knows how to fill in the blanks correctly."
</HARD-GATE>

## Method Selection

| Situation | Approach | Start At |
|-----------|----------|----------|
| New product, no pitches exist yet | Full inside-out build | Phase 1: Context Discovery |
| Have some pitches, need to improve | Audit existing → fill gaps | Phase 2: audit what exists first |
| Need one specific format (e.g., "write me a cold email") | Targeted format | Phase 3: jump to that format, but verify core narrative exists |
| Preparing for a specific meeting/event | Event-driven | Identify audience → pick format → build backward from what they need to hear |
| Internal/corporate innovation pitch | Corporate track | Phase 1 with corporate context, then Phase 3 with corporate-specific formats |

## Process

### Phase 1: Context Discovery

Before writing a single word of pitch content, build a complete picture of the business. Ask the user — don't assume or infer.

**Gather these inputs** (use `AskUserQuestion` to collect what's missing):

```
COMPANY/PRODUCT:
- What does it do? (in the user's own words)
- Who is the target customer? (specific persona, not "everyone")
- What problem does it solve? (from the customer's perspective)
- What exists today? (how do customers solve this without you?)

DIFFERENTIATION:
- What's the unique insight? (what do you know that competitors don't?)
- Why now? (what changed — technology, regulation, market — that makes this possible/necessary today?)
- What's the unfair advantage? (team background, data, partnerships, IP)

TRACTION & STAGE:
- What traction exists? (users, revenue, growth rate, pilots, LOIs)
- What stage? (idea, MVP, post-launch, scaling)
- What's the business model? (how do you make money?)

AUDIENCE & CONTEXT:
- Who are you pitching to? (VCs, internal execs, partners, customers)
- What's the context? (fundraise, internal incubator, demo day, cold outreach, conference)
- Is this external (startup/VC) or internal (corporate innovation)?
```

If the user has provided context in conversation or in memory, use it — but confirm assumptions before proceeding.

**CHECKPOINT — Confirm the narrative foundation:**

Present a summary back to the user:

> "Here's what I'm working with:
> - **Product:** [what it does]
> - **Customer:** [who]
> - **Problem:** [what pain]
> - **Why now:** [timing thesis]
> - **Traction:** [current proof points]
> - **Audience:** [who we're pitching to]
>
> Does this capture it, or should I adjust?"

Do NOT proceed until the user confirms. Everything downstream depends on this being right.

### Phase 2: Inside-Out Build

Build pitch formats from shortest to longest. Each format compresses thinking that makes the next format sharper. The order matters.

**Build Order:**

```
Layer 1 — Core Narrative (must get right first)
  ├── 2-Sentence Pitch (YC/Seibel)
  └── One-Liner (3 variants)

Layer 2 — Short-Form Pitches
  ├── Tagline / 10-Second Pitch
  ├── High Concept Pitch ("X for Y")
  ├── One-Word Pitch
  ├── Elevator Pitch (5-7 sentences)
  ├── Geoffrey Moore Positioning Statement
  └── Pixar Pitch (6-sentence story)

Layer 3 — Written Materials
  ├── Cold Email Pitch (150-200 words)
  └── One-Pager / Executive Summary

Layer 4 — Presentation Deck
  └── Full Pitch Deck (framework choice)
```

**For each format:**

1. **Explain the format** — what it is, when to use it, what makes it work (load from `references/pitch-formats.md` or `references/deck-frameworks.md`)
2. **Draft a version** — write a complete first draft based on Phase 1 context
3. **Present for feedback** — show the draft and ask for specific reactions
4. **Iterate** — refine based on feedback; propose alternatives where appropriate
5. **Save** — write the approved version to the pitch artifacts file

**Between each format, connect forward:**

> "Now that we've nailed the one-liner, let's expand into the elevator pitch. The one-liner becomes your opening sentence — now we add the problem, proof, and ask around it."

This makes the compounding effect visible to the user.

**CHECKPOINT — After Layer 1 (core narrative):**

> "We have the 2-sentence pitch and one-liner locked in. These are the foundation everything else builds on.
>
> Want to continue through all formats, or jump to a specific one?"

Let the user drive scope after the foundation is set.

### Phase 3: Format-Specific Drafting

When drafting each format, follow these principles:

**Clarity over cleverness.** Michael Seibel's test: "Make it sound dumber than you think it should." If a smart 10-year-old wouldn't understand it, rewrite it.

**Audience-aware language.** VC pitches emphasize market size, traction, and team. Corporate pitches emphasize strategic fit, ROI, and risk mitigation. Customer pitches emphasize pain relief and outcomes. Never use the same language for different audiences.

**Specificity beats abstraction.** "We reduced invoice processing from 3 hours to 12 minutes for 47 plumbing companies" beats "We leverage AI to optimize back-office workflows for SMBs."

**The backward-consistency test.** After drafting a longer format (elevator pitch, deck), trace it backward: Does the ask match the milestones? Do the milestones require the team you described? Does the team's history justify confidence? Every gap is a narrative inconsistency — fix it before polishing language.

**For pitch decks specifically:**

Let the user choose their framework. Present the options:

> "Which deck framework fits your situation?
> - **Guy Kawasaki 10/20/30** — classic VC format, 10 slides, emphasizes 'underlying magic'
> - **Sequoia** — 10 slides, distinctive 'Why Now?' slide, ends on vision
> - **YC Seed** — traction-forward, 6-8 slides, best for pre-seed/seed
> - **Corporate Innovation** — 15-18 slides, adds Strategic Fit + Research Results + Roadmap
> - **Custom** — I'll recommend a hybrid based on your situation"

Then guide them slide-by-slide. See `references/deck-frameworks.md` for the full structure of each framework.

**For corporate/internal pitches:**

Load `references/corporate-pitch.md` for the specific differences. Key points:
- Strategic Fit is the #1 slide — the internal equivalent of IRR
- Address "corporate antibodies" — middle managers who may block post-approval
- Include pilot plan and risk mitigation — execs approve low-risk experiments, not big bets
- Use the McKinney 5/5/30 layered approach — each layer is independent, not abbreviated

### Phase 4: Testing & Validation

After drafting, help the user stress-test their pitches:

**The 5-Second Test (clarity):** "If someone saw only your tagline/one-liner for 5 seconds, could they explain what you do?"

**The Stranger Test (jargon):** "Read this to someone outside your industry. Every place they stop to ask a question is jargon or assumed context."

**The Skeptic Test (logic):** "Give this to someone whose job is to find holes. Ask 'where don't you believe me?' — not 'is this good?'"

**The Backward Test (consistency):** Trace the deck from ask → projections → team → GTM → differentiation → problem. Every gap is a narrative inconsistency.

**The "Why Now?" Test:** "If your 'why now' slide says 'AI is trending' or 'market is growing,' it's too generic. What specifically changed in the last 12-24 months that makes this possible or necessary?"

**Anticipate objections:** For each pitch format, identify the 3 most likely objections the audience will raise and draft responses.

### Phase 5: Save & Hand Off

Save all pitch artifacts to a single file for easy reference and iteration:

```bash
# Get today's date
date +%Y-%m-%d
```

Save to: `docs/pitches/YYYY-MM-DD-<company-name>-pitch-materials.md`

**File structure:**

```markdown
# [Company Name] — Pitch Materials
Generated: YYYY-MM-DD

## Core Narrative
### 2-Sentence Pitch
[content]

### One-Liner
[content — all variants]

## Short-Form Pitches
### Tagline
### High Concept
### One-Word Pitch
### Elevator Pitch
### Positioning Statement (Moore)
### Pixar Pitch

## Written Materials
### Cold Email Template
### One-Pager Content

## Pitch Deck
### Framework: [chosen framework]
### Slide-by-slide content

## Testing Notes
### Objections & Responses
### Feedback received
```

**After saving, present options:**

> "Pitch materials saved to `[path]`. What's next?
> (a) Generate a presentation — invoke the `presentation` skill for an HTML deck or `pptx` for PowerPoint
> (b) Refine a specific format — iterate further on any section
> (c) Research competitors/market — deepen the positioning with competitive intelligence
> (d) Done for now"

## Narrative Arc Selection

Not all pitches tell the same story. Help the user choose their narrative arc early — it shapes every format from one-liner to deck.

| Arc | When to Use | Core Tension |
|-----|-------------|-------------|
| **The World Changes** | New technology or market shift creates the opportunity | "The world was fine, then X happened — here's who wins" |
| **The Disruptor** | Challenging entrenched incumbents | "The industry is broken and everyone accepts it — we don't" |
| **Personal Problem** | Founder lived the pain | "I experienced this, discovered it was universal, and built the fix" |
| **The Inevitable** | Macro trends converging | "Three forces are converging to make this inevitable — we're building the rails" |

The arc choice affects tone, sequencing, and which elements get emphasis. A "World Changes" pitch leads with the shift. A "Personal Problem" pitch leads with the founder's story.

## Bias Guards

| Trap | Reality | Do Instead |
|------|---------|------------|
| "Let me write all the pitches first, then show you" | User loses agency; assumptions compound | Draft one format at a time, get feedback, then proceed |
| "This template is the right one" | Different audiences need different formats | Ask about the audience before choosing a framework |
| "More detail = better pitch" | Pitches fail from too much information, not too little | Cut ruthlessly. If it doesn't earn its place, remove it |
| "The deck is the pitch" | The deck is a leave-behind; the conversation is the pitch | Focus on narrative clarity, not slide polish |
| "Generic 'why now' is fine" | 75% of decks fail the 'why now' test with vague market trends | Force a specific mechanism: what changed in the last 12-24 months? |
| "Same pitch for every audience" | VC ≠ corporate exec ≠ customer ≠ partner | Adapt language, emphasis, and structure for each audience |

## Anti-Patterns

| Anti-Pattern | What Happens | This Skill Prevents It By |
|--------------|-------------|--------------------------|
| Template stuffing | Fill blanks mechanically → generic, forgettable pitch | Building inside-out from core narrative; understanding WHY each field exists |
| Deck-first thinking | 20 slides before the founder can explain the company in 2 sentences | Hard gate: 2-sentence pitch before any slides |
| Jargon blindness | "AI-powered SaaS platform leveraging LLMs for workflow optimization" | Stranger test + Seibel's "make it sound dumber" rule |
| Kitchen sink | Every feature, metric, and vision crammed into one pitch | Format-specific constraints (80 chars for tagline, 2 sentences for YC, etc.) |
| Audience mismatch | VC-style pitch to internal execs who care about strategic fit, not TAM | Explicit audience detection in Phase 1; corporate-specific reference |
| One-and-done | Draft once, never iterate | Testing phase with structured validation methods |
| Narrative inconsistency | Ask doesn't match milestones; milestones don't match team | Backward-consistency test after every long-form draft |

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **Inside-out is non-negotiable.** The 2-sentence pitch forces clarity that no amount of slide design can substitute for. Start there every time.
- **One format at a time.** Draft, present, iterate, save. Then move to the next. Don't batch — compounding feedback is the mechanism.
- **The user's words matter.** When the user describes their product in Phase 1, listen to their natural language. Often their casual explanation is better than any template output.
- **Shorter is harder.** The tagline and one-liner take more iteration than the full deck. Budget time accordingly.
- **Corporate ≠ startup.** Internal innovation pitches have different failure modes (corporate antibodies, no executive sponsor, innovation theater). Don't apply VC frameworks to corporate contexts.
- **Test > polish.** A clear pitch with ugly slides beats a beautiful deck with a confusing narrative. Always prioritize narrative clarity over presentation design.
- **Save everything.** Every approved draft goes into the artifacts file. The user will iterate across sessions — make it easy to pick up where they left off.
