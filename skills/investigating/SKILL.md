---
name: investigating
description: >-
  Systematic multi-source investigation producing triangulated, dated,
  source-cited findings. ALWAYS invoke before design decisions, when entering
  unfamiliar code, when comparing approaches or products, when the user asks
  "what's the best X", "is Y actually true/safe/ready", "how does Z work",
  or any question whose answer should be backed by evidence rather than
  recall. Do not answer research-shaped questions from memory or a single
  search.
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
effort: high
---

# Investigating

Investigate before you act. Form hypotheses and test them — don't passively read.

## The investigation header (write it before the first search)

Different domains keep their signal in different places: broad web search on an enthusiast topic returns SEO noise; a forum deep-dive on an API question wastes time. The header forces strategy selection to happen — and makes it visible — before any searching starts. Write it before your first search, and include it at the top of your final deliverable (the answer document or message), so the strategy choice is auditable; a header that exists only in scratch thinking doesn't count:

```
Question:   <one sentence — if it doesn't fit, split it>
Domain:     technical | consumer/enthusiast | academic | market | mixed
Strategy:   <from the matching reference file — where the signal lives>
Hypothesis: <what you currently suspect, so you can try to break it>
Done when:  <what a sufficient answer looks like>
```

Read the matching reference file before writing the Strategy line — that's where the per-domain source map lives:

| Signal | Domain | Reference |
|--------|--------|-----------|
| Code, APIs, libraries, architecture, debugging | Technical | [references/technical-research.md](references/technical-research.md) |
| Products, hobbies, services, recommendations, reviews | Consumer/Enthusiast | [references/consumer-research.md](references/consumer-research.md) |
| Papers, scientific evidence, clinical data | Academic | Google Scholar, PubMed, institutional sources over blogs |
| Market sizing, competitive landscape | Market | market-analysis skill |
| Mixed | Lead with the domain holding more unknowns | — |

## Standing rules (apply throughout the investigation)

**Triangulate.** Never conclude from a single source. Multiple independent sources agreeing → high confidence. Contradicting → flag it and investigate the context behind each; contradictions are usually context-dependence in disguise, and resolving them is often the most valuable finding.

**Date every claim.** Note when each source was published or when you verified it. In fast-moving domains (AI tooling, cloud, frameworks), a 14-month-old "current best practice" is a trap; flag any load-bearing claim whose source predates the domain's churn rate.

**Attempt refutation on load-bearing claims.** Before reporting a finding the user will act on, spend one search trying to break it ("X considered harmful", "X problems", "moving away from X"). A claim that survives a refutation attempt is worth more than three confirmations, because confirmation searches find what you asked for.

**Negative evidence is a finding.** Zero results, missing docs, no community discussion — present the absence as the answer when it is the answer, with the search coverage that backs it. Don't pad weak near-matches into a fake comparison.

**Primary sources outrank aggregators — for facts.** Official docs, papers, and source code beat blogs; long-term user reports beat launch reviews; specialist communities beat SEO listicles. Top search results are optimized for ranking, not accuracy.

**For recommendations and defaults, vendor guidance is one voice, not the verdict.** A vendor's docs are authoritative on what exists and how it works, and biased on what's best — "use our newest X" is marketing posture as often as engineering truth. Triangulate any recommendation against practitioner and community experience, and when vendor stance and community consensus diverge, report both and label which is which. An answer that repeats the vendor's default as the answer has skipped the investigation.

**Iterate depth.** Round 1 reveals what you don't know; use the gaps to sharpen round 2. Each round narrows scope and increases depth. Quick lookups stop after one pass; deep investigations expect 2-3.

## Scoping

| Type | When | Depth |
|------|------|-------|
| Quick lookup | Known question, likely one source | Single search or file read |
| Exploration | Understand a system or topic | Multi-source, 1 round |
| Deep investigation | Decision with trade-offs | Multi-source, 2-3 rounds |
| Comprehensive review | New domain, high-stakes decision | Multi-source, iterative rounds |

Default to exploration. Escalate when you hit contradictions, multiple valid approaches, or surprising complexity.

## Parallel exploration

Launch parallel sub-investigations targeting different facets; don't explore sequentially what can run simultaneously. Contradictions between parallel results are valuable, not noise.

- **Technical:** structure (Glob/Read entry points) · API surface (Grep routes/exports) · docs (README, specs) · external context (web, library patterns)
- **Consumer:** specialist forums · relevant subreddits · manufacturer/official specs · broad web for niche reviewers

## Output format

```markdown
[Investigation header — the Question/Domain/Strategy/Hypothesis/Done-when block from above]

## Answer
[Direct answer — 1-3 sentences. Lead with this.]

## Key Findings
1. **Finding** — evidence + source + date. [Confidence: high/medium/low]
   [For load-bearing claims: what the refutation attempt found.]

## How It Works / How It Compares
[Architecture or data flow for technical; comparison matrix for consumer.]

## Contradictions & Surprises
[What conflicted between sources and what context resolves it. What deviated from the hypothesis.]

## Sources
- `path/to/file.ts` or [Title](url) — date published/verified

## Open Questions
[What's still unclear; what a deeper round would target.]

## Promote to context/
[System-level findings that should become architectural truth, for the invoking
skill (design/plan/test-planning) to write into context/<topic>.md. Omit if none.]
```

Conclusions with evidence, not process narration. Every finding carries a source and a date; unverified single-source findings say so.

## Bias guards

| Trap | Antidote |
|------|----------|
| Confirmation bias | The refutation attempt is mandatory for load-bearing claims |
| Anchoring on the first result | 2-3 sources before concluding anything |
| Cargo cult ("they do it, so it's right") | Ask why the pattern exists; check the context still applies |
| Availability bias (familiar solution) | Search for alternatives you haven't used |
| Premature convergence | The header's "Done when" line defines sufficiency — check against it, not against fatigue |
| SEO trust | Specialist sources beat ranking-optimized content |
| Wrong-domain strategy | Re-check the header's Domain line; are you searching where experts actually discuss this? |

## Stopping criteria

Stop when the question has an evidence-backed answer, key findings are triangulated from 2+ independent sources, contradictions are investigated (not just noted), and further rounds return diminishing information. Don't stop because you found *an* answer; stop because you found *the right* answer with evidence — or because you can state precisely what remains unknown and why.
