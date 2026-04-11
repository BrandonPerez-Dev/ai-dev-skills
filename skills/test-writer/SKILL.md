---
name: test-writer
description: >-
  Write test code from user-validated contracts in spec/<capability>.md —
  integration tests first, one vertical at a time. Translate each contract
  into executable test code using AAA structure, confirm red (failing for the
  right reason), and commit as locked artifacts. Use after test-planning has
  landed contracts in spec/, before build begins implementation. Tests
  committed by this skill are immutable — build implements against them but
  cannot modify them.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - AskUserQuestion
---

# Test Writer

Write the contract in code. Prove it fails. Lock it down.

<HARD-GATE>
Do NOT write implementation code — no route handlers, service methods, adapters,
or business logic. test-writer produces test files only. If you are writing code
that makes a test pass, you are in the wrong skill — that is build's job.
The structural separation between test authoring and implementation is what
prevents the #1 AI testing failure: modifying tests to match the code.
</HARD-GATE>

<HARD-GATE>
Every test MUST trace to a user-validated contract in `spec/<capability>.md`.
Do NOT invent test scenarios, assertions, or expected values from your
understanding of the code. If the spec doesn't specify an error case, ask —
don't fill the gap yourself. The user validated the contracts in `spec/`
because they know what "correct" means for their system. You don't.
</HARD-GATE>

<HARD-GATE>
NEVER modify a test that has been committed — not the assertions, not the
expected values, not the test logic, not even "just a small fix." If a test
appears wrong during build, the test-writer's job is done — escalate to the
user or back to test-planning. Tests are contracts, not suggestions. Once
committed, they define "done" and only the user can change that definition.
WHY: The entire pipeline depends on test-writer and build being separate
phases with separate authors. If the same agent that writes implementation
can also edit tests, it WILL adjust assertions to match buggy code — this is
the #1 measured failure mode in AI-assisted development. The structural
separation is load-bearing. Removing it collapses the feedback loop.
</HARD-GATE>

<HARD-GATE>
Every test MUST fail before committing. Run the test suite and confirm each
new test fails for the RIGHT reason — "not found," "not implemented," or
"no such method." If a test fails because of broken test infrastructure
("connection refused," "module not found"), fix the infrastructure first.
If a test passes immediately, the feature already exists or the test is
wrong — investigate before proceeding.
</HARD-GATE>

## Method Selection

Different contracts produce different test types. Integration tests are always the starting point.

| Contract Type | Test Type | Priority |
|--------------|-----------|----------|
| API endpoint behavior (status, response shape) | Integration test through real HTTP | Write first — highest confidence |
| Error/failure scenarios (network error, invalid input) | Integration test with mock at boundary | Write alongside happy path — not optional |
| Data transformation or business logic | Unit test if logic is complex and isolated | Write after integration tests |
| Cross-service workflow | E2E test | Write sparingly — only critical user journeys |

**Default to integration.** Unit tests only when the contract explicitly calls for isolated logic testing or when build adds them during implementation.

## Process

### 0. Check Prerequisites

