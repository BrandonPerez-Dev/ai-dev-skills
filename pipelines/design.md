# PR-Gated Pipeline — Conceptual Design v1 (2026-07-14)

Two automated versions of the engineering pipeline, driven entirely through the GitHub UI. The human never opens Claude Code; the agent never acts unsummoned. One shared core, two thin variants.

- **Variant A — spec-as-source.** `spec/` + `context/` are durable product artifacts; the codebase must stay true to them (audited).
- **Variant B — change-level spec.** For existing codebases and teams: no durable spec adoption; each change carries its own plain-English change spec (file-level details + repo map). The team sees the change spec and the final PR, nothing else.

Two design principles:

1. **The repo is the state machine.** Phase, decisions, contracts, and progress all live in branches and PRs; every triggered run is stateless and reconstructs from what it reads.
2. **Merge-driven advancement.** Every stage delivers its output as a PR into the feature branch. Reviewing that PR is the conversation; **merging it is the approval AND the trigger for the next stage.** No separate `/approve` commands — GitHub's merge button is the gate. The feature branch only ever contains merged, approved work, so the branch that finally PRs to main is clean by construction.

---

## 1. Actors

| Actor | Role |
|---|---|
| **Driver** (you) | Summons the agent, reviews each stage PR (line comments, review batches), merges stage PRs to approve + advance. GitHub UI only. |
| **Agent runs** | Stateless runs, one per event. Each run: read state → do stage work → push/comment/open PR → update state. Two interchangeable runners (§2.6). |
| **Team** (Variant B; A optional) | Sees only the fresh final feature→main PR (+ change spec, walkthrough, quiz). Normal human review. |

## 2. Shared core

### 2.1 Stage advancement and the story anchor

The lifecycle is a chain of **stage PRs into the feature branch**:

```
intake ──▶ [Planning PR] ──merge──▶ [Contract PR × slice] ──merge──▶ [Tests PR (slice)]
             ▲ interrogate here                ▲ contract review              ▲ test-code review
                                                                        ──merge──▶ [Build PR (slice)]
all slices built ──▶ assembly ──▶ [fresh Final PR: feature → main] ──▶ team review ──▶ merge ──▶ post
```

- **Trigger rule:** a stage PR merging into the feature branch fires the dispatcher, which reads `state.json`, checks the merged PR is the one the state expects (phase-lock), and starts the next stage. Merges are serialized by git, which removes most label-race concerns from v0.
- **Slices flow independently** once their contract PR merges: slice A can be in build while slice B's contract review is still open. This is the agent-discretion model — contracts are authored all at once, but each slice proceeds on its own merges.
- **Story anchor — a tracking issue**, opened at intake. Phase PRs come and go; the issue is the stable surface: it carries the phase label projection, links every stage PR, receives `/status` output, and syncs with the board. (Labels live here because the feature branch itself has no label surface.)
- The agent never merges a gated stage PR itself; the driver merges. Build PRs may auto-merge when green if the repo config allows (§6).

### 2.2 Durable machine state — `.pipeline/state.json` (committed to the feature branch)

```json
{
  "story":     {"source": "linear|jira|manual", "id": "ENG-123", "title": "...", "issue": 17},
  "variant":   "spec-as-source | change-spec",
  "stage":     "interrogate | contracts | slices | assembly | final-review",
  "processed": {"comments": [123456789], "reviews": [987654]},
  "iterations": {"interrogate": 2, "slices": {"payments-create-intent": 1}},
  "slices":    [{"name": "payments-create-intent",
                 "stage": "pending|contracted|tests-locked|built",
                 "prs": {"contract": 42, "tests": 43, "build": 45}}],
  "budgets":   {"max_rework_rounds": 5, "escalated": false}
}
```

Updated by bot commit on each transition. Labels on the tracking issue are the queryable projection; this file is the record. (Check-run mirrors: cut from v0 — SHA-fragile, labels suffice.)

