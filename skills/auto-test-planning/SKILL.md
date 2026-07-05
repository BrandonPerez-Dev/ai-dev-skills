---
name: auto-test-planning
description: >-
  Autonomous test contract writing for GitHub-driven development. Reads context/
  and spec/ files, writes integration test contracts into spec/<name>.md, classifies
  confidence on every contract decision, and posts assumptions/questions as PR
  comments on the slice PR. Proceeds on medium-confidence assumptions without
  waiting for human review.
when_to_use: >-
  Use after auto-plan-grill has produced a plan with spec stubs. Picks up
  unblocked slices and writes integration test contracts into their spec files.
  Do NOT use for interactive test planning — use test-planning for that.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Task
argument-hint: "[spec file path or plan path]"
effort: high
---

# Auto Test Planning

Write integration test contracts autonomously. Read the spec stubs from auto-plan-grill, fill in contracts, classify confidence, post questions to GitHub, and hand off to auto-test-writer.

## The Model

Each `spec/<name>.md` file describes one testable slice. auto-plan-grill created stubs with `status: planned` and placeholder contracts. This skill fills in the real contracts: setup, action, input, expected output, side effects, and error cases.

<HARD-GATE>
Contracts live in `spec/<name>.md`, never in the plan. The plan holds rationale only. Don't duplicate — the spec file is the single source of truth.
</HARD-GATE>

<HARD-GATE>
Do not write test code. Do not write implementation code. Output is contract text inside spec files. auto-test-writer translates contracts to code; auto-build implements against them.
</HARD-GATE>

## Input

One of:
- **Plan path** — `changes/NNN-<topic>/plan.md` listing all in-scope specs
- **Single spec path** — `spec/<name>.md` to write contracts for one slice
- **Slice PR** — the agent reads slice branch state and finds specs needing contracts

## Process

### 0. Load Context and Spec

**`context/` — always loaded.** Read all files. Architectural decisions inform mock boundaries.

**`spec/` — loaded per change.** Read spec files listed in the plan's "Spec changes" section.

**Existing test patterns.** Read existing test files to understand the project's test conventions (framework, helpers, fixtures, assertion style).

### 1. Pick the Next Unblocked Slice

Work slices in dependency order from the plan. Skip slices blocked by unanswered low-confidence questions from auto-plan-grill.

### 2. Define Mock Boundaries

Decide mock boundaries autonomously using context/ and codebase patterns.

| Dependency Type | Default | Why |
|----------------|---------|-----|
| Controlled (your DB, file system, queue) | Real instance | You own it. Test against production-equivalent infrastructure. |
| Uncontrolled WITH test environment (Stripe test mode, sandbox APIs) | Real test environment | Higher confidence. Catches API changes. |
| Uncontrolled WITHOUT test environment (production-only, paid, destructive) | Mock at HTTP client layer | Can't use safely. Mock far enough out that adapter logic still runs real. |

**Never use in-memory substitutes.** No SQLite for Postgres, no fake Redis.

**Promote to context/.** When mock boundary decisions reveal system-level patterns, write them to `context/testing.md`. Mark as agent-proposed.

### 3. Write Integration Test Contracts

For each slice spec, write the integration test contract directly in the file.

**Contract shape:**

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

**Confidence classification per contract:**

| Confidence | Action | GitHub artifact |
|---|---|---|
| **High** | Write the contract. Proceed. | FYI comment on slice PR: "Contract ready for `<slice>`, proceeding to test writing." |
| **Medium** | Write the contract with assumptions marked. Proceed. | Assumption comment on spec file: "ASSUMPTION: [decision]. Building against this unless corrected." |
| **Low** | Write the contract as a proposal. Do NOT hand off to test-writer. | Blocking comment on spec file: "BLOCKING: [question]. Cannot write reliable tests until resolved." |

**What raises confidence:**
- context/ documents the mock boundary or testing pattern
- Existing tests demonstrate the pattern
- The spec's "Does" and "Done when" are unambiguous

**What lowers confidence:**
- Multiple valid testing approaches with no clear signal
- The slice touches systems not documented in context/
- Error case behavior isn't specified in the plan or context/
- Security or data-integrity scenarios

### 4. Walking Skeleton Contract (Greenfield Only)

On greenfield, the first slice spec's contract describes the walking skeleton path: the thinnest request that flows through every boundary and returns a contract-shaped stub response. Assert on response shape, not business logic.

### 5. Commit and Push to Slice Branch

1. Commit updated spec files to the slice branch
2. Push
3. Post PR comments for each contract:
   - High confidence: single FYI comment summarizing contracts ready
   - Medium confidence: assumption comment on the specific spec file lines
   - Low confidence: blocking comment with slices affected

### 6. Update Open Questions

If any contracts are low-confidence, update `changes/NNN-<topic>/open-questions.md` with the new blocking questions.

### 7. Next Slice

Move to the next unblocked slice. Repeat from step 1.

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
- [No test exists yet — auto-test-writer will produce one when this slice is built.]

## Notes
- [Decisions, rationale]

## Changes
- NNN (YYYY-MM-DD) — [what was added]
```

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Marking all contracts as blocking** | Most contracts can be derived from context/ and codebase patterns. Only block when the wrong contract would require significant rework. |
| **Skipping error cases** | Every contract needs error cases. Happy path only = false confidence. |
| **Guessing mock boundaries** | Derive from context/ and existing test patterns. If genuinely unknown, mark as medium-confidence assumption. |
| **Writing test code** | Contracts are plain text. auto-test-writer translates to code. |
| **Duplicating spec content in the plan** | The spec holds contracts. The plan points at specs. |
| **Asking the human before checking context/** | Context/ and existing tests answer most questions. Only post to GitHub if genuinely stuck. |

## Output

This skill produces:
1. Updated `spec/<name>.md` files with integration test contracts
2. PR comments on slice PRs (FYI, assumption, or blocking)
3. Updated `open-questions.md` (if new blocking questions)
4. Context/ updates for discovered testing patterns (marked agent-proposed)

## Handoff

After this skill completes:
- **auto-test-writer** picks up specs with high/medium-confidence contracts and writes executable tests
- The human reviews contracts asynchronously via slice PR comments
- As answers arrive, blocked slices become unblocked

## Guidelines

- **GitHub is the communication channel.** Post questions as PR comments on the slice PR, not in conversation.
- **Silence = approval.** For high and medium-confidence contracts, the human doesn't need to respond.
- **Error cases are not optional.** Every contract needs failure scenarios.
- **One slice per spec file.** Don't bundle.
- **The contract is the definition of done.** Without it, a spec is an unfinished idea.
- **Proceed on unblocked work.** Don't wait for all questions to be answered.
