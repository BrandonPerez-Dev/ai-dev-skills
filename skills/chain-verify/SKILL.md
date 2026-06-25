---
name: chain-verify
description: >-
  L1 chain creator — Phase 4. Smoke tests a generated L2 agent chain by
  running every referenced command, checking every referenced file path,
  validating skill structure, and testing internal consistency. Reports
  pass/fail per check with actionable fixes for failures.
when_to_use: >-
  Use after chain-generate has produced L2 skills in the target repo's
  .claude/skills/. Validates that the generated chain is correct and
  ready for autonomous use. Also use to audit an existing chain after
  repo changes that might have broken skill references.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
argument-hint: "[path/to/target-repo]"
effort: medium
---

# Chain Verify

Smoke test the generated chain. Every command must run. Every file reference must resolve. Every pattern must exist in the codebase. Report what passes and what's broken.

<HARD-GATE>
Do not fix problems found during verification. Report them. chain-generate
(or the human) fixes them. Verification that also fixes is untrustworthy
verification.
</HARD-GATE>

## Input

Target repo path (same repo where chain-generate wrote L2 skills).

## Process

### 1. Inventory

List everything that was generated:

```bash
# L2 skills
find .claude/skills -name 'SKILL.md' -type f

# Chain config
cat .claude/agent-chain.yaml

# CLAUDE.md
cat CLAUDE.md

# Chain artifacts
ls .claude/chain/
```

Record the inventory — this defines what gets checked.

### 2. Command Verification

For every command referenced in any generated artifact (CLAUDE.md, skills, agent-chain.yaml):

| Command | Source | Status | Output |
|---|---|---|---|
| `[build cmd]` | CLAUDE.md, agent-chain.yaml | ✅/❌ | [summary] |
| `[test cmd]` | CLAUDE.md, agent-chain.yaml | ✅/❌ | [summary] |
| `[lint cmd]` | CLAUDE.md, agent-chain.yaml | ✅/❌ | [summary] |
| `[format cmd]` | CLAUDE.md, agent-chain.yaml | ✅/❌ | [summary] |

Run each command. A command that fails is a verification failure even if the survey said it worked — the repo may have changed since the survey.

### 3. File Reference Verification

For every file path referenced in any generated skill:

```bash
# Extract file paths from skills
grep -rn 'context/' .claude/skills/ --include='*.md'
grep -rn 'spec/' .claude/skills/ --include='*.md'
# Check each referenced path exists
```

| Referenced Path | In Skill | Exists? |
|---|---|---|
| `context/architecture.md` | plan-grill | ✅/❌ |
| `context/testing-strategy.md` | test-planning | ✅/❌ |

### 4. Pattern Verification

For each code pattern or helper referenced in generated skills:

| Pattern/Helper | In Skill | Verified? | How |
|---|---|---|---|
| `McpClient::spawn()` | test-planning | ✅/❌ | `grep -r "McpClient::spawn" src/ tests/` |
| `tempfile::TempDir` | test-writer | ✅/❌ | `grep -r "tempfile::TempDir" tests/` |
| Error type usage | build | ✅/❌ | `grep -r "anyhow::Result" src/` |

### 5. Skill Structure Verification

For each generated L2 skill:

| Check | Status |
|---|---|
| Valid frontmatter (name, description, when_to_use, allowed-tools) | ✅/❌ |
| Has at least one HARD-GATE | ✅/❌ |
| Has anti-pattern table | ✅/❌ |
| Has handoff section | ✅/❌ |
| No generic placeholders remaining (`[placeholder]`) | ✅/❌ |
| No references to L0 templates | ✅/❌ |

### 6. Chain Config Verification

For agent-chain.yaml:

| Check | Status |
|---|---|
| All referenced skills exist in `.claude/skills/` | ✅/❌ |
| Build command matches CLAUDE.md | ✅/❌ |
| Test command matches CLAUDE.md | ✅/❌ |
| Commit style matches actual git log | ✅/❌ |
| Trigger types are valid | ✅/❌ |

### 7. CLAUDE.md Verification

| Check | Status |
|---|---|
| Build command works | ✅/❌ |
| Test command works | ✅/❌ |
| Project structure matches reality | ✅/❌ |
| Listed conventions match code samples | ✅/❌ |

### 8. Internal Consistency

Cross-check between generated artifacts:

| Check | Status |
|---|---|
| Skills reference same commands as CLAUDE.md | ✅/❌ |
| Skills reference same commands as agent-chain.yaml | ✅/❌ |
| Mock boundaries consistent across test-planning and test-writer skills | ✅/❌ |
| Naming conventions consistent across all skills | ✅/❌ |
| Error handling pattern consistent across build and domain skills | ✅/❌ |

### 9. Report

Write `.claude/chain/verification.md`:

```markdown
# Chain Verification: [project-name]

> Date: YYYY-MM-DD
> Status: pass | fail | partial

## Summary
- **Total checks:** [N]
- **Passed:** [M]
- **Failed:** [K]
- **Warnings:** [J]

## Command Verification
[Table from step 2]

## File References
[Table from step 3]

## Pattern References
[Table from step 4]

## Skill Structure
[Table from step 5]

## Chain Config
[Table from step 6]

## CLAUDE.md
[Table from step 7]

## Internal Consistency
[Table from step 8]

## Failures (actionable)

### [Failure 1]
- **What:** [what check failed]
- **Where:** [which file, which line]
- **Fix:** [specific action to resolve]

### [Failure 2]
...

## Warnings

### [Warning 1]
- **What:** [what's not wrong but concerning]
- **Recommendation:** [what to consider]
```

### 10. Post Results

1. Commit verification.md
2. Post PR comment with summary:
   ```
   📋 STATUS: Chain verification [passed/failed]
      Checks: [M]/[N] passed
      [If failures: list top 3 failures with fix suggestions]
      [If all passed: Chain is ready for autonomous use]
   ```

## Verification Severity

| Severity | Meaning | Example |
|---|---|---|
| **Failure** | Chain will break during autonomous use | Referenced command fails, helper doesn't exist |
| **Warning** | Chain will work but may produce suboptimal results | Assertion style mismatch, convention drift |
| **Info** | Observation, no action needed | "Survey found 3 test patterns, skill documents 2" |

## Re-verification

Chain-verify can be re-run after fixes. Compare against the previous verification.md to confirm regressions are fixed and no new ones appeared.

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Fixing problems during verification** | Hard gate. Report only. Fixer and checker must be separate. |
| **Skipping command runs** | Commands must actually run. "It worked during survey" is stale. |
| **Accepting partial passes** | Every failure needs a fix path. Partial pass = needs work. |
| **Verifying only structure, not content** | Structure checks catch formatting. Content checks catch wrong commands. Both matter. |

## Handoff

After this skill completes:
- If **all checks pass**: L2 chain is ready for autonomous use. Human reviews and approves.
- If **failures exist**: chain-generate fixes the issues, then chain-verify re-runs.
- The verification report is committed for human review.
- After human approval, the autonomous agent chain is operational.