Open point: `.pipeline/` in the final diff against main. Options — assembly deletes it (history survives in git), or it migrates into the change record (`changes/<story>/` in B). Resolve in S5 design.

### 2.3 Magic commands (shrunk — merge replaced approval)

| Command | Effect |
|---|---|
| `@claude <question/instruction>` | Summon within the current stage PR (answer threads, revise, fix) |
| `/revise <note>` | Explicit rework request (counts toward iteration cap) |
| `/escalate` | Stop; human takes over in Claude Code |
| `/status` | Agent posts state summary on the tracking issue |

Approval = merging the stage PR. The agent never reacts to plain comments without a summon — unsolicited whole-diff re-passes are the documented trust-killer. Commands honored only from `author_association` ∈ {OWNER, MEMBER, COLLABORATOR}; processing is idempotent via `processed` IDs.

### 2.4 Branch and PR topology

```
main
 └─ feat/<story>                          ← clean: only merged stage PRs + state commits
     ├─ pipe/<story>/planning             → Planning PR   (interrogate conversation lives here)
     ├─ pipe/<story>/contract-<slice>     → Contract PR   (one per slice, opened together)
     ├─ pipe/<story>/tests-<slice>        → Tests PR      (red tests, locked on merge)
     ├─ pipe/<story>/build-<slice>        → Build PR      (TDD implementation)
     └─ (assembly) fresh Final PR: feat/<story> → main    (clean conversation, team-facing)
```

