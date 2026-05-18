
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
Prompt engineering is context engineering. The shape of the information matters more than the words. Before optimizing wording, optimize structure: what information is present, where it's positioned, and how it's organized. Wording refinements on a poorly structured prompt produce marginal gains at best.
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

Anthropic spent more time optimizing tool descriptions than system prompts for their SWE-bench agent. Small description refinements yielded dramatic improvements.

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

**Response format options (66% token reduction measured):**
Give tools a `detail_level` parameter so agents request only what they need:
```typescript
// Agent chooses: "concise" for routing decisions, "detailed" for deep work
detail_level: "concise" | "detailed"
// concise: { id, name, status }
// detailed: { id, name, status, created_at, metadata, relationships, ... }
```

**Tool consolidation:** One tool with parameters beats multiple similar tools. `schedule_event(type, date, details)` not `schedule_meeting()` + `schedule_reminder()` + `schedule_deadline()`. Fewer tools = less confusion.

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

XML creates semantic anchoring — discrete boundaries help models maintain context across sections. Measured: 23% accuracy improvement on mathematical reasoning with XML scaffolding vs. JSON.

### 5. Context Engineering (29-39% improvement measured)

The attention budget is finite. More tokens ≠ better answers. Strategic compaction improves performance.

**Measured improvements:**
- Context editing alone: 29% improvement
- Context editing + memory tool: 39% improvement
- Web search compaction: 84% token reduction with same quality

**Just-in-time loading:** Store file paths, not full file contents. Let the agent discover what it needs:
```
Bad:  Paste entire 500-line file into system prompt
Good: "Schema is in src/schema.ts. Read it when you need schema details."
```

This is exactly what skill `references/` files do — progressive disclosure as context engineering.

**Token waste to watch for:**
- 31 poorly-described tools = ~4,500 tokens per call
- Redundant context repeated across sections
- Full error traces when a one-line summary suffices
- Boilerplate that doesn't change between invocations

### 6. Hallucination Prevention (prompt design, not model capability)

Hallucination is often a prompt design problem, not a model limitation.

**Information grounding:**
```
"Answer using ONLY the provided documents.
If the answer is not in the documents, say 'Not found in provided context.'
Do not use training knowledge for factual claims."
```

**Permission to not know:**
Explicitly granting permission to say "I don't know" drastically reduces false information. Without this, models fabricate plausible answers rather than admitting uncertainty.

**Reasoning-first ordering:**
Ask for the explanation BEFORE the answer. If you ask for the answer first, the model commits to a position and then rationalizes it:
```
Bad:  "What's the bug? Then explain your reasoning."
Good: "Analyze the error trace step by step. Then state the root cause."
```

**Investigate-first for code agents:**
```
"Never speculate about file contents. If the user references a file,
ALWAYS read it before responding. Do not guess at code structure."
```

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
| Model overthinks simple tasks | CoT requested when unnecessary | Remove chain-of-thought for simple classification |
| Model triggers wrong skill | Description vague or overlapping | Description writing for routing |

## Self-Check Pattern

Before finalizing any prompt, verify:

```
1. □ Structure: Is information positioned for attention? (edges > middle)
2. □ Altitude: Are instructions at the right specificity level?
3. □ Motivation: Do rules explain WHY, not just WHAT?
4. □ Examples: Are there 3-5 diverse, relevant examples?
5. □ Tools: Are descriptions unambiguous with format specs?
6. □ Grounding: Is the model told where to source facts?
7. □ Permission: Can the model say "I don't know"?
8. □ Tokens: Is context loaded just-in-time, not upfront?
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

## Guidelines

- **Structure first, then words.** Reorganizing information (positioning, XML sections, progressive disclosure) beats rewriting sentences. The shape of context matters more than the wording.
- **Explain WHY, not just WHAT.** Motivation-based rules generalize. Bare rules get followed literally and miss related cases.
- **3-5 examples beat 10.** Diversity matters more than quantity. Include at least one edge case.
- **Tool descriptions are prompts.** The 40% improvement from tool description optimization means this is some of the highest-leverage prompt work you can do. Treat every parameter description, error message, and response format as prompt engineering.
- **Permission to not know.** Explicitly granting uncertainty reduces hallucination more than any "be accurate" instruction.
- **Measure, don't guess.** If you can't tell whether a prompt change improved things, you're optimizing by feel. Use the diagnosis checklist to identify the actual problem before applying techniques.
