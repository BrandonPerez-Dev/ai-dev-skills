---
name: build
description: Implements a plan one vertical at a time using the tdd skill for test-first execution. Accepts complete plans, partial plans, or single verticals. Use after design produces at least one ready vertical with a validated test contract.
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
2. If no path, search `specs/` for the most recently modified `plan.md`
3. If no plan exists, ask the user what to build

Identify which verticals are **ready** (have done criteria + test contract) vs **headlines** (need more planning).

## Pre-Flight Check

Before writing any code:
- [ ] Dev environment works (build runs, tests pass, server starts if applicable)
- [ ] At least one vertical has done criteria + a user-validated test contract (from test-planning)
- [ ] Dependencies between verticals are clear
- [ ] Test plan exists — if not, invoke **test-planning** before proceeding

If pre-flight fails, fix it before writing feature code. Infrastructure problems compound.

<HARD-GATE>
Do NOT write feature code until pre-flight passes: build runs, existing tests pass, at least one vertical has committed test files from test-writer. If no test files exist, stop — invoke test-planning then test-writer first.
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

### Vertical 0: Walking Skeleton

Always first. One request flows through every layer and returns a hardcoded response. No real logic.

- Hardcode all return values (static data, no DB queries, no real API calls)
- Prove the wiring works: request enters the system, passes through each layer, response comes back
- Integration test asserts the hardcoded response is returned
- Deploy/run the skeleton before building features on it

If this fails, you've found an infrastructure problem. Fix it now.

After the walking skeleton passes, report to the user: "Walking skeleton green — [describe what the path does]. Proceeding to V1 unless you want to inspect."

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

1. Read the plan and extract ready verticals
2. Create a task per vertical
3. Note working directory, branch, and context subagents need

### Per Vertical

#### 1. Dispatch Implementer

Provide the subagent with:
- Full vertical description (done criteria + test files committed by test-writer)
- Instruction: implement against the locked tests — do NOT modify test files
- Constraints from the plan
- Context: what previous verticals built, architectural decisions
- Working directory

#### 2. Spec Compliance Review

Dispatch a reviewer subagent with:
- The vertical's done criteria and test contract (from the plan)
- The file paths changed by the implementer
- Instruction: "Read the actual code at these paths. For each done criterion, state PASS or FAIL with evidence (file:line). Do NOT trust the implementer's summary."

- **All PASS** → proceed to code quality review
- **Any FAIL** → resume implementer with the specific failures, then re-review

#### 3. Code Quality Review

Dispatch a subagent with the code-review skill. Provide:
- The commit range for this vertical
- The plan file path and vertical number
- The list of files changed

- **Pass** → mark vertical complete
- **Fail** → resume implementer to fix, re-review

#### 4. Mark Complete

Update task. Status to user. Move to next ready vertical.

### Subagent Red Flags

- **Never** dispatch parallel implementer subagents for dependent verticals
- **Never** skip spec review
- **Never** start code quality review before spec compliance passes
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
