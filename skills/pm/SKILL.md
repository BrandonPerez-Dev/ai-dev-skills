---
name: pm
description: Product-management operations on a Linear backlog for the Cadre pipeline — prioritize and order the backlog, triage intake, find what needs refinement, decompose epics into ready stories, write and refine stories, map an outcome into a story set, and plan the roadmap, all via the Linear MCP. ALWAYS invoke when asked to prioritize / order / rank the backlog, decide what to work on next, triage or groom issues, find refinement candidates or check what's sprint-ready, split / decompose an epic, write / refine / size a Linear story, plan the stories to deliver an outcome or initiative, set issue priority, plan a cycle, or plan a roadmap in Linear. Every ordering and every write shows its scoring rationale and is confirmed before it touches Linear. Do not hand-order a backlog, set priorities, or write stories ad hoc without this skill.
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
argument-hint: "[what to do — 'prioritize the Cadre backlog', 'what needs refinement', 'decompose NEX-126', 'map the stories for X', 'plan the roadmap']"
---

# PM — Linear-native product management for Cadre

**Central thesis:** the backlog's order and every issue write are *defensible* — each carries a shown score or reason, and nothing is written to Linear until the human confirms it. A silent reshuffle is a bug, not a convenience.

This skill owns the **Linear-native** layer: reading the real board, scoring and ordering work, triaging intake, finding and refining what isn't ready, writing pipeline-ready stories, and shaping the roadmap. It does not re-derive story methodology — for the deep acceptance-criteria rubric and the splitting patterns it composes [[backlog-refinement]].

<HARD-GATE>
Never write to Linear (create/update issues, set priority, reorder, move state, add relations, edit projects/initiatives) until you have shown the proposed change and its rationale and the user has confirmed. Reads are free; writes are proposed first. This is the money-and-trust boundary — batch the proposal, then execute on approval.
</HARD-GATE>

**Story-ready means** three things — the single bar for "ready," referenced throughout (Readiness lane, Story, Decompose, Cycle) rather than restated:

- **Vertical** — a user- or operator-facing outcome, not a component task.
- **Testable done** — enough testable acceptance criteria that "done" is unambiguous, including a failure/edge case *when one applies* (a pure display, a config toggle, or a chore may have none). A small handful is typical; the **count is a signal** — too few = under-specified or trivial, many = probably an epic — **not a hard floor**. Because an AI executor has none of a human's tacit context, the outcome should also be clear enough it can't be *grossly* misread — but residual ambiguity is resolved downstream (planning/grill, and soon labels), not gated to death here. (AC-quality rubric → [[backlog-refinement]].)
- **One coherent outcome the pipeline can plan-and-slice** — *not* "one session." A Cadre story becomes a feature branch the planning phase slices into build units; **multi-slice is the normal shape** (PIPE-1 was six slices). "One session" is the bar for a **slice**. It fails this only when it bundles *several distinct outcomes*, or is too large/vague for planning to slice — then it's an epic (decompose) or needs a spike.

Miss any → epic or task, not ready: decompose, slice-in-planning, or reframe.

## Always, before any write

1. **Read the live board first.** `list_issue_statuses`, `list_issue_labels`, `list_projects`, `list_cycles` for the team in play — states, labels, project/initiative structure, and whether cycles exist drift over time. The board is the source of truth.
2. **Introspect the Linear tool surface.** The MCP write set evolves; confirm the tool and its params (e.g. `save_issue` exposes `priority`, `stateId`, `projectId`, `labelIds`, `parentId`, `milestone`, and relations `relatedTo`/`blocks`/`blockedBy`/`duplicateOf`) before relying on a capability. Don't hard-code what you remember.

## Method selection

Different requests need different flows — don't run one procedure for everything. Each flow ends in proposed writes that wait for confirmation.

