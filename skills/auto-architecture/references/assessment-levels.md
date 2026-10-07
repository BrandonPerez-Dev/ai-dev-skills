# Assessment levels — L1 self-check, L2 decision review, L3 scenario review

Reference for the auto-architecture skill. Source of truth: the design record `/home/juiz/research/engineering-nodes-2026-10/nodes/architecture.md` §A4, §B5. No study compares
how much each level catches; the levels are a cost ladder, not a validated detection ladder.

| Level | When | Person's time | Based on |
|---|---|---|---|
| L1 Self-check | After every design round | 0 — results shown on the page | ADD step 7 (opinion) |
| L2 Decision review | At the north-star freeze; at a revisit that changes ≥ 2 decisions | 20–40 min | DCAR, van Heesch et al., IEEE Software 2014 (moderate) |
| L3 Scenario review | Before committing to the thinnest slice; before any split into separate deployables | 30–60 min | Mini-ATAM (moderate); TARA, Woods 2012 (weak–moderate) |

## L1 — self-check (every round)

Run it yourself and put the answers in a short block on the page.

1. For each top-3 scenario: trace it through the current design. Which element handles the stimulus, and does
   the design meet the response measure? Answer *meets / at risk / not yet designed*.
2. Is every driver (top-3 qualities, key use cases, constraints) addressed by at least one decision?
3. List the decisions still open, in crux order — this names the next round.
4. Has anything this round contradicted an earlier record or a non-goal?

## L2 — decision review (at freeze)

For each of the 5–10 key decisions:
1. Show the one-sentence version and the forces **for** and **against** as they stand now.
2. The person votes **keep** or **revisit**. A revisit vote reopens that card before the freeze.

Then the independent risk storm:
- **Three independent reviewers**, no shared context, each given the architecture summary and the records'
  Y-statements, each with one lens: (a) failure and data integrity; (b) security and trust boundaries;
  (c) operability, cost and scale. Mix model families where available.
- **No debate round.** Merge by union, deduplicating — never vote, never summarise.
- One **verifier pass** that must cite the diagram element or record behind each risk; unsupported risks drop.
- Rank by how many reviewers flagged a risk; keep the top 5. Each gets a disposition: becomes a quality
  scenario, becomes a record assumption with a trigger, or is accepted in writing.

Why union and not vote: risk finding is a recall task. Independent reading then pooling finds about as much as
a meeting (Votta 1993; Johnson & Tjahjono 1998, strong for human inspection). For LLMs, debate does not beat
independent sampling (Choi et al., arXiv 2508.17536, strong on reasoning tasks). The number three is opinion;
the measurement plan tests it.

## L3 — scenario review (before the thinnest slice)

A mini-ATAM on the slice's interfaces:
1. **Utility tree** from the top-3 scenarios (see `quality-attributes.md`).
2. For each scenario, walk the design and mark:
   - **sensitivity points** — a decision the response measure depends on;
   - **trade-off points** — a decision that is a sensitivity point for two qualities pulling opposite ways;
   - **risks** — a decision likely to miss a response measure;
   - **non-risks** — decisions confirmed safe.
3. On existing code, add a TARA-style pass: read the actual dependency graph and compare it with the intended
   containers before approving the slice.

Output: a table of the above, with a disposition for every risk, shown on the slice-approval page.
