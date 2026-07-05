---
name: grill
description: >-
  Interrogate a plan, design doc, or proposal — try to knock it down before
  it becomes locked artifacts. Surfaces tensions, terminology collisions,
  prior-decision conflicts, and attempts refutation. Emits a visible Grill
  section with each challenge and resolution.
when_to_use: >-
  After a plan or design doc exists but before test contracts lock. Use
  whenever a non-trivial plan needs adversarial pressure. Can be invoked
  standalone or as part of the engineering flow. For autonomous agents,
  use auto-plan-grill instead.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Agent
argument-hint: "[path/to/plan-or-design-doc.md]"
effort: high
---

# Grill

Interrogate the plan instead of admiring it. The planning conversation builds it up; this step tries to knock it down. Plans that skip the grill carry wrong assumptions into locked tests, where they're expensive to fix.

<HARD-GATE>
Read the plan AND `context/` before grilling. You can't find contradictions
with existing decisions if you haven't read them.
</HARD-GATE>

<HARD-GATE>
The grill emits a visible artifact — a `## Grill` section in the plan (or
a separate grill findings doc). Each challenge raised, the resolution, and
what was written back. A grill that lives only in conversation didn't happen.
</HARD-GATE>

## Input

A plan, design doc, or proposal to interrogate. Read it fully before starting.

Also read:
- All files in `context/` — existing architectural decisions and terminology
- All files in `spec/` that the plan touches or could contradict
- Any referenced research or prior art

## Process

### 1. Tensions and Structure

Concrete, structural challenges. Raise findings **one at a time** (never a questionnaire):

- Relationships and cardinality — "does one X hold many Y?"
- Deletion and cascade semantics
- State transitions and who owns them
- Ordering and idempotency under retry
- Boundary and scope questions — "does this subsystem really own this?"
- Missing modes — "what happens for greenfield / empty / degraded state?"
- Dependency direction — "A depends on B, but B references A"

Prefer questions whose answer changes a contract or a spec. Skip aesthetic concerns.

### 2. Terminology Collisions

Challenge every load-bearing term against the project's existing language in `context/`.

- If the plan says "session" and `context/` says "connection," that's a defect now or a bug later
- If two concepts use the same word, one of them is wrong
- Sharpen fuzzy terms before they enter a spec

Confirmed language writes back to `context/`.

### 3. Prior-Decision Conflicts

Find the existing spec contract or `context/` decision this plan contradicts or quietly re-decides.

Name it explicitly: keep the old decision, or supersede it on purpose — never both implicitly. Every prior decision that's being changed should be acknowledged in the plan.

### 4. Refutation Attempt

Close with one refutation attempt: state the strongest argument that the plan is wrong or oversized:

- A simpler version that achieves 80% of the value
- An existing capability that already covers it
- An invariant it breaks
- A fundamental assumption that might be wrong
- Research or evidence that contradicts the approach

Resolve it — either the refutation holds (plan needs to change) or it doesn't (document why).

### 5. Research (when needed)

If a tension or refutation requires evidence beyond what's in the codebase:

- Spawn a research agent to investigate the specific question
- Look for prior art, papers, framework documentation, practitioner experience
- Ground the grill in evidence, not speculation

Research is not mandatory for every grill. Use it when a question can't be answered from the codebase and context alone.

## Output

Write the grill results as either:

**Option A: `## Grill` section in the plan** (for smaller grills)
```markdown
## Grill

### Tension: [title]
**Challenge:** [the question]
**Resolution:** [what was decided]
**Write-back:** [what was updated in context/ or spec/, if anything]

### Terminology: [term]
**Collision:** [what conflicted]
**Resolution:** [which term wins]
**Write-back:** [context/ update]

### Refutation: [thesis]
**Argument:** [strongest case against the plan]
**Resolution:** [why it holds or doesn't]
```

**Option B: Separate grill findings doc** (for larger grills)
- Save to `changes/NNN-<topic>/grill-findings.md`
- Reference research in `changes/NNN-<topic>/research-*.md`
- Link from the plan

Write-backs follow the promotion rule: sharpened terms and decisions that are hard to reverse, surprising without context, or carry real trade-offs go to `context/`. The rest stays in the plan.

## Scaling

| Change Size | Grill Depth | Time |
|---|---|---|
| **Small** (1-2 specs) | One sanity question + quick terminology check | 2-5 min |
| **Medium** (2-4 specs) | Full three lenses + refutation | 10-15 min |
| **Large** (4+ specs, new system) | Full lenses + research + deep refutation | 15-30 min |

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Questionnaire dump** | One question at a time. Wait for resolution before the next. |
| **Aesthetic criticism** | Focus on structural issues that change contracts, not style preferences. |
| **Grilling without reading context/** | Hard gate — you can't find contradictions you haven't looked for. |
| **Grill that lives only in conversation** | Hard gate — write the artifact. No artifact = no grill. |
| **Skipping the refutation** | The refutation is the most valuable part. Always attempt one. |
| **Research without a specific question** | State what you need to learn before spawning research. |
| **Over-grilling small changes** | One sanity question is enough for a 1-spec change. |
