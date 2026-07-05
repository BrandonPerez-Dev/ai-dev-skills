---
name: auto-test-writer
description: >-
  Autonomous test writing for GitHub-driven development. Translates integration
  test contracts from spec/<name>.md into executable test code using AAA structure,
  confirms each test fails for the right reason, commits to the slice branch, and
  pushes. Tests are locked artifacts — auto-build implements against them but
  cannot modify them.
when_to_use: >-
  Use after auto-test-planning has landed an integration test contract in at
  least one spec/<name>.md file. Picks up slices with validated contracts and
  writes executable tests. Do NOT use for interactive test writing — use
  test-writer for that.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
argument-hint: "[spec file path or plan path]"
effort: high
---

# Auto Test Writer

Write the contract in code. Prove it fails. Lock it down. Push to the slice branch.

<HARD-GATE>
Do NOT write implementation code — no route handlers, service methods, adapters,
or business logic. This skill produces test files only. If you are writing code
that makes a test pass, you are in the wrong skill — that is auto-build's job.
</HARD-GATE>

<HARD-GATE>
Every test MUST trace to a contract in `spec/<name>.md`. Do NOT invent test
scenarios, assertions, or expected values beyond what the contract specifies.
The contract was validated (or assumed at medium confidence) — it defines
what correct means.
</HARD-GATE>

<HARD-GATE>
NEVER modify a test that has been committed. Tests are contracts, not suggestions.
Once committed, they define "done" and only the human can change that definition.
If a test appears wrong, post a PR comment explaining the concern — do not fix it.
</HARD-GATE>

<HARD-GATE>
Every test MUST fail before committing. Run the test suite and confirm each
new test fails for the RIGHT reason — "not found," "not implemented," or
"no such method." If a test passes immediately, the feature already exists
or the test is wrong — investigate before proceeding.
</HARD-GATE>

## Input

One of:
- **Plan path** — `changes/NNN-<topic>/plan.md` listing all in-scope specs
- **Single spec path** — `spec/<name>.md` with a completed integration test contract
- **Slice PR context** — reads slice branch state to find specs ready for test writing

## Process

### 0. Check Prerequisites

Before writing any test code:
- At least one spec file contains an integration test contract (from auto-test-planning)
- The contract is high or medium confidence (low-confidence/blocking contracts are skipped)
- Test infrastructure is ready (database, test runner, etc.)
- Existing test patterns in the codebase have been read

If prerequisites are missing, post a PR comment explaining what's needed and move to the next slice.

### 1. Pick the Next Slice Spec

Work one slice at a time, in dependency order. Skip slices without completed contracts.

### 2. Read the Contract

Read `spec/<name>.md`. Find:
- **Setup** — preconditions
- **Action** — the operation
- **Input** — request body, parameters
- **Expected output** — response status, body shape
- **Side effects** — database changes, events, external calls
- **Error cases** — failure scenarios

The spec file is the authoritative source.

### 3. Read Existing Test Patterns

Before writing, read existing test files. Match:
- File naming convention
- Import patterns and test utilities
- Setup/teardown patterns
- Assertion style
- Test runner configuration

Write tests that look like they belong in this codebase.

### 4. Write the Integration Test (AAA)

Structure every test as **Arrange-Act-Assert**.

```
test "When [condition], Then [expected outcome]":

  // Arrange — set up preconditions from the contract
  [setup code]

  // Act — perform the operation
  [action code]

  // Assert — verify contract's expected output
  [assertions]

  // Assert side effects
  [side effect checks]
```

Adapt to the project's language and test framework. The three phases are the constant — syntax varies.

### 5. Write Error Case Tests

For every error case in the contract, write a separate test with the same AAA structure. Error cases are first-class, not optional.

Common categories:
- Invalid input
- Missing dependencies / resource not found
- External failures (network errors, timeouts)
- Authorization failures
- Boundary conditions

### 6. Confirm Red

Run the test suite. Every new test must fail.

| Failure Reason | Status | Action |
|---------------|--------|--------|
| "Not found" / "not implemented" / 404 | Correct | Proceed to commit |
| "Connection refused" / "module not found" | Wrong — infrastructure broken | Fix infrastructure, re-run |
| Test passes | Wrong — feature exists or test is broken | Investigate. Post PR comment if unclear. |
| Assertion error with unexpected values | Wrong — test may have incorrect expectations | Check against contract. Post PR comment if unclear. |

If infrastructure issues prevent tests from running, post a PR comment:
```
🔴 BLOCKING: Test infrastructure issue for `<slice>`
   Cannot run tests: [description of issue]
   Needs: [what must be fixed]
```

### 7. Update Spec and Commit to Slice Branch

1. Edit `spec/<name>.md` to fill in the `## Tests` section:

```markdown
## Tests
- `<test file path>` § `"<test name>"` — covers § Integration test contract.
- `<test file path>` § `"<test name>"` — covers § Error cases (specifically: <which one>).
```

2. Commit BOTH test files AND spec edits in a single commit:
```
test(scope): integration tests — [slice name]
```

3. Push to the slice branch.

4. Post FYI comment on slice PR:
```
🟢 FYI: Tests committed for `<slice-name>`
   [N] integration tests, [M] error case tests — all confirmed red.
   auto-build can proceed.
```

### 8. Next Slice

Move to the next slice with a completed contract. Repeat from step 1.

## Mock Boundary Rules

Follow the same mock boundary rules as auto-test-planning and the interactive test-writer:

- **Default: live testing.** Real controlled deps, real test environments for uncontrolled deps when they exist.
- **Push the mock boundary outward.** Mock the HTTP client the adapter calls, not the adapter itself.
- **Never use in-memory substitutes.** No SQLite for Postgres.
- **Three mock types:** Isolation (good), Simulation (acceptable), Implementation (avoid).

## Test Naming Convention

**Pattern:** `When [condition], Then [expected outcome]`

Test names are documentation. When a test fails in CI, the name alone should tell you what broke.

## Test Isolation

Every test must be independent:
- Each test creates its own data in the Arrange phase
- Tests must pass in any order
- Use beforeEach/afterEach for cleanup, not beforeAll
- Match the project's existing isolation pattern

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Modifying tests to match code** | Tests are locked. If they seem wrong, post a PR comment. |
| **Improvised contracts** | Every test traces to a spec contract. Don't invent scenarios. |
| **Happy path only** | Error cases are first-class. Every contract needs them. |
| **Over-mocking** | Only mock uncontrolled deps without test environments. |
| **Skipping confirm-red** | Every test must fail before commit. No exceptions. |
| **Writing implementation code** | Test files only. auto-build implements. |

## Output

This skill produces:
1. Test files committed to the slice branch
2. Updated `spec/<name>.md` with `## Tests` pointers
3. PR comments on slice PRs (FYI for committed tests, BLOCKING for infrastructure issues)

## Handoff

After this skill completes:
- **auto-build** picks up slices with committed red tests and implements against them
- Tests are locked — auto-build cannot modify them
- The human can review tests via the slice PR

## Guidelines

- **Tests are contracts, not suggestions.** Once committed, they define "done."
- **Integration first, always.** Start with integration tests for every slice.
- **Error paths are first-class.** Not optional, not "if time allows."
- **Match the codebase.** Consistency in style, naming, and patterns.
- **AAA is non-negotiable.** Arrange, Act, Assert. Every test.
- **GitHub is the communication channel.** Post issues as PR comments.
