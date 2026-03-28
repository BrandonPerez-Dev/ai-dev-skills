---
name: research
description: >-
  Systematic investigation — codebase exploration, documentation, web research,
  consumer/enthusiast deep dives, product comparisons, local recommendations.
  Use before design decisions, when entering unfamiliar code, when multiple
  approaches exist, when you need evidence to support a recommendation, when
  researching products, hobbies, or services ("what's the best X", "recommend
  a Y", "find Z near me"), or any domain where real-world experience matters
  more than marketing copy. Auto-detects technical vs consumer research
  strategies. Produces triangulated findings from multiple sources.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Task
  - mcp__playwright__browser_navigate
  - mcp__playwright__browser_snapshot
  - mcp__playwright__browser_click
  - mcp__playwright__browser_evaluate
  - mcp__searxng__searxng_web_search
  - mcp__searxng__web_url_read
  # NOTE: mcp-searxng exposes one search tool (searxng_web_search) covering all categories,
  # plus web_url_read for fetching page content. No separate image/news/video tools.
---

# Research

Investigate before you act. Form hypotheses and test them — don't passively read.

<HARD-GATE>
Do NOT use the same search strategy for every question. Different domains have different signal sources. Identify WHERE the best information lives BEFORE searching. A broad web search for an enthusiast topic returns SEO noise. A forum deep-dive for an API question wastes time. Match the search strategy to the domain.
</HARD-GATE>

## Core Principles

These apply to ALL research, regardless of domain:

**Active over passive.** Form a specific question, hypothesize an answer, then seek evidence. Don't wander.

**Triangulate.** Never conclude from a single source. Findings supported by multiple independent sources get high confidence. Contradictions between sources get flagged — they're often more interesting than agreements.

**Seek disconfirmation.** Actively look for evidence that contradicts your initial hypothesis. First impressions anchor you — fight it. If a pattern looks like the obvious answer, search for cases where it doesn't apply.

**Negative evidence matters.** A search that returns zero results is informative. Missing tests, missing docs, missing forum discussion — absence tells you something about the domain's assumptions and blind spots.

**Iterate depth.** Research is not one pass. Round 1 reveals what you don't know. Use those gaps to form sharper questions for round 2. Each round should go deeper on fewer threads.

## Scoping the Investigation

Size the effort to the question:

| Type | When | Depth | Example |
|------|------|-------|---------|
| **Quick lookup** | Known question, likely one source | Single search or file read | "What's the API for library X?" |
| **Exploration** | Understand a system or topic | Multi-source, 1 round | "How does auth work in this app?" |
| **Deep investigation** | Decision with trade-offs | Multi-source, 2-3 rounds | "Should we use SSE or WebSockets?" |
| **Comprehensive review** | New domain, high-stakes decision | Multi-source, iterative rounds | "What espresso setup should I invest in?" |

Default to **exploration**. Escalate when you find contradictions, multiple valid approaches, or surprising complexity.

## Process

### 1. Frame the Question

State what you need to learn in one sentence. If you can't, the scope is too broad — break it into sub-questions.

For each question, note:
- What you already know or suspect (your hypothesis)
- What sources are likely to have the answer
- What a useful answer looks like (so you know when to stop)

### 2. Detect the Domain

**Before searching**, classify the question and load the right strategy:

| Signal | Domain | Strategy |
|--------|--------|----------|
| Involves code, APIs, libraries, architecture, debugging, system design | **Technical** | See [references/technical-research.md](references/technical-research.md) |
| Involves products, hobbies, recommendations, reviews, services, consumer decisions | **Consumer / Enthusiast** | See [references/consumer-research.md](references/consumer-research.md) |
| Involves academic papers, scientific evidence, clinical data | **Academic** | *(Future: references/academic-research.md)* — For now, prefer Google Scholar, PubMed, institutional sources over blogs |
| Involves market sizing, competitive landscape, industry trends | **Market** | *(Future: references/market-research.md)* — For now, use the market-analysis skill |
| Mixed or unclear | **Start with the dominant signal** | If a question spans domains (e.g., "best database for my use case"), lead with the domain that has more unknowns |

**Auto-detection heuristic:**
1. Does the answer require reading source code, API docs, or system internals? → **Technical**
2. Could the answer come from someone's personal experience, daily usage, or community consensus? → **Consumer/Enthusiast**
3. Both apply? → Lead with whichever domain has more unknowns.

**You MUST read the appropriate reference file before proceeding to the Diverge phase.** The reference file contains the search strategy — without it, you'll default to generic web search, which is the failure mode this skill exists to prevent.

### 3. Diverge — Explore Broadly

Launch parallel investigations using the domain-specific strategy loaded from the reference file. Don't explore sequentially when you can explore simultaneously.

The reference file tells you:
- **Where to search** (which sources have the best signal for this domain)
- **How to search** (what query patterns work, what to avoid)
- **How to weight sources** (what counts as credible in this domain)

### 4. Deepen — Follow-Up Rounds

After the first pass, assess what you've learned vs what's still unclear:

- **Sharpen questions.** Round 1 answers should produce better questions for round 2. "How does X work?" becomes "Why does X use pattern Y instead of Z?"
- **Fill gaps.** If one source type was thin (e.g., no forum results), compensate with another (e.g., manufacturer specs, expert blogs).
- **Resolve contradictions.** If sources disagree, investigate the context behind each. Often both are right in different situations.
- **Go deeper on fewer threads.** Each round should narrow scope and increase depth.

Skip this step for quick lookups. For deep investigations, expect 2-3 rounds.

### 5. Converge — Evaluate and Triangulate

Compare findings across sources with attention to source quality:

- **Convergent findings** (multiple sources agree) → high confidence, note as established
- **Divergent findings** (sources contradict) → investigate the contradiction, don't dismiss either side. Often reveals context-dependent trade-offs.
- **Single-source findings** → flag as unverified, note the source

Source credibility weighting is **domain-specific** — see the reference file for what counts as authoritative in each domain.

### 6. Synthesize and Present

Compile into a structured summary. Every finding gets a source reference. Lead with the answer. The user needs conclusions with evidence, not a narration of your search process.

## Output Format

```markdown
## Answer
[Direct answer to the research question — 1-3 sentences]

## Key Findings
1. **Finding** — Evidence with source reference. [Confidence: high/medium/low]
2. **Finding** — Evidence from multiple sources

## How It Works / How It Compares
[Architecture/data flow for technical. Comparison matrix for consumer. Whatever structure fits.]

## Sources
- `path/to/file.ts` — or [Forum Thread Title](url)
- List all sources that informed findings

## Contradictions & Surprises
[Anything that conflicted between sources, or deviated from expectations]

## Open Questions
[What's still unclear. What would need a deeper investigation.]
```

## Parallel Exploration Patterns

For any domain, launch multiple agents targeting different facets simultaneously:

**Technical:**
```
Agent 1: Structure — Glob + Read entry points, config
Agent 2: API surface — Grep for routes, exports, interfaces
Agent 3: Documentation — Read docs/, README, specs
Agent 4: External context — Web search for library patterns
```

**Consumer/Enthusiast:**
```
Agent 1: Forum deep-dive — search specialist communities
Agent 2: Reddit communities — search relevant subreddits
Agent 3: Manufacturer/official — product specs, official sites
Agent 4: Broad web — fill gaps, find niche blogs and reviewers
```

Wait for all agents, then synthesize across their findings. Contradictions between agents are valuable.

## Bias Guards

| Trap | Antidote |
|------|----------|
| **Confirmation bias** — only finding evidence that supports your hypothesis | Explicitly search for counterexamples |
| **Anchoring** — over-weighting the first thing you found | Check at least 2-3 sources before concluding |
| **Cargo cult** — "they do it this way so it must be right" | Ask WHY the pattern exists. Check if the context still applies |
| **Availability bias** — favoring the familiar solution | Search for alternatives you haven't used before |
| **Premature convergence** — jumping to a conclusion before exploring enough | Ensure you've done the divergent phase before narrowing |
| **SEO trust** — treating top search results as authoritative | Top results are optimized for ranking, not accuracy. Specialist sources beat SEO content. |
| **Wrong domain strategy** — using broad web search for everything | Re-check domain detection. Are you searching where the experts actually discuss this? |

## Stopping Criteria

Stop researching when:
- The original question has a clear, evidence-backed answer
- Key findings are triangulated from 2+ independent sources
- Contradictions have been investigated (not just noted)
- Follow-up rounds are returning diminishing new information
- You can articulate what's known, what's uncertain, and what's unknown

Don't stop just because you found *an* answer. Stop because you found *the right* answer with evidence.

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **Domain detection is step zero.** Before any search, know where the signal lives. A broad web search for an enthusiast topic returns SEO noise. A forum deep-dive for an API question wastes time. Read the reference file for your domain before any search query.
- **Start broad, narrow fast.** But "broad" means different things in different domains — for technical, it means Glob/Grep the codebase; for consumer, it means identify specialist communities.
- **Always include source references.** Every finding links to evidence.
- **Flag uncertainty.** Ambiguous? Say so. Don't guess.
- **Be concise.** Conclusions, not process narration.
- **Parallelize aggressively.** Independent questions = parallel agents.
