---
name: auto-build
description: >-
  Autonomous implementation for GitHub-driven development. Implements slice specs
  one at a time using TDD against locked tests from auto-test-writer. Reads
  context/ for architectural constraints and spec/<name>.md for done criteria.
  Commits to slice branches, opens slice PRs when green, and posts stuck-points
  as PR comments. For greenfield, splits into V0a (boundary scaffold) and V0b
  (walking skeleton) phases.
when_to_use: >-
  Use after auto-test-writer has committed red tests for at least one slice.
  Implements against locked tests — red to green to refactor. Do NOT use for
  interactive building — use build for that.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - Task
argument-hint: "[spec file path or plan path]"
effort: high
---

# Auto Build

Execute slice specs autonomously. One at a time, integration-test first, working software after every slice. Communicate progress and stuck-points via GitHub.

## The Model

Three persistent layers at the project root:

- **`context/`** — architectural truth. Always loaded before any code is written.
- **`spec/`** — behavioral specs. Each file describes one slice with its integration test contract and done criteria.
- **`changes/NNN-<topic>/plan.md`** — narrative for this change; declares which specs are in scope.

Build reads the plan, implements each spec until its locked test is green, marks the spec `built`, invokes refactor, and moves to the next.

<HARD-GATE>
Never modify test files written by auto-test-writer. Tests are locked contracts
that define "done." If a test appears wrong, post a PR comment — do not adjust
assertions, expected values, or test logic. The structural separation between
test authoring and implementation prevents the #1 AI testing failure mode:
modifying tests to match buggy code.
</HARD-GATE>

## Input

One of:
- **Plan path** — `changes/NNN-<topic>/plan.md` with in-scope specs ready
- **Single spec path** — `spec/<name>.md` for one slice
- **Slice PR context** — reads slice branch to find specs with committed red tests

### Reading State

1. Read the plan (or find the most recent one in `changes/`)
2. Read all files in `context/` — architectural constraints
3. Read in-scope `spec/<name>.md` files
4. Filter by readiness: needs `status: planned` or `in-progress` AND committed red tests

<HARD-GATE>
Read `context/` and the in-scope `spec/` files in full before writing any feature code.
</HARD-GATE>

## Pre-Flight Check

Before writing any code:
- Dev environment works — build runs, existing tests pass
- Each in-scope spec contains an integration test contract
- Each in-scope spec has a committed red test from auto-test-writer
- Dependencies between specs are clear

If pre-flight fails:
- Missing test contract → post PR comment, skip to next slice
- Missing red test → post PR comment, skip to next slice
- Build environment broken → post PR comment as BLOCKING

## The First Slice in a Greenfield Project: V0a + V0b

When this is the first slice (no existing code), implement in two phases.

### V0a: Boundary Scaffold (from spec/)

Derive boundary code from the spec. Type-check only — no execution yet.

- Route handler signatures with typed inputs/outputs (no logic)
- Adapter interfaces declared (no implementations)
- Type definitions matching the spec's contract
- Database schema declared (migrations in place)

Rules:
- Every type traces to a field in the spec's contract
- No business logic. Signatures and declarations only.
- Type-check and linter must pass.

Commit: `build(scope): V0a boundary scaffold from spec/`

### V0b: Walking Skeleton through Typed Boundaries

Wire V0a boundaries together with typed stub responses. A request flows through each boundary and returns a typed object matching the contract's output shape.

- Stub responses are typed objects matching the spec
- Integration test passes with stub data
- Deploy/run the skeleton before building features

Commit when green. Mark spec `status: built`. Move to next slice.

## Execution Loop (per slice spec)

For each `planned` or `in-progress` slice in dependency order:

### 1. Implement Against Locked Tests

auto-test-writer has committed failing tests. Make them pass:

- Read the failing test to understand "done"
- Implement minimum code to make the test green
- Add unit tests at each layer during implementation
- Follow mock boundaries from spec and context/

The test is the source of truth, not the implementation.

