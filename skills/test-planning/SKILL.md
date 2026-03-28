---
name: test-planning
description: >-
  Plan what to test and how — vertical slices, integration test contracts, mock boundaries.
  Use during design phase to define the test strategy before implementation begins.
  This is a "line-drawing" skill: the user validates that the test contracts match how
  the system actually works. Heavy user involvement with checkpoints.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Skill
  - Task
---

# Test Planning

Define the lines before the AI colors between them. The user validates every test contract.

<HARD-GATE>
Do NOT finalize a test plan without user validation of the integration test contracts. If the contracts are wrong, the AI will perfectly implement the wrong thing. The user must confirm that the inputs, outputs, and assertions match how the system actually works.
</HARD-GATE>

## Why This Is Separate from Writing Tests

Test planning is a design activity. Writing tests is a build activity. Different phases, different concerns:

| Phase | Skill | Who Leads | Question |
|-------|-------|-----------|----------|
| **Design** | test-planning | Human + AI together | What should we test? What are the contracts? |
| **Build** | tdd | AI (autonomous) | Red → green → refactor against the approved plan |

If you skip test planning and jump to writing tests, the AI will write tests that pass but don't validate the right behavior. The test plan is how the user communicates "this is what correct looks like."

## Method Selection

| Situation | Approach | Depth |
|-----------|----------|-------|
| **Greenfield feature** | Full process: walking skeleton → slices → contracts | Deep — every contract validated |
| **Adding to existing system** | Start from existing test patterns, identify new slices | Medium — validate new contracts, reference existing |
| **Refactoring** | Characterization tests first: capture current behavior, then plan changes | Medium — contracts should NOT change |
| **Bug fix** | Single regression test: reproduce the bug as a failing test contract | Light — one contract, user confirms the bug scenario |

## Process

### 1. Understand the Feature

Read the design doc, spec, or user description. Before planning tests, understand:
- What does the user do? (the action)
- What should happen? (the expected outcome)
- What systems are touched? (the path through layers)

If any of these are unclear, ask. Don't guess at behavior — wrong assumptions here cascade through every test.

### 2. Identify Vertical Slices

Cut the feature into vertical slices. Each slice:
- Has a clear user action ("create a workflow run")
- Touches every layer from API to data/external system
- Can be integration tested independently
- Delivers visible value when complete

**Present slices in groups of 3-4** (working memory limit). For larger features, group related slices and present one group at a time.

**CHECKPOINT 1: Validate slices with user.**

Present the slices and ask:

"Here are the vertical slices I've identified:
1. **[Slice name]** — [user action → path through system]
2. **[Slice name]** — [user action → path through system]
3. **[Slice name]** — [user action → path through system]

Does this match how you think about the feature? Am I missing a path, or is one of these wrong?"

Do NOT proceed until the user confirms. Slices are the foundation — if they're wrong, everything built on them is wrong.

### 3. Define Mock Boundaries

For each slice, identify which dependencies are real and which are mocked:

| Dependency Type | Mock? | Why |
|----------------|-------|-----|
| **Controlled** (your database, your file system, your queue) | No — test against real instances | You own it. Test against production-equivalent infrastructure. |
| **Uncontrolled** (third-party APIs, payment processors, external LLMs) | Yes — mock at the adapter boundary | You can't guarantee their behavior. Verify you send the right request. |

**Never use in-memory substitutes** (SQLite for Postgres, in-memory cache for Redis). Test against the same type and version as production.

Present the boundary decisions to the user — they know which systems are controlled vs uncontrolled better than the AI does.

### 4. Design Integration Test Contracts

For each slice, define the integration test contract:

```markdown
### Slice: [Name]

**Setup:** [What state must exist before the test runs]
**Action:** [The API call or user action]
**Input:** [Request body, parameters, headers]
**Expected output:** [Response status, body shape, key fields]
**Side effects:** [Database changes, events emitted, files created]
**Error cases:** [What happens with bad input, missing deps, edge cases]
```

This is the most important checkpoint. The contract defines "correct" — everything the AI builds will be measured against it.

**CHECKPOINT 2: Validate contracts with user.**

Present one slice's contract at a time (decision scaling — high stakes = one at a time):

