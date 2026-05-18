
---
name: skill-eval
description: >-
  Test and validate skills by running them against realistic prompts and comparing results.
  Use after creating or improving a skill to verify it actually works. Supports blind A/B
  comparison between skill versions, baseline comparison (with-skill vs without), grading
  against assertions, and qualitative user review. The skill-creator builds skills — this
  skill proves they work.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Skill Eval

A skill without evidence is an opinion. Test it before you trust it.

<HARD-GATE>
Never declare a skill "done" based on reading the SKILL.md alone. Run it against realistic test prompts and evaluate the outputs. Reading a skill tells you what it SAYS it does. Running it tells you what it ACTUALLY does.
</HARD-GATE>

## When to Use

- After creating a new skill (skill-creator)
- After improving an existing skill
- When a skill produces unexpected results and you want to diagnose why
- When deciding between two versions of a skill
- When the user asks "does this skill actually work?"

## Process

### 1. Design Test Prompts

Create 3-5 realistic test prompts — things a real user would actually say that should trigger the skill. Quality matters more than quantity.

**Good test prompts are:**
- Realistic and specific (include file paths, context, details a real user would give)
- Varied — cover different situations the skill handles (method selection paths, edge cases, typical use)
- Challenging enough that the skill adds value (trivial prompts don't test anything)
- Include at least one near-miss that should NOT trigger the skill (tests description accuracy)

**Bad test prompts:** generic, abstract, one-word, or obviously aligned with the skill.

| Bad | Good |
|-----|------|
| "Review this code" | "I just pushed a PR with auth changes to the login flow — can you review it? The PR touches src/auth/oauth.ts and adds a new refresh token rotation" |
| "Debug this" | "My vitest integration tests pass locally but fail in CI with a timeout on the database connection. Started after I upgraded to Node 22" |
| "Write a spec" | "We need to add webhook support to the MCP server so external systems can subscribe to events. Can you write up what that looks like?" |

Present the test prompts to the user for review before running them.

**CHECKPOINT: Confirm test prompts with user.**

"Here are the test prompts I'll run:
1. [prompt summary]
2. [prompt summary]
3. [prompt summary]

Do these cover the right scenarios? Want to add or change any?"

### 2. Set Up the Comparison

Decide what you're comparing:

| Scenario | Version A | Version B | What It Tests |
|----------|-----------|-----------|---------------|
| **New skill** | With skill | Without skill (baseline) | Does the skill add value? |
| **Skill improvement** | Old version | New version | Is the new version better? |
| **Alternative approaches** | Version 1 | Version 2 | Which approach wins? |

**For skill improvements — snapshot first:**

Before making any changes to the skill, snapshot the current version:

```bash
cp -r /path/to/skill /path/to/workspace/skill-snapshot
```

This preserves the old version for comparison. Make improvements to the original, then run both.

### 3. Run Test Prompts

For each test prompt, spawn two subagents in parallel — one for each version. Both get the exact same prompt.

**With-skill run:**
```
Subagent prompt:
"You have access to the skill at [path]. Use it to accomplish this task:
[test prompt]
Save your final output to [workspace]/eval-N/version-a/output.md"
```

**Baseline or old-version run:**
```
Subagent prompt (baseline):
"Accomplish this task WITHOUT any specialized skill:
[test prompt]
Save your final output to [workspace]/eval-N/version-b/output.md"

Subagent prompt (old version):
"You have access to the skill at [snapshot-path]. Use it to accomplish this task:
[test prompt]
Save your final output to [workspace]/eval-N/version-b/output.md"
```

**Launch all runs in parallel.** Don't wait for one to finish before starting the next.

### 4. Grade Results

After all runs complete, evaluate each output. Two types of grading:

**Quantitative — assertions:**

Define 3-5 objectively verifiable assertions per test prompt. These should check outcomes, not process.

```markdown
Assertions for eval-1:
- [ ] Output identifies the root cause, not just symptoms
- [ ] Output includes file:line references to specific code
- [ ] Output proposes a fix, not just a diagnosis
- [ ] Output does NOT suggest changes outside the scope of the problem
```

Grade each assertion as PASS or FAIL with evidence (quote from the output that supports the verdict).

**Communication quality (user-facing skills only):**

For skills that produce multi-step output with user decisions, also check:
- [ ] Output is chunked (no ungrouped lists longer than 4 items)
- [ ] Each message covers one topic, not multiple
- [ ] Decisions are scaled to stakes (not everything presented as a big choice)
- [ ] Checkpoints are concise, not info dumps

Skip this for utility skills (commit-and-pr, verification, etc.).

**Qualitative — user review:**

Present the outputs to the user. For each test prompt, show both outputs and ask:
- Which output is better?
- What specifically is better about it?
- What's missing from the weaker output?

### 5. Blind Comparison (When Comparing Versions)

This is the most important step when evaluating a skill improvement. It removes bias — you won't unconsciously favor the version you just worked on.

**How it works:**

1. **Randomize.** For each test prompt, randomly assign which version is "Output A" and which is "Output B". Flip a coin or use:
   ```bash
   echo $((RANDOM % 2))  # 0 = current is A, 1 = current is B
   ```

2. **Present blindly.** Show the user both outputs without revealing which version produced which:

   "For test prompt: '[prompt summary]'

   **Output A:**
   [output content or summary]

   **Output B:**
   [output content or summary]

   Which output is better? What makes it better?"

3. **Collect the verdict.** Record the user's choice and reasoning for each prompt.

4. **Reveal.** After the user has judged ALL test prompts, reveal the mapping:

   "Here's what produced each output:
   - Eval 1: A = new version, B = old version → User picked: A
   - Eval 2: A = old version, B = new version → User picked: A
   - Eval 3: A = new version, B = old version → User picked: A

   Score: New version won 2/3, Old version won 1/3"

**Why blind matters:** Without blinding, there's a strong bias to prefer the version you just improved. You expect it to be better, so you see it as better. Blind comparison catches cases where your "improvement" actually made things worse.

### 6. Analyze and Decide

After grading and blind comparison, summarize:

```markdown
## Eval Summary

**Comparison:** [old version vs new version / with skill vs without]
**Test prompts:** [count]

### Assertion Results
| Eval | Version A | Version B |
|------|-----------|-----------|
| 1    | 4/5 pass  | 3/5 pass  |
| 2    | 3/5 pass  | 2/5 pass  |
| 3    | 5/5 pass  | 4/5 pass  |

### Blind Comparison
| Eval | User Picked | Winner Was |
|------|-------------|------------|
| 1    | A           | New version |
| 2    | A           | Old version |
| 3    | B           | New version |

### Verdict
[Clear recommendation: ship, iterate more, or revert]

### What to Fix (if iterating)
- [Specific issue seen across multiple evals]
- [Pattern in the failures]
```

### 7. Iterate or Ship

Based on the results:

- **Clear win:** Ship the new version. Delete the snapshot.
- **Mixed results:** Identify what's weaker in the new version. Fix those specific issues. Re-run evals (new iteration).
- **Clear loss:** Revert to the snapshot. Diagnose why the changes hurt. Try a different approach.

**When iterating,** only re-run the evals that failed or were close. Don't re-run prompts where both versions performed well.

## Workspace Structure

```
skill-eval-workspace/
├── test-prompts.md           # The test prompts
├── iteration-1/
│   ├── eval-1/
│   │   ├── version-a/
│   │   │   └── output.md
│   │   └── version-b/
│   │       └── output.md
│   ├── eval-2/
│   │   └── ...
│   ├── assertions.md         # Assertion definitions + grades
│   ├── blind-results.md      # Blind comparison results
│   └── summary.md            # Eval summary + verdict
├── iteration-2/              # If iterating
│   └── ...
└── skill-snapshot/            # Snapshot of the old version
```

## Anti-Patterns

| Anti-Pattern | What Happens | Instead |
|--------------|-------------|---------|
| Reading the skill and declaring it good | Skill has structural quality but doesn't work in practice | Run it against real prompts |
| Generic test prompts | "Do the thing" tests nothing — any response passes | Specific, realistic, varied prompts |
| Knowing which output is which | Bias toward the version you worked on | Blind comparison with randomized assignment |
| Testing only happy paths | Skill works for typical cases but fails on edge cases | Include at least one edge case and one near-miss |
| Single test prompt | One prompt can't reveal patterns | 3-5 prompts minimum, covering different scenarios |
| Skipping baseline | No way to know if the skill actually adds value | Always compare against without-skill or old version |
| Changing test prompts between iterations | Can't compare across iterations | Keep prompts stable; add new ones, don't replace |

## Guidelines

- **Run it, don't read it.** The only way to know if a skill works is to test it against realistic prompts. Reading the SKILL.md tells you what it claims, not what it does.
- **Blind comparison is non-negotiable for improvements.** If you're claiming "the new version is better," prove it with blind A/B testing. Unblinded comparison is confirmation bias in disguise.
- **Test prompts are the foundation.** Bad prompts produce meaningless results. Invest time in designing prompts that would challenge the skill.
- **Assertions check outcomes, not process.** "The output identifies the root cause" is a good assertion. "The output follows the 5-step methodology" is a bad one — you care about results, not compliance.
- **Keep prompts stable across iterations.** If you change the prompts, you can't compare results. Add new prompts if coverage is insufficient, but don't replace existing ones.
