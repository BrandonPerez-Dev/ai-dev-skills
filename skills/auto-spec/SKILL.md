---
name: auto-spec
description: >-
  Pipeline intake stage (S0) as a deep skill: story → planning artifact → planning PR.
  Orchestrates by change difficulty, drafts the spec in a two-layer driver-first
  structure, then runs a fresh-context adversarial critic (interrogate lenses +
  legibility) and revises before the driver ever reads it. Only questions that
  genuinely need the driver survive as PR review comments. Owns all intake
  mechanics: feature branch, tracking issue, planning branch/PR, state.json.
when_to_use: >-
  Fired by the pipeline runner's intake stage prompt with a story and branch
  bindings. Do NOT use for interactive planning — use engineering + slicing for
  that. The daemon's interrogate stage (driver-thread processing) is
  auto-interrogate, not this skill.
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
  - Agent
argument-hint: "[story text or kickoff path; runner supplies branch/issue bindings]"
effort: high
---

# Auto Spec

One stateless run: story in, planning PR out — with the spec already interrogated and rewritten *before* the driver sees it. The runner's ground rules (never merge, marker on every post, never push to the default branch) bind throughout.

Merging the planning PR is the driver's approval gate for scope. That makes the spec's **human legibility load-bearing**: a spec the driver can't parse fast turns the gate into a rubber stamp. Everything below serves two goals — decision quality and driver reading cost.

## Inputs

From the runner's stage prompt: story text/id/title, `$feature_branch`, `$planning_branch`, `$default_branch`, variant (`change-spec` | `spec-as-source`), tracking-issue conventions, agent marker. If a previous intake attempt left partial work (branch/issue/PR exists), resume and repair — never duplicate.

## Process

### 1. Mechanics

1. `git fetch origin`; create `$feature_branch` off `origin/$default_branch`; create `.pipeline/state.json` (runner schema, `"stage": "interrogate"`, slices empty); commit, push with `-u`.
2. Create `$planning_branch` off `$feature_branch` — exactly that name; the daemon routes by it.

### 2. Load context

Read the codebase before planning anything: stack, conventions, structure, existing tests, prior specs/decisions (`changes/`, `context/`, `spec/` as the variant provides). Invoke the **investigating** skill for anything non-obvious (unfamiliar APIs, feasibility questions); dated findings land in the artifact's record layer, cited.

<HARD-GATE>
Do not plan against an imagined architecture. Read the code the change touches.
</HARD-GATE>

### 3. Orchestrate — size the effort to the change

Classify the change and let the tier set the budget for everything downstream:

| Tier | Signals | Critic rounds | Spec ceiling (read layer) |
|---|---|---|---|
| **Small** | One seam, obvious approach, ≤2 slices | 1 | ~1 screen |
| **Medium** | Multiple seams or one open design question | 2 | ~2 screens |
| **Large** | Cross-cutting, prior-decision conflicts likely, ≥4 slices | 2 + deep refutation | ~3 screens; consider telling the driver to split the story |

The ceiling bounds the **read layer** (below), not the record layer. A scope that could be settled in a few prompts must not become a 300-line spec.

### 4. Positive pass — draft the spec

Derive scope with the slicing skill's methodology in autonomous mode: no user checkpoints; reasoning, alternatives, and non-goals go in the artifact instead. Propose the slice list (and, when the target repo's pipeline supports flow-as-data rosters, the roster block: story-level flow + per-slice flows, with every omitted default node justified by name).

- Variant **change-spec**: write `changes/<story_slug>/change-spec.md` per the structure standard below.
- Variant **spec-as-source**: land scope as `spec/*.md` stubs + `context/*.md` ADR entries per the engineering skill's model; the structure standard applies to each spec stub's body.

Classify confidence per decision (high / assumption / open). Bias security, data-model, and deletion semantics toward open.

### 5. Adversarial pass — fresh-context critic

Spawn a **subagent critic with fresh context** (Task tool). Give it only: the story text, the drafted artifact(s), and the repo path. Do **not** pass your planning reasoning — the critic must reconstruct or fail to reconstruct the design's justification from what a reader would actually have; that failure is itself a finding.

The critic runs all of these lenses and returns findings with severity (blocking / should-fix / minor):

