---
name: build
description: >-
  Implements slice specs one at a time using TDD against locked tests. Reads
  context/ for architectural constraints, spec/<name>.md for the slice's
  integration test contract and done criteria, and the locked test file from
  test-writer. For the first slice in a greenfield project, splits the slice
  into boundary scaffold (V0a) and walking-skeleton wiring (V0b) phases.
when_to_use: >-
  Use after test-planning has landed an integration test contract in at least
  one spec/<name>.md file and test-writer has committed the corresponding red
  test. Also accepts a single spec passed directly for parallel-session work.
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

Execute slice specs from the plan. One at a time, integration-test first, working software after every slice.

## The Model

Three persistent layers at the project root:

- **`context/`** — architectural truth. Always loaded before any code is written.
- **`spec/`** — behavioral specs. Each file describes one slice with its integration test contract in plain text + done criteria + status frontmatter.
- **`changes/NNN-<topic>/plan.md`** — narrative for this change; declares which specs are in scope and in what order.

Build reads the plan to know which specs are in scope for *this* change, then implements each spec until its locked integration test is green, marks the spec's status `built`, and moves to the next.

## When to Use

- After test-planning has landed an integration test contract in at least one `spec/<name>.md` and test-writer has committed the corresponding red test
- When handed a single spec to build in a parallel session
- After design transitions to build

**You don't need every spec finalized.** You need at least one slice spec with a validated integration test contract and a committed red test.

## Input

| Mode | Input | When |
|---|---|---|
| **Full plan** | Path to `changes/NNN/plan.md` with all in-scope specs ready | Build sequentially through them |
| **Partial plan** | Plan with some specs ready, others still in test-planning | Build ready specs; pause when you hit one that's still being detailed |
| **Single spec** | Path to one `spec/<name>.md` | Parallel session — this build pass implements one slice |

### Reading State