### 2. Full-Suite Gate

After making the slice's test green, run the full suite:
- All integration tests pass (current + all previous)
- All unit tests pass
- Type check passes
- Linter passes

<HARD-GATE>
Never advance to the next slice with any test red. All tests, type check,
and linter must pass. A red test carried forward becomes invisible.
</HARD-GATE>

### 3. Commit + Update Spec Status

Commit the implementation to the slice branch:
```
build(scope): implement [slice-name]
```

Update the spec's frontmatter `status` to `built` and append to Changes log.

### 3b. Simplify

Invoke **refactor** on the just-committed changes. Commit separately:
```
refactor(scope): [slice-name] cleanup
```

### 4. Open or Update Slice PR

After the slice is green and refactored:

1. If no slice PR exists yet, open one:
   - Title: `[Agent] <slice-name>`
   - Label: `agent-slice`
   - Body: slice summary, tests passing, link to plan PR

2. If slice PR already exists (from test commits), update the description with build status.

3. Post status comment:
```
📋 STATUS: `<slice-name>` built
   Integration test: green
   Unit tests: [N] added
   Full suite: all passing
   Refactored: [yes/no changes needed]
```

4. If this is the last slice and all are green, request review on all slice PRs.

### 5. Next Slice or Report Stuck

Move to the next slice with committed red tests.

If stuck after 2 attempts on a slice:
```
🔴 BLOCKING: Stuck on `<slice-name>`
   Attempted: [what was tried]
   Failing: [which test, what error]
   Needs: [what might fix it]
   Moving to next unblocked slice.
```

Skip the stuck slice and continue with others.

## When You're Stuck

| Situation | Strategy | Max Attempts |
|---|---|---|
| Test fails for wrong reason | Fix test setup, not implementation | 2 |
| Implementation doesn't satisfy test | Re-read the assertion. Work backward. | 3 |
| Unclear requirement | Check spec. If it doesn't answer, post PR comment. | 1 (then post) |
| Same error after 2 attempts | Post PR comment. Move to next slice. | 0 (skip) |

## Common AI Build Failure Patterns

| Pattern | Detection | Fix |
|---|---|---|
| **Modifying tests to pass** | Test file diff shows assertion changes | Revert. Tests are locked. |
| **Hallucinated APIs** | Import errors, too-convenient methods | Verify packages exist before using |
| **Happy-path-only error handling** | try-catch that only logs | Implement error cases from spec |
| **Passing target test, breaking older tests** | Older spec tests now red | Full-suite gate catches it |

## Verification Checklist (after every slice)

- Integration test for this slice passes
- Unit tests pass
- Type check passes
- Linter clean
- No regressions in previously built specs
- Spec frontmatter updated to `status: built`
- Spec Changes log updated
- Slice PR opened/updated with status

## Output

### Per-Slice Status (PR comment)
```
📋 STATUS: `<slice-name>` built
   Integration test: green
   Unit tests: [N]
   Full suite: passing
```

### Final Summary (PR comment on plan PR)
```
📋 STATUS: Build complete
   Slices built: [N]
   Tests: [integration count] integration, [unit count] unit
   Slices blocked: [list, or "none"]
   Deviations from plan: [any, or "none"]
```

## After Build

All in-scope slice specs should be `status: built`, all tests green, slice PRs open and ready for review. The human reviews and merges.

## Guidelines

- **Specs are the source of truth.** The spec tells you what done looks like.
- **The integration test is the contract.** Make it green. Don't change it.
- **One slice at a time.** Never implement dependent slices in parallel.
- **Full-suite gate every slice.** Passing your test while breaking older tests is the #1 failure mode.
- **Update spec status as you go.** `built` is the durable signal that a slice is done.
- **GitHub is the communication channel.** Post stuck-points, status updates, and questions as PR comments.
- **Skip and continue.** If stuck on one slice, move to the next unblocked one. Don't burn time.
- **Never modify locked tests.** Post a PR comment if a test seems wrong.
