---
name: refactor
description: >-
  Review changed code for reuse, quality, efficiency, and contract compliance.
  Runs 4 parallel review agents scoped to the git diff, then fixes issues.
  Aware of spec/ contracts and context/ architectural decisions — will not
  make changes that violate them. Invoked automatically after each vertical
  commit during build, and as a final pass before ship.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - Task
---

# Refactor

Review changed code. Fix what's wrong. Don't break contracts.

<HARD-GATE>
Do NOT make changes that violate contracts in `spec/<capability>.md` or architectural decisions in `context/`. If simplification would change behavior defined in spec/, skip it. The spec is the source of truth — cleaner code that breaks a contract is not cleaner.
</HARD-GATE>

<HARD-GATE>
Do NOT modify test files. Tests are locked contracts from test-writer. If a test looks like it could be simplified, skip it — that's test-writer's domain, not yours.
</HARD-GATE>

## When to Use

- After each vertical commit during build (Step 3b)
- As a final pass before ship's verification gate (Step 1)
- When code works but could be cleaner
- When asked to refactor or polish

## Phase 0: Scope and Context

### Identify Changes

Run `git diff` (or `git diff HEAD` if there are staged changes) to see what changed. If there are no git changes, review the most recently modified files from the conversation.

Exclude from review:
- Generated files, vendor code, lock files
- Test files (locked contracts — do not touch)
- Files in `changes/` (rationale docs, not code)

### Load Contracts and Architecture

Before dispatching review agents, load the context they need:

1. **If `spec/` exists:** read the capability files relevant to the changed code. These define behavioral contracts — any simplification must preserve them.
2. **If `context/` exists:** read all files. These contain architectural decisions (technology choices, integration patterns, infrastructure constraints) that simplification must respect.

Summarize the relevant constraints for each agent:
- Which contracts apply to the changed code (endpoint behaviors, invariants, error cases)
- Which architectural decisions constrain the implementation (e.g., "all external calls go through the proxy adapter")

If neither `spec/` nor `context/` exists, proceed without constraints — but note this in the output.

## Phase 1: Launch Four Review Agents in Parallel

Dispatch all four agents concurrently. Pass each agent:
- The full diff
- The relevant spec/ contracts (summarized)
- The relevant context/ constraints (summarized)

Cap at **4 parallel agents** for reliability.

### Agent 1: Code Reuse Review

For each change:

1. **Search for existing utilities and helpers** that could replace newly written code. Look for similar patterns elsewhere in the codebase — utility directories, shared modules, files adjacent to the changed ones.
2. **Flag any new function that duplicates existing functionality.** Suggest the existing function to use instead.
3. **Flag any inline logic that could use an existing utility** — hand-rolled string manipulation, manual path handling, custom environment checks, ad-hoc type guards.

### Agent 2: Code Quality Review