1. If given a plan path, read it. Otherwise search `changes/` for the most recently modified `plan.md`.
2. Read all files in `context/` — architectural commitments that constrain implementation.
3. Read the in-scope `spec/<name>.md` files (from the plan's "Spec changes" section).
4. Filter by status — `planned` or `in-progress` specs are buildable; `built` are done; `superseded` are skipped.

<HARD-GATE>
Read `context/` and the in-scope `spec/` files in full before writing any feature code. Architectural commitments and slice contracts compound — implementing against an imagined spec produces cascading failures harder to debug than the original issue.
</HARD-GATE>

## Pre-Flight Check

Before writing any code:
- Dev environment works — build runs, existing tests pass, server starts if applicable
- Each in-scope slice spec contains an integration test contract (setup, action, input, expected output, side effects, error cases)
- Each in-scope slice spec has a corresponding locked test file from test-writer
- Dependencies between specs are clear (each spec's `depends_on` frontmatter or content)

If pre-flight fails, fix it before writing feature code. If a spec has no test contract, escalate to test-planning. If a contract has no committed red test, escalate to test-writer.

<HARD-GATE>
Never modify test files written by test-writer. Tests are locked contracts that define "done." If a test appears wrong, escalate to the user or back to test-writer — do not adjust assertions, expected values, or test logic to match your implementation. The structural separation between test authoring and implementation exists because AI agents will otherwise adjust tests to match buggy code — this is the #1 documented failure mode.
</HARD-GATE>

## Mode Selection

| Mode | When | How |
|---|---|---|
| **Inline** | Exploratory work, tight iteration, or user wants to stay in conversation | Execute slices directly in this conversation |
| **Subagent** (recommended) | Slice specs are well-defined with clear done criteria | Dispatch each slice to a fresh subagent |

Recommend subagent mode when specs have clear done criteria. Recommend inline for exploratory work. State your recommendation and let the user override.

## The First Slice in a Greenfield Project: V0a + V0b

When this is the **first slice** in a project (no existing skill graph of working code, no existing boundary types), the slice gets implemented in two phases. Subsequent slices skip this split — they implement against the boundary types established here.

Why two phases: hardcoded magic literals can pass an integration test without the boundary types matching the spec. Splitting V0 means the walking skeleton walks *through* real typed boundaries derived from the spec, not around them. The spec and the code cannot drift because the boundary code IS the spec materialized.

### V0a: Boundary Scaffold (from spec/)

Derive the boundary code from the slice spec. Type-check only — no execution yet.

- Route handler signatures with typed inputs/outputs (no logic)
- Adapter interfaces declared (no implementations)
- Zod schemas / shared type definitions matching the spec's contract
- Event type unions
- Database schema declared (migrations in place, no data)

Rules:
- Every type in V0a traces to a field in the slice spec's integration test contract. If you want a boundary that isn't in the spec, stop — that's a design question. Escalate to test-planning or the user.
- No business logic. Signatures and declarations only.
- No hardcoded business values — types, not magic literals.
- Type-check and linter must pass.

Commit V0a as its own step: `build(scope): V0a boundary scaffold from spec/`. The scaffold is a clean, reviewable spec→code translation, diffable against the spec during review. This is the only mid-slice commit in the build flow — all other slices commit once at Step 3 of the execution loop.

### V0b: Walking Skeleton through Typed Boundaries

Wire the V0a boundaries together end-to-end with typed stub responses. A request enters the system, flows through each scaffolded boundary, returns a typed object that satisfies the contract's expected output shape.

- Stub responses are typed objects matching the spec's output shape (e.g., `const stub: WorkflowResponse = { id: "stub-id", status: "queued", createdAt: new Date() }`)
- Integration test asserts the stub response matches the contract (test-writer committed this test before build started)
- Deploy/run the skeleton before building features on it

If V0b fails:
- **Infrastructure** (DB won't connect, port busy, migrations broken) → fix the infrastructure
- **Type mismatch between spec and scaffold** → back to V0a; the scaffold wasn't faithful to the spec. Do not paper over with casts.
- **Integration test doesn't match the contract** → back to test-writer or test-planning. Do not modify the test.

After V0b passes, mark the slice spec's `status: built`, report to the user, and move to the next slice (no more V0a/V0b — those phases only apply to the first slice).

---

## Inline Mode

### Execution Loop (per slice spec)

For each `planned` or `in-progress` slice spec in dependency order:

#### 1. Implement Against Locked Tests

test-writer has already committed failing integration tests for this slice. Your job is to make them pass — red-green-refactor:

- Read the failing test to understand what "done" looks like
- Implement the minimum code to make the test green
- Add unit tests at each layer during implementation (route, service, adapter)
- Refactor while keeping all tests green
- Follow mock boundaries from the spec: controlled deps (your DB, server) real, uncontrolled (third-party APIs without test environments) mocked at the HTTP client layer

The test is the source of truth, not the implementation. If the test fails, debug the implementation. If the test seems wrong, escalate — do not modify it.

#### 2. Verify — No Regressions Anywhere

After making the slice's test green, run the full suite:
- All integration tests pass (current slice + every previously built spec)
- All unit tests pass
- Type check passes
- Linter passes

This is the regression-awareness check — research on agentic TDD (TDAD, March 2026) shows the #1 silent failure is agents that pass their target test while breaking older tests. The full-suite gate catches it.

<HARD-GATE>
Never advance to the next slice with any test red. All integration tests (current + previously built specs), unit tests, type check, and linter must pass. A red test carried forward becomes invisible — the next slice's failures mask it, and you lose the ability to isolate which change broke what.
</HARD-GATE>

#### 3. Commit + Update Spec Status

Commit the slice. Then update the slice spec's frontmatter `status` to `built` and append to its "Changes" log:

```markdown
## Changes
- 008 (2026-05-13) — initial implementation
```

#### 3b. Simplify

Invoke **refactor** on the just-committed changes. It reviews for reuse, quality, efficiency, and contract compliance, then fixes issues. Commit refactoring separately: `refactor(scope): <slice-name> cleanup`.

If refactor finds nothing, move on. This step prevents debt from accumulating across slices.

Brief status to user: "`create-workflow` done — integration test green, 3 unit tests, simplified. Moving to `list-workflows`."

#### 4. Next Slice

Move to the next `planned`/`in-progress` spec in the plan. If the next spec doesn't have a validated integration test contract yet, pause and tell the user: "`<spec-name>` needs a test contract before I can build it" — either user details it now (via test-planning → test-writer), or you skip to a different ready spec.

---

## Subagent Mode

Fresh subagent per slice + two-stage review. The controller (you) stays clean; subagents implement.

### Setup

1. Read the plan and extract the in-scope slice specs
2. Read all `context/` files into your controller context — these get passed to every subagent
3. Read each in-scope `spec/<name>.md` into your controller context so you can paste relevant sections into subagent prompts
4. Create a task per slice
5. Note working directory and branch

### First-Slice (V0) Dispatch — Greenfield Only

V0a and V0b dispatch as separate subagents because V0b depends on V0a's committed scaffold.

**V0a:** Dispatch implementer with the spec file content, instruction to scaffold types per V0a rules, and working directory. After it reports green, commit `build(scope): V0a boundary scaffold from spec/`. Then dispatch V0b.

**V0b:** Dispatch second implementer with the spec content, V0a scaffold paths, the locked walking-skeleton test, and instruction to wire boundaries with typed stub responses. Do not modify the test or V0a scaffold types.

After V0b is green, proceed to spec compliance review for the slice.

### Per-Slice Dispatch

For each slice after V0 (or for every slice if not greenfield):

#### 1. Dispatch Implementer

Provide the subagent with:
- The slice spec's full content (pasted, not just a path — subagents have fresh context)
- The locked test file(s) committed by test-writer
- Instruction: "Implement against the locked tests. Do not modify test files. Do not modify the contract in spec/. Make the tests green by implementing the business logic."
- Constraints from the plan
- Context from previous slices (architectural decisions, what was built)
- Working directory

#### 2. Spec Compliance Review

Dispatch a reviewer subagent with:
- The slice spec's done criteria and integration test contract (pasted)
- The file paths changed by the implementer
- Instruction: "Read the actual code at these paths. For each done criterion and each field in the spec's integration test contract, state PASS or FAIL with evidence (file:line). Do not trust the implementer's summary. If the implementation deviates from the spec, that's a FAIL even if tests pass."

- **All PASS** → proceed to code quality review
- **Any FAIL** → resume implementer with the specific failures, then re-review

#### 3. Code Quality Review

Dispatch with the **code-review** skill. Provide commit range, plan path, spec file path, and file list. Pass → refactor. Fail → resume implementer to fix.

#### 3b. Simplify

Invoke **refactor** on the slice's changes. Commit refactoring separately: `refactor(scope): <slice-name> cleanup`.

#### 4. Mark Complete

Update slice spec status to `built`, append to its Changes log, update task, status to user, move to next slice.

### Subagent Red Flags

- Never dispatch parallel implementer subagents for dependent slices
- Never skip spec compliance review
- Never start code quality review before spec compliance passes
- Never dispatch V0a and V0b in parallel — V0b depends on V0a's committed scaffold
- Never pass only file paths to subagents for spec content — paste the relevant sections. Fresh subagent context won't load the spec unless you give it to them.
- If a subagent fails, dispatch a fix subagent — don't fix manually (context pollution)

---

## Handling Partial Plans

When building from a partial plan:
- Build all ready slices in dependency order
- When you reach a spec without a test contract, stop and report
- Either the user fills it in (via test-planning), or you skip to a different ready spec
- Update spec statuses as you build — `planned → in-progress → built`

## Parallel Session Pattern

For building multiple slices concurrently in separate terminal sessions:
- Each session receives one slice spec
- Each session works on its own branch (use git worktrees)
- Sessions are independent — no shared state during build
- Merge results after slices are individually green

This gives each slice a full context window and its own subagent capacity.

---

## When You're Stuck

| Situation | Strategy | Max Attempts |
|---|---|---|
| Test fails for wrong reason | Fix test setup, not implementation | 2 |
| Implementation doesn't satisfy test | Re-read the assertion. Work backward from it. | 3 |
| Unclear requirement | Check the spec. If it doesn't answer, ask the user. | 1 (then ask) |
| Same error after 2 attempts | Stop. Explain what you tried. Ask the user. | 0 (escalate) |

## Common AI Build Failure Patterns

| Pattern | Detection | Fix |
|---|---|---|
| **Modifying tests to pass** | Test file diff shows assertion changes | Revert. Tests are locked. |
| **Hallucinated APIs** | Import errors, too-convenient methods | Verify packages exist before using |
| **Happy-path-only error handling** | try-catch that only logs | Implement the error cases from the spec |
| **Missing edge cases** | Empty arrays, null values untested | The spec lists edge cases — implement them |
| **Data model mismatches** | Runtime crashes on property access | Validate against actual API contracts |
| **Passing target test, breaking older tests** | Older spec tests now red | Full-suite gate catches it — fix or escalate |

## Verification Checklist (after every slice)

- Integration test for this slice passes
- Unit tests at every layer pass
- Type check passes
- Linter clean
- No regressions in any previously built spec's tests
- Slice spec frontmatter updated to `status: built`
- Slice spec Changes log updated with this change number

After the final slice in the plan, also verify:
- The feature works when actually used (manual smoke test)
- Plan updated if reality diverged from the planned spec changes

## Output Format

### Per-Slice Status
```
<slice-name> done — integration test green, <N> unit tests, simplified. Next: <next-slice>.
```

### Final Summary (after all slices)
```
## Build Complete: <Change Name>

Slices built: <N>
Tests: <integration count> integration, <unit count> unit
Spec status: <list of specs marked `built`>
Deviations from plan: <any changes, or "None">

Ready for ship.
```

## After Build

The terminal state is invoking **ship** (or the user starting a ship session). All in-scope slice specs should be `status: built`, all tests green, plan updated if scope shifted.

## Guidelines

- **Specs are the source of truth.** The plan tells you which slices are in scope; the slice specs tell you what done looks like.
- **The integration test is the contract.** Tests are committed before you write code. Make them green. Don't change them.
- **One slice at a time.** Parallel slices in subagents are fine for *independent* slices, but never for dependent ones.
- **Full-suite gate every slice.** TDAD-style regression awareness — passing your slice's test while breaking older tests is the #1 silent failure mode.
- **Update spec status as you go.** A spec marked `built` is the durable signal that this slice is done.
