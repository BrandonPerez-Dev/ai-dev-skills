---
name: tdd
description: >-
  TDD methodology reference — the red-green-refactor philosophy, mock boundary
  rules, and testing trophy principles. Referenced by test-writer (writes tests)
  and build (implements against locked tests). Use when you need guidance on
  TDD methodology, mock boundaries, or the testing trophy approach. For writing
  tests, use test-writer. For implementing against tests, use build.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
---

# TDD

Write the failing test. Make it pass. Clean up. Next slice.

<HARD-GATE>
Never start implementing a slice without a failing integration test. The test defines "done" — without it, you're guessing. If no test plan exists, invoke the **test-planning** skill first.
</HARD-GATE>

## Philosophy

**"Write tests. Not too many. Mostly integration."** Integration tests provide the highest confidence-to-cost ratio. They test how components actually work together, not how you imagine they do in isolation.

The **testing trophy** (not the pyramid): static analysis at the base, then unit tests, then a thick band of integration tests, then a thin layer of E2E. Most effort goes to integration.

## Double-Loop TDD

Two loops working together:

**Outer loop** (integration test) — Write a real integration test for the slice. It stays red until the full vertical slice is built. This is the guiding test.

**Inner loop** (unit tests) — As you build each layer, write unit tests for component logic. These go green quickly and drive the design of each piece.

The outer loop tells you WHAT to build. The inner loop tells you HOW to build each piece.

## Process

### 0. Check Prerequisites

Before writing any code:
- Test plan exists (from **test-planning** skill or design doc)
- Integration test contracts are user-approved
- Test infrastructure is ready (database, CI, mock servers)
- If greenfield: walking skeleton is green

If any prerequisite is missing, stop. Don't improvise test contracts — go back to test-planning.

### 1. Write the Integration Test

Translate the approved contract into a real test. This test runs against the real system — real API, real database, real controlled dependencies.

```typescript
describe('Feature: Trigger workflow run', () => {
  it('should start a workflow and return task status', async () => {
    const response = await fetch(`${BASE_URL}/api/agents/${agentId}/tasks`, {
      method: 'POST',
      body: JSON.stringify({ type: 'workflow_run' }),
    })
    expect(response.status).toBe(201)

    const task = await response.json()
    expect(task.data.status).toBe('queued')
  })
})
```

### 2. Watch It Fail (Red)

Run the test. It should fail because the feature doesn't exist. Confirm it fails for the **right reason** — "not found" or "not implemented," not because the test itself is broken.

If the test passes immediately, either the feature already exists or the test is wrong. Investigate before proceeding.

### 3. Build the Slice (Inner Loop)

Implement each layer. Add unit tests at each layer as you go:
- Route handler + route unit tests
- Service method + service unit tests
- Adapter implementation + adapter unit tests
- Type definitions
- Schema changes if needed

### 4. Integration Test Goes Green

When the full slice is implemented, the integration test passes. Run it. If it doesn't pass, debug — the contract is the source of truth, not the implementation.

### 5. Refactor

Clean up while all tests stay green. If refactoring breaks tests, the tests were testing implementation, not behavior — fix the tests.

### 6. Regression Check

Run ALL previous slices' integration tests. No regressions allowed. If a previous test breaks, fix it before moving on. Never carry red tests forward.

### 7. Next Slice

Move to the next slice in the test plan. Repeat from step 1.

**Never start a new slice while any integration test is red.**

## The Mock Boundary

| Dependency Type | Mock? | Reasoning |
|----------------|-------|-----------|
| **Controlled** (your database, your file system, your message queue) | No — use real instances | You own it. Test against production-equivalent infrastructure. |
| **Uncontrolled** (third-party APIs, payment processors, external services) | Yes — mock at the adapter boundary | You can't guarantee their behavior. Verify you send the right request. |

**In integration tests:** use real controlled dependencies. Mock uncontrolled dependencies at the adapter boundary.

**In unit tests:** mock anything outside the unit under test.

**Never use in-memory substitutes** (SQLite for Postgres). Test against the same type and version as production.

## Three Test Layers

| Layer | Mocks? | Speed | Confidence | When |
|-------|--------|-------|------------|------|
| **Integration** | Controlled: no. Uncontrolled: mock at adapter. | Slow | High | First — from test plan contract |
| **Unit** | Yes — isolate the component | Fast | Medium | During build, at each layer |
| **E2E** | None | Very slow | Highest | Sparingly — critical user journeys only |

## Recommended Tools

**Ready now (no account needed):**
- **@djankies/vitest-mcp** — AI-optimized Vitest runner with line-by-line coverage analysis, log capturing, structured JSON output. 780+ GitHub stars, includes CLAUDE.md guide. Install: `npm install @djankies/vitest-mcp`.

**When available (needs account/setup):**
- **Postman MCP** — API testing and collection management. Useful for validating API contracts during integration testing.
- **GitHub MCP** — CI/CD monitoring, workflow logs, re-run failed jobs. Check if tests pass in CI without leaving the agent context.

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **Integration test is the source of truth.** If it passes, the slice works. If it fails, the slice is incomplete.
- **Vertical over horizontal.** Complete one slice before starting another. Never build all routes, then all services, then all adapters.
- **Test behavior, not implementation.** Refactoring shouldn't break tests. If it does, the test is testing the wrong thing.
- **Mock at the boundary, not everywhere.** Real controlled deps. Mocked uncontrolled deps. No in-memory substitutes.
- **Red means stop.** If any integration test is red, fix it before new work. Carrying red tests forward creates compounding debt.
- **The test plan is the contract.** Don't deviate from approved contracts. If you discover the contract is wrong during implementation, go back to the user — don't silently adjust.
