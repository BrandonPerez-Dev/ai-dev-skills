
---
name: eval-driven-dev
description: >-
  Eval-driven development for AI agents and LLM features. Use when building, testing,
  or improving non-deterministic AI systems. Covers eval suite design, grader selection,
  statistical confidence over multiple trials, and transcript review. Classical TDD
  doesn't fit agents — this adapts it for non-deterministic systems.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - WebSearch
  - WebFetch
---

# Eval-Driven Development

An agent without evals is a demo, not a product. Measure before shipping.

<HARD-GATE>
Do NOT ship an agent or LLM feature without running evals. A single successful run proves nothing — agent behavior is non-deterministic. Run 3-5 trials per task and measure pass rates before deploying.
</HARD-GATE>

## Why Not Classical TDD?

Classical TDD assumes deterministic behavior: same input → same output. Agents violate this:
- **Non-deterministic** — same prompt can produce different responses
- **Open-ended** — multiple valid approaches to the same task
- **Tool-dependent** — behavior varies with tool availability and responses
- **Context-sensitive** — performance degrades with context length and complexity

Eval-driven development adapts TDD principles for this reality. Instead of "test passes/fails," you measure "pass rate across trials."

## Method Selection

| Situation | Approach | Trials |
|-----------|----------|--------|
| **New agent from scratch** | Full eval suite: 5-10 tasks, 3-5 trials each | 15-50 runs minimum |
| **Adding a tool to existing agent** | Targeted evals: tasks that exercise the new tool | 3-5 trials per task |
| **Agent underperforming** | Diagnostic evals: isolate the failing component | 5 trials per suspect task |
| **Pre-deployment check** | Full suite re-run: all tasks, fresh trials | Full coverage |
| **Prompt change** | A/B comparison: same tasks, before and after | 5 trials each, compare pass rates |

## Core Vocabulary

- **Task** — A single test scenario with defined inputs and success criteria
- **Trial** — One attempt at a task (multiple trials account for non-determinism)
- **Grader** — Logic that scores agent performance on a task
- **Transcript** — Complete record of outputs, tool calls, and reasoning
- **Pass rate** — Fraction of trials that succeed for a given task
- **pass@k** — Succeeds at least once in k trials (measures capability)
- **pass^k** — Succeeds every time in k trials (measures reliability)

## Grader Types

| Type | When | Strengths | Weaknesses |
|------|------|-----------|------------|
| **Code-based** | Deterministic outcomes (file created? API returned 200? correct format?) | Fast, cheap, reproducible | Brittle to valid variations |
| **Model-based** | Subjective quality (helpful? follows rubric? correct reasoning?) | Flexible, captures nuance | Non-deterministic itself, needs calibration |
| **Human** | High-stakes or ambiguous (medically accurate? legally sound?) | Gold standard for quality | Slow, expensive, doesn't scale |

**Default to code-based.** Use model-based for quality assessment. Calibrate model-based graders against human judgment before trusting them.

### Code-Based Grader Examples

```typescript
// Structural check: did the agent produce the right artifact?
function gradeFileCreated(transcript: Transcript): boolean {
  return transcript.toolCalls.some(
    call => call.tool === 'Write' && call.args.file_path.endsWith('.test.ts')
  );
}

// Outcome check: did the task succeed?
function gradeTestsPassing(transcript: Transcript): boolean {
  const bashCalls = transcript.toolCalls.filter(c => c.tool === 'Bash');
  return bashCalls.some(c => c.result.includes('Tests: ') && !c.result.includes('failed'));
}
```

### Model-Based Grader Pattern

```typescript
// Use a separate model call to evaluate quality
async function gradeResponseQuality(transcript: Transcript): Promise<number> {
  const response = await evaluate({
    rubric: `Score 1-5 on: accuracy, completeness, and actionability.
             5 = correct, complete, immediately usable.
             1 = wrong, incomplete, or misleading.`,
    content: transcript.finalResponse,
  });
  return response.score;
}
```

Calibrate model graders: run on 20+ examples where you know the right score, check alignment.

