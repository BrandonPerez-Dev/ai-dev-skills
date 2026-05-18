---
name: test-planning
description: >-
  Land integration test contracts inside spec/<name>.md files — one file per
  slice. Each contract names setup, action, input, expected output, side
  effects, and error cases in plain text. Reads context/ for architectural
  constraints that inform mock boundaries. On greenfield, bootstraps spec/
  from the plan. Heavy user involvement with checkpoints.
when_to_use: >-
  Use after plan declares which specs this change adds, modifies, or
  supersedes — typically invoked by design between plan and test-writer. Also
  use directly when you need to update a spec's contract without going through
  a full design pass.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - AskUserQuestion
  - Skill
  - Task
effort: high
---

# Test Planning

Define the lines before the AI colors between them. Land integration test contracts inside `spec/<name>.md` files — the source of truth for what each slice does and what proves it done.

## The Model

Each `spec/<name>.md` file describes one thing:

- **A slice spec** — a single testable behavior. Contains an integration test contract (setup, action, input, expected output, side effects, error cases) that defines "done."
- **An invariant spec** — cross-cutting rules that apply across slices. Contains rules + a test list that all relevant slices must satisfy.

Spec files are flat, named descriptively (`create-workflow.md`, `workflow-lifecycle.md`, `payment-intent-flow.md`), and self-contained. No subdirectories. No grouping into capability files.

<HARD-GATE>
Contracts live in `spec/<name>.md`, never in `changes/NNN/plan.md`. The plan holds rationale only. Don't duplicate — the spec file is the single source of truth; git history is the change log.
</HARD-GATE>

<HARD-GATE>
Contracts require user visibility. At high confidence, present and proceed unless flagged. At medium/low confidence, wait for explicit validation. If the contract is wrong, the AI will perfectly implement the wrong thing — when in doubt, round confidence down.
</HARD-GATE>

## Why This Is Separate from Writing Tests

Test planning is a design activity. Writing tests is a build activity.

| Phase | Skill | Who Leads | Question |
|-------|-------|-----------|----------|
| Design | test-planning | Human + AI together | What should we test? What are the contracts? |
| Build | test-writer → build | AI (autonomous) | Translate contracts into tests, then red → green → refactor |

If you skip test planning and jump to writing tests, the AI writes tests that pass but don't validate the right behavior. The test plan is how the user communicates "this is what correct looks like."

## Method Selection

| Situation | Approach | Depth |
|-----------|----------|-------|
| Greenfield (first change in project) | Bootstrap `spec/` — derive slice spec files from the plan's What/Why/Constraints | Deep — every contract validated; spec/ is being defined for the first time |
| Adding to existing system | Read in-scope spec files from the plan, edit in place to extend/refine contracts, or create new slice spec files | Medium — validate new contracts, respect existing invariants |
| Refactoring | Characterization contracts first: capture current behavior in spec/ (if missing), then plan changes | Medium — contracts should NOT change |
| Bug fix | Add a failing-test contract to the relevant slice spec that reproduces the bug | Light — one contract, user confirms the bug scenario |

## Process

### 0. Load Context and Spec

Before planning contracts:

**`context/` — always loaded.** Read all files. Architectural decisions here inform mock boundaries — e.g., if `context/proxy.md` says "all LLM calls go through LiteLLM," that determines which dependencies are real vs mocked.

**`spec/` — loaded per change.**
- Read `spec/README.md` if it exists.
- If the plan has a "Spec changes" section, load those exact files.
- If no plan or no spec changes section, ask the user which specs this work touches.

**If `spec/` doesn't exist (greenfield, first change):**
Bootstrap `spec/` during this skill's run. Derive slice spec file names from the plan's What/Why/Constraints. Propose the list before creating any files:

> "I'm going to create these slice specs: `create-workflow.md`, `list-workflows.md`, `workflow-lifecycle.md` (invariants). Does this slicing match how you think about the feature?"

Only create files after confirmation. Seed each with the plan's relevant rationale.

**What counts as one spec file:**
- One testable slice = one file (`create-workflow.md`)
- One coherent set of cross-cutting rules = one file (`workflow-lifecycle.md` for "orders transition forward only" + related invariants)
- A multi-step workflow that needs to be tested end-to-end = one file (`checkout-flow.md`)

**Not** one file per source module. **Not** one file per capability that bundles many slices. **One slice or one invariant set per file.**

### 1. Understand the Change

Read the plan at `changes/NNN-<topic>/plan.md`. Before planning contracts, understand:
- What does the user do? (the action)
- What should happen? (the expected outcome)
- What systems are touched? (the path through layers)