| Request | Flow | Core move |
|---|---|---|
| "Prioritize / order / rank", "what's next" | **Prioritize** | Sequence by CD3/WSJF (cost of delay ÷ duration; leverage & carrying-cost fold into CoD); set priority + Backlog/Todo lane; one ranking |
| "What needs refinement", "groom for readiness", "is the board ready to pull" | **Refine (discovery)** | Scan the board, classify each unready item by *why* it fails the bar, emit a ranked refinement queue |
| "Split / decompose this epic", an item bundling several outcomes | **Decompose** | Drive the multi-outcome epic into child stories written under it (`parentId`), composing [[backlog-refinement]] splitting patterns |
| "Write / refine / size a story" | **Story** | Vertical, testable-done, one coherent outcome; compose [[backlog-refinement]] |
| "Plan the stories for X", an outcome/initiative with no stories yet | **Story mapping** | Backbone of steps → a sliced story set that delivers the outcome |
| "Triage this issue", new intake | **Triage** | Classify (severity vs priority), dedup, accept/defer/delete |
| "Plan / adjust the roadmap" | **Roadmap** | Now/Next/Later over projects/initiatives |
| "Plan the cycle / sprint" | **Cycle** | Pull top-CD3 ready stories to a review-bounded capacity budget; cadence, not scope-freeze |

## Prioritize

**Default: CD3 / WSJF — cost of delay per duration.** For each candidate, estimate its **Cost of Delay** and its **duration**, and sequence by:

```
CD3 = Cost of Delay ÷ Duration        (higher = do sooner)
```

- **Cost of Delay (CoD)** = **value** (what the outcome is worth) + **time-criticality** (does its value decay, or its cost *grow*, with delay — a deadline lives here, and so does **carrying cost**: a rename every new story makes costlier has rising time-criticality) + **risk-reduction / opportunity-enablement** (does it retire risk or unblock other work — **dependency leverage** lives here: an enabler gating three stories scores high). Score the three relatively (1–10 each) and sum, or reason them qualitatively — always *show the components* so the number is auditable.
- **Duration** = rough size (slice/story effort; person-days, not points). Cheap to estimate for agent-built work.

