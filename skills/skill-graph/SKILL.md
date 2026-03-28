---
name: skill-graph
description: >-
  Manage the skill router's embedding graph — add nodes for new skills, diagnose
  weak routing, and tune descriptions for better semantic matching. Use when creating
  a new skill that needs graph routing, when a skill isn't being routed to correctly,
  or when you need to analyze routing quality across skills.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
---

# Skill Graph Management

Ensure every skill is discoverable by writing embedding text that matches how users ask for it, not how the skill describes itself.

<HARD-GATE>
Do NOT add a node or modify a description without running diagnostic scoring before AND after.
Intuition about what "sounds right" for embeddings is unreliable — measure with real queries.
</HARD-GATE>

## When to Use

| Situation | Mode | What Happens |
|-----------|------|-------------|
| New skill created, needs routing | **Add** | Read SKILL.md, generate node, wire edges, rebuild, verify |
| Skill not triggering on expected queries | **Diagnose** | Score test queries, show competition, identify weak spots |
| Node exists but scores poorly | **Tune** | Rewrite description/keywords, rebuild, verify improvement |
| Bulk audit of routing quality | **Audit** | Score representative queries across all skills |

## Key Paths

- **Graph definition:** `skill-router/src/skill-graph.ts` (relative to repo root)
- **Embedding code:** `skill-router/src/embed.ts`
- **Build script:** `skill-router/src/build-graph.ts`
- **Router:** `skill-router/src/router.ts`
- **Built graph:** `skill-router/skill-graph.json`
- **Skills directory:** `skills/` (also available via `~/.claude/skills/`)

## Embedding Optimization Principles

These principles are derived from nomic-embed-text documentation and RAG retrieval research. They govern how node descriptions and keywords should be written.

### 1. User Intent First, Technical Terms Second

The embedded text matches against user prompts. Users say "design a database schema," not "paradigm selection for workload-optimized data modeling."

**Lead with what users say when they need this skill:**
```
"Design database schemas and model data relationships. Use when deciding
what tables, columns, or indexes to create, or asking 'how should I
structure this data' or 'what's the right schema for this'."
```

**Not with abstract capability descriptions:**
```
"Schema and data modeling decisions — choosing between relational, graph,
document, and time-series paradigms based on workload analysis."
```

### 2. Keywords as Natural Phrases

The build script appends keywords as `Keywords: word1, word2, ...`. Comma-separated single words embed poorly compared to natural phrases.

**Good keywords:** `["design a database", "what tables do I need", "foreign key relationships", "normalize this schema"]`

**Bad keywords:** `["schema", "ERD", "relational", "normalization"]`

Include both user-language triggers AND technical terms, but phrase them naturally.

### 3. Task Prefixes (search_document / search_query)

nomic-embed-text is trained with asymmetric prefixes:
- Documents: `search_document: <text>`
- Queries: `search_query: <text>`

These are applied in `embed.ts` and `build-graph.ts`. If they're missing, add them — this is a significant accuracy improvement for free.

### 4. Optimal Length: 200-400 Tokens

- **Too short (<100 tokens):** Underspecified, loses to more verbose competitors
- **Sweet spot (200-400 tokens):** Rich enough to capture intent, specific enough to differentiate
- **Too long (>600 tokens):** Semantic dilution — the core intent gets buried

A good node description is 2-3 sentences of what the skill does + 3-5 trigger phrases + natural keyword phrases.

### 5. Avoid Negation

"NOT for network scanning" still embeds "network scanning" into the skill's semantic neighborhood. Focus descriptions on what the skill IS, not what it isn't. Use edge relationships and macro categories for disambiguation instead.

### 6. Include Example Trigger Phrases

The highest-ROI technique. Include actual phrases users say:
```
"Use when someone says 'audit this code for security issues',
'check for vulnerabilities', or 'is this API secure'"
```

This creates direct phrase overlap between user queries and the embedded document.

## Mode: Add Node

### Step 1: Read the SKILL.md

Read the new skill's `SKILL.md` frontmatter to get the `name` and `description`.

### Step 2: Generate Node Definition

Write the node following this structure:

```typescript
"skill-id": {
  id: "skill-id",
  type: "skill",  // or "macro" or "reference"
  description:
    "[2-3 sentences: what users need this for, in their language]. " +
    "Use when [3-5 trigger phrases users would actually say]. " +
    "[1 sentence: key capabilities using domain terms].",
  invoke: "skill-id",
  keywords: [
    "natural trigger phrase 1",
    "natural trigger phrase 2",
    "technical term as phrase",
    // 8-12 keywords total
  ],
},
```

### Step 3: Choose Macro Category and Wire Edges

Pick the macro category that best fits. Current categories:
- `software-design` — building features, architecture, design, data modeling
- `quality` — debugging, review, testing, verification
- `product` — specs, requirements, task breakdown
- `business` — opportunities, market analysis, business cases
- `ai-engineering` — agents, prompts, evals, tools, ML
- `infrastructure` — scaffolding, CI/CD, cloud, workspaces
- `security` — app security, infra security, auditing
- `meta` — skill creation, maintenance, orchestration
- `delivery` — commits, PRs, kanban, file formats