If any of these are unclear, ask. Wrong assumptions cascade through every test.

### 2. Identify or Confirm Slice Names

For each slice spec the plan declared (added or modified), confirm the slice it represents. A slice:
- Has a clear user action ("create a workflow run")
- Touches every layer from API to data/external system
- Can be integration tested independently
- Delivers visible value when complete

If the plan declared a spec that turns out to be too big (two slices smushed together), propose splitting. If two declared specs are actually one slice, propose merging. Confirm with the user before proceeding.

**Checkpoint 1: validate slice naming with the user — confidence-gated.**

High confidence: present the list as FYI and move on. Medium/low: present and wait.

### 3. Define Mock Boundaries

**Default posture: live testing.** Mocks are a fallback when hitting a real system is genuinely impractical.

| Dependency Type | Default | Why |
|----------------|---------|-----|
| Controlled (your DB, file system, queue) | Real instance | You own it. Test against production-equivalent infrastructure. |
| Uncontrolled WITH a safe test environment (Stripe test mode, GitHub sandbox, OAuth dev apps, sandbox APIs) | Prefer the real test environment over mocking | Higher confidence. Catches API changes the day they happen. |
| Uncontrolled WITHOUT a safe test environment (production-only APIs, paid services with no sandbox, destructive side effects) | Mock at the HTTP client layer, pushed as far outward as practical | Can't use safely in tests. Mock far enough out that the adapter's own logic still runs for real. |

**Push the mock boundary outward.** Mock the HTTP client the adapter calls, not the adapter's public interface. Every layer inside the mock runs real; every layer outside runs stubbed.

**Never use in-memory substitutes.** No SQLite for Postgres, no fake Redis, no in-memory queue. Test against the same type and version as production. In-memory substitutes hide the bugs that hurt most: schema mismatches, constraint violations, driver quirks.

Present boundary decisions to the user — they know which systems have usable test environments better than the AI does. Ask: "Does [service] have a test mode we can hit in CI?"

**Promote to context/.** When mock boundary decisions reveal system-level patterns ("all external APIs go through a proxy," "test suite uses real Postgres, never SQLite"), write these to `context/testing.md` or the relevant topic file.

### 4. Write Integration Test Contracts into Each Spec File

For each slice spec, write or extend the integration test contract directly in the file. The contract lands in `spec/<name>.md`, not in the plan.

**Contract shape (plain text inside the spec file):**

```markdown
## Integration test contract

**Setup:** [What state must exist before the test runs]
**Action:** [The API call or user action]
**Input:** [Request body, parameters, headers]
**Expected output:** [Response status, body shape, key fields]
**Side effects:** [Database changes, events emitted, files created]

### Error cases
- **When [condition], Then [behavior]** — [details]
- **When [condition], Then [behavior]** — [details]
```

A slice spec can have **multiple error cases and edge cases** — each is a test case under the same contract. Don't artificially limit to one.

**Editing the spec file:**
- If the file exists, propose additions or modifications. New cases are new bullets; modified cases show before/after.
- If the file doesn't exist (new slice spec), create it using the slice spec format below.

**Checkpoint 2: validate contract edits with the user — confidence-gated.**

High confidence: present contracts together, apply edits unless flagged.
Medium confidence: present one contract at a time, wait for confirmation.
Low confidence: present one at a time, explicitly ask about inputs/outputs/side effects/error cases.

Apply edits to the spec files as they're validated. The file is the durable record.

### 5. Plan Unit Test Coverage (Optional Sketch)

For each slice, sketch which unit tests at each layer add value beyond the integration test:
- Route handler: input validation, status code mapping
- Service: complex business logic, error mapping
- Adapter: API response transformation, error handling

Unit tests are lower stakes — the AI determines most during implementation. Flag any unit tests where the business logic is non-obvious or has edge cases the user should know about. Don't enumerate exhaustively; the integration test contract is the load-bearing artifact.

### 6. Walking Skeleton Contract (Greenfield Only)

On greenfield, the first slice spec's contract describes the **walking skeleton path**: the thinnest request that flows through every boundary and returns a contract-shaped stub response. Assert on the response shape, not on business logic.

Build handles the V0a (boundary scaffold) / V0b (walking skeleton wiring) split internally — you don't write separate contracts for them. One walking skeleton contract describes the V0 outcome; build derives the two-phase implementation.

Infrastructure checks (server starts, DB connects, CI runs tests) are build's pre-flight responsibility, not test contracts.

### 7. Confirm Spec Updates Landed

