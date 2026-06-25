
---
name: prompt-engineering
description: >-
  Craft effective instructions, tool descriptions, and structured context for AI models.
  Use when writing system prompts, skill descriptions, tool/MCP descriptions,
  optimizing existing prompts, or improving how information is structured for model consumption.
  Applies to skill creation, agent building, and any work where instruction quality
  affects model behavior.
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
  - AskUserQuestion
---

# Prompt Engineering

Structure information for the model's attention — don't just write instructions for a human to read.

<HARD-GATE>
Prompt engineering is ONE COMPONENT of context engineering. In Anthropic's 2026 vocabulary ([Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)), context engineering is the broader discipline: curating the optimal set of tokens during inference, across every layer (system prompt, tool definitions, conversation history, retrieved docs, memory). Prompt design is one lever inside that. Before optimizing wording, optimize *what's in the context and where*: information present, position, organization. Wording refinements on a poorly engineered context produce marginal gains at best.

"Context rot": model accuracy degrades as token volume grows, even before hitting hard limits (n² attention scaling). The discipline is "keep signal density high," not "give Claude more context."
</HARD-GATE>

## When to Use

- Writing or improving a skill's SKILL.md or frontmatter description
- Writing tool descriptions for MCP servers or agent tool definitions
- Crafting system prompts for agents (Claude Agent SDK or otherwise)
- Optimizing an existing prompt that's underperforming
- Structuring context for retrieval-augmented tasks
- Writing subagent descriptions for routing

## Method Selection

Different prompt work requires different techniques. Start with the right approach.

| Work Type | Primary Lever | Start With |
|-----------|--------------|------------|
| **Tool description** | Parameter clarity + response format | Tool Description Patterns below |
| **Skill description (frontmatter)** | Trigger accuracy | Description Writing for Routing below |
| **System prompt** | Structure + altitude calibration | System Prompt Structure below |
| **Existing prompt optimization** | Diagnose → apply specific technique | Diagnosis Checklist below |
| **Context structuring** | Positioning + attention budget | Context Engineering below |

## Core Techniques (by measured impact)

### 1. Tool Description Optimization (40%+ improvement measured)

Anthropic spent more time optimizing tool descriptions than system prompts for their SWE-bench agent. Small description refinements yielded dramatic improvements. ([How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), June 2025 — pre-2026 source, no contradicting 2026 measurement.)

**Parameter descriptions:**
```
Bad:  user: string        — ambiguous, model guesses format
Good: user_id: string     — "The user's UUID (e.g., '550e8400-e29b-41d4-a716-446655440000')"
```

**Format specifications — be concrete:**
```
Bad:  date: string
Good: date: string — "ISO 8601 date string (YYYY-MM-DD), e.g., '2026-03-04'"
```

**Response format enum (~65% token reduction, [Writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)):**
Give tools a `response_format` parameter so agents request only what they need:
```typescript
// Agent chooses: "concise" for routing decisions, "detailed" for deep work
response_format: "concise" | "detailed"
// concise: { id, name, status }                          → ~72 tokens
// detailed: { id, name, status, created_at, metadata, … } → ~206 tokens
```

**Tool consolidation:** One tool with parameters beats multiple similar tools. `schedule_event(type, date, details)` not `schedule_meeting()` + `schedule_reminder()` + `schedule_deadline()`. Fewer tools = less confusion.

**Namespacing matters at scale.** Prefix tools by service (`asana_search`, `jira_search`) to delineate boundaries. Anthropic notes prefix-vs-suffix has "non-trivial effects on tool-use evaluations" — when stakes are high, measure rather than guess.

**Error messages as onboarding.** Errors must give "specific and actionable improvements, rather than opaque error codes or tracebacks." A tool that returns `Error 400` teaches nothing; a tool that returns `error: field 'date' must be ISO 8601 (YYYY-MM-DD), got '2026/01/15' — try '2026-01-15'` teaches Claude to fix the problem itself on the next call.