## Process

### 1. Define Success Criteria

Before building anything, define what "good" looks like for each task. Be specific enough that a grader can check it.

```markdown
**Task:** Agent fixes a failing TypeScript test
**Success criteria:**
- [ ] The test passes after the agent's changes (code-based: run test, check exit code)
- [ ] No other tests regressed (code-based: full test suite passes)
- [ ] Changes are minimal (model-based: score 1-5 on change minimality)
```

### 2. Build the Eval Suite

Start with 5-10 tasks from real use cases. Include:
- **Easy tasks** (2-3) — baseline capability, should pass >90%
- **Medium tasks** (3-4) — core use cases, target >80%
- **Hard tasks** (2-3) — edge cases, acceptable at >50%
- **Known failure cases** — tasks that previously broke the agent

Each task needs:
- Input (prompt, context, files)
- Success criteria (grader logic)
- Expected difficulty level

### 3. Run Trials

Run each task 3-5 times. Non-determinism means single runs are meaningless.

**Measure both:**
- **pass@k** (succeeds at least once in k trials) — measures capability
- **pass^k** (succeeds every time) — measures reliability

An agent that passes@5 at 100% but passes^5 at 20% is capable but unreliable. Both metrics matter.

### 4. Grade at Multiple Levels

Don't just check end-to-end outcomes. Also grade intermediate steps:
- Did the agent use the right tools?
- Did the plan make sense?
- Did it recover from errors?
- Did it use tokens efficiently?

Intermediate grading catches agents that pass by luck or brute force.

### 5. Read Transcripts

**This is not optional.** Automated graders miss subtle failures.

Review transcripts looking for:
- Agent passes eval but with bad reasoning (fragile success)
- Agent retries the same failing approach repeatedly
- Agent uses 10x more tokens than necessary
- Agent ignores key context or instructions
- Agent succeeds despite poor tool selection

A passing eval with bad process is worse than a failing eval — it means your grading is wrong.

### 6. Iterate

After evals reveal failure modes:

| Symptom | Fix |
|---------|-----|
| Pass rate too low across all tasks | System prompt needs improvement — invoke **prompt-engineering** |
| One task consistently fails | Agent lacks a tool or the task is ambiguous — add tool or clarify task |
| Pass@k high but pass^k low | Non-determinism issue — add structure (XML tags, examples) to reduce variance |
| Passes but with bad process | Graders are too lenient — add intermediate grading |
| Regressions after prompt change | A/B eval: compare before/after on full suite |

### 7. Evolve the Suite

Evals are living artifacts. Update them as the product evolves:
- Add tasks for new features
- Retire tasks for deprecated features
- Increase difficulty as the agent improves
- Add tasks from production failure reports

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do Instead |
|--------------|-------------|------------|
| **Single trial** | One run proves nothing with non-deterministic systems | 3-5 trials minimum per task |
| **Exact string matching** | LLM output varies in format, wording, whitespace | Use structural and semantic checks |
| **Shared state between trials** | Previous trials corrupt current ones | Fresh state per trial |
| **Testing implementation** | "Did it call tool X?" is brittle | "Did it achieve the outcome?" is robust |
| **Ignoring transcripts** | Passing evals with bad process = fragile success | Review transcripts regularly |
| **Eval suite as afterthought** | Written after the agent, biased toward current behavior | Write evals before building the agent |
| **Only happy-path tasks** | Agent looks great until it hits an edge case | Include hard tasks and known failure cases |

## Guidelines

- **Evals before building.** Define what "good" looks like before writing agent code. Otherwise you're fitting evals to behavior, not behavior to evals.
- **Statistical confidence, not anecdote.** "It worked when I tried it" is not data. 3-5 trials, measured pass rates.
- **Code-based first.** Every eval should start with code-based graders. Add model-based only for subjective quality.
- **Transcripts reveal truth.** Automated evals catch outcomes. Transcript review catches process failures. Do both.
- **pass@k measures capability, pass^k measures reliability.** You need both. An unreliable agent that can occasionally succeed is not shippable.
