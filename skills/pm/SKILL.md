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

**Story-ready means** a **vertical slice** (a user- or operator-facing outcome, not a component task), **3+ testable acceptance criteria**, and a size **one AI build session can finish**. Missing any of the three → it's an epic or a task, not a ready story: decompose or reframe it. This definition is referenced throughout (Readiness lane, Story, Decompose, Cycle) rather than restated — it is the single bar for "ready."

## Always, before any write

1. **Read the live board first.** `list_issue_statuses`, `list_issue_labels`, `list_projects`, `list_cycles` for the team in play — states, labels, project/initiative structure, and whether cycles exist drift over time. The board is the source of truth.
2. **Introspect the Linear tool surface.** The MCP write set evolves; confirm the tool and its params (e.g. `save_issue` exposes `priority`, `stateId`, `projectId`, `labelIds`, `parentId`, `milestone`, and relations `relatedTo`/`blocks`/`blockedBy`/`duplicateOf`) before relying on a capability. Don't hard-code what you remember.

## Method selection

Different requests need different flows — don't run one procedure for everything. Each flow ends in proposed writes that wait for confirmation.

| Request | Flow | Core move |
|---|---|---|
| "Prioritize / order / rank", "what's next" | **Prioritize** | Score with ICE (dependency leverage folded into Impact); set priority + Backlog/Todo lane; one ranking |
| "What needs refinement", "groom for readiness", "is the board ready to pull" | **Refine (discovery)** | Scan the board, classify each unready item by *why* it fails the bar, emit a ranked refinement queue |
| "Split / decompose this epic", an item that fails the size bar | **Decompose** | Drive the epic into child stories written under it (`parentId`), composing [[backlog-refinement]] splitting patterns |
| "Write / refine / size a story" | **Story** | Vertical slice, agent-sized, 3+ AC; compose [[backlog-refinement]] |
| "Plan the stories for X", an outcome/initiative with no stories yet | **Story mapping** | Backbone of steps → a sliced story set that delivers the outcome |
| "Triage this issue", new intake | **Triage** | Classify (severity vs priority), dedup, accept/defer/delete |
| "Plan / adjust the roadmap" | **Roadmap** | Now/Next/Later over projects/initiatives |
| "Plan the cycle / sprint" | **Cycle** | Pull top-ICE ready stories to a capacity budget; cadence, not scope-freeze |

## Prioritize

**Default scorer: ICE.** For each candidate, score three factors 1–10 and multiply:

```
ICE = Impact × Confidence × Ease        (higher = do sooner)
```

- **Impact** — how much this moves the goal if it works.
- **Confidence** — how sure you are of the impact/effort estimate (your evidence, not a vibe).
- **Ease** — inverse of effort; a one-session change scores high, a multi-week epic scores low.

ICE is multiplicative (not an average) and has **no reach term** — the right default for a single scorer on a fast, continuous-flow team where estimation is cheap and throughput is high. Show the three numbers and the product for every item; the score is worthless if the reader can't see why one item beat another.

**When to leave ICE (author-set — research on framework routing was inconclusive, so adjust with the driver):**
- **RICE** = `(Reach × Impact × Confidence) / Effort` — only when candidates differ wildly in how many users they touch, so Reach changes the order. Effort is person-days here, not months.
- **WSJF** = `Cost of Delay / Job Size` — at the **initiative/project** level for economic sequencing, not individual issues.

Formulas, scales, and citations: `references/prioritization-frameworks.md` — read before applying RICE or WSJF.

**Map score → Linear priority** (1=Urgent … 4=Low, 0=None): a coarse bucket over the fine-grained score.

| Bucket | Rule of thumb |
|---|---|
| **1 Urgent** | Blocks others, active incident, or a hard external deadline — time-critical regardless of ICE |
| **2 High** | Top ICE tier of the ready backlog |
| **3 Medium** | Middle ICE tier |
| **4 Low** | Long tail; revisit later |

**Dependencies feed the score; they are not a second ordering.** There is one ordering principle — priority — and dependencies enter it two ways, never as a parallel "build order":

