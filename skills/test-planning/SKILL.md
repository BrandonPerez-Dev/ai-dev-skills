---
name: test-planning
description: >-
  Plan what to test and how — vertical slices, integration test contracts, mock boundaries.
  Maintains the living system specification at spec/<capability>.md: contracts land
  permanently in spec/, not in per-feature plans. Reads context/ for architectural
  constraints that inform mock boundaries. On greenfield, bootstraps spec/. Heavy
  user involvement with checkpoints.
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

Define the lines before the AI colors between them. The user validates every test contract. This skill materializes the **living system specification** at `spec/<capability>.md` — the permanent home of test contracts, intent, invariants, and boundaries.

<HARD-GATE>
Do NOT finalize a test plan without user validation of the integration test contracts. If the contracts are wrong, the AI will perfectly implement the wrong thing. The user must confirm that the inputs, outputs, and assertions match how the system actually works.
</HARD-GATE>

<HARD-GATE>
Contracts live in `spec/<capability>.md`, NEVER in `changes/NNN-<topic>/plan.md`. The changes folder holds rationale only. Do not duplicate — the spec file is the single source of truth; git history is the change log.
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
| **Greenfield feature (feature 1)** | Bootstrap `spec/` — propose capability file names, create each with intent + non-goals + contracts | Deep — every contract validated; spec/ is being defined for the first time |
| **Adding to existing system** | Read relevant `spec/<capability>.md` files, edit in place to add/modify contracts | Medium — validate new contracts, reference existing invariants |
| **Refactoring** | Characterization tests first: capture current behavior in spec/ (if missing), then plan changes | Medium — contracts should NOT change |
| **Bug fix** | Single regression test: reproduce the bug as a failing test contract, add to relevant spec/ file | Light — one contract, user confirms the bug scenario |

## Process

### 0. Load Project Context and Living Spec (or bootstrap)

Before planning new contracts, read the current state:

**`context/` — architectural truth (hot memory, always load first):**
If `context/` exists, read all files. Architectural decisions here directly inform mock boundaries (Step 3) — e.g., if `context/proxy.md` says "all LLM calls go through LiteLLM," that determines which dependencies are real vs mocked in tests. Infrastructure patterns here inform test stack decisions.

**`spec/` — behavioral contracts (cold memory):**
If `spec/` exists:
- Read `spec/README.md` for system intent and the capability index.
- Read the `spec/<capability>.md` files relevant to this feature.
  - **If the plan has a "Modifies spec files" section:** load exactly those files.
  - **If the plan does NOT have that section** (older plan format, or direct invocation without a plan): ask the user which capabilities this feature touches, then propose spec file names for confirmation before loading.

**If `spec/` does not exist (greenfield, feature 1):**
- You will **bootstrap** `spec/` during this skill's run. This is the only time test-planning creates capability files from scratch.
- Before creating any files, derive a candidate capability list from the feature plan's verticals. Group verticals that touch the same coherent behavioral area into one capability.
- Propose the capability list to the user: "I'm going to bootstrap `spec/` with these capabilities: `workflows.md`, `auth.md`, `events.md`. Does this partitioning match how you think about the system?"
- Only after user confirmation, create the files using the structure in "Living Spec File Format" below. Seed intent/non-goals/key-concepts from the plan's What/Why/Non-Goals/Constraints.

**What counts as a capability:**
A capability is a cohesive behavioral area — typically 3-7 related boundaries (endpoints, events, adapters) that share intent and invariants. Examples: `workflows`, `auth`, `payments`, `events`. Rules:
- **Not per-endpoint** — too granular; splits related behaviors.
- **Not per-source-file** — implementation-coupled; breaks under refactors.
- **Yes per-behavioral-area** — `spec/<capability>.md` should describe one coherent slice of what the system does.
- **Flat, not nested.** `spec/` contains a flat list of capability files plus `README.md`. No subdirectories.
- **Cross-cutting surfaces get their own file** when they span capabilities (e.g., `spec/events.md` for an event bus used by multiple capabilities, `spec/data-schemas.md` for shared entity definitions).

This partitioning choice — capability-based flat files — is deliberate. It matches how tests are organized (by vertical behavior, not by source module), gives agents a single loadable directory for full-system context, and prevents the Cucumber failure mode of nesting that drifts from code structure.

Either way, by the end of Step 0, you know which `spec/*.md` files this feature will touch. Every contract this skill produces lands in one of them — not in `changes/NNN-<topic>/plan.md`.