Why CD3 over a value-only or ease-based score: sequencing a single-resource queue by weight-over-duration *provably* minimises total weighted delay (Smith's 1956 WSPT theorem), and the ready lane **is** that queue. It also keeps **value and urgency separate**, where ICE's "Impact" mushes them and its "Ease" is a weak proxy for real duration. **Caveat, honestly:** WSPT is strictly optimal only for one resource, independent jobs, all available now — we have dependencies (lane-gated below) and parallel features — so CD3 is a well-grounded *heuristic* here, not a literal optimum.

**ICE stays as a quick-triage fallback** (`Impact × Confidence × Ease`) for a fast rough cut when a full CoD estimate isn't worth it. Formulas/scales/citations: `references/prioritization-frameworks.md`.

**Map score → Linear priority** (1=Urgent … 4=Low, 0=None): a coarse bucket over the fine-grained CD3 order.

| Bucket | Rule of thumb |
|---|---|
| **1 Urgent** | Highest CoD-per-duration — active incident, hard deadline, or steep time-criticality; do first regardless of size |
| **2 High** | Next CD3 tier of the ready backlog |
| **3 Medium** | Middle tier |
| **4 Low** | Long tail; low CoD, revisit later |

**Dependencies enter the score, not a second ordering** — there is one ranking:

- **Leverage → CoD's risk/opportunity-enablement term.** An enabler is worth more *because* it unblocks others; that lifts its CoD, so the single ranking already reflects it.
- **Hard blockers gate the lane, not the rank.** A blocked item *keeps* its priority and stays in **Backlog** until unblocked (see Readiness lane).
- **Model the dependency if it's real but unmodeled** — propose the `blocks`/`blockedBy` write so the lane gate is structural, not implied in your head.

**Nothing is parked — every unit of work is a ranked queue citizen.** What used to be "off the pull queue" is re-expressed, never removed:

- **Blocked** → ranked, lane-gated to Backlog (can't-start-yet); the fix is unblocking the blocker.
- **Quiet-window / mechanical chores** → ranked with their **carrying cost**; the "quiet window" is a *scheduling note* (a *when*), not a discount on priority.
- **Trackers/ledgers** (a standing checklist that never "ships") → *not work*: extract their items into ranked stories (see Decompose), and set the ledger itself to **None** — the index isn't pullable, and `None` says "not a work item" where `Low` would falsely rank the work as low-value. Its urgency lives in the extracted stories.

The discipline that stops this becoming a wish list: an item is either **ranked** (real work, even if Low, with a revisit trigger) or **deleted** — never a limbo.

**Output:** a single ranking — `Issue | Value | Time-crit | Risk/enable | CoD | Dur | CD3 | → Priority | Lane | note` — ordered by CD3 with the CoD components shown; then the proposed writes (`priority`, `state` promotions/demotions, any `blocks`/`blockedBy`); then wait for confirmation.

## Readiness lane

Importance and actionability are different axes on different Linear mechanisms: **priority** answers *how much it matters*; **workflow state** answers *can it be started now*. Keeping them separate is what lets neither lie.

- **Backlog** = planned but not startable — unrefined, an epic, or `blockedBy` something open.
- **Todo** = the ready lane — passes **Story-ready** *and* has no open blocker. "What's ready to pull" is then a live query (`list_issues state:Todo`), the queue the intake daemon drains.

Enforce the lane **bidirectionally**: propose promoting Backlog→Todo the moment an item becomes ready, and demoting Todo→Backlog the moment one regresses (newly blocked, or found unrefined). A stale Todo misleads the puller and the daemon exactly as much as a ready item stranded in Backlog. State changes are writes: propose, then confirm. The pull order *within* Todo is just the priority ranking restricted to the ready lane — there is no separate build order.

## Refine (discovery)

Prioritize and the Readiness lane *judge* an item you hand them; discovery *finds* the items that need work. Run it when asked what to groom, what's ready, or before a cycle. It is a scan, and its output is a **ranked refinement queue**, not a per-issue verdict.

1. **Read the backlog** (`list_issues` for the project/team, Backlog + Todo).
2. **Classify each item against Story-ready**, tagging *why* it fails — the reason drives the fix:
   - **Epic** (bundles several outcomes) → route to **Decompose**. *Large-but-coherent* (one outcome, many slices) is **not** an epic — flag it "large — planning will slice it," don't hand-split.
   - **No/weak AC** (done isn't testable) → route to **Story** (AC pass).
   - **Vague / no user-facing outcome** (fails the vertical bar) → reframe in **Story**.
   - **Blocked** (`blockedBy` open) → ranked, lane-gated to Backlog; the fix is the blocker, not this item.
   - **Tracker/ledger** (a standing checklist that never ships) → extract its items into ranked stories; set the index itself to **None**.
   - **Stale** (untouched for months, no deliberate hold) → triage (defer/delete).
   - **Mis-filed lane** (ready item in Backlog, or unready in Todo) → propose the promote/demote.
   - **Aging** — surface **Work Item Age** (from Linear timestamps): an item aging in **Todo** (ready but unpulled — why? review backed up, mis-ranked, too big?) or **In Progress** (a stuck WIP item) is a prompt to *ask why*, a factor among others — not an auto-rerank, and never a term in the score.
3. **Rank the queue** by leverage: an unready item that is high-CoD or blocks others is worth refining before a low-value one. Don't just list — order by which refinement unblocks the most pull-able work.
4. **Output** a table — `Issue | why not ready | fix (Decompose / AC / reframe / unblock / extract / triage / lane) | priority` — then propose the first batch of fixes (or ask which to take first). A *multi-outcome* epic is never left as just "not ready" — name it and route to decomposition; a *large-but-coherent* story is flagged large (planning slices it), not split.

## Triage

Follow the 4-step loop (gather → categorize → reprioritize around value → pick the next increment), with these rules:

- **Severity ≠ priority.** Severity is the technical blast radius (callable from the issue). Priority is the business decision of when. A high-severity edge case affecting no one can still be low priority.
- **Dedup before creating.** `list_issues` with a `query` on the title/keywords and scan open + recent items; if it's a dup, set `duplicateOf` rather than opening a new issue.
- **Accept / Defer / Delete.** The backlog is not a wish list. Accept items with a live connection to a current project/initiative; defer valid-but-not-now with a revisit trigger; delete duplicates and strategy-less items. State which and why.
- Apply the existing team labels (read them live; don't invent).

## Story

A Cadre story is a **vertical slice, one coherent outcome** (the Story-ready bar) — the sweet spot between a component task (too small, no user value) and an epic (several outcomes bundled).

- **Refine to the bar.** Write the user-facing outcome and enough testable Given/When/Then AC that done is unambiguous (incl. an unhappy path when one applies); confirm it's one coherent outcome. For the full AC-quality rubric and the splitting patterns, **invoke [[backlog-refinement]]** — don't reproduce it here.
- **Write it into Linear** as an issue with the outcome in the title, story + AC in the description, the right project/labels, and a proposed priority from Prioritize. Pipeline-ready means the next step could open `feat/<slug>` against it.

### Decompose (epic → child stories)

When an item bundles **several distinct outcomes** (the size failure from Story-ready — not merely *large*), it's an epic — turn it into ready stories. A *large-but-coherent* story (one outcome, many slices) is **not** an epic: leave it whole, flag it "large — planning will slice it," and don't hand-split what the pipeline slices natively.

1. **Split** with [[backlog-refinement]]'s patterns (find the core complexity, pick one axis of variation, reduce to a single case, defer the rest). Prefer splits that let you *throw one away* and that yield equal-sized small stories.
2. **Each child must clear Story-ready on its own** — vertical, testable-done, one coherent outcome. A split that yields "build the schema" + "build the API" is horizontal; try again.
3. **Propose the writes as a set:** keep the epic as the parent (or convert it), and `save_issue` each child with `parentId` set to it, a proposed priority, and the ready lane if unblocked. Show the parent→children tree and the per-child AC before writing anything.

## Story mapping

Prioritize orders stories that exist; mapping *creates the set* for an outcome or initiative that has none yet — the missing rung between a roadmap horizon and a written story.

1. **Anchor on the outcome** (from the roadmap initiative or the user): the user/operator result the set must deliver.
2. **Lay the backbone** — the sequence of steps a user takes to reach that outcome (the horizontal spine of a story map).
3. **Slice the first viable walk** — the thinnest set of stories that carries someone end-to-end through the backbone once; deeper variations become later stories under each step.
4. **Each story clears Story-ready** (compose [[backlog-refinement]] for AC and sizing); flag the ones that are still epic-sized for a later Decompose pass rather than forcing them now.
5. **Propose the set** as a tree (backbone → first-walk stories → deferred variations) with priorities, then write on confirm. The output is a *plan of stories*, ordered, not a single story.

## Roadmap

Model the roadmap as **Now / Next / Later** — three horizons of decreasing certainty, which fits continuous shipping better than dated timelines:

- **Now** — active or next-up; high certainty; concrete stories.
- **Next** — weeks out; medium certainty; shaped but not fully sliced.
- **Later** — direction; low certainty; themes, not stories.

Represent it in Linear with **initiatives** (strategic themes) linking **projects** (deliverables); horizon lives in project state/priority or a Now/Next/Later label. When you find a project with no initiative, surface it — an unlinked project is invisible to the roadmap view. Later/Next work is what eventually becomes a cycle's Now; when a Next initiative is ready to break down, that's a **Story mapping** pass.

## Cycle

The team runs **2-week cycles** as a **cadence bucket, not a committed sprint** — a planning-and-review rhythm, not a scope freeze. Flow continues underneath: when a build session finishes a story, the pipeline pulls the next-highest-CD3 ready item regardless of cycle boundaries. A frozen 2-week scope would only starve a pipeline that drains in hours.

- **Fill, don't freeze.** Pull the top-CD3 *ready* stories (Story-ready) into the cycle up to a rough capacity budget. Gauge that budget against the real binding constraint — **human review capacity**, not agent generation: an over-full ready lane just backs up at the merge gate. Surface that awareness in planning, but **never gate a ready story out of the lane on it** — the ready lane stays gated purely on readiness. Overflow stays in the backlog at its ranked position, free to be pulled early.
- **The cycle is a checkpoint, not a contract.** A lightweight plan at the start, a velocity/retro read at the end. An idle pipeline is the failure signal, not a missed "commitment."
- **Assign via `save_issue`'s `cycle` param**, proposed then confirmed. Only ready stories enter; unready ones get refined first (Story / Decompose) or stay out.

For the capacity/selection mechanics, compose **[[sprint-planning]]**.

## Bias guards

| Rationalization | Do instead |
|---|---|
| "The order is obvious, just reorder it" | Show the CoD components (or the reason) per item, even when confident — an unexplained rank is unauditable. |
| "I'll set priorities and mention it after" | Propose the writes, wait for confirmation. A silent write violates the trust boundary. |
| "Everything ready is High" | Force-rank; bucket by CD3 tier. If everything is High, nothing is. |
| "Emit a priority rank *and* a build order" | One ranking; separate blocked/unready work by *state* (Backlog), not a second list. Dependency leverage already lives in CoD. |
| "It's blocked, so drop its priority" | Keep the priority; move it to Backlog. The lane carries "can't start yet," not the rank. |
| "It's an epic — decompose it" | First check: *several outcomes* (epic → decompose) or *one big outcome, many slices* (large → planning slices it, don't hand-split)? |
| "It's a chore/rename — park it at Low" | Rank it with its **carrying cost** (cheap-now-expensive-later sequences early); record any quiet-window as a scheduling *note*, not a low priority. |
| "It's a ledger — leave it in Backlog" | A ledger isn't work — extract its items into ranked stories; set the index to **None** (never Low). |
| "No third AC, so it's not ready" | Ready = enough testable AC that done is unambiguous; a small slice may need 1–2. Don't pad to hit a number. |
| "Refine the whole backlog to be safe" | Refine deeply for the next 2-3 cycles; leave far-out items coarse. Over-refinement is waste. |
| "I remember Linear's fields" | Read states/labels/tools live first; the board and MCP surface drift. |
| "Just rank by value / impact" | Sequence by **cost of delay ÷ duration** — a high-value but long story can sit below a cheap, time-critical one. Show the CoD components. |
| "It's aging — bump it up" | Age is a *diagnostic*, not a priority term. Ask *why* it's aging (blocked? review backed up? mis-ranked?) and fix that; don't auto-rerank on age. |
| "Fill the ready lane to agent throughput" | The binding constraint is **human review**, not generation. Gauge cycle fill against review capacity — but never hold a *ready* item out of the lane on it. |

## Composition

- **[[backlog-refinement]]** — deep story methodology (AC rubric, splitting patterns, backlog-health metrics, DoR). `pm` handles Linear-native prioritization, triage, discovery, sizing, roadmap, and all writes; it delegates heavy refinement here.
- **[[sprint-planning]]** — cycle capacity/selection method. `pm` owns the Linear cycle read/write and the cadence-bucket stance.
- **engineering / slicing** — once a story is ready and prioritized, these carry it into the PR pipeline. `pm` stops at a ready, prioritized, written story.

## Output format

Lead with the decision and its rationale, then the concrete Linear writes as a checklist the user approves:

```
PRIORITIZED (Cadre backlog, CD3 = CoD ÷ duration):
  NEX-xxx  val8 tc6 risk9 → CoD23 /dur2 = 11.5  → P2 High   enables NEX-yyy
  NEX-zzz  val6 tc2 risk3 → CoD11 /dur4 = 2.8   → P3 Medium
PROPOSED WRITES (awaiting confirm):
  - NEX-xxx: priority None → High
  - NEX-zzz: priority Urgent → Medium (over-flagged; no deadline)
Confirm and I'll apply.
```