**Default response cap:** Claude Code truncates tool responses at 25,000 tokens by default. For tools that can return more, implement pagination, filtering, and `response_format` enums rather than relying on the truncation.

**Input examples for complex tools:**
```typescript
// For tools with nested objects, show a concrete example
// in the description — models use it as a template
input_example: {
  filter: { status: "active", created_after: "2026-01-01" },
  sort: { field: "name", order: "asc" },
  limit: 10
}
```

### 2. Context Positioning (15-30% performance swing)

LLMs have an attention distribution — they attend more to the beginning and end of context, less to the middle ("lost in the middle" effect).

**Measured impact:**
- Information at document edges: 85-95% accuracy
- Information in the middle: 76-82% accuracy
- Swing: up to 30% performance drop for critical info buried in the middle

**Practical rules:**
- Put long reference documents at the TOP of context
- Put the query/instructions at the BOTTOM
- This forces the model to read full context before deciding relevance
- Critical constraints and hard gates go at both the top AND bottom (reinforcement)
- In retrieval tasks: most relevant documents at edges, supporting context in middle

### 3. Few-Shot Examples (15-40% improvement)

Quality over quantity. 3-5 diverse examples beat 10 generic ones.

**Three requirements for effective examples:**
1. **Relevant** — mirror actual use cases, not abstract demonstrations
2. **Diverse** — cover edge cases, vary patterns, show different scenarios
3. **Structured** — wrap in `<example>` tags for clear boundaries

**Show reasoning inside examples:**
```xml
<example>
User: What caused the test failure?
<thinking>
The error is "Cannot read property 'id' of undefined" at line 42.
This means `user` is undefined when `.id` is accessed.
Tracing backward: `user` comes from `getUser(email)` at line 38.
The test passes a null email — getUser returns undefined for null.
Root cause: missing null check on the email parameter.
</thinking>
The test fails because getUser() returns undefined when called with a null
email. Add a null check before accessing user.id.
</example>
```

The model generalizes the reasoning pattern, not just the format.

**Anti-pattern:** All happy-path examples. Include at least one edge case or error scenario. Models calibrate behavior from the distribution of examples they see.

### 4. System Prompt Structure (5-20% improvement)

**The altitude principle — neither too specific nor too vague:**
```
Too specific: "Always use list comprehensions for filtering"
  → Brittle. Breaks when list comprehension isn't appropriate.

Too vague: "Write good code"
  → Useless. No actionable guidance.

Right altitude: "Prefer efficient implementations; balance readability
with performance. Choose the idiom that best fits the language."
  → Principled. Model applies judgment per situation.
```

**Motivation-based rules (explain WHY, not just WHAT):**
```
Without motivation: "NEVER use ellipses in responses."
  → Model follows rule literally but misses related cases.

With motivation: "Your response will be read aloud by a TTS system.
Never use ellipses, abbreviations, or symbols that TTS can't pronounce."
  → Model generalizes: also avoids "→", "≥", "..." and similar.
```

When you explain WHY a rule exists, the model extends it to related situations it hasn't been explicitly told about. This is one of the highest-leverage techniques for system prompts.