### 1. Understand the Feature

Read the feature plan at `changes/NNN-<topic>/plan.md`. Before planning tests, understand:
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

**Default posture: live testing.** Mocks are a fallback when hitting a real system is genuinely impractical — not a default because they're easier. For each slice, identify which dependencies are real and which are mocked, erring toward real whenever possible.

| Dependency Type | Default | Why |
|----------------|-------|-----|
| **Controlled** (your DB, file system, queue) | Real instance | You own it. Test against production-equivalent infrastructure. |
| **Uncontrolled WITH a safe test environment** (Stripe test mode, GitHub sandbox, OAuth dev apps, cheap/test LLM models, sandbox APIs) | **Prefer real test environment** over mocking the adapter | Higher confidence. Catches real API changes, schema drift, and contract shifts the moment they happen. Test-mode APIs don't charge money or send real emails. |
| **Uncontrolled WITHOUT a safe test environment** (production-only APIs, paid services with no sandbox, destructive side effects you can't roll back) | Mock at the HTTP client layer — pushed as far outward as practical | You can't use them safely in tests. Mock as far out as possible so the adapter's own logic (request shaping, auth, retries, error mapping) still runs for real. |

**Push the mock boundary outward.** When you must mock, put the mock at the furthest-out point practical — typically at the HTTP client or network layer, NOT at the adapter's public interface. Every layer inside the mock boundary runs real; every layer outside runs stubbed. Mocking at the adapter's public interface skips the adapter's own logic, which is your code and deserves to run in tests.

**Never use in-memory substitutes** (SQLite for Postgres, fake Redis, in-memory queue). Test against the same type and version as production. In-memory substitutes hide the bugs that hurt most: schema mismatches, constraint violations, driver quirks.

Present the boundary decisions to the user — they know which systems have usable test environments better than the AI does. Ask explicitly: "Does [service] have a test mode we can hit in CI, or do we need to mock at the HTTP client?"

**Promote to context/:** When mock boundary decisions reveal system-level infrastructure patterns (e.g., "all external APIs go through a proxy," "test suite uses real Postgres, never SQLite"), write these to `context/testing.md` or the relevant topic file. These are architectural truths that future features need, not feature-specific details.

### 4. Design Integration Test Contracts and Apply to Living Spec

For each slice, define the integration test contract and apply it to `spec/<capability>.md`. The contract lands **in the living spec**, not in a transient plan document.

**Contract shape:**

```markdown
### [Contract name — e.g., "POST /api/workflows" or "Event: workflow.queued"]

**Setup:** [What state must exist before the test runs]
**Action:** [The API call or user action]
**Input:** [Request body, parameters, headers]
**Expected output:** [Response status, body shape, key fields]
**Side effects:** [Database changes, events emitted, files created]
**Error cases:** [What happens with bad input, missing deps, edge cases]
```

**Editing the living spec:**

- **If `spec/<capability>.md` exists:** propose additions or modifications to the existing file. Contracts being added are new sections. Contracts being modified show the before/after shape.
- **If `spec/<capability>.md` does not exist (bootstrap):** create the file using the full structure (intent, non-goals, boundaries, invariants, test contracts, open questions) seeded from the plan's What/Why/Non-Goals/Constraints plus the new contracts.

See "Living Spec File Format" below for the canonical structure.

**CHECKPOINT 2: Validate contract edits with user.**

Present one slice's contract at a time (decision scaling — high stakes = one at a time). Show the edit being proposed to `spec/<capability>.md`:

"For the [slice name] slice, here's the contract I'm adding to `spec/workflows.md`:
- **Input:** POST /api/workflows with { type: 'scheduled', trigger: 'daily' }
- **Expected:** 201 with { id, status: 'queued', type: 'scheduled' }
- **Side effect:** Row inserted in workflows table with status='queued'
- **Error case:** 400 if type is missing, 409 if duplicate trigger exists

Does this match how the system should actually work? If yes, I'll apply the edit to `spec/workflows.md`."

For each contract, explicitly ask:
- Are the inputs right? (parameters, headers, body shape)
- Are the outputs right? (status code, response shape, key fields)
- Are the side effects right? (database changes, events, external calls)
- Am I missing an error case?

Once approved, apply the edit to `spec/<capability>.md` before moving to the next contract. The file is the durable record — don't batch edits across multiple checkpoints and apply at the end.

### 5. Plan Unit Test Coverage

For each slice, identify the key unit tests at each layer:

```markdown
**Slice: [Name]**
- Route handler: validates input schema, returns correct status codes
- Service: business logic for [specific rules], error mapping
- Adapter: transforms API response to domain model, handles [specific errors]
```

Unit tests are lower stakes — the AI can determine most of these during implementation. But flag any unit tests where the business logic is non-obvious or has edge cases the user should know about.

### 6. Walking Skeleton Contract (Greenfield Only)

On greenfield feature 1, the first vertical's contract describes the **walking skeleton path**: the thinnest request that flows through every boundary and returns a contract-shaped stub response. The contract should assert on the response shape (matching the spec's expected output), not on business logic.

