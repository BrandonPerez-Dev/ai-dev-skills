# Design process — the round protocol

Reference for the auto-architecture skill. Source of truth: the design record `/home/juiz/research/engineering-nodes-2026-10/nodes/architecture.md` §A2 (round 3, approved
2026-10-06). Load this file at the start of every architecture engagement and at every revisit.

## What you are doing

You design a system *with* one person over several review pages. You do not produce a finished architecture in
one pass. Each page settles one heavy decision. You finish with:

1. a north-star brief the person can read in ten minutes and re-tell (see `decision-card.md` § North-star brief);
2. one locked decision record per heavy decision (see `decision-card.md` § Decision record);
3. the thinnest runnable slice through the north-star structure;
4. boundary rules and invariants for other agents (see `boundary-rules.md`).

## The rounds, in order

One round per page. On a small project, merge rounds 0–2 onto one page.

| Round | You bring | The person decides |
|---|---|---|
| **0. Frame** (no design yet) | Problem, users, success measures, goals and **non-goals**, constraints, assumptions, core use cases, 6–10 candidate quality scenarios (`quality-attributes.md`), and the boring default stack as the baseline to deviate from (`technology-selection.md`). | Corrects the frame. Picks the top 3 qualities, each with a number. Accepts or rejects each non-goal. |
| **1. Domain and interface** | Core entities, who owns which data, the main flows and APIs, bounded areas. | Corrects them. Expect corrections: LLM-drafted domain models omit critical elements. |
| **2. High-level shape** | 2–3 whole-system shapes from `design-concepts.md`, simplest first, each justifying any complexity it adds over the simplest. | Picks one shape before any detail. This is the buy-in step. |
| **3..n. Deep dives** | The hardest open part first, as a decision card. Propose a **spike** when paper analysis cannot settle it. Estimate only when a number would change the decision. | One heavy decision per round. |
| **n+1. Cross-cutting and evolution** | Security, observability, failure modes, cost, rollout, and the growth path from the first slice to the north star. | Accepts the risks. Then the L2 decision review (`assessment-levels.md`), then the **north-star freeze**. |
| **Final. Thinnest slice** | The one scenario that crosses the most north-star boundaries, as a walking skeleton inside one deployable. | Approves it, after the L3 scenario review. |

After every round, run the L1 self-check (`assessment-levels.md`) and show its result on the page.

## Picking the next crux (rounds 3..n)

Take the open question that scores highest on all three:
- **Risk** — how badly the design fails if this is wrong.
- **Cost to reverse** — exit cost once code depends on it.
- **Drivers touched** — how many of the top-3 quality attributes it affects.

Typical cruxes, roughly in this order: data ownership and consistency; the top quality attribute's hot path;
the riskiest external integration; the deployment unit boundaries. Settle one driver per round (Attribute-Driven
Design: one driver per iteration).

### When to propose a spike

Propose a spike when two options are close on paper and the deciding fact is empirical (a latency, a library's
real behaviour, an integration's limits). A spike states: the question, the throwaway code to write, the number
or observation that settles it, and a time cap. Its result goes into the decision record's assumptions table.

### When to estimate

Only when a number would change the decision: "at 50 rps either option works, at 5,000 only one does." Never
open with back-of-envelope estimation for its own sake, and never assume hyperscale.

## How you behave

Borrowed from how staff-level system-design candidates are graded (one vendor's rubric, moderate evidence):
- **Find the crux.** Spend the rounds on the parts that can sink the system, not on the easy parts.
- **Start basic and justify complexity.** The simplest shape is always option one.
- **Recommend; do not hand over a menu.** Every card has your lean, your bias disclosure, and the case against.
- **Name the limits of your own design.** Every round says what is still undecided and what this design cannot do.

Avoid, from the interview genre: fixed time boxes, hyperscale by default, one-shot complete designs.

## North star first, thinnest slice backwards

- North-star **module boundaries** exist from the first slice. A container the north star needs but the first
  slice does not becomes a module behind a port inside one deployable, with a stub adapter. Splitting it out
  later moves an adapter, not a boundary.
- Boundary rules protect the north-star boundaries **from day one**.
- Counterweight: boundaries are the part most likely to be wrong early (Fowler, MonolithFirst 2015). Mark each
  boundary decision **firm** or **provisional**. Provisional boundaries get rules too, but a revisit can move
  them cheaply because they sit inside one deployable.

## Document weight

Scale with stakes. A Google mini design doc is 1–3 pages; a full one 10–20 (Ubl 2020). One page per round. The
north-star brief is capped at about 600 words plus two diagrams.

## Revisit mode

Entered from an `architecture.revisit` event (see `boundary-rules.md` § Revisits). Load only the decision
records the event names, plus any whose `Reconsider if` references the fired assumption or rule. Start from the
parked alternatives' switch sketches, not from scratch. Decide keep or switch; on switch, write a superseding
record, move rules, update the mutation manifest, and re-run the gate. Human review is the new Y-statement plus
the changed rule list, about 3–5 minutes.

## Where the order comes from

- **Interview frameworks** — Xu / ByteByteGo (2020), Hello Interview delivery framework, Educative RESHADED
  (2022), Donne Martin's system-design-primer, Exponent. All five teach: requirements → entities and API →
  high-level design → deep dives → wrap-up. Strong as a description of what is taught; opinion on outcomes.
  They disagree on when to estimate and on whether the API comes before the boxes.
- **On-the-job practice** — Google design docs (Ubl 2020), Uber RFCs and the Pragmatic Engineer survey of 70+
  companies (Orosz 2022-06-21), Amazon working backwards (Vogels 2006), Oxide RFDs (2020-07-24), Simon Brown
  (2020-07-07), Harmel-Law's advice process (2026). Converge on: frame → early buy-in on a rough shape → spike
  the biggest unknowns → detail with alternatives → cross-cutting and rollout → review and record. Moderate:
  convergent practice, no outcome study.
- **Why they differ** — interviews are time-boxed to 45 minutes, so they skip framing, non-goals, spikes and
  rollout. This protocol takes framing and iteration from the job, interface-before-boxes and crux-first deep
  dives from interviews, and one driver per round from ADD (Cervantes & Kazman 2016; LLM-assisted ADD,
  arXiv 2506.22688, 2025).
