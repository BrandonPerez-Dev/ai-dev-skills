---
name: test-planning
description: >-
  Land integration test contracts inside spec/<name>.md files — one file per
  slice. Each contract names setup, action, input, expected output, side
  effects, and error cases in plain text. Reads context/ for architectural
  constraints that inform mock boundaries. On greenfield, bootstraps spec/
  from the sliced scope. Heavy user involvement with checkpoints.
when_to_use: >-
  Use after slicing lands scope (specs marked planned/in-progress) — typically
  invoked by engineering between slicing and test-writer. Also use directly
  when you need to update a spec's contract without going through a full
  design pass.
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
Contracts live in `spec/<name>.md` and nowhere else — the spec file is the
single source of truth for what proves a slice done. Don't restate contract
content in context/, commit messages, or conversation summaries; point at the
spec instead.
</HARD-GATE>

<HARD-GATE>
Contracts require user visibility. At high confidence, present and proceed
unless flagged. At medium/low confidence, wait for explicit validation. If the
contract is wrong, the AI will perfectly implement the wrong thing — when in
doubt, round confidence down.
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
| Greenfield (first change in project) | Bootstrap `spec/` — derive slice spec files from the sliced scope and `context/` decisions | Deep — every contract validated; spec/ is being defined for the first time |
| Adding to existing system | Work the specs marked `planned`/`in-progress`, edit in place to extend/refine contracts | Medium — validate new contracts, respect existing invariants |
| Refactoring | Characterization contracts first: capture current behavior in spec/ (if missing), then plan changes | Medium — contracts should NOT change |
| Bug fix | Add a failing-test contract to the relevant slice spec that reproduces the bug | Light — one contract, user confirms the bug scenario |

## Process

### 0. Load Context and Scope

Before planning contracts:

**`context/` — always loaded.** Read all files. Architectural decisions here inform mock boundaries — e.g., if `context/proxy.md` says "all LLM calls go through LiteLLM," that determines which dependencies are real vs mocked. Standing rejections tell you which designs not to re-propose.

**`spec/` — the scope.**
- Read `spec/README.md` if it exists.
- The in-scope specs are those marked `status: planned` or `in-progress` (slicing set these). If invoked directly with specific spec names/paths, use those.
- Read each in-scope spec's stub — its `## Does`, `## Notes` (slice decisions, non-goals, open questions), and `## Changes` tell you the intent; `context/` tells you the constraints.

**If `spec/` doesn't exist (greenfield, first change):**
Bootstrap `spec/` during this skill's run. Derive slice spec file names from the sliced scope (the conversation + `context/` decisions). Propose the list before creating any files:

> "I'm going to create these slice specs: `create-workflow.md`, `list-workflows.md`, `workflow-lifecycle.md` (invariants). Does this slicing match how you think about the feature?"

Only create files after confirmation. Seed each with the relevant rationale in its `## Notes`.

**What counts as one spec file:**
- One testable slice = one file (`create-workflow.md`)
- One coherent set of cross-cutting rules = one file (`workflow-lifecycle.md`)
- A multi-step workflow that needs end-to-end testing = one file (`checkout-flow.md`)

**Not** one file per source module. **Not** one file per capability bundling many slices. **One slice or one invariant set per file.**

### 1. Understand the Change

From the in-scope specs' stubs, `context/`, and the user, establish:
- What does the user do? (the action)
- What should happen? (the expected outcome)
- What systems are touched? (the path through layers)

If any of these are unclear, ask. Wrong assumptions cascade through every test.

### 2. Identify or Confirm Slice Names

For each in-scope spec, confirm the slice it represents. A slice:
- Has a clear user action ("create a workflow run")
- Touches every layer from API to data/external system
- Can be integration tested independently
- Delivers visible value when complete

If a spec turns out to be too big (two slices smushed together), propose splitting. If two specs are actually one slice, propose merging. Confirm with the user before proceeding.

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

**Promote to context/.** When mock boundary decisions reveal system-level patterns ("all external APIs go through a proxy," "test suite uses real Postgres, never SQLite"), write these to `context/testing.md` or the relevant topic file — with any rejected alternative and its why-not.

### 4. Write Integration Test Contracts into Each Spec File

For each slice spec, write or extend the integration test contract directly in the file.

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
- Superseding an existing contract case (flagged by grill or slicing) is done here explicitly: mark the old case superseded, name the successor, and route the re-lock through test-writer.
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

### 7. Commit and Confirm

After all checkpoints:
- Every in-scope spec has its contract landed in the file
- `spec/README.md` updated if a new slice or invariant spec was added
- Commit the spec edits; the commit message summarizes contracts landed, mock boundaries decided, and any supersessions executed — that message is the durable test-planning record

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
- [Slice-specific decisions (with rejected alternatives where real), non-goals, open questions]

## Changes
- YYYY-MM-DD — [what changed and why, one line per change]
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
- YYYY-MM-DD — [what changed]
```

## Test-less Specs Block Modification

When a change touches a spec whose `## Tests` section is empty or backlogged ("none yet"), flag it before extending the contract: the slice needs characterization tests locked first, so its current behavior is pinned before it changes. Honest "no tests yet" notes beat fabricated contracts, but they are a debt marker, not a license — the debt comes due the moment the slice is reopened, not later.

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
- **The integration test contract is the definition of done.** Without it, a slice spec is an unfinished idea — don't hand it to build.