- **Leverage → Impact.** An item that unblocks others is more impactful *because* it unblocks them — fold that into its Impact (an enabler gating three stories outscores its standalone value). The single ranking then already reflects it.
- **Hard blockers gate the lane, not the rank.** A blocked item *keeps* its priority — importance doesn't fall because you can't start yet — and stays in **Backlog** until unblocked (see Readiness lane).
- **Model the dependency if it's real but unmodeled** — propose the `blocks`/`blockedBy` write so the lane gate is structural, not implied in your head.

Non-sequenceable work — trackers/ledgers (a standing checklist that never "ships") and quiet-window chores (wide mechanical changes best run when nothing's in flight) — isn't low-priority, it's *off the pull queue*: it lives in Backlog and is named as such.

**Output:** a single ranking — `Issue | Impact | Confidence | Ease | ICE | → Priority | Lane | note` — ordered by score; then the proposed writes (`priority`, `state` promotions/demotions, any `blocks`/`blockedBy`); then wait for confirmation.

## Readiness lane

Importance and actionability are different axes on different Linear mechanisms: **priority** answers *how much it matters*; **workflow state** answers *can it be started now*. Keeping them separate is what lets neither lie.

- **Backlog** = planned but not startable — unrefined, an epic, or `blockedBy` something open.
- **Todo** = the ready lane — passes **Story-ready** *and* has no open blocker. "What's ready to pull" is then a live query (`list_issues state:Todo`), the queue the intake daemon drains.

Enforce the lane **bidirectionally**: propose promoting Backlog→Todo the moment an item becomes ready, and demoting Todo→Backlog the moment one regresses (newly blocked, or found unrefined). A stale Todo misleads the puller and the daemon exactly as much as a ready item stranded in Backlog. State changes are writes: propose, then confirm. The pull order *within* Todo is just the priority ranking restricted to the ready lane — there is no separate build order.

## Refine (discovery)

Prioritize and the Readiness lane *judge* an item you hand them; discovery *finds* the items that need work. Run it when asked what to groom, what's ready, or before a cycle. It is a scan, and its output is a **ranked refinement queue**, not a per-issue verdict.

1. **Read the backlog** (`list_issues` for the project/team, Backlog + Todo).
2. **Classify each item against Story-ready**, tagging *why* it fails — the reason drives the fix:
   - **Epic** (fails the size bar) → route to **Decompose**.
   - **No/weak AC** (fails the testable-criteria bar) → route to **Story** (AC pass).
   - **Vague / no user-facing outcome** (fails the vertical bar) → reframe in **Story**.
   - **Blocked** (`blockedBy` open) → keep in Backlog; the fix is the blocker, not this item.
   - **Stale** (untouched for months, no deliberate hold) → triage (defer/delete).
   - **Mis-filed lane** (ready item in Backlog, or unready in Todo) → propose the promote/demote.
3. **Rank the queue** by leverage: an unready item that is high-ICE or blocks others is worth refining before a low-value one. Don't just list — order by which refinement unblocks the most pull-able work.
4. **Output** a table — `Issue | why not ready | fix (Decompose / AC / reframe / unblock / triage / lane) | priority` — then propose the first batch of fixes (or ask which to take first). An epic is never left as just "not ready": name that it's an epic and that the fix is decomposition.

## Triage

Follow the 4-step loop (gather → categorize → reprioritize around value → pick the next increment), with these rules:

- **Severity ≠ priority.** Severity is the technical blast radius (callable from the issue). Priority is the business decision of when. A high-severity edge case affecting no one can still be low priority.
- **Dedup before creating.** `list_issues` with a `query` on the title/keywords and scan open + recent items; if it's a dup, set `duplicateOf` rather than opening a new issue.
- **Accept / Defer / Delete.** The backlog is not a wish list. Accept items with a live connection to a current project/initiative; defer valid-but-not-now with a revisit trigger; delete duplicates and strategy-less items. State which and why.
- Apply the existing team labels (read them live; don't invent).

## Story

A Cadre story is a **vertical slice, agent-sized** (the Story-ready bar) — the sweet spot between a component task (too small, no user value) and an epic (too big for one session).

- **Refine to the bar.** Write the user-facing outcome, 3+ testable Given/When/Then AC, and confirm one-session sizing. For the full AC-quality rubric and the splitting patterns, **invoke [[backlog-refinement]]** — don't reproduce it here.
- **Write it into Linear** as an issue with the outcome in the title, story + AC in the description, the right project/labels, and a proposed priority from Prioritize. Pipeline-ready means the next step could open `feat/<slug>` against it.

### Decompose (epic → child stories)

When an item fails only the size bar, it's an epic — don't park it as "not ready," turn it into ready slices:

1. **Split** with [[backlog-refinement]]'s patterns (find the core complexity, pick one axis of variation, reduce to a single case, defer the rest). Prefer splits that let you *throw one away* and that yield equal-sized small stories.
2. **Each child must clear Story-ready on its own** — vertical, 3+ AC, one session. A split that yields "build the schema" + "build the API" is horizontal; try again.
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

The team runs **2-week cycles** as a **cadence bucket, not a committed sprint** — a planning-and-review rhythm, not a scope freeze. Flow continues underneath: when a build session finishes a story, the pipeline pulls the next-highest-ICE ready item regardless of cycle boundaries. A frozen 2-week scope would only starve a pipeline that drains in hours.

- **Fill, don't freeze.** Pull the top-ICE *ready* stories (Story-ready) into the cycle up to a rough capacity budget (recent throughput, not a story-point ceremony). Overflow stays in the backlog at its ranked position, free to be pulled early.
- **The cycle is a checkpoint, not a contract.** A lightweight plan at the start, a velocity/retro read at the end. An idle pipeline is the failure signal, not a missed "commitment."
- **Assign via `save_issue`'s `cycle` param**, proposed then confirmed. Only ready stories enter; unready ones get refined first (Story / Decompose) or stay out.

For the capacity/selection mechanics, compose **[[sprint-planning]]**.

## Bias guards

| Rationalization | Do instead |
|---|---|
| "The order is obvious, just reorder it" | Show ICE (or the reason) per item, even when confident — an unexplained rank is unauditable. |
| "I'll set priorities and mention it after" | Propose the writes, wait for confirmation. A silent write violates the trust boundary. |
| "Everything ready is High" | Force-rank; bucket by ICE tier. If everything is High, nothing is. |
| "Emit a priority rank *and* a build order" | One ranking; separate blocked/unready work by *state* (Backlog), not a second list. Dependency leverage already lives in Impact. |
| "It's blocked, so drop its priority" | Keep the priority; move it to Backlog. The lane carries "can't start yet," not the rank. |
| "It's an epic — just mark it not-ready and move on" | Name it an epic and decompose it into ready child stories. "Not ready" without the fix is a dead end. |
| "Refine the whole backlog to be safe" | Refine deeply for the next 2-3 cycles; leave far-out items at epic level. Over-refinement is waste. |
| "I remember Linear's fields" | Read states/labels/tools live first; the board and MCP surface drift. |

## Composition

- **[[backlog-refinement]]** — deep story methodology (AC rubric, splitting patterns, backlog-health metrics, DoR). `pm` handles Linear-native prioritization, triage, discovery, sizing, roadmap, and all writes; it delegates heavy refinement here.
- **[[sprint-planning]]** — cycle capacity/selection method. `pm` owns the Linear cycle read/write and the cadence-bucket stance.
- **engineering / slicing** — once a story is ready and prioritized, these carry it into the PR pipeline. `pm` stops at a ready, prioritized, written story.

## Output format

Lead with the decision and its rationale, then the concrete Linear writes as a checklist the user approves:

```
PRIORITIZED (Cadre backlog, ICE):
  NEX-xxx  I8 C7 E9 → 504  → P2 High   blocks NEX-yyy
  NEX-zzz  I6 C8 E4 → 192  → P3 Medium
PROPOSED WRITES (awaiting confirm):
  - NEX-xxx: priority None → High
  - NEX-zzz: priority Urgent → Medium (over-flagged; no deadline)
Confirm and I'll apply.
```