"For the [slice name] slice, here's the integration test contract:
- **Input:** POST /api/workflows with { type: 'scheduled', trigger: 'daily' }
- **Expected:** 201 with { id, status: 'queued', type: 'scheduled' }
- **Side effect:** Row inserted in workflows table with status='queued'
- **Error case:** 400 if type is missing, 409 if duplicate trigger exists

Does this match how the system should actually work?"

For each contract, explicitly ask:
- Are the inputs right? (parameters, headers, body shape)
- Are the outputs right? (status code, response shape, key fields)
- Are the side effects right? (database changes, events, external calls)
- Am I missing an error case?

### 5. Plan Unit Test Coverage

For each slice, identify the key unit tests at each layer:

```markdown
**Slice: [Name]**
- Route handler: validates input schema, returns correct status codes
- Service: business logic for [specific rules], error mapping
- Adapter: transforms API response to domain model, handles [specific errors]
```

Unit tests are lower stakes — the AI can determine most of these during implementation. But flag any unit tests where the business logic is non-obvious or has edge cases the user should know about.

### 6. Walking Skeleton (First Slice Only)

If this is a greenfield feature or new system, the first slice should be a walking skeleton:
- Can the server start?
- Can you hit the API?
- Does the database connect?
- Does CI run tests?

The walking skeleton proves infrastructure works. Every subsequent slice builds on it.

### 7. Compile the Test Plan

Assemble everything into the output format. This becomes the input to the **test-writer** skill, which translates these contracts into executable test code before build begins.

## Output Format

```markdown
## Test Plan

### Walking Skeleton (if greenfield)
- [ ] Server starts and responds to health check
- [ ] Database connects and migrations run
- [ ] CI pipeline runs tests

### Vertical Slices

#### Slice 1: [Name]
**User action:** [what the user does]
**Path:** [API → Service → Adapter → External]
**Mock boundary:** [what's real, what's mocked]

**Integration test contract:**
- Setup: [preconditions]
- Action: [API call]
- Input: [request shape]
- Expected: [response shape]
- Side effects: [state changes]
- Error cases: [failure scenarios]

**Key unit tests:**
- [Layer]: [what to test]
- [Layer]: [what to test]

#### Slice 2: [Name]
...

### Test Infrastructure Notes
- [Any setup needed: test database, fixtures, mock servers]
- [CI considerations: parallelism, timeouts, flaky test handling]
```

## Bias Guards

| Trap | Antidote |
|------|----------|
| **Testing what's easy, not what matters** | Ask: "If this test passes, am I confident the feature works?" If no, the test is wrong. |
| **Too many slices** | Most features are 3-5 slices. If you have 10+, you're slicing too thin or the feature is too big. |
| **Skipping error cases** | Every contract needs at least one error case. Happy path only = false confidence. |
| **Assuming mock boundaries** | Ask the user. They know which systems are controlled vs uncontrolled. |
| **Over-specifying unit tests** | Unit test planning is a suggestion, not a contract. The AI refines during implementation. |

## Recommended Tools

**When available (needs account/setup):**
- **PactFlow MCP** — AI-powered contract test generation. 60% faster test creation/maintenance. Strong fit for contract-first planning in step 4.

**Future (build ourselves):**
- **Stryker MCP** — mutation testing to validate test *quality*, not just coverage. No MCP exists yet. Would identify weak tests after generation.
- **Testcontainers MCP** — spin up ephemeral databases/services for integration tests. No MCP exists yet. Would eliminate manual Docker setup.

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **The user is the authority on correctness.** The AI knows testing methodology. The user knows how the system should behave. Combine both.
- **Contracts first, code later.** The test plan is a design document. Don't write test code here — that's the **test-writer** skill's job.
- **One contract at a time.** Don't dump all contracts on the user at once. Present, validate, move on. Communication-protocol's decision scaling applies — these are high-stakes decisions.
- **Error cases are not optional.** Every contract needs failure scenarios. The happy path is the easy part.
- **Walking skeleton for greenfield.** If there's no existing test infrastructure, prove it works before planning feature tests.
- **This plan is the input to test-writer.** The **test-writer** skill translates these contracts into executable test code, which build then implements against. If the plan is wrong, every downstream step is wrong.
