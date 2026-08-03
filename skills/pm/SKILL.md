---
name: pm
description: Product-management operations on a Linear backlog for the Cadre pipeline — prioritize and order the backlog, triage incoming issues, write pipeline-ready stories, and plan the roadmap, all via the Linear MCP. ALWAYS invoke when asked to prioritize / order / rank / stack-rank the backlog, decide what to work on next, triage or groom issues, write / refine / split / size a Linear story or issue, set issue priority, plan a 2-week cycle or sprint, or plan or adjust a roadmap in Linear. Every ordering and every write shows its scoring rationale and is confirmed before it touches Linear. Do not hand-order a backlog, set priorities, or write stories ad hoc without this skill.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Skill
  - AskUserQuestion
  - mcp__linear-server__list_issues
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_issue_statuses
  - mcp__linear-server__list_issue_labels
  - mcp__linear-server__list_projects
  - mcp__linear-server__get_project
  - mcp__linear-server__list_initiatives
  - mcp__linear-server__list_cycles
  - mcp__linear-server__list_users
  - mcp__linear-server__save_issue
  - mcp__linear-server__save_project
  - mcp__linear-server__save_comment
  - mcp__linear-server__save_milestone
  - mcp__linear-server__save_initiative
argument-hint: "[what to do — 'prioritize the Cadre backlog', 'triage NEX-131', 'write a story for X', 'plan the roadmap']"
---

# PM — Linear-native product management for Cadre

**Central thesis:** the backlog's order and every issue write are *defensible* — each carries a shown score or reason, and nothing is written to Linear until the human confirms it. A silent reshuffle is a bug, not a convenience.

This skill owns the **Linear-native** layer: reading the real board, scoring and ordering work, triaging intake, sizing/writing stories that the Cadre pipeline can build, and shaping the roadmap. It does **not** re-derive story methodology — for deep acceptance-criteria and epic-splitting work it composes [[backlog-refinement]].

<HARD-GATE>
Never write to Linear (create/update issues, set priority, reorder, move state, add relations, edit projects/initiatives) until you have shown the proposed change and its rationale and the user has confirmed. Reads are free; writes are proposed first. This is the money-and-trust boundary — batch the proposal, then execute on approval.
</HARD-GATE>

<HARD-GATE>
A story is not pipeline-ready without (a) a user-facing outcome (vertical, not a component task), (b) 3+ testable acceptance criteria, and (c) a size that one AI build session can complete. Missing any of these → it's an epic or a task, not a ready story. Split or reframe it.
</HARD-GATE>

## Always, before any write

1. **Read the live board first.** `list_issue_statuses`, `list_issue_labels`, `list_projects`, `list_cycles` for the team in play — states, labels, project/initiative structure, and whether cycles exist drift over time. Never assume; the board is the source of truth.
2. **Introspect the Linear tool surface.** The MCP write set evolves; confirm the tool and its params (e.g. `save_issue` exposes `priority`, `stateId`, `projectId`, `labelIds`, `parentId`, `milestone`, and relations `relatedTo`/`blocks`/`blockedBy`/`duplicateOf`) before relying on a capability. Don't hard-code what you remember.

## Method selection

Different requests need different flows — don't run one procedure for everything.

| Request | Flow | Core move |
|---|---|---|
| "Prioritize / order / rank the backlog", "what's next" | **Prioritize** | Score with ICE (dependency leverage folded into Impact); set priority + Backlog/Todo lane; propose one ranking |
| "Triage this issue", "groom the backlog", new intake | **Triage** | Classify (severity vs priority), dedup, accept/defer/delete |
| "Write / refine / split / size a story" | **Story** | Vertical slice, agent-sized, 3+ AC; compose [[backlog-refinement]] |
| "Plan / adjust the roadmap" | **Roadmap** | Now/Next/Later over projects/initiatives |
| "Plan the cycle / sprint", cycle boundary | **Cycle** | Pull top-ICE ready stories to a capacity budget; cadence, not scope-freeze |

