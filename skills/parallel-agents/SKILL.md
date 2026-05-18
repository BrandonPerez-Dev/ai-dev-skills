
---
name: parallel-agents
description: Dispatching multiple agents for independent problems. Use when facing 2+ independent tasks that can be worked on without shared state or sequential dependencies.
---

# Parallel Agents

Dispatch multiple subagents for genuinely independent work. Fan out, fan in, synthesize.

<HARD-GATE>
Before dispatching parallel agents, pass the independence test. If ANY check fails, run sequentially.
</HARD-GATE>

## When to Use

- 2+ tasks with no data dependencies between them
- Investigation across independent subsystems
- Research requiring multiple source types (codebase + docs + web)
- Review from multiple perspectives (security + performance + correctness)
- Fixing bugs in unrelated modules

## When NOT to Use

- Tasks share mutable state (same files, same database)
- Task B needs Task A's output as input
- Work is a single coherent problem (don't split what's naturally whole)
- Fewer than 3 subtasks (overhead exceeds benefit)

## Independence Test

All four must be YES before parallelizing:

```
1. Can Task B start right now without Task A's output?     → YES
2. Do they modify different files/resources?                → YES
3. Can one fail without cascading to others?                → YES
4. Are scope boundaries clear and non-overlapping?          → YES
```

If any is NO → run sequentially. If you're unsure → run sequentially.

## The Scope Triangle

Every subagent prompt needs three things. Missing any one causes rework.

### 1. Role — What kind of agent?
```
"You are a TypeScript test author focused on integration tests."
```

### 2. Scope — What can it touch, what can't it?
```
"Work only in src/auth/. Do not modify src/database/ or any config files."
```

### 3. Output — What should the result look like?
```
"Return: summary of findings, files changed with line numbers, and any open questions."
```

## Prompt Template

```markdown
## Task: [Specific task name]

**Role:** [What kind of agent — investigator, implementer, reviewer]

**Context:**
[2-3 sentences of relevant background. Include file paths, error messages, or design context.
Don't paste entire files — reference them by path so the agent can read what it needs.]

**Scope:**
- Files: [Specific files or directories this agent owns]
- Boundaries: [What NOT to touch]
- Tools: [Any tool restrictions — read-only for review agents]

**Deliverable:**
[Exactly what to return. Be specific: "Return the root cause with file:line reference"
not "Tell me what you find."]

**Constraints:**
- [Time/token budget if relevant]
- [Don't install dependencies / don't modify tests / read-only]
```

## Dispatch Patterns

### Fan-Out / Fan-In (Most Common)

Distribute independent tasks, collect all results, synthesize.

```
Main Agent
  ├─ dispatch → Agent 1 (module A)
  ├─ dispatch → Agent 2 (module B)
  └─ dispatch → Agent 3 (module C)

  [wait for all]

  synthesize results → unified summary
  verify → run full test suite
```

**Use when:** Independent subtasks with a single integration point.

### Scatter-Gather (Research)

Multiple agents explore the same question from different angles.

```
Main Agent
  ├─ dispatch → Agent 1 (codebase exploration)
  ├─ dispatch → Agent 2 (documentation review)
  └─ dispatch → Agent 3 (web research)

  [wait for all]

  triangulate → findings supported by 2+ sources = high confidence
```

**Use when:** Research questions where multiple perspectives matter.

### Parallel Review (Quality Gates)

Same code reviewed from different lenses simultaneously.

```
Main Agent
  ├─ dispatch → Agent 1 (correctness review)
  ├─ dispatch → Agent 2 (security review)
  └─ dispatch → Agent 3 (performance review)

  [wait for all]

  merge feedback → deduplicate, prioritize by severity
```

**Use when:** Code review where each perspective is independent.

## Claude Code Specifics

### Task Tool Options

| Mode | When | Trade-off |
|------|------|-----------|
| **Foreground** (default) | Need results before proceeding | Blocks until complete |
| **Background** (`run_in_background: true`) | Have other work to do in parallel | Can't approve permissions interactively |
| **Worktree** (`isolation: worktree`) | Agents modify the same files | Isolated git branches, manual merge needed |

### Model Selection

| Agent Type | Recommended Model | Why |
|-----------|-------------------|-----|
| **Exploration / read-only** | `haiku` | Fast, cheap, sufficient for Glob/Grep/Read |
| **Analysis / synthesis** | `sonnet` | Good balance of depth and speed |
| **Complex implementation** | `opus` or inherit | Full reasoning needed |

### Practical Limits

- **3-5 agents** is the sweet spot for most tasks
- **7 agents** is the practical maximum — beyond this, synthesis overhead dominates
- Each agent gets fresh context — large codebases mean expensive setup per agent
- Background agents need permissions pre-approved — they can't ask interactively