Before writing any test code:
- [ ] `spec/<capability>.md` exists and contains user-validated contracts for the vertical(s) you're writing tests for (from **test-planning**)
- [ ] Feature plan at `changes/NNN-<topic>/plan.md` references which spec files are in scope
- [ ] Test infrastructure is ready (database, test runner, any required mock servers)
- [ ] Existing test patterns in the codebase have been read (match conventions)
- [ ] Greenfield feature 1: you are WRITING the walking skeleton test for V0 (it will not exist yet — that's expected). Subsequent features: the walking skeleton test from the bootstrap feature is committed and passing.

If prerequisites are missing, stop. Don't improvise — go back to test-planning.

### 1. Pick the Next Vertical

Work one vertical at a time, in dependency order from the feature plan (`changes/NNN-<topic>/plan.md`). Do not write tests for multiple verticals in one pass. Report which vertical you're working on.

### 2. Read the Contract from the Living Spec

Read the relevant `spec/<capability>.md` file for this vertical. Find the contract(s) for the boundary this vertical touches and identify:
- **Setup** — what state must exist before the test
- **Action** — the API call or operation
- **Input** — request body, parameters, headers
- **Expected output** — response status, body shape, key fields
- **Side effects** — database changes, events emitted, external calls made
- **Error cases** — what happens with bad input, missing deps, failure scenarios

Each of these maps directly to a test. Also read the capability's **Invariants** section — any invariant relevant to this vertical should produce a test that enforces it.

The `spec/` file is the authoritative source. Do not read contracts from the feature plan in `changes/` — those are pointers, the spec is the truth.

### 3. Read Existing Test Patterns

Before writing new tests, read existing test files in the project. Match:
- File naming convention (e.g., `*.test.ts`, `*_test.go`, `test_*.py`, `*Test.java`)
- Import patterns (test utilities, helpers, factories)
- Setup/teardown patterns (how the project handles DB cleanup, fixtures)
- Assertion style (what expect/assert patterns are used)
- Test runner configuration (if any)

Write tests that look like they belong in this codebase. Consistency matters.

### 4. Write the Integration Test (AAA)

Structure every test as **Arrange-Act-Assert**. AAA makes test failures self-diagnosing: the Arrange shows what state existed, the Act shows what happened, and the Assert shows what was expected vs. actual. A reader debugging a failure at 2 AM needs this structure.

Use the project's language and test framework. The pattern is universal:

```
test "When refresh fails with network error, Then credential stays active and returns 503":

  // Arrange — set up the preconditions from the contract
  store = create_test_store(db_path)
  store.save_credential("user-1", "google", expired_token_set)
  mock_http_client to throw network_error on token refresh

  // Act — perform the operation under test
  response = HTTP GET /credentials/user-1/google

  // Assert — verify the contract's expected output
  assert response.status == 503
  assert response.body.error == "temporarily_unavailable"

  // Assert side effects — credential status unchanged
  credential = store.get_credential("user-1", "google")
  assert credential.status == "active"
```

Adapt this to whatever test framework the project uses (Vitest, pytest, JUnit, Go testing, etc.). The three phases and their purpose are the constant — syntax varies.

### 5. Write Error Case Tests

Error cases are first-class. They are not "nice to have" — they catch the bugs that wake people up at night.

For every error case in the contract, write a separate test with the same AAA structure. The Arrange phase sets up the failure condition. The Assert phase verifies the system handles it correctly.

Common error categories to cover from contracts:
- **Invalid input** — missing fields, wrong types, malformed data
- **Missing dependencies** — resource not found, service unavailable
- **External failures** — network errors, timeout, provider returns error
- **Authorization failures** — wrong credentials, expired tokens, insufficient permissions
- **Boundary conditions** — empty collections, max limits, concurrent requests

### 6. Confirm Red

Run the test suite. Every new test must fail. Check each failure:

| Failure Reason | Status | Action |
|---------------|--------|--------|
| "Not found" / "not implemented" / 404 | Correct — feature doesn't exist yet | Proceed to commit |
| "Connection refused" / "module not found" | Wrong — test infrastructure broken | Fix infrastructure, re-run |
| Test passes | Wrong — feature already exists or test is broken | Investigate before proceeding |
| Assertion error with unexpected values | Wrong — test may have incorrect expectations | Check against contract, ask user if unclear |

### 7. Commit

Commit the test file(s) for this vertical with a clear message:

```
test(scope): V1 integration tests — [slice name]
```

These committed tests are now locked artifacts. Build will implement against them.

### 8. Report and Next Vertical

Report status: "V1 tests written and committed (red). [N] integration tests, [M] error case tests."

Move to the next vertical. Repeat from step 1.

## Mock Boundary Rules

The mock boundary determines what is real and what is faked in tests. Getting this wrong is the most common source of false confidence.

**Default posture: live testing.** Prefer real systems over mocks whenever it's practical. Mocks are a fallback, not a default.

| Dependency | Default | WHY |
|------------|---------|-----|
| **Your database** | Real instance | Mocking your own DB hides schema mismatches, constraint violations, query errors |
| **Your server/API** | Real instance | Testing through the real API catches routing, middleware, serialization bugs |
| **Your file system** | Real (temp dirs) | File system bugs are real bugs |
| **Third-party APIs with test mode** (Stripe test, GitHub sandbox, OAuth dev apps, cheap/test LLMs) | **Prefer real test environment** over mocking | Higher confidence. Catches breaking changes the day they happen. Test-mode APIs don't charge money, send real emails, or trigger real side effects. |
| **Third-party APIs without test mode** (production-only, paid with no sandbox, destructive side effects) | Mock at the HTTP client layer — NOT at the adapter's public interface | Push the mock boundary as far outward as practical so the adapter's own logic (request shaping, auth, retries, error mapping) runs for real. Your adapter code is your code — it deserves to run in tests. |
| **External services with sandboxes** (SendGrid sandbox, Twilio test credentials, webhook.site) | Prefer real sandbox | Same reason as test-mode APIs. |
| **External services without sandboxes** (arbitrary outbound webhooks, legacy services) | Mock at the outbound HTTP client layer | Prevent side effects. Verify you send the right request body, headers, URL. |

**Push the mock boundary outward.** Every layer inside the mock runs real; every layer outside runs stubbed. Mock the HTTP client the adapter calls — not the adapter the service calls. The further out the mock, the more real code is exercised.

**Never use in-memory substitutes** for production infrastructure. Don't use SQLite for Postgres. Don't use a fake Redis. Test against the same type and version as production.

### Three Mock Types

Not all mocks are equal. Know which you're using and why.

| Mock Type | Purpose | Verdict | Example |
|-----------|---------|---------|---------|
| **Isolation** | Keep external systems out, verify outgoing requests | Good | Mock the OAuth token endpoint, verify correct client_id is sent |
| **Simulation** | Force a scenario you can't trigger via inputs | Acceptable | Mock `fetch` to throw `TypeError('fetch failed')` for network error test |
| **Implementation** | Check that internal code ran a certain way | Avoid | Assert that `logger.info` was called exactly 3 times |

**The formula for a bad mock:** It applies to *internal* code AND it appears in the *assert* phase. If you're asserting on how internal functions were called, you're testing implementation, not behavior.

When mocking external APIs, don't just verify the call was made — **verify the request body, headers, and URL**. "Ensuring an HTTP call was made to the right URL is not enough — verify the body contains necessary fields."

## Test Naming Convention

Test names are documentation. When a test fails in CI at 2 AM, the name alone should tell you what broke.

**Pattern:** `When [condition], Then [expected outcome]`

```
Good: 'When token refresh fails with network error, Then credential stays active and returns 503'
Good: 'When user submits order with empty cart, Then returns 400 with validation error'
Good: 'When OAuth provider returns invalid_grant, Then credential marked needs_reauth'

Bad:  'test refresh error handling'
Bad:  'should work correctly'
Bad:  'error test'
```

**For test groups/suites**, name the component or feature under test, then nest by scenario:

```
suite: "GET /credentials/:userId/:provider"
  group: "When credential requires token refresh"
    test: "Then refreshes token and returns fresh env vars"
    test: "When refresh fails with network error, Then returns 503 and keeps credential active"
    test: "When refresh fails with invalid_grant, Then returns 401 and marks needs_reauth"
```

Adapt to the project's grouping mechanism (`describe`/`it`, `class`/`def test_`, `func Test`, etc.).

## Test Isolation

Every test must be independent. No test should depend on state from another test.

**Rules:**
- Each test creates its own data in the Arrange phase
- Tests must pass in any order
- Use beforeEach/afterEach for cleanup, not beforeAll (state leaks between tests)
- If using a database: fresh instance per suite or truncate per test

**Read the project's existing isolation pattern** before writing new tests. Match it.

## Anti-Patterns

| Anti-Pattern | What Happens | This Skill Prevents It By |
|--------------|-------------|--------------------------|
| **Modify test to pass** | AI changes assertions to match buggy code | Structural separation — test-writer commits before build starts |
| **Improvised contracts** | Tests validate assumed behavior, not specified behavior | Hard gate — every test traces to a contract in `spec/<capability>.md` |
| **Happy path only** | Error cases untested, failures crash production | Error cases are first-class in the process, not optional |
| **Over-mocking** | Mock internal systems, tests pass but code is broken | Mock boundary table — only uncontrolled deps get mocked |
| **Implementation mocks** | Assert on internal function calls, tests break on refactor | Three mock types guide — avoid mocks in assert phase on internal code |
| **Test passes immediately** | Test doesn't actually test anything | Confirm red gate — every test must fail before commit |
| **Brittle assertions** | Test breaks on irrelevant changes (timestamps, IDs) | Assert on behavior and contract fields, not exact object equality |

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **Tests are contracts, not suggestions.** Once committed, they define "done." Build implements against them. If they seem wrong, escalate — don't adjust.
- **Integration first, always.** Integration tests catch 99% of bugs with less effort than comprehensive unit coverage. Start here for every vertical.
- **Error paths are first-class.** They catch the bugs that wake people up at night. Not optional, not "if time allows."
- **Match the codebase.** Read existing tests before writing new ones. Consistency in style, naming, and patterns makes the test suite maintainable.
- **AAA is non-negotiable.** Every test: Arrange (set up state), Act (do the thing), Assert (check the result). No exceptions.
- **Live testing is the default; mocks are a fallback.** Real controlled deps. Real test environments for uncontrolled deps when they exist. When you must mock, mock the HTTP client the adapter calls — not the adapter the service calls. Push the mock as far outward as practical so the most real code runs.
- **One vertical at a time.** Write, confirm red, commit. Then next. Don't batch.