## Prioritize

**Default scorer: ICE.** For each candidate, score three factors 1–10 and multiply:

```
ICE = Impact × Confidence × Ease        (higher = do sooner)
```

- **Impact** — how much this moves the goal if it works.
- **Confidence** — how sure you are of the impact/effort estimate (your evidence, not a vibe).
- **Ease** — inverse of effort; a one-session change scores high, a multi-week epic scores low.

ICE is multiplicative (not an average) and has **no reach term** — it's the right default for a single scorer on a fast, continuous-flow team where estimation is cheap and throughput is high. Show the three numbers and the product for every item; the score is worthless if the reader can't see why one item beat another.

**When to leave ICE (author-set rules — the research on framework routing was inconclusive, so these are deliberate choices, adjust with the driver):**
- **RICE** = `(Reach × Impact × Confidence) / Effort` — use *only* when candidates differ wildly in how many users/consumers they touch, so Reach actually changes the order. Effort is the divisor (person-days here, not person-months — cycle time is hours/days).
- **WSJF** = `Cost of Delay / Job Size` (CoD = Value + Time-Criticality + Risk/Opportunity-Enablement, Fibonacci) — use at the **initiative/project** level for economic sequencing, not for individual issues.

Formulas, scales, and citations: `references/prioritization-frameworks.md` — read it before applying RICE or WSJF, or when asked to justify a scale.

**Map score → Linear priority** (Linear priority is 1=Urgent … 4=Low, 0=None). This is a coarse bucket over the fine-grained score; the stack rank within a bucket is the ICE order.

| Bucket | Rule of thumb |
|---|---|
| **1 Urgent** | Blocks others, active incident, or a hard external deadline — time-critical regardless of ICE |
| **2 High** | Top ICE tier of the ready backlog |
| **3 Medium** | Middle ICE tier |
| **4 Low** | Long tail; revisit later |

Time-criticality can override raw ICE — a low-impact item with a hard deadline is Urgent. Say so when it does.

**Dependencies feed the score; they are not a second ordering.** There is one ordering principle — priority — and dependencies enter it two ways, never as a parallel "build order":

- **Leverage → Impact.** An item that unblocks others is more impactful *because* it unblocks them — fold that into its Impact score (an enabler gating three stories outscores its standalone value). The single ranking then already reflects it; don't emit a separate sequence beside it.
- **Hard blockers gate the lane, not the rank.** A blocked item *keeps* its priority — importance doesn't fall because you can't start yet — and instead stays in **Backlog** until unblocked (see Readiness lane). That's how "important but not startable" is expressed without a competing order or a dishonest priority.
- **Model the dependency if it's real but unmodeled** — propose the `blocks`/`blockedBy` write (same propose-then-confirm gate), so the lane gate is structural, not implied in your head.

