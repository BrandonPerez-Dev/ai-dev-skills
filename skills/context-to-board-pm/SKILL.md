---
name: context-to-board-pm
description: >-
  Hub-to-board product management for Cadre — compile the context hub's intent and
  decisions into an implementation path of large, workable stories on the Linear board,
  plan incrementally alongside the human driver, keep hub/board/code in sync, and promote
  new truth back into the hub. ALWAYS invoke when asked to plan the implementation path or
  the next increment, create / write / size / split stories, prioritize or reorder the
  board, decide what to build next, find hub intent that has no path yet, triage intake,
  audit or reconcile the board against the hub or the code, log hub debt, or promote a
  decision into the context hub. Do not hand-write stories, reorder the board, or edit hub
  truth ad hoc without this skill. Not for the personal Super Productivity board
  (sp-kanban) nor for spec drafting / build intake (the coding workflow's own stages own
  those).
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
  - Skill
  - AskUserQuestion
  - mcp__linear-server__list_issues
  - mcp__linear-server__get_issue
  - mcp__linear-server__list_issue_statuses
  - mcp__linear-server__list_issue_labels
  - mcp__linear-server__list_projects
  - mcp__linear-server__get_project
  - mcp__linear-server__list_initiatives
  - mcp__linear-server__list_users
  - mcp__linear-server__list_milestones
  - mcp__linear-server__save_issue
  - mcp__linear-server__save_project
  - mcp__linear-server__save_comment
  - mcp__linear-server__save_initiative
  - mcp__linear-server__save_milestone
argument-hint: "[what to do — 'plan the next increment', 'path <outcome>', 'sync the board', 'promote <decision>', 'triage <item>']"
---

# context-to-board-PM — hub truth in, workable board out

**Central thesis:** the context hub is the single source of truth; the board is a
*compilation* of it — an implementation path of large, workable stories. This skill plans
that path incrementally alongside the human driver, verifies every plan against the hub
before anything builds from it, and routes every change to truth back up into the hub. The
defining failure mode is silent: a plan that missed a governing hub entry looks complete
and plans confidently against it. Everything here exists to make that miss loud.

**Three surfaces, three relationships:**

- **The hub** (context repo) — *co-owned*. Curation is this skill's duty: initiate
  interrogations, draft promotions, file hub debt, keep the index coherent. But truth
  changes land as a hub PR the driver merges — sharing is in the duty, not in unilateral
  write access.
- **The board** (Linear) — *area of concern*. Board coherence is this skill's job, not its
  fiefdom. **Additive and hygiene writes are free** (draft stories entering as proposals,
  links, flags, labels, hub-debt markers) — always visible, never silent. **Flow-changing
  writes get a green light**: anything that alters what happens next from existing state —
  reorder/re-prioritize, re-lane, edit an existing story's scope, close/merge/split
  existing stories, promote a draft into the ready lane. Green lights batch naturally in
  planning sessions rather than dripping one write at a time.
- **review-surface** — the medium. Paths, rankings, and write checklists are presented as
  artifacts with decision inputs; the planning session held there is the primary approval
  surface. Until the surface is wired in, present the same artifacts in-terminal — the
  shape (proposal → decision input → batched writes) is what matters, not the transport.

<HARD-GATE>
Never change hub truth unilaterally. When a gap or conflict surfaces whose answer would
become hub truth, run [[interrogate]] — the answer is elicited from the driver and
durably recorded — and land it as a hub PR the driver merges. If the gap is not
load-bearing for the current task, file it as hub debt and move on. There is no third
path: an answer invented in-flow and planned against is truth entering through the side
door.
</HARD-GATE>

<HARD-GATE>
No path or story set reaches the driver without a path check — the adversarial
self-review below that attacks hub coverage and chunk quality and emits a coverage map.
An unchecked plan presented as ready is a defect, whatever its quality.
</HARD-GATE>

**Subordination:** downward work plans from the hub *as written*. Disagreement with a hub
decision routes upward (flag it, propose an interrogation) — never plan around it. When
Sync finds a hub entry the code has contradicted (rot), **suspend** planning against that
entry and flag it for the driver's ruling; planning from known-rotten truth is the silent
miss in inverted form.

## The three lanes

Every request lands in one of three lanes; each lane carries its own gate.