- **Structure & tensions** — cardinality, state ownership, ordering/idempotency, error propagation; prefer challenges whose answer changes a contract.
- **Terminology** — collisions with the codebase's and prior specs' existing language.
- **Prior-decision conflicts** — name the conflict, propose keep-or-supersede; never leave both implicitly in effect.
- **Necessity & scope** — observed demand, the one-branch simpler version, concept budget, wiring completeness (spec'd-but-unwired is a defect).
- **Refutation attempt** — the strongest case against doing this at all, resolved explicitly.
- **Legibility (driver-read test)** — does the opening hook a reader who doesn't have the story paged in (intent before mechanism)? Can they find every decision that needs them within the first screen? Grasp the whole change in two minutes? Any section where history/rationale is interleaved into a decision statement? Any compression that costs clarity (fragments, unexpanded jargon, arrow chains)?

### 6. Revise — and repeat per the tier's round budget

Fix what you accept; where you reject a finding, record it as a rejected alternative in the record layer with the why-not. Re-run the critic (fresh subagent, current draft) until the round budget is exhausted or only minor findings remain. Apply the same lenses yourself to any scope a revision *added* — fixes must not smuggle in unexamined additions.

**Only findings that survive revision AND genuinely need a human call become driver-facing questions.** Everything you could resolve yourself, you already did — the driver adjudicates decisions, not your first draft.

### 7. Planning PR + surviving questions

1. Commit and push the artifact(s).
2. Open the planning PR (base `$feature_branch`, head `$planning_branch`, title `[planning] <story_id>: <title>`). Body, in order: the **story hook** (see below), a link to the board story, the slice list, the self-interrogation counts, and a **"How to drive this PR"** section (line comments / review to discuss; summon token in backticks; merge = approve scope and start contract authoring).
3. Post surviving driver questions as **one PR review** of line comments on the relevant artifact lines, each with your recommendation and what it blocks. Review body: `Self-interrogation: N findings resolved internally, M need you — see threads.` The internal-resolution count is signal, not ceremony: it tells the driver the spec was already pressured.
4. Update `.pipeline/state.json` on `$feature_branch` (planning PR number, slices `"stage": "pending"`); commit, push.

**The story hook.** The PR body and the spec's What & why each open by getting a cold reader up to speed — someone who wrote the story weeks ago or has never seen it. State what you understand the story's *intent* to be, in the story's own terms (the problem it names, why it matters), before any mechanism or design detail. A reader should know what is about to be discussed and why they should care before the first technical noun. Opening with your solution's internals ("the dispatcher fires builds off tests-merge…") fails a reader who doesn't have the story paged in.

## Spec structure standard — two layers

Writing like a research paper: abstract and conclusions first, method and receipts after. The driver should never have to read layer 2 to act.

**Layer 1 — the read (first screen(s), bounded by the tier ceiling):**

1. **What & why** — ≤4 sentences opening with the story hook: the story's intent in its own terms, then what this change is, why now, and what it deliberately is not. Reader baseline before technical detail.
2. **Driver calls** — the open questions, first, each one line: the question, your recommendation, what it blocks. If none: "No driver calls — merge when the scope reads right."
3. **Decisions** — table or tight list: decision · one-line rationale · confidence. Statements only; no history, no thread references.
4. **Slices** (and roster, when supported) — name, one-line "does," dependency order.

**Layer 2 — the record (everything below a `---`):**

Rationale in full, rejected alternatives with the why-not, research citations, and interrogation provenance. Later revision rounds (auto-interrogate) update layer 1 statements in place and append their provenance *here* — decision sections never accrete history.

**Sentence-level bar:** terse means selective, not compressed. Complete sentences; one precise sentence over a paragraph; a table over a prose enumeration; expand jargon a driver skimming at speed would trip on; cut restatement, hedging, and ceremony. Dense *and* parseable — if forced to choose, parseable wins.

## Anti-patterns

| Anti-pattern | Fix |
|---|---|
| Shipping draft one + a pile of open threads | The critic loop exists so the driver reviews a pressured spec, not a first draft. |
| Critic as self-grading in the same context | Fresh subagent, blind to your reasoning. |
| Every finding becomes a driver question | Resolve at your confidence; the driver gets decisions only they can make. |
| History interleaved into decisions | Layer 1 states; layer 2 remembers. |
| Terse-as-compression | Fragments and arrow chains are reading debt, not brevity. |
| Legibility pass skipped on "simple" stories | Small tier still gets one critic round — legibility lens included. |
| Asking before trying to answer | Research first; a question posted with no best-guess recommendation is unfinished work. |
| Opening with mechanism instead of the story hook | The reader doesn't have the story paged in; give them its intent before your design. |

## Output

A pushed feature branch + planning branch, tracking issue, `.pipeline/state.json`, and a planning PR whose artifact meets the structure standard — self-interrogated, with only genuinely-human questions posted as review threads. Downstream: the driver comments (auto-interrogate handles the threads) and merges to start contract authoring.