Review changes against coding-standards principles (Kent Beck's 4 rules in priority order: passes tests, reveals intention, no accidental duplication, fewest elements):

1. **Naming** — do names tell the story? Functions as verb phrases, booleans as questions, variables with units. If a comment explains WHAT, rename instead.
2. **Shallow modules** — functions that don't earn their abstraction. If the reader must jump to the definition to understand, the function is too shallow. Combine into fewer, deeper functions.
3. **Redundant state** — state that duplicates existing state, cached values that could be derived, observers/effects that could be direct calls.
4. **Parameter sprawl** — adding new parameters instead of restructuring. 3+ parameters usually means the function does too much.
5. **Copy-paste with slight variation** — near-duplicate blocks that should be unified. But: three similar lines doing different things is fine. Only abstract when the duplication represents the same concept.
6. **Leaky abstractions** — exposing internal details that should be encapsulated, breaking existing abstraction boundaries.
7. **Stringly-typed code** — raw strings where constants, enums, or branded types already exist in the codebase.
8. **Noise comments** — comments explaining WHAT (well-named identifiers do that). Delete WHAT comments, keep WHY comments (hidden constraints, subtle invariants, workarounds).
9. **Premature abstraction** — `createHandler(config)` wrapping a single handler. Write it directly. Abstract after the third use.
10. **Type theater** — complex generics that add safety theater but no real safety.

### Agent 3: Efficiency Review

Review changes for unnecessary work:

1. **Redundant computation** — repeated calculations, duplicate file reads, duplicate API calls, N+1 patterns.
2. **Missed concurrency** — independent operations run sequentially when they could run in parallel.
3. **Hot-path bloat** — blocking work added to startup or per-request/per-render paths.
4. **No-op updates** — state updates that fire unconditionally inside loops or event handlers. Add change-detection guards.
5. **TOCTOU** — checking existence before operating. Operate directly and handle the error.
6. **Memory** — unbounded data structures, missing cleanup, event listener leaks.
7. **Overly broad reads** — reading entire files/collections when only a portion is needed.

### Agent 4: Contract Compliance Review

Review changes against spec/ and context/:

1. **Behavioral preservation** — do the changes preserve every contract in spec/? Check inputs, outputs, side effects, and error cases. Flag any simplification that would change observable behavior.
2. **Invariant preservation** — do the changes preserve invariants listed in spec/? (e.g., "status only transitions forward")
3. **Architectural compliance** — do the changes respect decisions in context/? (e.g., mock boundaries, proxy patterns, technology choices)
4. **Boundary integrity** — are adapter boundaries, interface contracts, and type definitions still faithful to spec/?

If this agent finds a violation, that finding **overrides** suggestions from Agents 1-3. Cleaner code that breaks a contract is a regression, not an improvement.

## Phase 2: Fix Issues

Wait for all four agents to complete. Aggregate findings and fix each issue directly.

**Priority order when findings conflict:**
1. Contract compliance (Agent 4) — cleaner code that breaks a contract is a regression, not an improvement
2. Efficiency (Agent 3) — real performance issues affect users; readability doesn't
3. Code quality (Agent 2) — readability compounds over time but isn't urgent
4. Code reuse (Agent 1) — DRY is a preference, not a requirement

If a finding is a false positive or not worth addressing, skip it silently. Don't argue with findings — just skip and move on.

**Do not over-fix.** If the code is already clean, say so. A refactor pass that changes nothing is a valid outcome.

## Phase 3: Commit (if changes were made)

If changes were made:
- Run tests to verify nothing broke
- Commit with: `refactor(scope): V[N] cleanup` (during build) or `refactor(scope): final cleanup` (during ship)

If no changes were needed, report clean and move on.

## Worked Example

```diff
 // service/invoice.ts
+function getInvoiceTotal(invoice: Invoice): number {
+  const subtotal = invoice.lines.reduce((sum, l) => sum + l.amount, 0);
+  const tax = subtotal * 0.1;
+  const dt = `${invoice.date.getMonth()+1}/${invoice.date.getDate()}`;
+  console.log(`Calculated on ${dt}`);
+  return subtotal + tax;
+}
```

Given `spec/invoices.md` says "tax rate is configurable per region" and `utils/dates.ts` exports `formatDate`:

| Agent | Finding | Action |
|-------|---------|--------|
| 1 (Reuse) | `formatDate` utility exists — replace hand-rolled date formatting | Fix |
| 2 (Quality) | `console.log` isn't this function's job; remove side effect | Fix |
| 3 (Efficiency) | No issues | — |
| 4 (Contracts) | **Hardcoded 10% tax violates spec/** (must be configurable per region) | Escalate — contract violation, not a refactor fix |

**Result:** Agent 4 blocks the tax constant extraction (contract issue, not cleanup). Agents 1+2 fixes applied. Violation reported to user.

## Output

Brief summary — what was fixed, what was skipped, any contract concerns:

```
## Refactor: V[N]

**Fixed:** 3 issues
- Replaced hand-rolled date formatting with existing `formatDate` utility (reuse)
- Combined 3 shallow wrapper functions into 1 deeper function (quality)
- Added change guard to polling interval state update (efficiency)

**Skipped:** 1 false positive
- Agent 1 flagged similar-looking but semantically different validation logic

**Contracts:** All spec/ contracts preserved. No violations found.
```

Or:

```
## Refactor: V[N]

Code is clean. No changes needed.
```

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Simplifying test files** | Never. Tests are locked contracts. |
| **Breaking spec/ contracts for cleaner code** | Contract compliance overrides all other agents |
| **Over-abstracting during refactor** | Refactor removes unnecessary complexity. It does not add new abstractions. |
| **Changing error handling behavior** | Error cases are specified in contracts. Don't refactor them away. |
| **Running without loading spec/context** | Always load constraints first. Blind simplification is dangerous. |
