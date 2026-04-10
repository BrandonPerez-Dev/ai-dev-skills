---
name: build
description: Implements a plan one vertical at a time using the tdd skill for test-first execution. Reads context/ for architectural constraints, spec/<capability>.md for boundary contracts, and locked test files from test-writer. V0 splits into V0a (boundary scaffold from spec/) and V0b (walking skeleton). Accepts complete plans, partial plans, or single verticals.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
---

# Build

Execute verticals from a plan. One at a time, integration-test first, working software after every vertical.

## When to Use

- After the plan skill defines at least one ready vertical (with done criteria + test contract)
- When handed a single vertical to build in a parallel session
- After design transitions to build

**You don't need a complete plan.** You need at least one vertical with done criteria and a test contract.

## Input

Build accepts three input modes:

| Mode | Input | When |
|---|---|---|
| **Full plan** | Path to plan.md with all verticals detailed | Plan is complete, build sequentially |
| **Partial plan** | Path to plan.md, some verticals detailed, some headlines | Build ready verticals; pause at headlines |
| **Single vertical** | Vertical description passed directly | Parallel session — this session builds one vertical |

### Reading the Plan

1. If given a file path, read the plan
2. If no path, search `changes/` for the most recently modified `plan.md`
3. If no plan exists, ask the user what to build
4. If `context/` exists, read all files — these contain architectural commitments that constrain implementation (e.g., "all API calls go through a proxy" means you don't call external services directly). Without these, you risk implementing against assumptions the team has already resolved.
5. Read the plan's "Modifies spec files" section and load the referenced `spec/<capability>.md` files. The spec is the source of truth for boundaries and contracts — the plan is a pointer to the change.

Identify which verticals are **ready** (have done criteria + a contract landed in `spec/`) vs **headlines** (need more planning).

## Pre-Flight Check

Before writing any code:
- [ ] Dev environment works (build runs, tests pass, server starts if applicable)
- [ ] `spec/` exists and contains the capability files this feature touches (bootstrapped by test-planning if greenfield)
- [ ] At least one vertical has done criteria + a user-validated contract in `spec/<capability>.md`
- [ ] Dependencies between verticals are clear
- [ ] Test files exist from test-writer — if not, invoke **test-planning** → **test-writer** before proceeding

If pre-flight fails, fix it before writing feature code. Infrastructure problems compound.

<HARD-GATE>
Do NOT write feature code until pre-flight passes: build runs, existing tests pass, `spec/` contains the relevant capability files, and at least one vertical has committed test files from test-writer. If no spec files exist, stop — test-planning must bootstrap `spec/` first. If no test files exist, stop — test-writer must generate them first.
</HARD-GATE>

<HARD-GATE>
NEVER modify test files written by test-writer. Tests are locked contracts that define "done." If a test appears wrong, escalate to the user or back to test-writer — do not adjust assertions, expected values, or test logic to match your implementation. The structural separation between test authoring and implementation exists to prevent the #1 AI testing failure: changing tests to match buggy code.
</HARD-GATE>

## Mode Selection

| Mode | When | How |
|---|---|---|
| **Inline** | Exploratory work, tight iteration, or user wants to stay in conversation | Execute verticals directly in this conversation |
| **Subagent** (recommended) | Verticals are well-defined with clear done criteria | Dispatch each vertical to a fresh subagent |

Recommend subagent mode when verticals have clear done criteria. Recommend inline for exploratory work. State your recommendation and let the user override.

---

## Inline Mode

### Vertical 0: Boundaries + Walking Skeleton

V0 is the foundational slice. It has **two phases**: scaffold the boundary types from the living spec, then walk a request through them end-to-end with typed stub responses. Both phases must be green before V1 starts.

Why two phases and not one hardcoded skeleton: hardcoding magic literals lets the skeleton pass without the boundary types actually matching the spec. Splitting V0 means the walking skeleton walks *through* real typed boundaries derived from `spec/`, not around them. The spec and the code cannot drift because the boundary code IS the spec materialized.

#### V0a: Boundary Scaffold (from spec/)

Derive the boundary code from `spec/<capability>.md`. Type-check only — no execution yet.

- Route handler signatures with typed inputs/outputs (no logic)
- Adapter interfaces declared (no implementations)
- Zod schemas / shared type definitions matching the spec's contracts
- Event type unions
- Database schema declared (migrations in place, no data)

**Rules:**
- Every type in V0a must trace to a contract or invariant in `spec/<capability>.md`. If you want a boundary that isn't in spec/, stop — that's a design question, not a build question. Escalate to test-planning or the user.
- No business logic. Signatures and declarations only.
- No hardcoded business values — types, not magic literals.
- Type-check and linter must pass. No end-to-end execution yet.

Commit V0a as its own step before starting V0b: `build(scope): V0a boundary scaffold from spec/`. Why a mid-vertical commit: V0a is a clean, reviewable "spec → code translation" artifact, independently valuable even if V0b later discovers a wiring problem. The commit boundary makes the scaffold diffable against `spec/` during review and gives you a safe rollback point if V0b uncovers a spec/scaffold mismatch. This is the only mid-vertical commit in the build flow — V1+ commit once per vertical at Step 3 of the Execution Loop.

#### V0b: Walking Skeleton through Typed Boundaries

Wire the boundaries from V0a together end-to-end with **typed stub responses** — not hardcoded literals. A request enters the system, flows through each scaffolded boundary, and returns a typed object that satisfies the contract's expected output shape.

- Stub responses are typed objects matching the spec's output shape (e.g., `const stub: WorkflowResponse = { id: "stub-id", status: "queued", createdAt: new Date() }`)
- Prove wiring works: request enters, passes through each boundary from V0a, response comes back
- Integration test asserts the stub response matches the contract shape (the test-writer already committed this test before build started)
- Deploy/run the skeleton before building features on it

If V0b fails, diagnose:
- **Infrastructure problem** (DB won't connect, port busy, migrations broken) — fix the infrastructure
- **Type mismatch between spec and scaffold** — go back to V0a, the scaffold wasn't faithful to spec/. Do not paper over with casts.
- **Integration test doesn't match the contract** — go back to test-writer or test-planning. Do not modify the test.

After V0b passes, report to the user: "V0a boundary scaffold green (typed, no logic). V0b walking skeleton green — [describe the path]. Proceeding to V1 unless you want to inspect."

### Execution Loop (per vertical)

For each ready vertical in dependency order:

#### 1. Implement Against Locked Tests

The **test-writer** skill has already committed failing integration tests for this vertical. Your job is to make them pass — following TDD methodology (red-green-refactor):

- Read the failing test to understand what "done" looks like
- Implement the minimum code to make the test green
- Add unit tests at each layer during implementation (route, service, adapter)
- Refactor while keeping all tests green
- Follow mock boundaries: controlled deps (your DB, server) = real, uncontrolled (third-party APIs) = mock at adapter

**The test is the source of truth, not the implementation.** If the test fails, debug the implementation. If you believe the test is wrong, escalate to the user — do not modify the test.

#### 2. Verify — No Regressions

After tdd completes the vertical, run the full suite:
- All integration tests pass (current + all previous verticals)
- All unit tests pass
- Type check passes
- Linter passes

<HARD-GATE>
Never advance to the next vertical with any test red. All integration tests (current + previous), unit tests, type check, and linter must pass.
</HARD-GATE>

#### 3. Commit + Status

Commit the vertical. Brief status to user: "V1 done — integration test green, 4 unit tests. Moving to V2."

#### 4. Next Vertical

Move to the next ready vertical. If the next vertical is a **headline** (not detailed):
- Pause and tell the user: "V4 needs done criteria and a test contract before I can build it"
- Either the user details it now (via test-planning → test-writer), or you skip to a different ready vertical

---

## Subagent Mode

Fresh subagent per vertical + two-stage review. The controller (you) stays clean; subagents implement.

### Setup

1. Read the plan at `changes/NNN-<topic>/plan.md` and extract ready verticals
2. If `context/` exists, read all files into your controller context — these get passed to every subagent
3. Read the plan's "Modifies spec files" section and load the referenced `spec/<capability>.md` files into your controller context so you can pass them to subagents
4. Create a task per vertical
5. Note working directory, branch, and context subagents need

### V0: Two Subagent Dispatches

V0 is the only vertical that dispatches twice, because V0a and V0b are separate commits with separate success criteria.

#### V0a Dispatch — Boundary Scaffold

Dispatch an implementer subagent with:
- The relevant `spec/<capability>.md` file(s) — full content, not a reference
- Instruction: "Scaffold boundary code from `spec/<capability>.md`. Signatures, type declarations, Zod schemas, adapter interfaces, migrations. No business logic. No hardcoded literals. Type-check must pass. See build skill V0a rules."
- Working directory

After V0a subagent reports green: commit `build(scope): V0a boundary scaffold from spec/`. Then dispatch V0b.

#### V0b Dispatch — Walking Skeleton Wiring

Dispatch a second implementer subagent with:
- The relevant `spec/<capability>.md` file(s)
- The committed V0a scaffold code paths (so the subagent knows what to wire, not build from scratch)
- The locked walking-skeleton test file from test-writer
- Instruction: "Wire the V0a boundaries together with typed stub responses matching the spec's expected output shape. Make the walking skeleton test green. Do NOT modify the test. Do NOT modify the V0a scaffold types."

After V0b subagent reports green: proceed to Spec Compliance Review for V0.

### V1+ Per-Vertical Dispatch

For each ready vertical after V0:

#### 1. Dispatch Implementer

Provide the subagent with:
- The vertical's done criteria from `changes/NNN-<topic>/plan.md`
- The relevant contract(s) from `spec/<capability>.md` — the specific boundary sections this vertical implements, pasted in full
- The locked test files committed by test-writer for this vertical
- Instruction: "Implement against the locked tests. Do NOT modify test files. Do NOT modify the contracts in spec/. Your job is to make the tests green by implementing the business logic behind the V0a boundary types."
- Constraints from the plan
- Context: what previous verticals built, architectural decisions
- Working directory

#### 2. Spec Compliance Review

Dispatch a reviewer subagent with:
- The vertical's done criteria (from the plan at `changes/NNN-<topic>/plan.md`)
- The relevant boundary contract(s) from `spec/<capability>.md` (pasted in full — the reviewer must see the authoritative source, not trust the implementer's summary)
- The file paths changed by the implementer
- Instruction: "Read the actual code at these paths. For each done criterion AND each field in the spec/ contract, state PASS or FAIL with evidence (file:line). Do NOT trust the implementer's summary. If the implementation deviates from spec/, that's a FAIL even if tests pass."

- **All PASS** → proceed to code quality review
- **Any FAIL** → resume implementer with the specific failures, then re-review

#### 3. Code Quality Review

Dispatch a subagent with the code-review skill. Provide:
- The commit range for this vertical
- The plan file path and vertical number (`changes/NNN-<topic>/plan.md`)
- The relevant `spec/<capability>.md` file path (so the reviewer can cross-check implementation against the contract)
- The list of files changed

- **Pass** → mark vertical complete
- **Fail** → resume implementer to fix, re-review

#### 4. Mark Complete

Update task. Status to user. Move to next ready vertical.

### Subagent Red Flags

- **Never** dispatch parallel implementer subagents for dependent verticals
- **Never** skip spec review
- **Never** start code quality review before spec compliance passes
- **Never** dispatch V0a and V0b in parallel — V0b depends on V0a's committed scaffold
- **Never** pass only file paths to subagents for `spec/<capability>.md` — paste the relevant sections in full. Subagents have fresh context and won't load spec/ unless you give it to them.
- **If subagent fails** — dispatch a fix subagent, don't fix manually (context pollution)

---

## Handling Partial Plans

When building from a partial plan:
- Build all ready verticals in dependency order
- When you reach a headline, stop and report what needs detailing
- The user can detail it, invoke plan, or decide to stop here
- Update the plan file as you build — mark completed verticals, note deviations

## Parallel Session Pattern

For building multiple verticals concurrently in separate terminal sessions:
- Each session receives one vertical's constraints + done criteria + test contract
- Each session works on its own branch (use git worktrees)
- Sessions are independent — no shared state during build
- Merge results after verticals are individually green

This gives each vertical a full context window and its own subagent capacity.

---

Follow the communication-protocol skill for all user-facing output and interaction.

## When You're Stuck

| Situation | Strategy | Max Attempts |
|---|---|---|
| **Test fails for wrong reason** | Fix test setup, not implementation | 2 |
| **Implementation doesn't satisfy test** | Re-read the assertion. Work backward from it. | 3 |
| **Unclear requirement** | Check the plan. If it doesn't answer, ask. | 1 (then ask) |
| **Same error after 2 attempts** | Stop. Explain what you tried. Ask the user. | 0 (escalate) |

## Common AI Code Failure Patterns

| Pattern | Detection | Fix |
|---|---|---|
| **Hallucinated APIs** | Import errors, too-convenient methods | Verify packages exist before using |
| **Happy-path-only error handling** | try-catch that only logs | Implement real error boundaries |
| **Missing edge cases** | Empty arrays, null values untested | Test with empty/null/boundary inputs |
| **Data model mismatches** | Runtime crashes on property access | Validate against actual API contracts |

## Verification Checklist (run after every vertical)

- [ ] Integration test passes
- [ ] Unit tests pass at every layer
- [ ] Type check passes
- [ ] Linter clean
- [ ] No regressions (all previous verticals still pass)

After the final vertical, also verify:
- [ ] The feature works when you actually use it (manual smoke test)
- [ ] Plan updated if reality diverged

## Output Format

### Per-Vertical Status
```
V[N] done — [integration test result], [unit test count] unit tests. [Next action].
```

### Final Summary (after all verticals)
```
## Build Complete: [Feature Name]

**Verticals:** [N] completed
**Tests:** [integration count] integration, [unit count] unit
**Deviations from plan:** [any changes, or "None"]

Ready for ship.
```

## After Build

When all verticals are complete and verified, transition to **ship** for delivery.