> Stage branches carry their own `pipe/` prefix rather than nesting under the feature branch: git forbids `feat/<story>/planning` while branch `feat/<story>` exists (a ref can't be both a file and a directory). Found the hard way on the first sandbox intake, 2026-07-14.

- Stage PRs merge with **merge commits, never squash** (squash breaks head-deletion auto-retargeting and loses stage history). Squash allowed only at feature→main.
- The Final PR is **opened fresh at assembly** — the planning-era PRs stay archived and cross-linked, so the team never wades through interrogate threads. (GitHub forbids two open PRs on the same head/base anyway.)
- Red tests merged into feature before their slice is built are **skip-marked by slice status** (test filter reads `state.json`), so feature CI stays green; the slice's Build PR unskips them. Mechanism per stack — resolve in S3 design.
- **Test lock is mechanical:** a CI check on each Build PR verifies test files are byte-identical to the Tests PR's locked commit. Build cannot quietly modify tests.

### 2.5 Guardrail stack

1. Default `GITHUB_TOKEN` semantics wherever possible (bot events don't retrigger workflows).
2. **Phase-lock:** an event only acts if it matches the stage/PR `state.json` expects next.
3. Actor filtering: ignore bots; commands from allowed associations only.
4. Iteration caps per stage (default 5 rework rounds) → escalate + summary comment.
5. Concurrency group per story — serializes racing events.
6. Turn/budget caps per run; token spend logged per run to MLflow.
7. Actions runner: action SHA pinned; no `allowed_non_write_users`.

### 2.6 Runner abstraction (work has no claude-code-action)

The stage logic lives in **skills**; the event→stage mapping lives in a thin **dispatcher** with one contract, implemented twice:

> **Dispatcher contract:** given (GitHub event, `state.json` at feature HEAD) → either no-op (phase-lock/actor/idempotency reject) or (skill to invoke, inputs, expected outputs). Deterministic, no model calls.

| | **Actions runner** (home/personal) | **Local runner** (work laptop) |
|---|---|---|
| Events | `pull_request` (closed+merged), `issue_comment`, `pull_request_review*`, `workflow_dispatch` | Polling with ETag conditional requests (free against rate limits); webhook tunnel optional later |
| Execution | `claude-code-action`, Max OAuth token, pinned SHA | Daemon invokes `claude -p` (headless CLI — an official surface, Max billing legitimate) on a local checkout |
| Skills | Loaded from repo `.claude/skills` | Same repo skills, same versions |
| State | Identical (`state.json`, labels, PRs) | Identical — runners are interchangeable mid-story |

The local daemon overlaps heavily with the remote-terminal-orchestrator/OpenClaw work — same shape: poll → map → headless CLI invocation. Design once, share.

### 2.7 Skill/agent reuse map

| Stage | Existing | New to build |
|---|---|---|
| Intake | `engineering` (steps 0–2), `investigating`, `slicing` | `intake` (story → branch/issue/Planning PR wiring) |
| Interrogate | `interrogate` | PR-threaded mode note in interrogate SKILL.md (batched review threads) |
| Contracts | `test-planning` / `auto-test-planning` | per-slice PR packaging |
| Tests | `test-writer` / `auto-test-writer` | — |
| Build | `auto-build`, `refactor`, `code-review` (scope lenses), `tdd` | — |
| Assembly | — | `pr-walkthrough` (study guide + HTML quiz), `adversarial-review` (bounded critics → judge → one comment) |
| Post (A) | — | `spec-audit` (post-merge drift check; scheduled pass deferred — no observed demand yet) |
| Change spec (B) | — | `change-spec` (file-level plain-English details + repo map) |

Every run logs to MLflow (`log_dev_cycle.py` extended): stage, skill versions, tokens, iterations — the pipeline feeds the same evolution loop as everything else.

## 3. Stage map

Each stage below is a discrete unit — its own dispatcher entry + skill(s) + subagents — to be designed individually. **Design points** are what that per-stage design session must resolve.

### S0 — Intake
- **Trigger:** manual dispatch / local CLI command (story ID or pasted text); board webhook later.
- **Work:** create `feat/<story>` + tracking issue + `state.json`; run engineering steps 0–2 autonomously (context load → investigate → slice); push planning artifacts to `pipe/<story>/planning`; open **Planning PR**; post a **self-interrogation review** — the agent's own interrogate findings (all lenses) as line-comment threads.
- **Gate:** none (output is the Planning PR, which S1 gates).
- **Skills/subagents:** `intake` (new) orchestrating `engineering`, `investigating`, `slicing`; research subagents.
- **Design points:** board MCP transport; how much investigation budget intake gets; variant detection/config; what a "scope too big — split the story" outcome looks like.

### S1 — Interrogate (on the Planning PR)
- **Trigger:** review/comment events on the Planning PR, phase-locked; summon required.
- **Work:** process **all** open threads per run — reply per-thread, spawn research where evidence is needed (findings land on the branch, cited in replies), push artifact revisions. Lenses applied against every driver thread.
- **Gate:** driver **merges the Planning PR** → sliced scope + decisions land in feature.
- **Skills/subagents:** `interrogate` (PR-threaded mode), `investigating`; research subagents.
- **Design points:** thread-resolution semantics (who resolves — agent on reply, or driver only); suggested-changes vs commits for artifact edits; ADR placement per variant.

### S2 — Contracts (per slice, authored together)
- **Trigger:** Planning PR merged.
- **Work:** test-planning authors integration test contracts for **all** slices in one pass, then opens **one Contract PR per slice** (small, independently mergeable). Driver line-reviews; agent revises on summon.
- **Gate:** merging slice N's Contract PR — which immediately unlocks S3 for slice N while other contract reviews stay open.
- **Skills/subagents:** `test-planning`/`auto-test-planning` + per-slice packaging.
- **Design points:** Variant B file layout — contracts must be per-slice files (`changes/<story>/contracts/<slice>.md`?) or N PRs conflict on one change-spec file; whether trivial stories collapse to a single Contract PR; mock-boundary presentation for line review.

### S3 — Tests (per slice)
- **Trigger:** slice N's Contract PR merged.
- **Work:** test-writer translates slice N's contract into red tests on `pipe/<story>/tests-<slice>`; confirms each fails for the right reason; opens **Tests PR**. Driver line-reviews actual test code (training-wheels gate — per-repo config can later auto-merge).
- **Gate:** merge = tests locked. Lock recorded in `state.json` (locked commit SHA) for the mechanical CI check.
- **Skills/subagents:** `test-writer`/`auto-test-writer`.
- **Design points:** skip-marker mechanism per test stack (filter reads slice status); how the lock-check CI job works cross-stack; failure-reason evidence format in the PR body.

### S4 — Build (per slice)
- **Trigger:** slice N's Tests PR merged.
- **Work:** auto-build runs TDD against locked tests on `pipe/<story>/build-<slice>` → refactor → code-review (scope lenses) → opens **Build PR** with self-review posted. Lock check + scoped CI must be green.
- **Gate:** configurable — auto-merge when green + clean self-review, or driver skim.
- **Skills/subagents:** `auto-build`, `refactor` agent, `code-review` agent, `test-runner`.
- **Design points:** iteration-cap behavior mid-TDD; what "clean self-review" means mechanically; slice-split-during-build (updates `state.json` slice list — needs a rule).
- **Exit:** when the last slice's Build PR merges (all slices `built`), dispatcher starts S5.

### S5 — Assembly
- **Trigger:** all slices built.
- **Work:** full **as-if-against-main CI** on feature; `adversarial-review` (bounded critics → judge → ONE consolidated severity-filtered comment); `pr-walkthrough` (study guide + HTML quiz); Variant B: finalize change spec (refresh repo map against the real diff). Findings above severity threshold become **fix-slices** routed back through S3→S4 (the back-edge); below threshold, posted for team judgment.
- **Gate:** clean pass → close/archive planning-era PRs, open **fresh Final PR** feature→main. Body: change spec (B) / spec-diff summary (A) + walkthrough + quiz links + tracking-issue link.
- **Skills/subagents:** `adversarial-review` (new), `pr-walkthrough` (new), `change-spec` (B).
- **Design points:** quiz/walkthrough hosting (artifact vs gh-pages vs committed HTML); `.pipeline/` cleanup vs migration into the change record; severity threshold definition.

### S6 — Final review (team)
- **Trigger:** events on the Final PR.
- **Work:** agent responds to summons only; team fix requests become fix-slices through the same S3→S4 machinery, merged into feature, Final PR updates automatically.
- **Gate:** team merges (squash allowed here).

### S7 — Post-merge
- **Trigger:** Final PR merged.
- **Work:** MLflow cycle log; board status update + tracking issue close; branch cleanup. **Variant A:** `spec-audit` post-merge pass — verifies code still satisfies spec contracts + context decisions; findings → issues.
- **Design points:** audit finding routing (issue vs auto-opened fix story).

## 4. Variant deltas

### A — spec-as-source
- Planning artifacts: edits to durable `spec/*.md` + `context/*.md` (interrogate ADRs → context/). Contracts live in the slice specs (current model — already per-slice files, so S2's per-slice PRs are natural).
- **`spec-audit`** at S7 (post-merge only in v0; scheduled drift pass deferred until demand is observed).
- Team visibility optional; the spec is the owner's instrument.

### B — change-level spec
- Planning artifact: `changes/<story-id>/change-spec.md` — problem, approach, **repo map**, **file-level plain-English change details**; contracts as per-slice files under `changes/<story-id>/` (S2 requirement).
- Nothing durable required of the host repo; `changes/` accumulates as readable history.
- No audit; the change spec is scoped to its change by construction. The Final PR embeds it as the team's review companion.

Everything else — advancement rule, state file, commands, topology, guardrails, dispatcher, stage map — is byte-identical shared core.

## 5. Target-repo onboarding

- **All repos:** onboarding = an **install script** (workflows + labels + state-file convention), run before any story flows. This is necessarily outside the state machine — it *creates* the machine, so it can't be a state of it.
- **New repo:** the foundation IS story #1 — "CI, test/eval harness, deploy path, one heartbeat behavior end-to-end" planned through the normal spine. Existing skills already branch on greenfield: engineering step 0 detects missing `context/`/`spec/`, test-planning bootstraps `spec/`, build runs V0a/V0b (walking skeleton). No new intake type, no new state.
  - Rejected: `/bootstrap` special intake type — minted a new command + flow for behavior the spine and the skills' greenfield modes already cover.
- **Mature repo:** install only. First story's P1 may include a characterization pass where the change touches untested code (test-planning's test-less-spec rule already mandates this).

## 6. Open questions

1. Build PR autonomy: auto-merge green slices vs. driver skim — per-repo config flag?
2. Board intake transport: Linear webhook → repository_dispatch, vs. polling, vs. manual dispatch only for v0.
3. Quiz/walkthrough hosting: artifact link vs gh-pages vs committed HTML.
4. Native gh-stack GA (preview 2026-04) could simplify topology — re-check at build time.
5. Whether gated merges should additionally require a GitHub approving review (branch-protection on `feat/*`) for auditability.
6. `.pipeline/` in the final diff: delete at assembly vs migrate into the change record.
7. Contract PRs: always per-slice, or collapse to one PR for 1–2-slice stories?

### Resolved

- ~~Interrogate cadence under Actions latency~~ (2026-07-14): fully batched — PR review threads replace serial questioning entirely; each run handles all open threads, research included.
- ~~`/bootstrap` intake type~~ (2026-07-14): killed. Install script + foundation-as-story-#1. See §5.
- ~~`/approve <phase>` commands~~ (2026-07-14): replaced by merge-as-approval — every stage delivers via PR into feature; merging advances the machine.
- ~~All-tests-upfront~~ (2026-07-14): per-slice Tests PRs; contracts authored together but merged per slice; agent discretion starts any slice whose contract has merged.
- ~~Engineering-PR-doubles-as-final-PR~~ (2026-07-14): refuted — team gets a fresh, clean Final PR at assembly; planning PRs archived + cross-linked.
- ~~Check-run phase mirrors~~ (2026-07-14): cut from v0 (SHA-fragile; labels on the tracking issue suffice).

## 7. Build order

1. ~~**Dispatcher contract spec**~~ — ✅ 2026-07-14: `runner/runnerlib/dispatcher.py` (pure functions + offline tests).
2. ~~Sandbox repo, **local runner** skeleton~~ — ✅ 2026-07-14: `pipelines/runner/` implements S0–S4 + revise loops + assembly stub (see `runner/README.md` for v0 deviations: registry-authoritative dispatch, marker loop-guard, no-retry). Sandbox project scaffolded (`pipeline-sandbox`, linkbox CLI); e2e pending repo creation.
3. S2–S3 (per-slice contracts + gated tests) exercised end-to-end on the sandbox.
4. S4 build loop end-to-end on one real story.
5. Actions-runner implementation of the same dispatcher contract (home use).
6. Variant B extras (change-spec + repo map) → pilot on a team-shaped repo.
7. Variant A deltas (spec/context wiring + spec-audit) → pilot on ostia or arboreus-api.
8. Assembly aids (walkthrough + quiz, adversarial pass) — additive, last.

## Interrogate log

- **2026-07-14** — session on design v0: `/bootstrap` killed (install script + foundation-as-story-#1; spine + greenfield modes already cover it). Interrogate PR mode = batched review threads (deliberate supersession of one-question-at-a-time; threads resolve independently). Slicing gap closed (intake runs engineering 0–2 + self-interrogation). Per-slice test/build confirmed as original intent; contracts authored together, merged per slice → agent discretion. Assembly back-edge added (fix-slices through S3→S4). Refutation partially held: fresh Final PR replaces engineering-PR-flip. Merge-as-approval replaced `/approve` commands (user: every stage PRs into feature; merge triggers next step). Runner abstraction added for work-laptop constraint (no claude-code-action): dispatcher contract + Actions/local-daemon implementations.
