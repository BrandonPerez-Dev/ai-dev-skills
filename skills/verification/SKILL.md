
---
name: verification
description: Before ANY claim of completion — run verification. Evidence before assertions, always. Use when finishing a bug fix, feature, refactor, config change, or dependency update.
---

# Verification

Evidence before assertions. Every time. No exceptions.

<HARD-GATE>
Do NOT claim work is complete, fixed, passing, or done without running verification commands and confirming their output. Reading code is not verification. Reasoning about correctness is not verification. Only executed commands with observed output count as evidence.
</HARD-GATE>

## The Iron Law

**No completion claims without fresh verification evidence.**

- "Tests pass" means you ran them THIS session and saw the output
- "Build succeeds" means you ran it THIS session and saw exit 0
- "Feature works" means you tested it THIS session in a running system
- Stale evidence is not evidence. Re-run if anything changed since last verification

## When to Use

Every time you're about to say any of these:

- "The bug is fixed"
- "The feature is complete"
- "Tests are passing"
- "The refactor is done"
- "It should work now"
- "I've verified this works"

If the word "done," "fixed," "complete," "passing," or "works" is about to leave your mouth — stop and verify first.

## Verification by Work Type

Different work requires different verification. Use the right checklist.

### Bug Fix

```
1. □ Reproduce original symptom → confirm it FAILS (bug exists)
2. □ Apply fix
3. □ Reproduce original symptom → confirm it PASSES (bug gone)
4. □ Run regression test red-green: revert fix → test fails, restore → test passes
5. □ Run full test suite → no other tests broken
6. □ Manually test the exact scenario from the bug report
7. □ Check: does the fix handle similar edge cases?
```

**Evidence format:** "Reproduced [symptom] → [error]. Applied fix. Reproduced → [success]. Full suite: [N/N] pass, 0 regressions."

### New Feature

```
1. □ Integration test RED before implementation (test is real)
2. □ Integration test GREEN after implementation
3. □ All unit tests GREEN at each layer
4. □ All PREVIOUS tests still GREEN (no regressions)
5. □ TypeScript compiles clean (or equivalent type check)
6. □ Linter clean
7. □ Manually test in running system (feature actually works)
8. □ Test happy path + 2-3 realistic edge cases
9. □ Spec compliance: matches slice spec (`spec/<name>.md`) exactly
10. □ Error handling verified (not just happy path)
```

**Evidence format:** "Integration test green. All [N] previous tests still pass. Manual test: [action] → [result]. Edge cases: [tested X, Y, Z]."

### Refactor

```
1. □ Checkpoint: all tests green BEFORE starting
2. □ Refactor incrementally
3. □ Run full suite after each change → still green
4. □ If any test breaks: REVERT (don't fix the test)
5. □ Verify behavior unchanged (same inputs → same outputs)
6. □ Check no performance regression in hot paths
```

**Evidence format:** "All [N] tests green before and after. Behavior unchanged: [specific assertion]. No test modifications required."

### Config Change

```
1. □ Change applied
2. □ Tests pass locally
3. □ Verify setting actually took effect (log it, inspect it — don't assume)
4. □ Test in staging/target environment if applicable
5. □ Confirm rollback is safe
6. □ Monitoring/logging captures the change
```

**Evidence format:** "Config set to [value]. Verified active: [evidence]. Tests: [N/N] pass. Rollback tested: [result]."

### Dependency Update

```
1. □ Check migration guide for breaking changes
2. □ Search codebase for deprecated APIs
3. □ Update each deprecated usage
4. □ Type check clean
5. □ Full test suite passes
6. □ Manual test in running system (no console errors, no runtime failures)
7. □ Document the upgrade in changelog
```

**Evidence format:** "Updated [dep] [old] → [new]. Breaking changes: [none/list]. Deprecated APIs: [none/updated N]. Full suite: [N/N] pass. Manual test: [clean/issues]."

## Verification Sequence

Run in this order. If any step fails, stop — fix and re-verify from that step. Do not skip ahead.