Build handles the V0a (boundary scaffold) / V0b (walking skeleton wiring) split internally — you don't write separate contracts for V0a and V0b. One walking skeleton contract describes the V0 outcome; build derives the two-phase implementation.

Infrastructure checks (server starts, DB connects, CI runs tests) are build's pre-flight responsibility, not test contracts.

On subsequent features, skip this step — the walking skeleton already exists and is green.

### 7. Confirm Spec Updates Landed

After all checkpoints pass, verify:
- Every contract from the feature plan has been applied to the relevant `spec/<capability>.md`
- `spec/README.md` is updated if a new capability was added or a top-level concept changed
- `changes/NNN-<topic>/plan.md` references the spec files that were modified (no contracts duplicated there — just pointers)

Report to the user: "Spec updates applied. `spec/workflows.md` now contains the new schedule contract and the updated workflow lifecycle invariant. test-writer will read from spec/ directly."

## Living Spec File Format

Each `spec/<capability>.md` file follows the same structure. Test-planning edits these files in place; test-writer reads from them; build implements against the tests generated from them.

```markdown
# [Capability Name]

## Intent
Why this capability exists, who uses it, what problem it solves. 2-4 sentences.

## Non-goals
What this explicitly does NOT do. Prevents scope creep in future features.

## Key concepts
- **Concept**: definition used across contracts below
- **Concept**: definition

## Boundaries
### [HTTP route / Event / Adapter / CLI command / MCP tool — any external-facing surface]

**Setup:** [preconditions]
**Action:** [what happens]
**Input:** [shape]
**Expected output:** [shape]
**Side effects:** [state changes]
**Error cases:** [failure scenarios]

### [Next boundary]
...

## Invariants
- [Rule that must hold across all operations — e.g., status only transitions forward]
- [Rule]

## Open questions
- [Unresolved concerns that might affect future features]
```

## Output Format

Test-planning produces edits to `spec/<capability>.md` files (primary output) and a brief summary back to the design orchestrator:

```markdown
## Test Planning Summary

### Spec files modified
- `spec/workflows.md` — added POST /api/workflows contract, updated lifecycle invariant
- `spec/events.md` — added workflow.queued event contract

### Spec files created (bootstrap only)
- `spec/workflows.md` — new capability file (greenfield)

### Slices covered
- Slice 1: Create workflow → spec/workflows.md § "POST /api/workflows"
- Slice 2: Queue workflow event → spec/events.md § "workflow.queued"

### Mock boundaries
- Real: Postgres, workflow service, internal queue
- Mocked at adapter: GitHub API (uncontrolled), email provider (uncontrolled)

### Context files updated
- `context/testing.md` — added mock boundary decisions for external APIs
- [omit if no context/ changes]

### Test Infrastructure Notes
- [Any setup needed: test database, fixtures, mock servers]
- [CI considerations: parallelism, timeouts, flaky test handling]
```

The summary goes into `changes/NNN-<topic>/plan.md` as a "Test planning result" section. The contracts themselves live in `spec/`.

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
- **Walking skeleton on greenfield is one contract, not many.** V0's contract asserts the response shape matches the spec. Build's V0a/V0b split is an implementation detail — don't duplicate it in the test plan.
- **The living spec is the input to test-writer.** After this skill runs, `spec/<capability>.md` files contain the validated contracts. The **test-writer** skill reads from `spec/` directly — not from this skill's output summary. If the spec is wrong, every downstream step is wrong.
- **Bootstrap on greenfield is a one-time synthesis.** On feature 1, test-planning composes new `spec/<capability>.md` files from the plan's intent/constraints plus the new contracts. After that, every feature edits existing files in place.