After all checkpoints:
- Every contract declared in the plan has landed in the relevant `spec/<name>.md`
- `spec/README.md` updated if a new slice or invariant spec was added
- The plan still references which spec files were modified — no contract content duplicated there

Report to the user:
> "Contracts applied. `spec/create-workflow.md` and `spec/workflow-lifecycle.md` updated. test-writer will read from spec/ directly."

## Slice Spec File Format

```markdown
---
status: planned     # planned | in-progress | built | superseded
depends_on: []      # other spec file names this slice requires
---

# [Slice Name]

## Does
[One sentence — what this slice accomplishes for the user]

## Done when
- [Observable outcome 1]
- [Observable outcome 2]

## Integration test contract

**Setup:** [preconditions]
**Action:** [what happens]
**Input:** [shape]
**Expected output:** [shape]
**Side effects:** [state changes]

### Error cases
- **When [condition], Then [behavior]**
- **When [condition], Then [behavior]**

## Tests
- `<test file path>` § `"<test name>"` — covers § <case or contract section>
- [If no test exists yet (slice is `planned` / `in-progress`), state that explicitly: "No test exists yet — test-writer will produce one when this slice is built."]

## Notes
- [Decisions, rationale, things to remember about this slice]

## Changes
- NNN (YYYY-MM-DD) — [what was added in this change]
```

The `## Tests` section is the forward pointer from spec → enforcing test. test-planning leaves the placeholder (or a "no test yet" note for `planned` slices); **test-writer** fills it in when it commits the test files. Build reads it to find the locked tests it must implement against.

## Invariant Spec File Format

```markdown
---
status: built       # invariants are typically already enforced; this tracks whether they're documented
---

# [Invariant Set Name]

## Rules
- [Rule 1] — [why it must hold]
- [Rule 2] — [why it must hold]

## Tests that enforce these rules
- `spec/<slice-name>.md` § Error cases — checks rule 1 via [scenario]
- `spec/<slice-name>.md` § Integration test contract — checks rule 2 via [scenario]

## Notes
- [Cross-cutting decisions, history]

## Changes
- NNN (YYYY-MM-DD) — [what changed]
```

## Output Format

Test-planning produces edits to `spec/*.md` files (primary output) and a brief summary back to the design orchestrator:

```markdown
## Test Planning Summary

### Spec files modified
- `spec/create-workflow.md` — added integration test contract + 3 error cases
- `spec/workflow-lifecycle.md` — added new transition rule (paid → shipped)

### Spec files created
- `spec/list-workflows.md` (new) — slice spec for GET /api/workflows

### Mock boundaries
- Real: Postgres, workflow service, internal queue
- Mocked at HTTP client: GitHub webhook delivery (no sandbox), email provider

### Context updates
- `context/testing.md` — added "external APIs without sandbox mock at HTTP client" decision

### Test infrastructure notes
- [Setup needed: test database, fixtures, mock servers]
- [CI considerations]
```

The summary gets pasted into `changes/NNN/plan.md` as a "Test planning result" section. The contracts themselves live in `spec/`.

## Bias Guards

| Trap | Antidote |
|------|----------|
| Testing what's easy, not what matters | Ask: "If this test passes, am I confident the slice works?" If no, the contract is wrong. |
| Too many slices | Most changes are 1–5 slices. If you have 10+, you're slicing too thin or the change is too big. |
| Skipping error cases | Every contract needs error cases. Happy path only = false confidence. The slice isn't tested. |
| One test case per contract | A contract can have many cases — happy path, errors, edge conditions. Don't artificially limit. |
| Assuming mock boundaries | Ask the user. They know which systems are controlled vs uncontrolled. |
| Over-specifying unit tests | Unit test planning is a suggestion. The AI refines during implementation. |
| Capability files bundling many slices | One spec = one slice (or one invariant set). Don't recreate the old "workflows.md contains everything workflow-related" pattern. |

## Guidelines

- **The user is the authority on correctness.** The AI knows testing methodology. The user knows how the system should behave.
- **Contracts first, code later.** test-planning is a design activity. Don't write test code here — that's test-writer's job.
- **Pacing depends on confidence.** High: present contracts together and proceed. Medium/low: one at a time. When in doubt, round confidence down.
- **Error cases are not optional.** Every contract needs failure scenarios. The happy path is the easy part.
- **One slice per spec file.** Don't bundle. Don't nest. Each file describes one testable thing.
- **The integration test contract is the definition of done.** Without it, a slice spec is an unfinished idea — don't hand it to test-writer.