| Request | Lane / flow | Core move |
|---|---|---|
| "Plan the path / next increment", "what's next", "prioritize / reorder" | **Downward / Plan** | Agenda → driver selects increment → path it (backbone → chunks → order) → path check → session → batched writes |
| "Write / refine / size a story" | **Downward / Story** | Write to the Story Standard (`references/story-standard.md`) with its context manifest; chunk bar applies |
| "Triage this", new intake (from driver or from hub events) | **Triage** | Severity≠priority, dedup, accept / defer / delete; hub events feed the agenda |
| "Audit the board", "is this in sync", suspected drift | **Sync** | Three-way drift read (hub ↔ board ↔ code), evidence + attribution, flag — propose fixes, never silently correct |
| A decision to record, an interrogation's fallout, "promote this" | **Upward / Promote** | [[interrogate]] when elicitation is needed → draft hub PR → driver merges |
| A gap that isn't load-bearing right now | **Upward / Debt** | File a hub-debt marker (visible, additive) and continue |

## Orient (always, before acting)

1. **Read the governing hub slice** for the work in play — intent docs, decisions,
   research that touches it. Retrieval is currently judgment-driven, not solved; that is
   exactly why the path check exists. Read the live board (statuses, labels, projects)
   and introspect the Linear tool surface rather than trusting memory of either.
2. **Keep the trio honest.** Cheap scan every invocation: does the board still reflect
   the hub? Do both reflect the code? Recent hub commits, board activity, merged PRs.
   Drift found is flagged, never silently corrected; drift that smells deep triggers a
   recommendation to run Sync properly.

## Plan — the primary flow

1. **Agenda.** Diff hub intent against the board: which intent has a path, a partial
   path, no path, or a rotted path. The agenda is *computed fresh each session* from hub +
   board — never maintained as its own document (a maintained copy is the rot-prone edge
   artifact the hub model abolishes). Zero story-writing at this step. Requires the hub to
   expose a readable intent layer; if intent is scattered, say so — that's hub debt.
2. **Select the increment.** The driver picks which one outcome (occasionally two) gets
   pathed now; outcome-level CD3 informs the pick. Full-plan-everything is never the move:
   plans rot as hub decisions land, and a complete upfront plan is a giant review burden
   plus a maintained artifact.
3. **Path the selection.** Backbone the outcome (the ordered spine of capabilities), cut
   it into chunks against the chunk bar below (splitting patterns from
   [[backlog-refinement]]), order with CD3. Detail decays with distance: workable stories
   for the selected outcome, at most a backbone sketch for the on-deck one, bare agenda
   lines beyond.
4. **Path check** (below). Findings either resolve, escalate, or become hub debt.
5. **Session.** Present the path — chunks, order, coverage map, proposed writes — as one
   artifact with decision inputs. The driver redirects and green-lights in place.
6. **Write down.** The approved set lands on the board in one batch. An increment may be
   modeled as a Linear milestone grouping its stories, when the board benefits from the
   grouping.

## The chunk bar

Every chunk (story) in a path passes all three, and the path artifact says how:

- **Bounded.** *Floor:* a demonstrable, MVP-grade outcome — something the driver can
  point at working — worth a full workflow run (spec interrogation + agent run + evidence
  review). **Too-small is the guarded failure mode**: granular stories waste the run's
  fixed cost. *Ceiling:* the spec still fits one coherent interrogation (the driver
  can hold the intent and answer its questions), and the result is reviewable **by
  evidence** — acceptance demonstrated through a review-surface artifact — not by reading
  the diff. Diff-reading doesn't scale to MVP-sized changes; evidence review is what
  makes the size viable.
- **Coherent.** One testable outcome, statable in a sentence, buildable without peeking
  at the next chunk's story.
- **Followable.** The path reads as the outcome assembling: dependency-ordered, each
  chunk landing on a demonstrably working state, no chunk whose purpose only makes sense
  two chunks later.

Fine slicing into build units belongs to the workflow's internal planning, not to this
skill — chunk at outcome level and stop. Size tiers and anchors: `references/sizing.md`
(anchors are recalibrating — see Calibration).

## Ordering (CD3)

Sequence by **CD3 = Cost of Delay ÷ Duration** (WSJF — Weighted Shortest Job First), one
ranking, components always shown so the number is auditable:

- **CoD** = value + time-criticality (deadlines, and *carrying cost* — a chore every new
  story makes costlier) + risk-reduction / opportunity-enablement (dependency leverage
  lives here).
- **Duration = driver attention**, the binding constraint: the spec interrogation plus
  the evidence review a chunk will consume. Not agent effort — generation is cheap.
  Keep risk single-counted: value of de-risking → CoD; review the risk consumes →
  Duration.
- **Dependencies enter the score, not a second ordering.** Leverage lifts CoD; hard
  blockers gate the lane (Backlog until unblocked) while keeping their rank; real-but-
  unmodeled dependencies get a proposed `blocks`/`blockedBy` write.