Non-sequenceable work — trackers/ledgers (a standing checklist that never "ships") and quiet-window chores (wide mechanical changes best run when nothing's in flight) — isn't low-priority, it's *off the pull queue*: it lives in Backlog and is named as such, not ranked as if a session could pull it next.

**Output:** a single ranking — `Issue | Impact | Confidence | Ease | ICE | → Priority | Lane | note` — ordered by score, where Impact already carries any dependency leverage; then the proposed Linear writes (`priority`, `state` promotions/demotions, any `blocks`/`blockedBy` relations); then wait for confirmation.

## Readiness lane

Importance and actionability are different axes on different Linear mechanisms: **priority** answers *how much it matters*; **workflow state** answers *can it be started now*. Keeping them separate is what lets neither one lie — an important blocked item stays High priority *and* out of the ready lane.

- **Backlog** = planned but not startable — unrefined, an epic, or `blockedBy` something open.
- **Todo** = the ready lane — refined to the story hard-gate (vertical + 3 AC + one-session) **and** no open blocker. "What's ready to pull" is then a live query (`list_issues state:Todo`), not a hand reconstruction — and it's the queue the intake daemon will drain.

<HARD-GATE>
An issue belongs in **Todo** only if it has no open `blockedBy` **and** it passes the story hard-gate. Enforce this **bidirectionally**: propose promoting Backlog→Todo the moment an item becomes ready, and propose demoting Todo→Backlog the moment one regresses (newly blocked, or found unrefined). A stale Todo misleads the puller — and the daemon — exactly as much as a ready item stranded in Backlog. State changes are writes: propose, then confirm.
</HARD-GATE>

The pull order *within* Todo is just the priority ranking restricted to the ready lane — there is no separate build order to compute.

## Triage

Follow the 4-step loop (gather/analyze → categorize → reprioritize around value → pick the next increment), with these decision rules:

- **Severity ≠ priority.** Severity is the technical blast radius (a call you can make from the issue). Priority is the business decision of when to do it. Keep them distinct; a high-severity edge case affecting no one can still be low priority.
- **Dedup before creating.** `list_issues` with a `query` on the title/keywords and scan open + recent items. If it's a dup, set the relation (`duplicateOf`) rather than opening a new issue. Proposed, then confirmed.
- **Accept / Defer / Delete.** The backlog is not a wish list. Accept items with a live connection to a current project/initiative; defer valid-but-not-now with a revisit trigger; delete duplicates and strategy-less items. State which and why.
- Apply the existing team labels (type: Feature/Bug/Improvement; area labels) — read them live, don't invent.
- **Lane hygiene.** Grooming includes making state match readiness (the Readiness-lane gate): propose promoting ready + unblocked Backlog items to Todo, and demoting blocked or unrefined Todo items back to Backlog. Do it both directions — a misfiled state is a lie about what's pullable.

## Story

A Cadre story is a **vertical slice, agent-sized**: one AI build session can carry it end-to-end, and it produces an outcome a human can validate. That's the sweet spot between "component task" (too small, no user value) and "epic" (too big for one session).

- **Split with the meta-pattern:** find the core complexity, pick one source of variation, reduce it to a single case, defer the rest as separate stories. Tie-breakers: (1) prefer the split that lets you *throw away* a resulting story (most value hides in a fraction of the scope); (2) prefer splits that yield equal-sized small stories.
- **Acceptance criteria:** 3+ testable Given/When/Then. For the full AC-quality rubric, splitting patterns, and Definition-of-Ready checklist, **invoke [[backlog-refinement]]** — don't reproduce it here.
- **Write it into Linear** as an issue with the outcome in the title, the story + AC in the description, the right project/labels, and a proposed priority from the Prioritize flow. Pipeline-ready means the next step could open `feat/<slug>` against it.

## Roadmap

Model the roadmap as **Now / Next / Later** — three horizons of decreasing certainty, which fits continuous shipping better than dated timelines:

- **Now** — active or next-up; high certainty; concrete stories.
- **Next** — weeks out; medium certainty; shaped but not fully sliced.
- **Later** — direction; low certainty; themes, not stories.

Represent it in Linear with **initiatives** (strategic themes) linking **projects** (deliverables); horizon lives in project state/priority or a Now/Next/Later label. When you find projects with no initiative (a disconnected roadmap), surface it — an unlinked project is invisible to the roadmap view.

Roadmap and cycles are different altitudes and both hold: the roadmap is the *strategic* horizon (quarters of certainty); the **cycle** is the *execution* cadence (what's in flight this fortnight). Later/Next work is what eventually becomes a cycle's Now.

## Cycle

The team runs **2-week cycles**, but as a **cadence bucket, not a committed sprint** — the cycle is a planning-and-review rhythm, not a scope freeze. Flow continues underneath: when an AI build session finishes a story, the pipeline pulls the next-highest-ICE ready item regardless of cycle boundaries. This fits a merge-driven pipeline that drains work in hours; a frozen 2-week scope would only starve it.

What "plan the cycle" means here:

- **Fill, don't freeze.** Pull the top-ICE *ready* stories (vertical + 3 AC + one-session-sized — the story hard-gate) into the current cycle up to a rough capacity budget (recent throughput, not a story-point ceremony). Overflow stays in the backlog at its ranked position, free to be pulled early if the cycle drains.
- **The cycle is a checkpoint, not a contract.** Use it for a lightweight plan at the start and a velocity/retro read at the end — what shipped, what stalled, what to re-rank. Missing the "commitment" is not a failure signal; an idle pipeline is.
- **Assign via `save_issue`'s `cycle` param**, proposed then confirmed like any write. Only *ready* stories enter a cycle; unready ones get refined first (Story flow) or stay out.

For the capacity/selection mechanics, compose **[[sprint-planning]]** — `pm` supplies the Linear-native cycle read/write and the cadence-bucket stance; sprint-planning supplies the selection method.

## Bias guards

| Rationalization | Reality | Do instead |
|---|---|---|
| "The order is obvious, just reorder it" | Obvious to you ≠ shown. An unexplained rank is unauditable. | Show ICE (or the reason) per item, even when confident. |
| "I'll set priorities and mention it after" | A silent write violates the trust boundary. | Propose the writes, wait for confirmation. |
| "Everything ready is High" | If everything is High, nothing is. Priority requires ordering. | Force-rank; bucket by ICE tier. |
| "Emit a priority rank *and* a build order" | Two orderings that can disagree force the reader to ask which to obey; dependency leverage already lives in Impact. | One ranking; separate blocked/unready work by *state* (Backlog), not a second list. |
| "It's blocked, so drop its priority" | Importance didn't change, only actionability did — demoting hides that it still matters (and that unblocking it is valuable). | Keep the priority; move it to Backlog. The lane carries "can't start yet." |
| "It's important, so put it in Todo" | Todo means *startable*, not important. An important blocked/epic item in Todo misleads whoever pulls next. | Gate Todo on unblocked ∧ story-ready; important-but-not-ready stays in Backlog. |
| "This story is basically ready" | Ready = vertical + 3 AC + one-session-sized. | Run the two-hard-gate check; split if it fails. |
| "Score it with RICE/WSJF to look rigorous" | Reach/economics rarely change a single-scorer order; the math is theater then. | Default ICE; escalate only on the stated triggers. |
| "I remember Linear's fields" | The board and MCP surface drift. | Read states/labels/tools live first. |
| "The cycle is committed — hold the scope" | Here the cycle is a cadence bucket; a frozen scope starves a pipeline that drains in hours. | Let flow pull the next-highest-ICE ready item; re-plan at the boundary, not mid-cycle. |
| "Put it in the cycle to get it moving" | Only *ready* stories enter a cycle. | Refine to the story hard-gate first, or leave it in the backlog. |

## Composition

- **[[backlog-refinement]]** — deep story methodology (AC rubric, 7+ splitting patterns, backlog-health metrics, DoR). `pm` handles Linear-native prioritization, triage, sizing, roadmap, and all writes; it delegates heavy refinement here.
- **[[sprint-planning]]** — cycle capacity/selection method. `pm` owns the Linear cycle read/write and the cadence-bucket stance (fill, don't freeze); sprint-planning supplies how much to pull.
- **engineering / slicing** — once a story is ready and prioritized, these carry it into the PR pipeline. `pm` stops at a ready, prioritized, written story.

## Output format

Lead with the decision and its rationale, then the concrete Linear writes as a checklist the user approves:

```
PRIORITIZED (Cadre backlog, ICE):
  NEX-xxx  I8 C7 E9 → 504  → P2 High   blocks NEX-yyy
  NEX-zzz  I6 C8 E4 → 192  → P3 Medium
  ...
PROPOSED WRITES (awaiting confirm):
  - NEX-xxx: priority None → High
  - NEX-zzz: priority Urgent → Medium (over-flagged; no deadline)
Confirm and I'll apply.
```