**Now backed by alignment research:** [Teaching Claude Why](https://alignment.anthropic.com/2026/teaching-claude-why/) (May 2026) found that training Claude on the *principles* underlying aligned behavior generalized better than training on demonstrations of that behavior alone. The same mechanism appears to operate at runtime: prompts that explain why generalize better than prompts that only state the rule. Anthropic's [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) doc formalizes this: "Providing context or motivation behind your instructions ... can help Claude better understand your goals and deliver more targeted responses."

**Tell what to do, not what not to do** (formal 2026 confirmation):
```
Weak:   "Do not use markdown."
Strong: "Your response should be composed of smoothly flowing prose paragraphs."
```
Stronger still: match prompt style to desired output style — removing markdown from the prompt itself reduces markdown in the output. For format hints inside prose: `Write the prose sections in <smoothly_flowing_prose_paragraphs> tags`.

**XML sections for multi-part prompts:**
```xml
<role>You are a code review agent specializing in TypeScript.</role>

<constraints>
- Only review files in the diff, not the entire codebase
- Flag security issues as CRITICAL, style issues as OPTIONAL
</constraints>

<instructions>
1. Read the diff
2. Identify issues by severity
3. Provide specific line references
</instructions>

<output_format>
## Critical Issues
- [ ] Issue (file:line) — description

## Suggestions
- [ ] Suggestion (file:line) — description
</output_format>
```

XML creates semantic anchoring — discrete boundaries help models maintain context across sections. The technique is confirmed in current 2026 docs ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)) but the often-cited "23% improvement on math reasoning" number has **no 2026 source** — treat it as anecdotal until measured again on Claude 4.x.

### 5. Context Engineering (29-39% improvement measured)

The attention budget is finite. More tokens ≠ better answers. Strategic curation improves performance.