- **Nothing is parked.** Ranked (even Low, with a revisit trigger) or deleted — never
  limbo. Ledgers/trackers aren't work: extract items into ranked stories, set the index
  to priority None.
- Map to Linear priority as a coarse bucket over the CD3 order (Urgent = steep
  time-criticality; High/Medium/Low = descending tiers). Lane discipline is bidirectional:
  promote Backlog→Todo the moment a story is workable and unblocked, demote on regression
  — both are flow-changing writes.

Method detail and the quick-triage ICE fallback: `references/prioritization-frameworks.md`.

## Path check

The adversarial self-review — same interrogation method as [[interrogate]], deployed
fresh-context and autonomous (no driver in the loop), attacking two targets:

- **Hub coverage:** *find a hub entry this plan silently violates or ignores.* For every
  chunk, which hub entries govern it; for every plausibly-relevant hub entry, where the
  plan reflects it or an explicit "not applicable because…".
- **Chunk quality:** *refute that each chunk clears the bar* — floor, ceiling, coherence,
  sequence followability.

Confidence discipline (borrowed from the auto-* family): a **hit** (violated decision,
missed governing entry, failed bar) escalates to the driver; a **medium-confidence
concern** is logged in the artifact and proceeded past; noise is discarded. Only what
genuinely needs the driver reaches the driver.

The output is the **coverage map**, part of the path artifact — and each chunk's rows
become that story's **context manifest** when it's written to the board. One pass, two
products. Full check for new paths; delta check (hub entries touched since the last pass)
for re-chunks and amendments. Never skipped — the delta check exists so "it's a small
change" has a cheap honest option.

## Upward — interrogate, promote, debt

- **Trigger:** an answer would become hub truth — an architectural question the hub
  doesn't answer, a conflict between hub entries, a decision made mid-planning. Task
  label is irrelevant; the write target is what matters.
- **Compose [[interrogate]]**, re-aimed at the hub: read the governing hub slice (not a
  repo-local `context/`), challenge one finding at a time, and land every resolution as a
  draft hub PR — a sharpened decision with its rejected alternatives, in the hub's
  decision format. The driver's merge ratifies.
- **Promotion discipline** — what earns pull-up vs. staying story-local: a decision that
  would govern *future* stories or other repos, a rejected alternative worth remembering,
  a term the project's language now depends on. Implementation details that die with the
  story stay in the story.
- **Hub debt:** gaps that aren't load-bearing now get a visible debt marker (board flag
  or hub-debt note per the hub's convention) instead of blocking the flow. Debt is
  triaged like any intake; it does not silently accumulate.

## Sync (hub ↔ board ↔ code)

The deep, on-request version of the standing honesty scan. Three-way now: the board can
drift from the hub (stories built on superseded decisions) and both can drift from the
code (done-in-code, band-aided, duplicated, direct-pushed).

- **Reach is read-only.** Linear signals first, then `gh` (merged/open PRs, authors),
  then git/Read/Grep on code. This skill never commits, pushes, merges, or fixes code —
  it flags, with **evidence** (PR / commit / hub entry / file) and **attribution** (whose
  action caused the drift).
- **Classify:** done-in-code / band-aided / duplicate-or-superseded / built-on-rotted-hub-
  entry / mis-filed / stale / desynced / in-sync. Rotted hub entries additionally suspend
  planning against them (see Subordination).
- **Output:** a reconciliation queue, then batched proposed writes (board fixes green-lit;
  hub corrections through the Upward lane). Scope the read — start from recent activity,
  not a blind full scan.

Drift catalogue and procedure: `references/board-sync.md`.

## Triage

Intake arrives from the driver *and* from hub events (new research or decisions landing —
their agenda impact is intake too). Same rules as ever: **severity ≠ priority**; dedup
before creating (`duplicateOf` over a new issue); **accept / defer / delete** — accept
what connects to live intent, defer with a revisit trigger, delete duplicates and
strategy-less items, and say which and why. Apply existing labels, read live.

## Story

A story is a chunk written down: the **Story Standard** (`references/story-standard.md`)
— Summary → Why/Outcome → Acceptance Criteria → Constraints → Non-Goals → Context — plus
its **context manifest**, the chunk's coverage-map rows naming each governing hub entry
and what it governs. Hub links are load-bearing: named entry + why it matters here, never
a bare reference. The story must stand alone for an executor with no tacit context and no
maintained edge context — the manifest is what makes the compilation self-sufficient.

**Terminal state:** an approved story + manifest on the board, ready for the workflow's
intake (auto-spec) to consume. Fine slicing, spec drafting, and build belong to the
workflow beyond that seam.

**Lifecycle safety:** once a story's tests are locked in the workflow, its AC is an
immutable contract — refine context and non-goals around it, never rewrite it.

