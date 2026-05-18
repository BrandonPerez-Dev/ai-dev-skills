
---
name: ai-agent-building
description: >-
  Building AI agents with Claude — Agent SDK, tool design, orchestration patterns,
  and eval-driven testing. Use when designing, building, or debugging AI agent systems.
  Covers both Claude Agent SDK programmatic agents and Claude Code skills (which are agents).
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
  - Skill
---

# AI Agent Building

Start with one agent and the right tools. Earn complexity.

<HARD-GATE>
Do NOT ship an agent without running evals. Agent behavior is non-deterministic — a single successful run proves nothing. Run 3-5 trials per eval task and measure pass rates before deploying. An agent without evals is a demo, not a product.
</HARD-GATE>

## The Agent Equation

Every agent — whether built with the Claude Agent SDK or as a Claude Code skill — is the same thing:

```
Agent = System Prompt + Tools + Context + Orchestration
```

The SKILL.md body is a system prompt. The `allowed-tools` list is a tool configuration. The `references/` directory is a knowledge base. Invoking other skills is agent chaining. Understanding this equivalence means agent-building best practices improve everything you build.

## Method Selection

| Situation | Approach | Start With |
|-----------|----------|------------|
| **New agent from scratch** | Full process below | Step 1: Define |
| **Adding tools to existing agent** | Tool design focused | Step 3: Tools, then re-eval |
| **Multi-agent system** | Orchestration patterns | Verify single agent fails first |
| **Agent underperforming** | Diagnose before changing | Diagnosis table below |
| **Building a Claude Code skill** | Same process, different packaging | Skill-creator + this skill |

## Process

### 1. Define the Task

In one sentence: what does this agent do? If you can't say it in one sentence, the scope is too broad — split it.

Establish:
- **Success criteria** — measurable, not "works well"
- **Input/output contract** — what goes in, what comes out
- **Boundary** — what this agent deliberately does NOT do

### 2. Design the Prompt

Invoke the **prompt-engineering** skill. Key decisions:

- **Altitude** — how specific should instructions be? (fragile operations → low freedom, judgment calls → high freedom)
- **Motivation-based rules** — explain WHY, not just WHAT. Models generalize from motivation.
- **Structure** — XML sections for multi-part prompts. Position critical constraints at edges (top and bottom).
- **Examples** — 3-5 diverse examples beat 10 generic ones. Include edge cases.
- **Grounding** — tell the agent where to source facts. Grant permission to say "I don't know."

### 3. Design the Tools

Tools are where the agent acts. Anthropic found that optimizing tool descriptions alone improved task completion by 40%.

**Principles:**
- **Fewer tools = more reliable.** Agents degrade above ~15 tools. Start with 3-5.
- **Quality over quantity.** One well-described tool beats three vague ones.
- **Consolidate similar tools.** `manage_event(action, ...)` not `create_event()` + `update_event()` + `delete_event()`.

**For each tool, specify:**
- Unambiguous parameter names with format examples (`date: string — "ISO 8601, e.g., '2026-03-04'"`)
- What the tool returns (and a `detail_level` parameter if responses can be large)
- Structured error responses with suggested fixes
- Input examples for complex parameter shapes

See `references/claude-agent-sdk.md` for SDK-specific tool configuration, MCP server setup, and hooks.

### 4. Design the Architecture

For anything beyond a single agent with tools, invoke the **architecture** skill.

**Default: single agent with tools.** Only add complexity when you can demonstrate the single agent fails. Reasons to split:

| Signal | Pattern to Consider |
|--------|-------------------|
| Tool count > 15 | Split into orchestrator + specialist agents |
| Conflicting instructions | Separate agents with different system prompts |
| Security boundaries | Agents with different permission levels |
| Sequential specialization | Pipeline: Agent A → Agent B → Agent C |
| Independent parallel work | Fan-out/fan-in with result merging |

**Orchestration costs are real.** Multi-agent systems use ~15x more tokens than single agents. Token usage explains 80% of performance variance in complex systems. Every additional agent must justify its cost.

### 5. Build with Evals

Invoke the **eval-driven-dev** skill. Agent evals are the outer loop — write them before implementation.

