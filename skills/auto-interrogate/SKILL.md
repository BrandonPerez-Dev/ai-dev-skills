---
name: auto-interrogate
description: >-
  Pipeline interrogate stage (S1) as a skill: process driver review threads on
  the planning PR. Researches before answering, revises the spec while
  preserving its two-layer structure (decisions updated in place, provenance
  appended to the record), pushes back with reasoning where the driver's point
  doesn't hold, and drives threads toward resolution within the round budget.
when_to_use: >-
  Fired by the pipeline runner when the driver leaves comments/reviews on an
  open planning PR. Not for the initial spec (auto-spec) and not for stage PRs
  after planning (the revise prompt). Do NOT use interactively — use
  interrogate for that.
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
argument-hint: "[planning PR number; runner supplies round bindings]"
effort: high
---

# Auto Interrogate

You were summoned: the driver left new comments or reviews on the planning PR. Process **all** open conversation in one pass and drive threads toward resolution — the runner escalates after the round budget, so converge, don't ping-pong. The runner's ground rules bind (never merge, marker on every post).

## Process

1. You are on a clean `$planning_branch`. Read the planning artifact(s) fresh, layer 1 first.
2. Collect the full open conversation: unresolved review threads (`gh api graphql` on the PR's `reviewThreads` — `isResolved`, bodies, ids, paths), plus PR-level comments and review bodies.
3. For **each** open item, in artifact order:
   - **Think it through against the codebase** — read the relevant code before answering. If a point needs outside evidence, research it (investigating skill); durable findings go in the artifact's record layer, cited from your reply.
   - **Reply in that thread** (`in_reply_to`). Where the point holds, say concretely what changed. Where it doesn't, push back with reasoning — interrogate is adversarial both ways; silent compliance is a failure mode, and so is re-litigating something the record layer already settled (link it instead).
   - **Revise the artifact per resolution**, preserving the two-layer standard: layer 1 decision statements are rewritten in place — never annotated with history; the resolution's provenance (thread, date, rejected alternative) is appended to layer 2. Commit per logical resolution, message naming the thread.
4. Apply auto-spec's critic lenses (structure/tensions, terminology, prior-decision conflicts, necessity, legibility) to any scope your revisions **added** — fixes must not smuggle in unexamined additions. If a revision round materially restructures the spec, re-run the driver-read test on layer 1 before pushing.
5. Resolve only threads **you** opened and have now addressed. The driver resolves their own.
6. Push. Post one PR comment: round summary — what changed, which decisions moved, which threads await the driver — closing with: "When the scope is right, merge this PR — that locks it and starts contract authoring."

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Appending thread history into decision sections | Layer 1 states; layer 2 remembers. |
| Answering from memory of the spec | Re-read artifact and code each round — you are stateless. |
| Conceding to save a round | A wrong concession costs more downstream than a round of pushback. |
| Fixing exactly what was asked, unexamined | New scope from a fix gets the lenses too. |
| Resolving the driver's threads | Never. Merging and resolving are their signals. |