### Resume Pattern

If an agent fails (permissions, timeout, wrong approach):

```
1. Check the agent's output for what went wrong
2. Resume with the agent ID if the context is still valid
3. OR dispatch a fresh agent with corrected prompt if the approach was wrong
```

Don't resume an agent after the codebase has changed underneath it — the context is stale.

## Synthesis

After all agents return, synthesis is your job. Don't skip it.

### Merge Checklist

```
1. □ Read each agent's summary
2. □ Check for conflicts: did any agents touch the same files?
3. □ Check for contradictions: do findings disagree?
4. □ Check for gaps: did any agent miss its scope?
5. □ Integrate changes (apply sequentially, test after each)
6. □ Run full test suite — agents verified independently, you verify together
```

### Conflict Resolution

| Conflict Type | Detection | Resolution |
|--------------|-----------|------------|
| **File conflict** | Two agents edited the same file | Apply one agent's changes first, then manually merge the other |
| **Semantic conflict** | Agent A's fix breaks Agent B's assumption | Re-run Agent B with Agent A's changes as context |
| **Test interference** | Agent A's new test affects Agent B's | Run tests in isolation to identify, then fix ordering |
| **Architecture mismatch** | Agents assumed different patterns | Pick the better pattern, re-run the other agent with constraint |

## Partial Failure Handling

When some agents succeed and others fail:

```
All agents succeeded?
  → YES: Synthesize and verify
  → NO: How many failed?
    → 1 of N: Integrate successes, re-dispatch failed agent
    → Most failed: Something is systematically wrong — investigate before retrying
    → Infrastructure failure (permissions, timeout):
      Resume in foreground to approve/retry
    → Real failure (wrong approach, bad results):
      Dispatch fresh agent with corrected prompt
```

Don't block all progress because one agent failed. Integrate what succeeded, fix what didn't.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| **Monolithic parallelism** | All agents attack the same problem from the same angle | Structure the problem into naturally independent parts first |
| **Scope overlap** | Agents compete for the same files → merge conflicts | Assign explicit file boundaries per agent |
| **Over-specification** | 500-word prompts that constrain agents into brittle solutions | Scope triangle only — role, boundaries, deliverable |
| **Under-specification** | "Fix the tests" with no scope → agents solve different problems | Be specific: which tests, which files, what's expected |
| **Context dumping** | Pasting entire files into every agent prompt | Reference by path — let agents read what they need |
| **Ignoring uncertainty** | Agent says "I'm unsure about X" and you treat result as definitive | Uncertainty from agents = open question for you to investigate |
| **Parallelizing sequential work** | Dispatching agents that actually depend on each other's output | Run the independence test. If it fails, run sequentially. |

## Examples

### Parallel Bug Investigation

Three test failures in unrelated modules:

```
Agent 1: "Investigate test failure in src/auth/login.test.ts. The test
'should reject expired tokens' fails with 'expected 401, got 200'.
Read the test, trace the auth middleware, find root cause.
Return: root cause with file:line reference."

Agent 2: "Investigate test failure in src/billing/invoice.test.ts. The test
'should calculate tax correctly' fails with 'expected 10.50, got 10.00'.
Read the test, trace the calculation logic, find root cause.
Return: root cause with file:line reference."

Agent 3: "Investigate test failure in src/notifications/email.test.ts. The test
'should send welcome email' fails with timeout.
Read the test, check the email service mock, find root cause.
Return: root cause with file:line reference."
```

### Parallel Research

Understanding a new codebase:

```
Agent 1 (haiku): "Explore the project structure. Read package.json,
tsconfig, entry points. Map: what frameworks, what build tools,
what test runner. Return: project overview with key file paths."

Agent 2 (haiku): "Find all API endpoints. Grep for route definitions,
HTTP handlers, middleware. Return: list of endpoints with
file:line references."

Agent 3 (haiku): "Read all documentation: README, docs/, .context/.
Return: summary of architecture decisions, conventions, and
any documented gotchas."

Agent 4 (sonnet): "Search the web for [specific library] best practices
and known issues. Return: key findings with source links."
```

## Guidelines

- **Independence test is non-negotiable.** If tasks aren't independent, parallelism creates more problems than it solves.
- **Scope triangle for every agent.** Role + scope + output. Missing any one = vague agent = rework.
- **3-5 agents is the sweet spot.** More agents = more synthesis overhead. Only go higher for trivially independent tasks.
- **Synthesis is work.** Don't just concatenate results. Check for conflicts, contradictions, and gaps.
- **Use the right model.** Haiku for exploration, Sonnet for analysis, Opus for complex implementation. Don't burn tokens on read-only agents.