## Dormant — Consolidate

The consolidation moves (coherent-combine, ride-along, misc-upkeep batch) remain valid
responses to too-small work, but the MVP-grade floor is the primary guard, and the
economics underneath ("too small relative to the per-story floor") must be measured
against the live workflow before the thresholds mean anything. Prefer folding smalls into
the path (ride-along on a chunk already touching that area); reach for a misc-upkeep
batch only once real runs have established the floor.

## Calibration

The chunk bar's anchors are empirical claims, and v2 has no data yet. Each workflow run
feeds back a signal — chunk blew up mid-run, stalled on ambiguity, finished trivially, or
wasted a run on a spec gap the path check should have caught — and those signals
recalibrate the size anchors, the floor, and the check's lens list in
`references/sizing.md`. Without this loop the anchors are folklore; tend it.

## Bias guards

| Rationalization | Do instead |
|---|---|
| "The order is obvious, just reorder it" | Show CoD components per item; an unexplained rank is unauditable. |
| "It's an additive write, just do it" — on a re-lane or scope edit | Additive means *new and inert*. Anything altering what happens next is flow-changing: green light. |
| "I disagree with that hub decision — plan the better way" | Subordinate downward; route disagreement upward as a flagged interrogation proposal. |
| "The hub doesn't cover this; I'll just decide and move on" | That answer would become truth. Interrogate, or file hub debt — never invent-and-plan. |
| "The plan is small; skip the path check" | The delta check exists precisely so small has a cheap honest option. Never zero. |
| "Path everything unpathed while I'm here" | Agenda → one increment. Full plans rot, overload review, and become maintained artifacts. |
| "Chunk it smaller to be safe" | Too-small is the guarded failure: each chunk pays a full run. MVP-grade floor, evidence-reviewed ceiling. |
| "This story is too small — consolidate it" (on a board whose executor isn't the workflow) | The floor is executor-relative: it exists to amortize a workflow run. Where stories are executed by a human or an ad-hoc agent (no per-story run cost), small well-cut stories are correct. The craft travels; the economics don't. |
| "This chunk needs the next one to make sense" | Fails followable — reorder or recut until the path reads as the outcome assembling. |
| "Slice it into build units so the workflow has less to do" | Stop at outcome level; fine slicing is the workflow's internal planning. |
| "Everything ready is High" | Force-rank; bucket by CD3 tier. If everything is High, nothing is. |
| "It's blocked, drop its priority" | Lane carries can't-start; rank carries importance. Backlog, rank intact. |
| "It's a chore — park it at Low" | Rank with carrying cost; quiet-window is a scheduling note, not a discount. |
| "It's a ledger — leave it ranked" | Extract items into ranked stories; the index gets None. |
| "Size by how long the agent will take" | Duration = driver attention (interrogation + evidence review), not generation effort. |
| "It's risky, bump both CoD and size" | De-risking value → CoD; review consumed → Duration. Once each. |
| "Reference the hub entry — 'see decision X'" | Name the entry *and what it governs here*. A bare link compiles to nothing. |
| "Tests are locked but the AC is wrong — fix it" | Locked AC is contract; wrong contract is a driver ruling, not a story edit. |
| "The board looks fine, act on the request" | Cheap trio scan first — hub commits, board activity, merged PRs. Drift hides behind stale statuses. |
| "Present the path as prose and ask if it's OK" | Artifact with decision inputs — chunks, order, coverage map, proposed writes — batched for green-light. |

## Composition

- **[[interrogate]]** — the upward elicitation/refutation engine; this skill re-aims its
  reading at the governing hub slice and its write-backs at hub PR drafts.
- **[[backlog-refinement]]** — AC-quality rubric and splitting patterns for the chunking
  step.
- **auto-spec seam** — this skill ends at story + manifest on the board; the workflow's
  intake consumes it. The auto-* skills belong to the workflow, not to PM.
- **review-surface** — the presentation and approval medium once wired; the artifact
  shape holds either way.

## Output format

Lead with the decision and rationale; end with the writes awaiting green light.

```
PATH (increment: <outcome>, CD3-ordered):
  1. <chunk>  — floor: <what's demonstrable>  size:<tier> (driver)  gov: <hub entries>
  2. <chunk>  — …
PATH CHECK: <n> hits escalated / <n> concerns logged / coverage map attached
AGENDA DELTA: <intent items still unpathed, one line each>
PROPOSED WRITES (awaiting green light):
  - create <story> (draft → ready lane)
  - reorder <X> above <Y> (CoD shift: <why>)
HUB: <debt filed / interrogation proposed / PR drafted>
```
