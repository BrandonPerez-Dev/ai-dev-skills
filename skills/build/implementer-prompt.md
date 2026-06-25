# Implementer Subagent Prompt

Template for dispatching an implementer subagent per vertical slice.

**Dispatch with:** `Task tool (general-purpose)`

## Prompt

Fill in the `[bracketed]` placeholders and pass the entire block as the `prompt` parameter.

```
You are implementing a vertical feature slice.

The integration test for this slice is ALREADY COMMITTED by test-writer — a locked contract. Do NOT write or modify any integration test; locate it via the slice spec's `## Tests` section, run it red, and implement until it passes.

## Slice

[FULL TEXT of the slice spec from spec/<name>.md — paste the complete slice here]

## Context

[Where this fits in the feature. What previous slices built. Key architectural
decisions. Relevant codebase conventions (naming, patterns, file structure).]

Working directory: [absolute path]

## Process: TDD Double-Loop

Follow this exactly.

### Outer Loop — Integration Test First

1. Write the integration test from the slice outline
   - Real controlled dependencies (your database, your file system)
   - Mock uncontrolled dependencies (third-party APIs) at the adapter boundary
2. Run it — confirm it fails for the RIGHT reason
   - "not found" or "not implemented" = correct
   - Test infrastructure error = fix the test setup first

### Inner Loop — Build Layer by Layer

For each layer, write a failing unit test, make it pass, refactor:

- Type definitions / interfaces
- Database schema changes (if any)
- Adapter / data layer + unit tests
- Service layer + unit tests
- Route / API endpoint + unit tests
- Client components + unit tests (if frontend)

### Integration Test Green

Run the integration test. When it passes, the slice works end-to-end.

### Verify — No Regressions

Run the full suite:
- All integration tests pass (current + previous slices)
- All unit tests pass
- TypeScript compiles clean (npx tsc --noEmit)
- Linter passes

### Commit

Make atomic commits per logical unit. Use conventional commits:
type(scope): description

Each commit should compile and pass tests independently.

## Before You Begin

If ANYTHING is unclear — requirements, approach, dependencies, assumptions —
ask now. Don't guess. It's always OK to pause and clarify.

## While You Work

If you encounter something unexpected, ask. Don't make assumptions.

## Before Reporting: Self-Review

Review your own work before reporting back:

- **Completeness:** Did I implement everything in the slice spec? Missing requirements? Unhandled edge cases?
- **TDD discipline:** Did the integration test exist BEFORE implementation? Do tests verify behavior, not implementation details?
- **Quality:** Clear names? Clean code? Follows existing codebase patterns?
- **YAGNI:** Did I only build what was requested? No extra features?

Fix anything you find before reporting.

## Report

When done, report:
- What you implemented (brief)
- Integration test: what it asserts, pass/fail
- Unit tests: count, what they cover, pass/fail
- Full verification result (tests, typecheck, lint)
- Commit SHAs
- Files changed
- Self-review findings (what you caught and fixed, if any)
- Open concerns (if any)
```