Add edges:
```typescript
{ from: "macro-id", to: "skill-id", rel: "contains" },
// Add precedes/requires/references edges as needed
```

### Step 4: Rebuild

```bash
cd "$(git rev-parse --show-toplevel)/skill-router"
npm run build && npm run build-graph
```

### Step 5: Diagnostic Scoring

**CHECKPOINT: Always run diagnostics after adding a node.**

Run the diagnostic script to verify the new skill routes correctly:

```bash
cd "$(git rev-parse --show-toplevel)/skill-router"
node scripts/diagnose.js "query that should match" skill-id
```

Or manually test via the hook:
```bash
echo '{"userMessage": "your test query"}' | ~/.claude/hooks/skill-router.sh
```

Write 5-8 test queries that represent how users would ask for this skill. The target skill should:
- Score **>0.60** on at least 3 queries
- Be the **top match** on at least 4 of the queries
- Score **>0.45** (threshold) on all queries

If scores are weak, go to Tune mode.

## Mode: Diagnose

### Step 1: Identify the Problem

What's happening?
- Skill never triggers → scores below 0.45 threshold
- Wrong skill triggers instead → competitor has higher score
- Skill triggers on wrong queries → description is too broad

### Step 2: Run Comparative Scoring

Score the problem query against the target skill AND its likely competitors:

```bash
cd "$(git rev-parse --show-toplevel)/skill-router"
node -e "
async function test() {
  const { readFileSync } = require('fs');
  const graph = JSON.parse(readFileSync('./skill-graph.json', 'utf-8'));
  const { embed, cosineSimilarity } = await import('./dist/embed.js');

  const queries = [
    'the query that fails',
    'another way users might say it',
    'a third variant',
  ];

  // Include the target + suspected competitors
  const skills = ['target-skill', 'competitor-1', 'competitor-2'];

  for (const q of queries) {
    const qEmb = await embed(q);
    const scores = {};
    for (const s of skills) {
      if (graph.nodes[s]?.embedding) {
        scores[s] = cosineSimilarity(qEmb, graph.nodes[s].embedding).toFixed(3);
      }
    }
    const sorted = Object.entries(scores).sort((a,b) => b[1] - a[1]);
    console.log(q);
    sorted.forEach(([s, score]) => console.log('  ' + score + ' ' + s));
    console.log();
  }
}
test();
"
```

### Step 3: Analyze Results

Common patterns:
- **Low absolute scores (<0.50):** Description doesn't use the language users use. Add trigger phrases.
- **Close competitors (within 0.05):** Descriptions overlap semantically. Differentiate by adding unique trigger phrases.
- **Wrong winner:** The competitor's description accidentally covers your skill's use case. Sharpen both descriptions.

Present findings with specific scores and recommend which descriptions to rewrite.

## Mode: Tune

### Step 1: Record Baseline

Run diagnostic scoring on 5-8 test queries. Save the scores — these are your "before" numbers.

### Step 2: Rewrite Description

Apply the optimization principles:
1. Lead with user intent language
2. Include 3-5 trigger phrases users would say
3. Use natural keyword phrases
4. Stay within 200-400 tokens for the combined description + keywords
5. Avoid negation

### Step 3: Rebuild and Re-score

```bash
cd "$(git rev-parse --show-toplevel)/skill-router"
npm run build && npm run build-graph
```

Run the same diagnostic queries. Compare before/after:
- Did the target skill's scores improve?
- Did any other skill's scores degrade unexpectedly?
- Is the target skill now the top match for its intended queries?

### Step 4: Verify No Regressions

Check that the rewrite didn't steal traffic from other skills. Run a few queries that should NOT match this skill and confirm scores stayed low.

**Present results as a before/after table:**

| Query | Before | After | Delta | Rank |
|-------|--------|-------|-------|------|
| "user query 1" | 0.52 | 0.65 | +0.13 | 1st |
| "user query 2" | 0.48 | 0.61 | +0.13 | 1st |

## Mode: Audit

Run representative queries for each skill and check that the right skill wins. Focus on:
- Skills that were recently added or modified
- Skills with overlapping domains (e.g., `architecture` vs `data-modeling`)
- Skills that users have reported routing issues with

## Anti-Patterns

| Anti-Pattern | What Happens | Fix |
|--------------|-------------|-----|
| Writing descriptions for humans | Academic language doesn't match user queries | Lead with user intent phrases |
| Keyword stuffing | Comma-separated single words dilute the embedding | Use natural phrases |
| Skipping diagnostics | "It looks right" but scores 0.48 | Always measure before and after |
| Over-tuning for one query | Description becomes too specific, misses other valid queries | Test 5-8 diverse queries |
| Copying SKILL.md description verbatim | SKILL.md describes the methodology; graph node describes when users need it | Write a separate user-intent-focused description |

## Bias Guards

| Thought | Reality | Do Instead |
|---------|---------|------------|
| "This description sounds good" | Embeddings don't care how it sounds to you | Run the diagnostic scorer |
| "Just add more keywords" | Keyword lists embed poorly | Use natural phrases |
| "The score went up on my test query" | One query isn't enough | Test 5-8 diverse queries and check for regressions |
| "0.50 is close enough" | Users will hit edge cases where 0.50 drops below threshold | Aim for >0.60 on primary queries |