**Minimum viable eval suite:**
- 5-10 representative tasks from real use cases
- Mix of easy, medium, and hard
- 3-5 trials per task (non-determinism requires statistical confidence)
- Target: >80% pass rate before shipping

**Grader selection:**

| Grader | When | Example |
|--------|------|---------|
| **Code-based** | Deterministic outcome | Did the file get created? Did the API return 200? |
| **Model-based** | Subjective quality | Was the response helpful? Did it follow the rubric? |
| **Human** | High-stakes or ambiguous | Is this medically accurate? Is this legally sound? |

Use code-based wherever possible. Calibrate model-based graders against human judgment.

**Eval anti-patterns:**
- Single trial per task — one run proves nothing
- Exact string matching for LLM output — use structural and semantic checks
- Testing implementation ("did it call tool X?") vs. outcome ("did it solve the problem?")
- Shared state between trials — previous trials corrupting current ones

### 6. Iterate

After evals reveal failure modes:
1. Read agent transcripts — automated evals miss subtle failures
2. Diagnose using the table below
3. Fix the specific component (prompt, tools, or architecture)
4. Re-run evals to verify improvement
5. Watch for regressions in previously passing cases

## Diagnosis Table

When an agent underperforms, identify the failing component before changing anything.

| Symptom | Likely Component | Fix |
|---------|-----------------|-----|
| Agent uses wrong tool | Tool descriptions overlap or are vague | Rewrite descriptions (prompt-engineering skill) |
| Agent retries same failing action | No retry limit or fallback strategy | Add max retry + approach-change logic to prompt |
| Agent loses context mid-task | Context window overflow | Use subagents for independent subtasks; summarize intermediate results |
| Agent hallucinates tool params | Parameter descriptions ambiguous | Add format specs and input examples to tool definitions |
| Agent ignores key instructions | Critical info buried in middle of prompt | Reposition to edges; use `<HARD-GATE>` blocks |
| Agent claims success without checking | No verification step in prompt | Add explicit verification instructions; use hooks for enforcement |
| Agent scope creeps | Boundary not defined | Add "Non-goals" section to system prompt |
| Agent picks wrong subagent | Subagent descriptions overlap | Rewrite descriptions with clear "Use when" clauses |

## Rationalization Guards

| Thought | Reality |
|---------|---------|
| "I need multi-agent orchestration" | Start with one agent + tools. Prove it fails before splitting. |
| "The prompt just needs tweaking" | If 2+ prompt iterations haven't fixed it, the problem is tools or architecture. |
| "One successful run means it works" | Non-deterministic. Run 3-5 trials. |
| "More tools = more capable" | More tools = more confusion above ~15. Quality over quantity. |
| "I'll add evals later" | You'll ship without them. Write evals first. |
| "The agent is smart enough to figure it out" | Agents need explicit structure. Ambiguity causes hallucination. |

## SDK & Configuration Reference

For implementation details, see the reference files in this directory:

- **`references/claude-agent-sdk.md`** — Claude Agent SDK API reference (TypeScript + Python). Verified signatures for `query()`, hooks, MCP servers, subagents, session resume. Read this when writing SDK code.
- **`references/model-selection.md`** — Current model IDs, pricing, and selection heuristics. Read this when choosing models for agent tiers.

## Guidelines

- **One agent first.** Multi-agent systems are harder to debug, test, and reason about. Start simple. Add orchestration only when the single agent demonstrably fails — not when it feels like it should fail.
- **Tools are prompts.** Every tool description, parameter name, and error message is prompt engineering. Treat them with the same rigor as system prompts. A 40% improvement from description optimization means this is some of the highest-leverage work you can do.
- **Evals before shipping.** Non-deterministic systems need statistical evidence. "It worked when I tried it" is anecdote, not data. 3-5 trials minimum per eval case.
- **Transcripts reveal truth.** Automated evals catch outcomes. Transcript review catches process failures — agents that pass evals with bad reasoning are fragile. Read transcripts regularly.
- **Diagnose before fixing.** When an agent underperforms, identify which component is failing (prompt, tools, architecture, context) before changing anything. The diagnosis table prevents wasted iteration.
