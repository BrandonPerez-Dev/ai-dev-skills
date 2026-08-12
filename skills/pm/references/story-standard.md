# Cadre Story Standard

Read when **writing or refining any Cadre story** (a Linear issue that feeds the pipeline). The `pm`
skill's `Story` and `Refine` flows apply this — it is the shape every Cadre story should hold, at any
point in its lifecycle.

**The idea in one line:** a story is **scannable on the surface, structurally complete underneath** —
a human grasps it in ~30 seconds; an agent gets enough to implement without guessing. It carries
**intent (what / why), not implementation (how)** — the *how* is the planning member's change-spec.

Two reasons this shape, not prose:

- **Ambiguity breaks agents.** Vague or omitted-detail requirements measurably degrade AI code
  correctness, and the agent won't reliably stop to ask — so "done" must be testable and at least one
  example must be concrete, resolved at authoring time, not left for the implementer to guess.
- **Humans scan, they don't read.** Front-loaded, labeled, bulleted text is grasped far faster than
  paragraphs; bury the point and it's missed.

## Contents
- The template (6 sections)
- What to exclude
- Lifecycle-safety (refining at any stage)
- Worked example
- Anti-patterns

## The template

Six sections, in order — front-loaded, most-scannable first. **Prose only in Summary and Why; bullets
everywhere else.** Non-Goals is **conditional** (include it only when there's an over-reach to head off
— see below); the other five are the standard shape.

### 1. Summary
One sentence: what changes and for whom — the human hook, scannable in isolation. ~25–40 words (soft).

### 2. Why / Outcome
The problem and the user/operator outcome — the *why*. 1–3 sentences.

### 3. Acceptance Criteria
As many testable, observable pass/fail bullets as it takes for "done" to be unambiguous — often just
**one** for a trivial slice, several for a rich one. **Count is a signal, never a floor** (too few =
under-specified or trivial; many = probably an epic). Include **at least one concrete example** (an
input→output, a before→after) — examples kill the two ambiguity types that hurt agents most: omitted
detail and multiple meanings.

For the deep AC-quality rubric (Given/When/Then; testable / observable / independent; unhappy-path when
one applies) and the splitting patterns, **compose [[backlog-refinement]]** — don't reproduce it here.

### 4. Constraints
Hard limits any valid solution must respect. **State properties, not implementation** — over-specifying
the *how* pre-empts the planner, whose lane it is.

This is a **lean, not a law:** name a specific mechanism when the **driver has explicitly called for
it**, or when the **context genuinely requires it** (v1 parity with a v0 behavior, a technical
necessity, an interface it must match). When in doubt, favor the property and let planning choose the
mechanism.

- *Property — keep:* "the read client stays read-only"; "no runtime deps — stdlib-first".
- *Mandated how — keep (it has a reason):* "scrub `ANTHROPIC_API_KEY` & siblings — v0 parity, billing
  safety"; "branch prefix `pipe/` not nested under `feat/` — git forbids the nesting".
- *Unmandated how — cut to the change-spec:* a chosen fixture, branch layout, or storage location the
  planner could reasonably decide differently.

### 5. Non-Goals / Out of Scope *(when it earns its place)*
Include this **when there's a plausible over-reach worth heading off** — an adjacent thing the agent
might wrongly pull in (a neighboring refactor, a related-but-separate behavior, a rename in passing).
Naming it is the cheapest scope-ambiguity killer, because the agent won't stop to ask. **Omit it when
the scope is self-evident** — a padded exclusion is noise, not signal (the same "signal, not a floor"
logic as AC). Prefer naming *deferred* work over leaving it implied.

### 6. Context & Links
The agent-facing block: named artifacts, paths, prior decisions — each with **what it's for**. Link to
maintained context rather than duplicating it, but **never a bare cross-reference** ("see NEX-98"). Say
what to look at and why: "NEX-98 change-spec — the roster/flow-as-data model this extends." A bare link
is as useless to the agent as no link; stale inlined context is worse.

## What to exclude
- **The how** — tech stack, design, slicing. That belongs in the planning member's change-spec.
  (Constraints' two escape hatches aside.)
- **Speculative future work** and **stale narrative** that no longer matches reality.

## Lifecycle-safety — refining at any stage

The same template applies whether writing new or refining existing — but **what you may safely change
depends on the stage:**

| Stage | Safe to change |
|---|---|
| **New / Backlog** | Everything — shape the story freely. |
| **In refinement, pre-build** (no locked tests yet) | Fill missing sections, tighten AC, add examples / non-goals freely. |
| **In-flight, tests locked** (a `tests` PR has merged) | **Do not rewrite the AC the locked tests enforce** — locked tests are an immutable contract. You may *add* context, sharpen non-goals, or clarify *around* the contract — never contradict it. If the AC itself is wrong, that's a fix-slice / driver call, not a story edit. |

Refining = filling missing sections and stripping bloat / vague refs — **not** rewriting prose that
already works.

## Worked example (golden)

> **Summary** — CI runs the full suite on a clean self-hosted runner, so a green check attests the code
> actually works, not that a stray binary happens to sit on the machine's PATH.
>
> **Why / Outcome** — Today CI runs on the dev laptop, where stale global installs can false-green a
> build. An operator needs green to mean "this works on a clean environment" — the whole point of CI as
> an attestation.
>
> **Acceptance Criteria**
> - Given a push to any branch, When CI runs, Then the suite executes on the self-hosted runner, not a
>   hosted Actions minute.
> - Given a checkout with no global `pipeline` install, When the entry-point tests run, Then they pass
>   using the checkout's own code — *example:* with `PATH=/usr/bin:/bin`, `pipeline --help` still
>   resolves and exits 0.
> - Given the runner is offline, When a push arrives, Then the check reports "runner unavailable", not a
>   false green.
>
> **Constraints**
> - Zero hosted-Actions minutes (org policy — cost).
> - Outbound long-poll only, no inbound ports (the no-public-ingress constraint).
>
> **Non-Goals**
> - Fixing the PATH false-green itself — that's its own story.
> - Multi-runner scaling / matrix builds.
>
> **Context & Links**
> - NEX-128 — the entry-point false-green this pairs with; the clean runner is what makes its fix
>   observable.
> - CLAUDE.md, "CI is an attestation, not a checkbox" — the invariant this serves.

Note it names *what* and *why* (properties, testable AC with a concrete example, explicit non-goals,
load-bearing links) and never *how* (no "install actions-runner v2.x via…") — except the one mandated
constraint (zero minutes), which carries its reason.

## Anti-patterns
| Anti-pattern | Fix |
|---|---|
| Wall of prose / description bloat | Front-loaded bullets; scannable in ~30s. |
| Bare cross-reference ("see NEX-X") | Name the artifact **and what it's for**. |
| Over-specification (dictating the how, unmandated) | State the property; defer the how to the change-spec. |
| Under-specification (no example, vague outcome) | Add a concrete example; make "done" testable. |
| Stale inlined context | Link to the maintained source, don't copy it in. |
| Rewriting AC on a story whose tests are locked | Add context / non-goals around the locked contract; wrong AC → fix-slice, not a story edit. |
