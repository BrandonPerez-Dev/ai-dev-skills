
---
name: ai-agent-building
description: >-
  Building AI agents with Claude — Agent SDK, tool design, orchestration patterns,
  workflows vs agents (Anthropic's Dec 2024 framing), MCP as the production tool-calling
  standard, adaptive thinking, and eval-driven testing. Use when designing, building, or
  debugging AI agent systems. Covers both Claude Agent SDK programmatic agents and
  Claude Code skills (which are agents).
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

**Prefer the simplest pattern that works.** Most production "agent" features should be workflows, not agents. Start with one agent and the right tools. Earn complexity by demonstrating the simpler pattern fails.

## Workflows vs Agents (Anthropic's Dec 2024 framing)

Anthropic's [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents) (December 2024) draws the load-bearing distinction:

- **Workflows** orchestrate LLMs and tools through **predefined routes**. The path through the system is fixed at design time; the LLM fills in blanks but doesn't change the structure. Predictable, debuggable, cost-bounded.
- **Agents** are systems where the LLM **dynamically directs its own process and tool usage**. The path emerges at runtime. Flexible, expensive, harder to reason about.

**Five workflow patterns to consider before going agentic:**
1. **Prompt chaining** — fixed sequence of LLM calls, each operating on the previous output
2. **Routing** — classify input, dispatch to one of several predefined paths
3. **Parallelization** — concurrent LLM calls (sectioning for independent sub-tasks, voting for redundancy)
4. **Orchestrator-workers** — central LLM decomposes the task and assigns sub-tasks to worker LLMs
5. **Evaluator-optimizer** — one LLM generates, another evaluates and provides feedback in a loop

**The default.** Prefer the simplest pattern. Add complexity only when needed. Agentic loops typically multiply token usage 3-10x; one production deployment reported per-query costs of $0.02 (simple workflow) to $0.31 (complex agentic). Routing every query through an agent when most don't need it is the most expensive default this skill exists to prevent.

## Verify before shipping

Agent behavior is non-deterministic — a single successful run proves nothing. Run **3-5 trials per eval task** and measure pass rates before deploying. An agent shipped without evals is a demo, not a product. The same holds for workflow-shaped features whose outputs depend on LLM judgment. See Step 5: Build with Evals.

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

Tools are where the agent acts. Anthropic's [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) found that optimizing tool descriptions alone improved task completion by 40% on internal SWE-bench work.

**Principles (2026 guidance is qualitative, not a hard count):**
- **A few thoughtful tools beat many thinly-scoped ones.** Overlapping or vague tools distract agents; the official guidance is to "prefer a few thoughtful tools targeting specific high-impact workflows" rather than wrapping every API. There is no canonical hard ceiling on tool count, but degradation rises with overlap.
- **Quality over quantity.** One well-described tool beats three vague ones.
- **Consolidate similar tools.** `manage_event(action, ...)` not `create_event()` + `update_event()` + `delete_event()`. Fewer tools = less confusion at the dispatch step.
- **Namespace at scale.** Prefix tools by service (`asana_search`, `jira_search`) to delineate boundaries when multiple integrations share concept space.

**For each tool, specify:**
- Unambiguous parameter names with format examples (`date: string — "ISO 8601, e.g., '2026-03-04'"`)
- What the tool returns, including a `response_format` enum (`"concise" | "detailed"`) when responses can be large — Anthropic reports ~65% token reduction from agents picking concise for routing decisions and detailed only when needed
- **Errors as onboarding.** A tool that returns `Error 400` teaches nothing; a tool that returns `error: field 'date' must be ISO 8601 (YYYY-MM-DD), got '2026/01/15' — try '2026-01-15'` teaches the agent to fix itself on the next call.
- Input examples for complex parameter shapes (nested objects, filter+sort+limit combos)

**Response cap.** Claude Code truncates tool responses at 25,000 tokens by default. For tools that can return more, ship pagination/filtering/response_format rather than relying on truncation — truncation reads as success to the agent.

**MCP as the production default.** [Model Context Protocol](https://modelcontextprotocol.io/) launched November 2024, adopted by every major provider by March 2026 (10,000+ public MCP servers, 97M monthly downloads, donated to the Agentic AI Foundation under the Linux Foundation in December 2025 with Block / Google / Microsoft / AWS / Cloudflare backing). For new agentic systems in 2026, **define tools as MCP servers by default** — the network effect plus governance neutrality made MCP the standard tool-calling contract. Bespoke per-integration wiring pays an integration tax.

See `references/claude-agent-sdk.md` for SDK-specific tool configuration, MCP server setup, hooks, and the `skills` option (replaces deprecated `allowedTools: ["Skill"]`).

### 4. Design the Architecture

For anything beyond a single agent with tools, invoke the **architecture** skill.

**Default: single agent with tools.** Only add complexity when you can demonstrate the single agent fails. Reasons to split:

| Signal | Pattern to Consider |
|--------|-------------------|
| Tool surface too overlapping to describe cleanly | Split into orchestrator + specialist agents with disjoint tools |
| Conflicting instructions | Separate agents with different system prompts |
| Security boundaries | Agents with different permission levels |
| Sequential specialization | Pipeline: Agent A → Agent B → Agent C |
| Independent parallel work | Fan-out/fan-in with result merging |

**Orchestration costs are real.** Multi-agent systems use roughly 15x more tokens than single agents. Token usage explains 80% of performance variance in complex systems. Every additional agent must justify its cost.

**Sub-agent pattern (Anthropic's research-system example).** A LeadResearcher agent plans, spawns specialized Subagents with scoped sub-tasks, each subagent runs its own retrieval / tool loop, the lead synthesizes. Reported quality wins on open-ended questions, at the cost of many more model calls per query. Use when the task genuinely decomposes into independent investigations; pure overhead when sub-tasks are sequentially dependent.

### 4b. Production failure modes to guard against

These hit every agentic system within a month of real traffic. Ship guardrails at deployment, not after the first incident.

| Failure mode | Symptom | Guardrail |
|---|---|---|
| **Retrieval thrash / loop** | Agent keeps retrieving without converging; same content comes back across iterations | Hard step limit (MAX_STEPS=5-10), per-iteration cost cap, "give up gracefully with what you have" instruction in the system prompt |
| **Hallucinated tool calls** | LLM invents tool names, wrong parameter types, non-existent endpoints | Strict tool-schema validation; reject + re-prompt on schema violations with a clear error; track BFCL-style tool-use accuracy in eval |
| **Context bloat / tool storms** | Parallel or long-running tool calls fill the context window with retrieved snippets; reasoning degrades step over step | Per-step context budget; summarize older steps; cap concurrent tool calls |
| **Latency spirals** | Multi-second loop turns into 30-second turns into 90-second as outputs grow and context bloats | Wall-clock timeout per query; stream partial results so the user sees progress; expose "I'm taking longer than usual" states |

Observability (LangSmith, Langfuse, Arize Phoenix for SDK agents; built-in transcripts for Claude Code) is required to diagnose which failure mode is hitting you. Agentic loops without tracing are debug-by-prayer.

### 5. Build with Evals

Invoke the **eval-driven-dev** skill. Agent evals are the outer loop.

**A nuance worth knowing.** The strict "write the eval before the feature" dogma is contested even by its main advocates. Hamel Husain ([Should I practice eval-driven development?](https://hamel.dev/blog/posts/evals-faq/should-i-practice-eval-driven-development.html)) explicitly argues against it because LLM failure surfaces are infinite — you can't enumerate them upfront. The better workflow: **error analysis on real outputs first**, then write evaluators for the failures you discover. Exception: known hard constraints (`never mention competitors`, `never give medical advice`, schema validation) can and should be eval'd upfront — those have a finite enumeration. **The CI gate pattern IS canonical**: once you have evals, run them on every change that affects prompts, retrieval, or model configuration.

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

**LLM-as-judge biases to design around** (each documented in the literature):
- **Position bias** ([arXiv 2406.07791](https://arxiv.org/abs/2406.07791), IJCNLP 2025): pairwise judges prefer the first or last response; documented >10% accuracy shift in pairwise code judging. Randomize presentation order and average across both orderings.
- **Self-preference bias** ([arXiv 2410.21819](https://arxiv.org/abs/2410.21819), Oct 2024): judges prefer responses from their own model family. Use a judge from a different family than the candidates.
- **Style / verbosity bias**: judges prefer verbose, well-formatted responses. Explicit rubric criteria penalizing verbosity; control for response length in scoring.

**Tools (2026 landscape):**
- **[Inspect AI](https://inspect.aisi.org.uk/)** (UK AI Safety Institute, May 2024). Production-grade evaluation framework. 200+ pre-built evals, MIT licensed, supports tool calling + Docker/Kubernetes sandboxing + MCP. Adopted by Anthropic, DeepMind, xAI. The right default for any agentic eval where the model needs to call tools or browse.
- **lm-evaluation-harness** (EleutherAI v0.4.x). Standard for running standardized benchmarks (MMLU-Pro, GPQA, BBH, MuSR). Use to filter candidate models, not as a verdict for production fit.
- **DeepEval**, **promptfoo**, **RAGAS** (RAG-specific). Application-layer eval harnesses for CI integration.
- **BFCL** (Berkeley Function Calling Leaderboard). De facto standard for function-calling / tool-use eval; V4 Agentic (July 2025) added multi-hop reasoning, error recovery, memory management.
- **Tau-bench** (Sierra Research). Realistic agent-user-tool interactions, closer to production agent shape than single-turn benchmarks.

**Eval anti-patterns:**
- Single trial per task — one run proves nothing
- Exact string matching for LLM output — use structural and semantic checks
- Testing implementation ("did it call tool X?") vs. outcome ("did it solve the problem?")
- Shared state between trials — previous trials corrupting current ones
- Public benchmark rank as the verdict — public benchmarks (MMLU, HumanEval) are contaminated and saturated; treat them as candidate-pool filters, not final selection

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
| "I need an agent for this" | Most production features should be workflows, not agents. Anthropic's Dec 2024 guidance: prefer the simplest pattern; may mean not building agentic systems at all. |
| "The prompt just needs tweaking" | If 2+ prompt iterations haven't fixed it, the problem is tools or architecture. |
| "One successful run means it works" | Non-deterministic. Run 3-5 trials. |
| "More tools = more capable" | More tools = more confusion. The 2026 guidance is qualitative: a few thoughtful tools, not a count. |
| "I'll add evals later" | You'll ship without them. Run error analysis on real outputs early; write evals for the failures you discover. |
| "The agent is smart enough to figure it out" | Agents need explicit structure. Ambiguity causes hallucination. |
| "I'll let the LLM decide which tool to use; it's smart enough" | Tool selection accuracy is a tracked failure mode (BFCL). Schema validation + clear descriptions + namespace prefixes prevent hallucinated tool calls. |
| "Public benchmark says model A is better, ship it" | Public benchmarks are filters, not verdicts. Build an internal eval from your real inputs and let it pick the model. |

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
