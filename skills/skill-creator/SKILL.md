
---
name: skill-creator
description: >-
  Create or improve skills following agent-building best practices. Use when you need to
  create a new reusable skill, rewrite a weak skill, or evaluate skill quality. Covers
  the full lifecycle: research, gap analysis, tool discovery, prompt design, structural
  DNA, and quality scoring.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Task
  - Skill
  - AskUserQuestion
---

# Skill Creator

Create skills that teach Claude something it doesn't already know.

## The Central Question

**"What does this skill add that the model can't already do?"**

Claude is already a strong generalist. A skill earns its context window cost only when it provides one or more of:

- **A methodology** — a structured process for thinking through a class of problem (not a checklist of things to check, but a sequence of phases with entry/exit criteria, decision points, and failure modes)
- **Institutional knowledge** — domain-specific facts, schemas, conventions, or constraints Claude has no way to know (your company's API, your team's deployment process, your industry's regulatory requirements)
- **Deterministic operations** — scripts and templates that must execute the same way every time (file format conversion, project scaffolding)
- **Orchestration logic** — how skills, tools, and agents connect in your specific workflow (what invokes what, in what order, with what gates)

If a skill restates what Claude already knows ("check for SQL injection," "use semantic HTML," "write clear variable names"), it's wasting context window for zero value.

## Skills Are Agents

A skill is an agent definition. The mapping is direct:

| Agent Concept | Skill Equivalent |
|---------------|-----------------|
| System prompt | SKILL.md body |
| Tool list | `allowed-tools` in frontmatter |
| Knowledge base | `references/` directory |
| Deterministic tools | `scripts/` directory |
| Agent chaining | Invoking other skills via `Skill` tool |
| Subagent spawning | Using `Task`/`Agent` tool within a skill |
| Model selection | `model` field in frontmatter |
| Isolated execution | `context: fork` in frontmatter |

This means agent-building best practices apply directly to skill creation. Five dimensions, all interconnected:

**Prompt design (the SKILL.md body).** This is the agent's system prompt. The structural DNA patterns in this skill — central thesis, hard gates, method selection, checkpoints, bias guards — are context engineering techniques that shape how the agent processes information and makes decisions. Structure matters as much as content: the same instructions reorganized can produce dramatically different behavior.

**Tool design (the allowed-tools list).** Tools are where the agent takes action. Anthropic's own agent work found that optimizing tool descriptions alone improved task completion by 40%. Before writing the prompt, ask: what tools would make this agent more capable? Are there MCP servers to install, scripts to write, or existing tools to add? A research skill with `WebSearch` + `WebFetch` + `Context7` is fundamentally different from one without.

**Context engineering (references/ and progressive disclosure).** Anthropic's research shows context window management explains more performance variance than prompt wording in complex tasks. `references/` files are the skill's knowledge base — loaded on demand, not always in context. Design them like a retrieval system: organized by topic, clearly indexed from SKILL.md, with guidance on when each is relevant.

**Orchestration (skill chaining and subagents).** Skills can invoke other skills (agent chaining). A design skill that orchestrates research → architecture → test-planning is more reliable than one that tries to do all three inline. But orchestration has costs — coordination overhead, latency, failure modes. Default to single skill with tools; add orchestration only when a single skill demonstrably fails.

**Tool count discipline.** Agents degrade above ~15 tools. If a skill needs many tools, consider splitting into an orchestrator that delegates to focused sub-skills. `allowed-tools` isn't just a permission list — it's a cognitive budget for the agent.

When creating a skill, always ask: *"If I were building this as a standalone agent, what system prompt would I write, what tools would I give it, what knowledge would I preload, and what other agents would it delegate to?"* The answer maps directly to your skill design. Consult the **ai-agent-building** skill for deeper patterns.

<HARD-GATE>
Before creating any skill, invoke the **research** skill to investigate the problem space. Research best practices, existing approaches, prior art, and what gaps your skill should fill. Better input = better skill. Do not skip this step.
</HARD-GATE>

## Structural DNA — What Makes a Skill Work

The best skills share a structural pattern. The weak ones are missing most of it. When creating a skill, build with these elements:

### 1. Central Thesis

One sentence that anchors the entire skill. Everything flows from it. If the skill were reduced to a single instruction, this is what survives.

- research: *"Investigate before you act. Form hypotheses and test them — don't passively read."*
- systematic-debugging: *"Find the root cause before you touch the code."*
- verification: *"Evidence before assertions. Every time. No exceptions."*

A skill without a central thesis wanders. It becomes a list of tips instead of a coherent methodology.

### 2. Hard Gates

Explicit `<HARD-GATE>` blocks that prevent the single most damaging failure mode. These are non-negotiable constraints — the one thing that, if violated, makes the skill worthless.

```markdown
<HARD-GATE>
Do NOT [the thing that ruins everything] without [the thing that must happen first].
[Why this matters in one sentence.]
</HARD-GATE>
```

Use sparingly — one or two per skill. If everything is a hard gate, nothing is.

### 3. Method Selection

Different inputs need different approaches. A decision table at the top prevents the model from defaulting to one approach for everything.

```markdown
| Situation | Approach | Why |
|-----------|----------|-----|
| Known question, one source | Quick lookup | Don't over-investigate |
| Multiple valid approaches | Deep investigation | Need evidence for trade-offs |
| Regression bug | git bisect | Temporal search beats code reading |
```

This is what separates a methodology from a checklist. A checklist says "do these things." A method selection says "assess the situation, then choose the right approach."

### 4. Checkpoints

Built-in pause points where the human validates direction before the model continues. Prevents the model from disappearing for 10 minutes and returning with a finished product built on wrong assumptions.

```markdown
### Step 3: Check In

**CHECKPOINT: Do NOT skip this step.**

"Here's what I'm finding so far:
- [Key observation]
- [Surprise or contradiction]

Does this match your intuition, or should I adjust?"
```

Checkpoints are especially important in multi-step skills (design, opportunity-research). Utility skills (commit-and-pr, file tools) may not need them.

### 5. Bias and Rationalization Guards

A table of "if you're thinking X, stop — because Y." These catch the model's most common failure modes for this type of work.

```markdown
| Thought | Reality | Do Instead |
|---------|---------|------------|
| "This is simple, skip the process" | Simple problems have root causes too | Follow the process — it's fast for simple cases |
| "I know the answer already" | First impressions anchor you | Search for disconfirming evidence |
```

The best guards are specific to the skill's domain, not generic advice.

### 6. Structured Output Format

A template showing exactly what the skill produces. This anchors quality — the model knows what "done" looks like.

```markdown
## Output Format

## Answer
[Direct answer — 1-3 sentences]

## Key Findings
1. **Finding** — Evidence with source reference. [Confidence: high/medium/low]

## Open Questions
[What's still unclear]
```

### 7. Communication Design (User-Facing Skills Only)

Skills that produce multi-step output with user decisions need to design how they talk to the user. This applies to methodology and orchestrator skills (design, write-spec, research, etc.) — not utilities (commit-and-pr, verification).

Follow the **communication-protocol** skill. The key rules to build into the skill's process:

- **One topic per message.** Don't combine findings + decisions in one output.
- **Max 3-4 items per group.** If presenting more, cluster into named groups.
- **Lead with the point.** Conclusion first, evidence second. Name what you need: FYI, Validate, or Decide.
- **Scale decisions to stakes.** Low-stakes: recommend and move. High-stakes: pairwise comparison.
- **Progressive disclosure.** Layer 1 is a 30-second scan. Layer 2 is the evidence locker.

If a skill has checkpoints (structural DNA #4), each checkpoint should follow these rules. A checkpoint that dumps 500 words defeats its purpose.

### 8. Anti-Patterns Table

What the skill prevents. These are the specific failure modes this skill exists to stop.

```markdown
| Anti-Pattern | What Happens | This Skill Prevents It By |
|--------------|-------------|--------------------------|
| Info dump | 2,000 words, no structure | Chunking + lead with point |
| Guess and check | Random fixes, no root cause | Phased investigation |
```

## Context Economics

The context window is a shared resource. Every token your skill consumes is a token unavailable for conversation history, other skills, and the actual work.

**Budget guideline:** SKILL.md body should stay under 500 lines. If approaching this limit, split content into reference files.

### Progressive Disclosure

Skills load in three levels:

1. **Metadata** (name + description) — always in context (~100 words). This is the ONLY thing that determines whether the skill triggers. All "when to use" information must be in the description, not the body.
2. **SKILL.md body** — loaded when the skill triggers (<5k words target)
3. **Bundled resources** — loaded only when Claude determines they're needed (unlimited, since scripts can execute without reading into context)

### When to Split into Reference Files

Move content to `references/` when:
- Variant-specific details (AWS vs GCP vs Azure deployment patterns)
- Domain-specific schemas (finance.md, sales.md, product.md)
- Detailed API documentation or code examples
- Advanced techniques only needed in specific situations

Always reference split files from SKILL.md with clear guidance on when to read them:

```markdown
## Advanced Features
- **Form filling**: See [forms.md](forms.md) for the complete guide
- **Tracked changes**: See [redlining.md](redlining.md) when editing existing documents
```

Keep references one level deep from SKILL.md — no nested references.

### Degrees of Freedom

Match instruction specificity to task fragility:

| Freedom Level | When | Example |
|---------------|------|---------|
| **High** (prose guidance) | Multiple valid approaches, context-dependent | Research methodology, design decisions |
| **Medium** (pseudocode, parameterized) | Preferred pattern exists, some variation OK | API integration, test structure |
| **Low** (specific scripts, exact steps) | Fragile, error-prone, consistency critical | File format manipulation, deployment scripts |

Think of it as a bridge: narrow with cliffs needs guardrails (low freedom). Open field allows many routes (high freedom).

## Creation Process

### 1. Research the Problem Space

Invoke the **research** skill. Investigate:
- What methodologies exist for this type of work?
- What are the common failure modes?
- What prior art exists (other skills, tools, processes)?
- What does Claude already know vs. what is genuinely additive?

### 2. Identify the Gap

Answer concretely:
- What does this skill add that Claude can't already do?
- What failure modes does it prevent?
- What decisions does it make easier?
- Who is the audience — another Claude instance, not a human reader?

If you can't articulate the gap, the skill isn't needed. This is the kill switch.

### 3. Discover Tools

Invoke the **tool-discovery** skill. This is where skills gain capabilities nobody else has.

Don't just list which built-in tools the skill needs — that's the minimum. Tool discovery searches three layers:

1. **Existing MCP servers** — ready to install from registries, npm, GitHub
2. **APIs worth wrapping** — services with good APIs but no MCP server yet (route to **mcp-builder**)
3. **Software worth adopting** — systems worth installing *because* of their API, even if the user doesn't use them yet

The tool-discovery skill handles the full search and presents recommendations. After discovery, also consider:
- Custom scripts (`scripts/`) for deterministic operations
- Whether the skill needs to invoke other skills (add `Skill` to tools)
- Whether the skill needs subagents for parallel work (add `Task` or `Agent`)
- Tool count discipline — agents degrade above ~15 tools

### Checkpoint

**CHECKPOINT: Do NOT skip this step.**

Before writing the SKILL.md, present your plan to the user:
- "Here's the gap this skill fills: [gap]"
- "Here's what I found for tools: [tool recommendations]"
- "Here's the skill type I'm going with: [type]"
- "Does this match your vision, or should I adjust?"

This prevents building a skill on wrong assumptions. The cost of pausing here is low; the cost of rewriting a complete skill is high.

### 4. Choose the Skill Type

| Type | Structure | Examples |
|------|-----------|---------|
| **Methodology** | Central thesis → phases → decision tables → guards | research, systematic-debugging, verification |
| **Orchestrator** | Routing table → pipelines → sequencing | design, build, orchestrator |
| **Domain reference** | Context + patterns + scripts/templates | docx, xlsx, mcp-builder |
| **Utility** | Compact procedure, mostly templates | commit-and-pr, file tools |

Methodologies need all the structural DNA. Utilities may only need a central thesis and output format. Match the structure to the type.

### 5. Write the SKILL.md

#### Frontmatter

```yaml
---
name: my-skill-name              # Required: lowercase with hyphens
description: >-                   # Required: what it does AND when to trigger it
  What this skill does. Use when [specific triggers].
  Include all trigger conditions here — the body loads
  AFTER triggering, so "When to Use" sections in the body
  don't help with triggering.
allowed-tools:                    # Optional: restrict tool access
  - Read
  - Write
  - Bash
---
```

Other frontmatter fields:

| Field | Type | When to Use |
|-------|------|-------------|
| `disallowed-tools` | list | Block specific tools |
| `model` | haiku/sonnet/opus/inherit | Override model for this skill |
| `context` | fork | Run in isolated subagent |
| `disable-model-invocation` | bool | Manual `/skill` only |
| `user-invocable` | bool | Hide from slash-command menu |
| `argument-hint` | string | Help text (e.g., "[issue-number]") |

#### Body Structure

Follow this skeleton, adapting to the skill type:

```markdown
# Skill Title

[Central thesis — one sentence]

<HARD-GATE>
[The one thing that must not be violated]
</HARD-GATE>

## [Method Selection / Scoping Table]
[Decision table matching situations to approaches]

## Process
[Phased methodology with clear entry/exit criteria per phase]

### Phase N: [Name]
[What to do, when to stop, what comes next]

### Checkpoint
[Pause for human validation — especially in multi-step skills]

## Output Format
[Template for what this skill produces]

## [Bias Guards / Rationalization Prevention / Red Flags]
[Table of failure modes specific to this domain]

## Anti-Patterns
[What this skill exists to prevent]

## Guidelines
[Opinionated principles — not generic advice, but specific defended positions]
```

Not every skill needs every section. Utilities may skip checkpoints and bias guards. Methodologies should have all of them.

#### Apply Prompt Engineering

The SKILL.md body is a system prompt. The frontmatter description is a routing description. Both benefit from the **prompt-engineering** skill's techniques.

Invoke **prompt-engineering** for:
- **The frontmatter description** — this determines whether the skill triggers at all. Test it: "If I read only this description, would I know when to use this skill?"
- **The SKILL.md body** — apply context positioning (hard gates at edges), motivation-based rules (explain WHY), XML sections for structure, and the altitude principle (neither too specific nor too vague)
- **Tool descriptions** — if the skill creates or wraps tools, optimize their descriptions (40%+ improvement measured)

Run the prompt-engineering self-check before finalizing.

### 6. Add Bundled Resources (if needed)

```
skill-name/
├── SKILL.md              # Required
├── references/           # Documentation loaded on demand
│   └── advanced.md
├── scripts/              # Executable code (deterministic operations)
│   └── process.py
└── assets/               # Files used in output (templates, images)
    └── template.html
```

**Do NOT create:** README.md, INSTALLATION_GUIDE.md, CHANGELOG.md, or any documentation about the skill itself. The skill contains instructions for Claude, not documentation for humans.

### 7. Evaluate Against the Quality Rubric

Use the two-phase scoring methodology in `references/scoring-methodology.md`:

1. **Phase 1 (automated):** Run `scripts/generate-fact-sheet.sh <skill-name>` to produce an objective structural fact sheet. This detects hard gates, delegation, anti-patterns, and other markers that subjective evaluation can miss.
2. **Phase 2 (subjective):** Score the 7 dimensions using the rubric below, with the fact sheet as input. Every score must quote evidence. Scores that contradict the fact sheet must be explained.

Score the skill on all 7 dimensions before considering it done. Be honest — a skill that scores 6 and ships is worse than one that scores 6 and gets improved.

For each dimension scoring below 2, identify what's missing and fix it. Common gaps:
- **Additive value = 0**: The skill restates what Claude knows. Add methodology or institutional knowledge.
- **Central thesis = 0**: No anchoring principle. Write one sentence that everything else flows from.
- **Failure prevention = 0**: No gates or guards. Identify the single worst failure mode and add a hard gate.
- **Decision support = 0**: Linear "do these steps." Add a method selection table.
- **Tool design = 0**: Default tools, no discovery done. Run the tool-discovery skill.

### 8. Test and Iterate

Invoke the **skill-eval** skill to validate. It runs the skill against realistic test prompts and compares results — with-skill vs baseline (new skill) or old vs new (improvement). Includes blind A/B comparison to remove bias.

If you're short on time, at minimum use `/my-skill` on real tasks and watch for:
- Does it trigger correctly? (Test: describe a task that should invoke it — does the description match?)
- Does it produce the right output format?
- Does it catch the failure modes it's designed to prevent?
- Does it waste tokens on things Claude already knows?

If the skill fails, diagnose which component is weak (prompt, tools, context, orchestration) and fix that specific component. Don't rewrite the whole skill when one section needs adjustment.

## Quality Rubric

Score each dimension 0-2. A skill should score 8+ to ship.

| Dimension | 0 (Weak) | 1 (Adequate) | 2 (Strong) |
|-----------|----------|--------------|------------|
| **Additive value** | Restates what Claude knows | Adds some domain context | Teaches a methodology or provides knowledge Claude can't have |
| **Central thesis** | No anchoring principle | Has a principle but buried | Clear thesis in the opening, everything flows from it |
| **Failure prevention** | No guards or gates | Has output format but no gates | Hard gates + bias guards + anti-patterns |
| **Decision support** | "Do these steps" | Some conditional logic | Method selection table matching situations to approaches |
| **Structure** | Wall of text or generic checklist | Organized sections | Phased process with entry/exit criteria and checkpoints. For user-facing skills: output paced per communication-protocol (chunking, progressive disclosure, decision scaling) |
| **Tool design** | Default tools, no thought given | Tools match the task | Tools actively researched; MCP servers, scripts, or custom tools considered |
| **Context efficiency** | 500+ lines of generic advice | Right length but some filler | Every paragraph justifies its token cost |

**Score interpretation** (7 dimensions, max 14):
- **12-14:** Top tier — ships as-is
- **9-11:** Solid — minor polish needed
- **5-8:** Needs work — missing structural elements
- **0-4:** Rethink — may not be worth the context cost

## Anti-Patterns

| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| **The Generic Checklist** | "Check for security issues, performance, maintainability" | Teach a process for HOW to check, not WHAT to check |
| **The Reference Card** | Tech stack list with code snippets Claude already knows | Only include what's genuinely unknown (your conventions, your schemas) |
| **The Process Narration** | "First we'll research, then we'll plan, then we'll build" | Each phase needs entry/exit criteria, not just a name |
| **The Knowledge Dump** | 600 lines covering every possible scenario | Split into SKILL.md (methodology) + references/ (details on demand) |
| **The Sycophant** | "You are an expert X" followed by basic tips | Skip the flattery. Teach the methodology. |
| **Missing Triggers** | "When to Use" section in the body but vague description | All trigger logic in the frontmatter description |

## Guidelines

- **Methodology over checklist.** A checklist says "check X." A methodology says "here's how to think about X, here's how to choose your approach, here's how to know when you're done, and here's how to catch yourself when you're wrong."
- **Kill switch at step 2.** If you can't articulate what the skill adds beyond Claude's baseline, don't create it. Not every task needs a skill.
- **Description is the trigger.** The body loads AFTER the skill activates. If "when to use" information is only in the body, the skill will never trigger correctly.
- **Write for the reader, not the author.** The audience is a future Claude instance executing a task. Cut everything that doesn't help that instance do the job better.
- **Score before shipping.** Run the quality rubric. If it's below 8, improve it. If it can't reach 8, question whether it should exist.
- **Think like an agent builder.** Skills are agents. Consider all five dimensions: prompt design, tool selection, context engineering, orchestration, and evaluation. They're interconnected — improving one often reveals what's missing in another.