**Measured improvements** ([Managing context on the Claude Developer Platform](https://claude.com/blog/context-management), September 2025; no 2026 contradiction):
- Context editing alone: **+29%** on a 100-turn agentic search eval
- Context editing + memory tool: **+39%**
- Web-search compaction: **84%** token reduction with same quality

The three native context primitives (API-level, [Context Engineering Cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools), March 2026) are documented in detail in the `claude-api` skill — they're API features rather than prompt patterns. What matters for prompt design:

| Primitive | What it does | Prompt-side implication |
|---|---|---|
| **Compaction** | Summarizes old turns | Custom `instructions` parameter lets you tell Claude what to preserve. Default prompt is replaced, not supplemented. |
| **Tool-result clearing** | Replaces old tool_result blocks with placeholders | Zero inference cost. Use `exclude_tools: ["memory"]` to protect memory operations. |
| **Memory tool** | Persistent files across sessions | Auto-injected system prompt: "ALWAYS VIEW YOUR MEMORY DIRECTORY BEFORE DOING ANYTHING ELSE." You can shape what gets written ("Only write down info relevant to `<topic>`") and prevent clutter ("keep memory coherent and organized; do not create new files unless necessary"). |

**Just-in-time loading:** Store file paths, not full file contents. Let the agent discover what it needs:
```
Bad:  Paste entire 500-line file into system prompt
Good: "Schema is in src/schema.ts. Read it when you need schema details."
```

This is exactly what skill `references/` files do — progressive disclosure as context engineering.

**Long-document positioning** (current docs, [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)):
- "Queries at the end can improve response quality by up to 30% in tests, especially with complex, multi-document inputs."
- Documents at the top, query at the bottom — standard layout for RAG agent prompts.

**Token waste to watch for:**
- 31 poorly-described tools = ~4,500 tokens per call
- Redundant context repeated across sections
- Full error traces when a one-line summary suffices
- Boilerplate that doesn't change between invocations
- Verbose stdout logs from subagents (write to files instead — verbose stdout pollutes the context window per [Building a C compiler with parallel Claudes](https://www.anthropic.com/engineering/building-c-compiler), Feb 2026)

### 6. Hallucination Prevention (prompt design, not model capability)

Hallucination is often a prompt design problem, not a model limitation.

**Information grounding:**
```
"Answer using ONLY the provided documents.
If the answer is not in the documents, say 'Not found in provided context.'
Do not use training knowledge for factual claims."
```

**Quote grounding for long documents** (2026, [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)):
Ask Claude to quote relevant passages before reasoning. This cuts through document noise and creates an audit trail:
```xml
Find quotes from the patient records and appointment history relevant to
diagnosing the patient's symptoms. Place these in <quotes> tags. Then,
based on these quotes, list diagnostic information in <info> tags.
```

**Permission to not know:**
Explicitly granting permission to say "I don't know" reduces fabrication. The stronger 2026 pattern is *forcing* investigation rather than allowing uncertainty:

```xml
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a
specific file, you MUST read the file before answering. Make sure to
investigate and read relevant files BEFORE answering questions about the
codebase. Never make any claims about code before investigating unless
you are certain of the correct answer.
</investigate_before_answering>
```

**Reasoning-first ordering:**
Ask for the explanation BEFORE the answer. If you ask for the answer first, the model commits to a position and then rationalizes it:
```
Bad:  "What's the bug? Then explain your reasoning."
Good: "Analyze the error trace step by step. Then state the root cause."
```

**Code-review coverage-first** (2026, addresses Opus 4.7's strong instruction-following):
Opus 4.7 has ~11 percentage points better recall on bug-finding evals than prior models — but it also follows suppression instructions faithfully. A prompt like "only report high-severity issues" will measurably drop recall on the new model. Use a coverage-first pattern instead:

```
Report every issue you find, including ones you are uncertain about or
consider low-severity. Do not filter for importance or confidence at this
stage — a separate verification step will do that. Your goal here is coverage.
```

**Prefilled responses are deprecated on Claude 4.6+** (return 400). If you used prefill to force JSON, switch to Structured Outputs or a direct instruction ("Respond in valid JSON."). To eliminate preamble, use the system-prompt instruction "Respond directly without preamble." To continue a truncated response, move the continuation to the user turn ("Your previous response was interrupted ending with `[text]`. Continue from where you left off.").

## Voice in Prompts and Tool Descriptions

System prompts, agent prompts, MCP tool descriptions, and parameter descriptions are the prose Claude reads before producing its output. Their cadence primes the model's output cadence. This is mechanical, not aesthetic. AI-sounding prompts produce AI-sounding output, even when the user has not asked for that register.

The rules apply to: agent system prompts, subagent briefs, MCP tool descriptions, parameter docs, error message templates, response format guidance, and the prose of skills (which are themselves system prompts).

### Hard negative rules

Mechanical. Never violate in any prompt that ships.

1. **No em dashes** (`—`). Replace with commas, colons, periods, parentheses, or restructure.
2. **No "Not X, but Y" / "Not just X, it's Y" as default cadence.** Fine occasionally; not as a rhythm.
3. **No discourse hinges**: Fundamentally, Crucially, Importantly, Notably, Specifically, Interestingly.
4. **No setup interjections**: "Here's the thing", "Picture this", "Let me explain", "Consider the following".
5. **No summary closes** ("In summary", "To recap"). Prompts that end with a recap teach the agent to also produce recaps.
6. **No reflexive tricolons.** Pad-to-three for rhythm produces AI cadence.
7. **No nominalization defaulting.** Imperatives over noun-phrase instructions: "Read the file before answering" beats "The reading of the file should precede the answer".

### Positive style targets

- **Specificity over abstraction in instructions and examples.** Real schema field names, real version numbers, real product names, real edge case descriptions. Examples with placeholder values teach less than examples with real values.
- **Imperatives for instructions.** "Read the file" beats "It is important to read the file" beats "One should consider reading the file".
- **Cut hedges that carry no information.** "It is worth noting that", "Generally speaking", "In most cases". Either state the rule or drop it.
- **Cut signposting.** "Now, let's look at", "Moving on to", "In the next section". Section headers do this work.
- **Sentence-length variance.** A clipped sentence after a long one lands the rule.
- **Respect for the reader.** The reader is Claude. Don't pad with "obviously", "simply", "as you can see". Don't restate the previous sentence. Don't preview the next.

### Why this matters

A prompt is read at every invocation. Whatever register it teaches becomes the register of the output. Smooth transitions in the prompt produce smooth transitions in the output; balanced parallels in the prompt produce balanced parallels in the output; em dashes in the prompt produce em dashes in the output. The pattern is consistent enough to be relied on, and to be defended against.

### Self-check before publishing any prompt

Two-line check:

1. Read it aloud. Does it sound like instructions, or like a brochure?
2. Run `grep "—\|Fundamentally\|Crucially\|Notably\|Specifically"` against the prompt. Mechanical sweep catches the obvious tells.

If the prompt is going into an agent that produces user-facing prose (lessons, docs, reports, code review comments, anything a human reads), this check is load-bearing, not optional. The prompt's voice IS the output's voice.

## Adaptive Thinking & the Effort Parameter (Claude 4.x)

The reasoning architecture for Claude 4.x is **adaptive thinking** — Claude decides when and how much to think, based on the configured *effort level* and query complexity. This replaces manual `budget_tokens` and most "think step by step" scaffolding.

**`budget_tokens` is deprecated** on Opus 4.6 / Sonnet 4.6, and **returns 400 on Opus 4.7**. Migrate to the `effort` parameter ([Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)):

| Effort | When to use | Behavior |
|---|---|---|
| `max` | Intelligence-demanding tasks | Risk of overthinking on simple work |
| `xhigh` (4.7+) | Best for most coding and agentic tasks | Default for Opus 4.7 |
| `high` | Minimum for intelligence-sensitive work | Default for Sonnet 4.6 |
| `medium` | Cost-sensitive workloads | |
| `low` | Latency-sensitive, scoped, non-intelligence-sensitive | Opus 4.7 will *strictly* scope to what's asked — won't go above and beyond. Risk of under-thinking complex tasks. |

**Stop telling Claude 4.x to "think step by step."** From the current docs: *"If your prompts still contain phrases like 'think step by step' or 'reason carefully before responding,' delete them and raise the effort level instead."* These instructions were scaffolding for older models' limitations and are no longer load-bearing.

**Adaptive thinking trigger control** (when you want to limit auto-thinking):
```
Extended thinking adds latency and should only be used when it will
meaningfully improve answer quality — typically for problems that require
multi-step reasoning. When in doubt, respond directly.
```

**Commitment under uncertainty** (when Opus 4.6 over-explores):
```
When you're deciding how to approach a problem, choose an approach and
commit to it. Avoid revisiting decisions unless you encounter new
information that directly contradicts your reasoning.
```

**Manual CoT is still valid** *only when thinking is disabled.* Use `<thinking>` and `<answer>` tags. Few-shot examples with `<thinking>` blocks inside generalize to extended thinking blocks.

---

## Model-Specific Prompting (Claude 4.x)

The same prompt produces different behavior across Claude 4.x models. Designing an agent prompt without considering its target model leaves measurable performance on the table.

### Opus 4.7

- **More literal instruction following.** It will not silently generalize from one item to another. If you want broad application, state scope explicitly:
  > "Apply this formatting to every section, not just the first one."

- **Less tool use by default.** Relies more on reasoning. Raise effort to increase tool usage — don't rephrase the prompt.

- **Fewer subagents by default.** Steer with explicit guidance:
  ```
  Do not spawn a subagent for work you can complete directly in a single response.
  Spawn multiple subagents in the same turn when fanning out across items or reading multiple files.
  ```

- **More proactive progress updates.** Remove old scaffolding like "After every 3 tool calls, summarize progress" — it's now redundant and noisy.

- **Persistent default design aesthetic** (warm cream / serif / terracotta). If you want different visuals, supply concrete alternative specs or ask Claude to propose options first. Generic negation ("don't make it warm") does not steer effectively.

- **Long-context retrieval regression** ([WentuoAI third-party benchmark](https://blog.wentuo.ai/en/claude-opus-4-7-long-context-regression-en.html)): Opus 4.7 scored 32.2% on MRCR v2 8-needle at 1M context vs. Opus 4.6's 78.3%. **Use Opus 4.6 or Sonnet 4.6 for long-context retrieval tasks.** Opus 4.7 is optimized for agentic coding, not retrieval.

- **Recommended max output:** 64k tokens at max/xhigh effort. Tune from there.

### Opus 4.6

- **Does significantly more upfront exploration.** Remove blanket "use this tool by default" instructions — they overtrigger on 4.6.

- **Excessive subagent use** can be reined in with:
  > "Use subagents when tasks can run in parallel, require isolated context, or involve independent workstreams. For simple tasks, sequential operations, single-file edits, or tasks where you need to maintain context, work directly."

- For runaway thinking: lower `effort` OR add the commit-under-uncertainty prompt above.

### Sonnet 4.6

- **Defaults to `high` effort** (Sonnet 4.5 had no effort parameter). Teams migrating without setting effort experience unexpectedly high latency. For most applications set `medium`; for high-volume / latency-sensitive workloads set `low`.

- Best-in-class on computer use evaluations with adaptive thinking.

- `budget_tokens` is deprecated — migrate to adaptive thinking + effort.

### Common across 4.x

- **Sampling parameters (temperature, top_p, top_k) are rejected by Opus 4.7** — any non-default returns an error. Other 4.x models still accept them but deprecation may extend.

- **"CRITICAL: You MUST use this tool when..." overtriggers** on Claude 4.6+. The training has shifted models toward more responsive instruction-following; aggressive trigger language that was needed on older models is now harmful. Use altitude calibration instead.

---

## Agent Action Triggering

How you frame agency in the system prompt shapes the agent's default disposition toward acting vs. asking. Two named templates from the 2026 docs:

**Proactive (default to action):**
```xml
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's
intent is unclear, infer the most useful likely action and proceed, using
tools to discover any missing details instead of guessing.
</default_to_action>
```

**Conservative (default to asking):**
```xml
<do_not_act_before_instructions>
Do not jump into implementation or change files unless clearly instructed.
</do_not_act_before_instructions>
```

**Reversibility frame** (recommended for any agent that can affect shared state):
```
Take local, reversible actions freely, but for actions that are hard to
reverse, affect shared systems, or could be destructive, ask the user
before proceeding.

Examples that warrant confirmation:
- Destructive: deleting files/branches, dropping tables, rm -rf
- Hard to reverse: git push --force, git reset --hard, amending published commits
- Visible to others: pushing code, commenting on PRs, sending messages
```

**Parallel tool calling (~100% steerable on Claude 4.6+):**
```xml
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between
the tool calls, make all of the independent tool calls in parallel. Never
use placeholders or guess missing parameters in tool calls.
</use_parallel_tool_calls>
```
Largely unnecessary on Claude 4.6+ (parallel calling is already strong), but adding the template brings it to ~100% reliability.

---

## Subagent Briefing

Subagents need four components in their brief, every time ([How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)):

1. **Objective** — what to find or produce
2. **Output format** — how to return results (token-bounded summary, structured JSON, etc.)
3. **Tool guidance** — which tools and sources to use
4. **Task boundaries** — what is and isn't in scope

Vague delegation produces duplication and gaps. From the research-system post: **80% of BrowseComp performance variance is explained by token usage** (parallelizing across subagents with isolated contexts); model choice explains only ~5%. The lever is parallelization, not picking a smarter model.

**Return-summary discipline:** Have each subagent return a 1,000–2,000-token summary to the orchestrator. Larger returns trigger compaction and information loss ("game of telephone").

**File-based handoffs over context compression** ([Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)): for complex long-running work, write progress to files that fresh agent instances can read. Git history, progress files, and READMEs maintained for the agent's benefit (not just humans) outperform compaction summaries.

**Logging for agents, not humans:**
- Write detailed logs to files, not stdout — verbose stdout pollutes the context window
- Use grep-discoverable error format: `ERROR [reason on same line]`
- Update progress files frequently enough that a fresh container can orient in seconds

---

## Description Writing for Routing

Skill descriptions, tool descriptions, and subagent descriptions all serve the same function: helping a routing system select the right option. The quality of these descriptions determines selection accuracy.

**Measured: 95%+ routing accuracy with well-written descriptions.**

**Format: Action verb + specialization + "Use when" clause:**
```
Good: "Analyze Python code for performance bottlenecks. Use when profiling,
      optimizing hot paths, or investigating memory leaks."

Bad:  "code_analyzer" or "A tool for code analysis"
```

**Key principles:**
- Routing uses semantic/intent matching, not keyword matching
- Include both WHAT it does and WHEN to use it
- Mention specific triggers that should activate this tool/skill
- Avoid overlap with other descriptions in the same routing set
- For skills: everything in `description` matters for triggering; nothing in the body helps with triggering

**Test descriptions by asking:** "If I read only this description, would I know exactly when to use this vs. the alternatives?" If not, add specificity.

## Diagnosis Checklist (for optimizing existing prompts)

When a prompt underperforms, diagnose before rewriting:

| Symptom | Likely Cause | Technique |
|---------|-------------|-----------|
| Model ignores key instructions | Critical info in the middle of context | Reposition to edges (#2) |
| Model uses wrong tool | Tool descriptions overlap or are vague | Tool description optimization (#1) |
| Model hallucinates facts | No grounding instructions | Hallucination prevention (#6) |
| Model doesn't generalize rules | Rules stated without motivation | Motivation-based rules (#4) |
| Inconsistent output format | No examples or format template | Few-shot examples (#3) |
| Model confused by complex input | Flat text, no structure | XML sections (#4) |
| Token budget blown | Too much context loaded upfront | Just-in-time loading (#5) |
| Model overthinks simple tasks | Old "think step by step" instruction on Claude 4.x | Remove the scaffolding; lower `effort` |
| Model overthinks complex tasks | Effort too high; revisiting decisions | Lower effort + add the commit-under-uncertainty prompt |
| Model under-thinks complex tasks | `effort: low` on intelligence-sensitive work | Raise to `high` or `xhigh` |
| Opus 4.7 not generalizing rules | More literal instruction-following on 4.7 | State scope explicitly ("apply to every section, not just the first") |
| Opus 4.7 not using tools enough | Tool use de-emphasized in 4.7 | Raise effort, don't rephrase |
| Code-review agent missing bugs | Suppression instruction filtering out coverage | Coverage-first prompt (Hallucination section) |
| Subagent returning empty | Subagent brief missing one of the 4 components | Add objective / format / tool guidance / boundaries |
| Tool-trigger overfiring on 4.x | Aggressive "CRITICAL: You MUST..." language | Soften — Claude 4.x is highly responsive without it |
| Model triggers wrong skill | Description vague or overlapping | Description writing for routing |
| 400 error from `budget_tokens` | Deprecated on 4.6, broken on 4.7 | Migrate to adaptive thinking + `effort` |
| 400 error from prefill | Prefilled responses deprecated on 4.6+ | Use Structured Outputs or "Respond in valid JSON" |

## Self-Check Pattern

Before finalizing any prompt, verify:

```
 1. □ Structure: Information positioned for attention? (edges > middle)
 2. □ Altitude: Instructions at the right specificity level?
 3. □ Motivation: Rules explain WHY, not just WHAT?
 4. □ Examples: 3-5 diverse, relevant examples? At least one edge case?
 5. □ Tools: Descriptions unambiguous with format specs? Namespaced if 5+?
 6. □ Grounding: Told where to source facts? Quote-grounding for long docs?
 7. □ Investigation: Forced to read files before claiming? (code agents)
 8. □ Tokens: Context loaded just-in-time, not upfront?
 9. □ Model: Calibrated for target model? (4.7 literal / 4.6 over-exploring / Sonnet 4.6 effort default)
10. □ Effort: Set explicitly when migrating from older models or non-default?
11. □ Deprecated: No "think step by step", `budget_tokens`, or prefilled responses on 4.x?
12. □ Tell-don't-not-tell: Positive instructions over negation?
13. □ Subagents: All 4 brief components (objective / format / tools / boundaries) if delegating?
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|--------------|-------------|-----|
| **The Adjective Prompt** | "Be thorough, accurate, and helpful" — no actionable guidance | Replace adjectives with techniques and examples |
| **The Persona Without Instructions** | "You are an expert X" then no methodology | Persona sets tone; instructions drive behavior. Need both. |
| **The Wall of Rules** | 50 rules, model forgets most | Fewer rules with motivations. Model generalizes from WHY. |
| **Hidden Critical Info** | Most important constraint buried in paragraph 15 | Move to top AND bottom. Use `<HARD-GATE>` or XML tags. |
| **All Happy-Path Examples** | Model doesn't know how to handle errors | Include edge case and error examples |
| **Over-Specified Steps** | "Step 1: Click X. Step 2: Type Y" for context-dependent work | Use altitude principle — specify at the right level |
| **Token Gluttony** | Full file contents pasted when path reference suffices | Just-in-time loading |
| **Carryover Scaffolding** | "Think step by step" / "reason carefully" on Claude 4.x | Delete; raise `effort` instead. These are no-ops or worse on 4.x. |
| **Aggressive Tool Triggers** | "CRITICAL: You MUST use this tool when..." on Claude 4.6+ | Soften — overtriggering is now the common failure, not undertriggering |
| **Suppression in Coverage Tasks** | "Only report high-severity" on Opus 4.7 review agents | Coverage-first: "report every issue including uncertain ones" |
| **Manual Thinking Budgets** | `budget_tokens` on 4.6+ (deprecated) / on 4.7 (400 error) | Migrate to adaptive thinking + `effort` parameter |
| **Prefilled Last Turn** | 400 error on Claude 4.6+ | Use Structured Outputs or direct instruction |
| **Negation as Instruction** | "Do not use markdown" instead of "Use prose paragraphs" | Tell what to do, not what not to do. Match prompt style to output style. |
| **Vague Subagent Brief** | Missing one of: objective / format / tools / boundaries | All four are required — vague delegation produces duplication and gaps |
| **Verbose stdout from agents** | Logs flooding context window | Write to files; emit one-line grep-discoverable errors |

## Guidelines

- **Structure first, then words.** Reorganizing information (positioning, XML sections, progressive disclosure) beats rewriting sentences. The shape of context matters more than the wording.
- **Prompt engineering is one component of context engineering.** Think about the whole context window — system prompt, tools, history, retrieved docs, memory — not just the prompt text. Signal density > token volume.
- **Explain WHY, not just WHAT.** Motivation-based rules generalize. Bare rules get followed literally and miss related cases. Now backed by alignment research (Teaching Claude Why, May 2026).
- **3-5 examples beat 10.** Diversity matters more than quantity. Include at least one edge case.
- **Tool descriptions are prompts.** Some of the highest-leverage prompt work you can do (~40% task completion improvement, ~65% token reduction from response_format enums). Treat every parameter description, error message, and response format as prompt engineering.
- **Investigate, don't speculate.** For code-agent system prompts, force file reads before any claim. The 2026 docs version is more aggressive than "permission not to know" — *require* investigation.
- **Calibrate for the target model.** Same prompt, different behavior across Claude 4.x. Opus 4.7 is literal and tool-light; Opus 4.6 over-explores; Sonnet 4.6 defaults to `high` effort. Designing without considering the target model leaves measurable performance on the table.
- **Effort over scaffolding.** On Claude 4.x, raise `effort` instead of adding "think step by step." Old reasoning scaffolds are no-ops or worse.
- **Tell what to do.** Positive instructions beat negation. Match prompt style to desired output style.
- **Measure, don't guess.** If you can't tell whether a prompt change improved things, you're optimizing by feel. Use the diagnosis checklist to identify the actual problem before applying techniques. Treat benchmark deltas <3pp on agentic evals with skepticism — infrastructure noise alone can swing 6pp.
- **Attention is finite.** Every token competes for attention budget. Loading less context, positioned well, outperforms loading more context positioned poorly.
