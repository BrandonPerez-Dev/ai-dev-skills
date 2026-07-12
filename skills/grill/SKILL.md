---
name: grill
description: >-
  Interrogate a sliced scope or design — try to knock it down before it
  becomes locked artifacts. Surfaces tensions, terminology collisions,
  prior-decision conflicts, and attempts refutation. Resolutions write back
  into context/ (decisions with rejected alternatives) and spec Notes.
when_to_use: >-
  After slicing lands scope (specs marked planned/in-progress + context
  entries) but before test contracts lock. Use whenever a non-trivial design
  needs adversarial pressure. Can be invoked standalone or as part of the
  engineering flow. For autonomous agents, use auto-plan-grill instead.
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
argument-hint: "[spec names, or path/to/design-doc.md]"
effort: high
---

# Grill

Interrogate the design instead of admiring it. The slicing conversation builds it up; this step tries to knock it down. Designs that skip the grill carry wrong assumptions into locked tests, where they're expensive to fix.

<HARD-GATE>
Read the sliced scope AND all of `context/` before grilling. You can't find
contradictions with existing decisions if you haven't read them.
</HARD-GATE>

<HARD-GATE>
The grill leaves a durable trace. Every challenge resolves into one of:
a write-back to `context/` (a sharpened decision, with the rejected
alternative and why-not), a write-back to the affected spec's `## Notes`
(slice-scoped resolution), a flagged contract supersession for test-planning
to execute, or — for challenges the design survived unchanged — a line in the
grill commit message. A grill that lives only in conversation didn't happen.
</HARD-GATE>

## Input

The sliced scope to interrogate: the specs currently marked `planned`/`in-progress` (their stubs and Notes), the `context/` entries the slicing added or touched, or a standalone design doc if that's what exists. Read it fully before starting.

Also read:
- All files in `context/` — existing architectural decisions, terminology, and standing rejections
- All `spec/` files the scope touches or could contradict
- Any cited research in `context/research/`

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

- If the scope says "session" and `context/` says "connection," that's a defect now or a bug later
- If two concepts use the same word, one of them is wrong
- Sharpen fuzzy terms before they enter a spec

Confirmed language writes back to `context/` (a glossary file earns its place once collisions recur).

### 3. Prior-Decision Conflicts

Find the existing spec contract or `context/` decision this scope contradicts or quietly re-decides.

Name it explicitly: keep the old decision, or supersede it on purpose — never both implicitly. A superseded **locked contract** (spec test contract, locked test) is flagged for test-planning → test-writer to re-lock; grill names the supersession, it never edits locked artifacts itself.

### 4. Necessity and Scope

Correctness lenses ask "is this right?" — this lens asks "should this exist, at this size, now?" Slicing and specs amplify scope; nothing downstream of the grill pushes back on it. Apply per slice, not once overall:

- **Observed demand** — name the real, already-observed need this slice serves. A hypothetical actor ("if we ever have N reviewers…") is not demand. If the demand is speculative, name the evidence that would justify building it — that becomes the revival trigger.
- **The one-branch version** — state the simplest behavior that covers 100% of *current* reality (often "detect the case → stop and ask"). If the slice builds resolution machinery where a one-branch version suffices, the machinery gets parked, spec `status: parked`, with the revival trigger in its Notes.
- **Concept budget** — count the new load-bearing terms this scope mints per behavior it adds. Terms that exist only to name internal machinery are glossary debt; prefer reusing existing vocabulary. A scope that adds more nouns than behaviors is over-designed.
- **Wiring completeness declaration** — everything a spec declares (functions, statuses, vocabulary) must be exercised by the same change that builds it, or explicitly descoped/parked before build. Grill states this expectation so review can enforce it: spec'd-but-unwired at review time is a defect, not a future feature.

### 5. Refutation Attempt

Close with one refutation attempt: state the strongest argument that the design is wrong or oversized:

- A simpler version that achieves 80% of the value
- An existing capability that already covers it
- An invariant it breaks
- A fundamental assumption that might be wrong
- Research or evidence that contradicts the approach

Resolve it — either the refutation holds (the scope changes) or it doesn't. A rejected refutation is a **rejected alternative**: record it ADR-style in the relevant `context/` topic file ("Rejected: X — because Y") so it never gets re-litigated from scratch.

### 6. Research (when needed)

If a tension or refutation requires evidence beyond what's in the codebase:

- Spawn a research agent to investigate the specific question
- Look for prior art, papers, framework documentation, practitioner experience
- Ground the grill in evidence, not speculation

Durable findings go to `context/research/<topic>.md` (dated cache), cited from the topic file. Research is not mandatory for every grill.

## Where Resolutions Land

| Resolution type | Destination |
|---|---|
| Sharpened/new system-level decision | `context/<topic>.md`, ADR-style: decision + rationale + "Rejected: X — because Y" |
| Confirmed terminology | `context/` (glossary or topic file) |
| Slice-scoped resolution (affects one spec's behavior) | that spec's `## Notes` (+ `## Changes` entry) |
| Contract change / locked-test supersession | flagged, executed by test-planning → test-writer |
| Parked slice (speculative scope) | spec `status: parked` + revival trigger in its Notes |
| Challenge survived unchanged (no durable delta) | one line in the grill commit message |
| Dated evidence gathered | `context/research/<topic>.md`, cited from the topic file |

Commit the write-backs as a grill commit; its message lists each challenge → resolution in one line. That diff + message is the grill's visible artifact.

## Scaling

| Change Size | Grill Depth | Time |
|---|---|---|
| **Small** (1-2 specs) | One sanity question + quick terminology check | 2-5 min |
| **Medium** (2-4 specs) | Full lenses (incl. necessity per slice) + refutation | 10-15 min |
| **Large** (4+ specs, new system) | Full lenses + research + deep refutation | 15-30 min |

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Questionnaire dump** | One question at a time. Wait for resolution before the next. |
| **Aesthetic criticism** | Focus on structural issues that change contracts, not style preferences. |
| **Grilling without reading context/** | Hard gate — you can't find contradictions you haven't looked for. |
| **Resolutions that live only in conversation** | Hard gate — every challenge lands in context/, a spec's Notes, a flagged supersession, or the grill commit message. |
| **Recording a decision without its rejected alternative** | The why-not is the part that prevents re-litigating. Write "Rejected: X — because Y." |
| **Editing a locked contract directly** | Grill names supersessions; test-planning → test-writer executes them. |
| **Skipping the refutation** | The refutation is the most valuable part. Always attempt one. |
| **Scope without observed demand** | Machinery for hypothetical actors gets parked with a revival trigger, not built. Ask for the one-branch version. |
| **Minting nouns faster than behaviors** | New glossary terms are debt. Reuse existing vocabulary; a concept that only names internal machinery doesn't earn a term. |
| **Research without a specific question** | State what you need to learn before spawning research. |
| **Over-grilling small changes** | One sanity question is enough for a 1-spec change. |