```
1. Code integrity     → Type check compiles, linter passes
2. Automated tests    → Integration test green, unit tests green
3. Regression check   → ALL previous tests still green
4. Manual test        → Feature works in running system
5. Edge cases         → Boundary conditions, error paths handled
6. Spec compliance    → Matches slice spec (`spec/<name>.md`) / acceptance criteria
7. Documentation      → Docs updated if behavior changed
```

## Failure-Forcing Verification

For critical fixes and new features, prove your tests are real:

```
1. Apply your change
2. Run the test → GREEN (passes)
3. REVERT your change
4. Run the test → RED (fails)
5. RESTORE your change
6. Run the test → GREEN (passes again)
```

If step 4 doesn't fail, your test doesn't actually verify the change. Write a better test.

## Edge Case Checklist

Before claiming any feature complete, check these:

| Category | Test |
|----------|------|
| **Empty/null** | Empty string, null, undefined, empty array, empty object |
| **Boundaries** | 0, 1, -1, max int, max length, just over limit |
| **Type coercion** | String where number expected, number where string expected |
| **Concurrent** | Two requests at once (if stateful) |
| **Error paths** | Network timeout, service down, malformed response |
| **Auth** | Unauthenticated, wrong role, expired token |

You don't need ALL of these every time. Pick the ones relevant to your change. But actively think about which apply — don't default to "none."

## Specification Compliance

Before claiming a feature matches the design:

1. Re-read the slice spec (`spec/<name>.md`) section for this feature
2. List each acceptance criterion
3. For each criterion: is there a passing test that proves it?
4. For any deviation from the design: document WHY

If there's no slice spec (`spec/<name>.md`), verify against the user's original request. Quote the requirement, show the evidence.

## Cognitive Bias Guards

These biases actively undermine verification. Watch for them.

| Bias | How It Manifests | Antidote |
|------|-----------------|----------|
| **Completion bias** | Rushing to claim done because you're almost there | The last 10% is where bugs hide. Slow down at the finish line. |
| **Confirmation bias** | Only running tests you expect to pass | Run the FULL suite. Include tests you didn't write. |
| **Optimism bias** | "It should work" based on reading the code | Reading is not testing. Run it. |
| **Sunk cost** | Not reverting because you spent time on an approach | Revert is cheap. Debugging a bad approach is expensive. |
| **Authority bias** | Trusting AI-generated code because it looks authoritative | AI code is plausible, not correct. Verify it like any other code. |

## Red Flags — Stop and Verify

| Thought | What's Actually Happening |
|---------|--------------------------|
| "It should work now" | You're hoping, not verifying. Run the tests. |
| "I just need to commit this" | You're skipping the finish line. Verify first. |
| "The tests passed earlier" | Earlier is not now. Run them again. |
| "This is a small change, no need to test" | Small changes cause big bugs. Verify. |
| "I read the code, it's correct" | Reading is not running. Execute it. |
| "It works on my machine" | Test in the target environment. |
| "The linter is clean so it's fine" | Linter catches syntax, not logic. Run tests. |
| "I'll verify after I commit" | No. Verify BEFORE you commit. Always. |

## Evidence Standards

### What Counts as Evidence

- Command output you ran THIS session showing success
- Test results with pass/fail counts
- Manual test with specific input → specific output
- Screenshot or log output of the feature working

### What Does NOT Count as Evidence

- "I read the code and it looks right"
- "It worked last time I checked"
- "The logic is sound"
- "It should work because [reasoning]"
- Test results from a previous session
- Test results from before your last change

## Integration with Other Skills

Verification is invoked BY other skills at their gates:

- **build** invokes verification after each vertical slice
- **ship** invokes verification before user review
- **systematic-debugging** invokes verification after a fix
- **code-review** assumes verification has already run

Don't duplicate what these skills do. Verification provides the discipline; they provide the context.

## Guidelines

- **Same checklist, same order, every time.** Aviation learned this: standardized procedures prevent skipped steps. Don't customize away the discipline.
- **Failure-forcing is not optional for critical code.** If the fix matters, prove the test catches it.
- **Fresh evidence only.** Stale results are not results. If you changed anything, re-run.
- **Evidence format matters.** "Tests pass" is weak. "[N/N] tests pass with 0 regressions, manual test confirmed [specific behavior]" is strong.
- **Regression before celebration.** All previous tests must still pass. A feature that breaks something else is not done.
