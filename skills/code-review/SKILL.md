
---
name: code-review
description: >-
  Systematic code review — understand the change before judging it. Use after code changes,
  before committing, when reviewing PRs, or when asked to review specific files. Teaches
  a review methodology: context first, then strategic reading, then severity-ranked findings.
  Covers agent/MCP-specific review concerns (tool descriptions, prompt quality, token efficiency).
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - WebSearch
  - AskUserQuestion
---

# Code Review

Understand the change before judging it. Context first, critique second.

<HARD-GATE>
Do NOT start listing issues until you understand what the change is trying to do and why. Reviewing without context produces nitpicks, not insights. Read the scope first — commit messages, PR description, linked issues, or ask the author.
</HARD-GATE>

## Method Selection

| Review Type | When | Depth | Focus |
|-------------|------|-------|-------|
| **Quick scan** | Small change, trusted author, low-risk area | Skim diff, check for obvious issues | Correctness, missing tests |
| **Standard review** | New feature, bug fix, refactor | Full read, strategic file ordering | Correctness, contracts, edge cases, tests |
| **Deep review** | Security-sensitive, new patterns, system boundaries | Read implementation + surrounding code | Architecture, security, failure modes, contracts |
| **Agent/MCP review** | Agent systems, MCP servers, prompt changes | Standard + agent-specific checks | Tool descriptions, prompt quality, token efficiency, eval coverage |

Default to **standard**. Escalate to deep when you find something surprising.

## Process

### 1. Understand the Scope

Before reading any code, understand what changed and why:

- **What changed?** — `git diff --stat` or PR file list. How many files? Which layers?
- **Why?** — commit messages, PR description, linked issues. What problem does this solve?
- **What's the risk?** — is this touching auth? payments? data migration? new external integrations?

If the "why" is unclear, ask. Don't guess at intent — wrong assumptions about intent produce wrong review feedback.

### 2. Read Strategically

Don't read files top-to-bottom in alphabetical order. Start with the highest-leverage files:

**Read in this order:**
1. **Contracts first** — API routes, type definitions, interfaces, schemas. These define what the system promises. If the contracts are wrong, everything built on them is wrong.
2. **Data layer** — schema changes, migrations, queries. Data is the hardest to fix later.
3. **Business logic** — service layer, domain logic. This is where correctness bugs live.
4. **Glue code** — route handlers, adapters, configuration. Lower risk but check error handling.
5. **Tests** — do they cover the contracts? Do they test edge cases? Are they testing behavior or implementation?

**At each file, ask three questions:**
- Does this do what the author intended?
- Is what the author intended correct?
- What's NOT here that should be? (missing error handling, missing validation, missing edge cases)

The third question is the most valuable. Finding what's absent is harder than finding what's wrong.

### 3. Check for Real Issues

Focus on things that matter. Ignore things a linter handles.

**Blocking issues (request changes):**
- Incorrect behavior — the code doesn't do what it claims to
- Security vulnerabilities — injection, auth bypass, secrets exposure, OWASP top 10
- Data loss risk — migrations that drop data, missing transactions, race conditions
- Contract violations — API returns different shape than type says, schema mismatch
- Missing error handling on system boundaries — unhandled external API failures, missing validation on user input
- Breaking changes without migration path

**Suggestions (approve with comments):**
- Edge cases not covered
- Missing tests for important paths
- Performance concerns (N+1 queries, unnecessary iterations, missing indexes)
- Error messages that don't help debugging
- Abstraction level issues (premature or missing)

**Not worth mentioning:**
- Style issues when a formatter exists
- Naming preferences (unless genuinely confusing)
- "I would have done it differently" without a concrete problem
- Comments that restate what the code does

### 4. Agent/MCP-Specific Review

When reviewing agent systems, MCP servers, or prompt-related code, add these checks:

**Tool descriptions:**
- Are parameter descriptions unambiguous with format examples?
- Are response formats documented?
- Is there a `detail_level` parameter for large responses?
- Could description improvements make the agent more reliable? (40%+ improvement measured from description quality)

**Prompt quality:**
- Are critical instructions at the edges of context (not buried in the middle)?
- Do rules explain WHY, not just WHAT? (motivation-based rules generalize better)
- Is the prompt structured with XML sections or clear delimiters?
- Is there permission to say "I don't know"? (reduces hallucination)

**Token efficiency:**
- Are full file contents loaded when a path reference would suffice?
- Are tool responses being filtered/compacted?
- Is context being loaded just-in-time or all upfront?

**Eval coverage:**
- Do non-deterministic behaviors have eval tasks?
- Are graders checking outcomes, not implementation?
- Are there enough trials (3-5 per task)?

**MCP server specifics:**
- Does it follow the dual-mode pattern (mock + live)?
- Are tool handlers thin (delegate to provider)?
- Is error handling mapped to domain-specific codes?

### 5. Present Findings

Severity-ranked. Lead with the most important issue. Use `file:line` references.

## Output Format

```markdown
## Review: [Brief summary of what was reviewed]

**Verdict:** Approve / Approve with comments / Request changes

## Blocking Issues
- [ ] **[Severity]** `file.ts:42` — [What's wrong and why it matters]. Fix: [concrete suggestion].

## Suggestions
- [ ] `file.ts:85` — [What could be better]. Consider: [alternative approach].

## Questions
- `file.ts:120` — [Something unclear about intent]. Is this intentional?

## What's Good
- [Specific pattern or decision that's well done and why]
```

**Verdict rules:**
- Any blocking issue → Request changes
- Suggestions only → Approve with comments
- Nothing material → Approve (don't invent issues to justify the review)

## Bias Guards

| Trap | Antidote |
|------|----------|
| **Bikeshedding** | Spending 10 minutes on a variable name while missing a logic bug. Read contracts and data layer first. |
| **Rubber-stamping** | "LGTM" without reading. The hard gate prevents this — understand scope first. |
| **Style policing** | Complaining about formatting when a linter exists. Only mention style if it causes confusion. |
| **Nitpick cascade** | Finding 20 minor issues that obscure 1 real problem. Rank by severity, lead with what matters. |
| **Missing the forest** | Reviewing each line but not understanding the design. Step back: does this approach make sense? |
| **Assuming intent** | Flagging "bugs" that are intentional behavior. When unsure, ask — don't assume. |
| **Scope creep** | Reviewing code that wasn't changed. Only review adjacent code if a change creates a new risk. |

## Anti-Patterns This Skill Prevents

| Anti-Pattern | What Happens | This Skill Prevents It By |
|--------------|-------------|--------------------------|
| Generic checklist | "Does it handle edge cases?" without knowing which ones | Context-first methodology — understand the change before judging |
| Style over substance | Blocking on semicolons while missing auth bypass | Severity classification — blocking vs suggestion vs nitpick |
| Missing what's absent | Finding typos but not missing error handling | "What's NOT here?" as an explicit review question |
| Agent-blind review | Reviewing MCP code like regular code, missing tool description quality | Agent/MCP-specific review checklist |
| Unactionable feedback | "This could be better" without saying how | Concrete fix suggestions required for every issue |

## Recommended Tools

These MCP servers enhance code review when available. None are required.

**Ready now (no account needed):**
- **Semgrep MCP** — `semgrep mcp` CLI. 5000+ SAST rules, security vulnerabilities, bug patterns. Run on security-sensitive or deep reviews.
- **CodeScene MCP** — local complexity/hotspot analysis. Identifies technical debt before reading code. Docker or npm.
- **ESLint MCP** — built into ESLint 9.26+ via `eslint --mcp`. Zero setup for JS/TS linting.

**When available (needs account/setup):**
- **GitHub MCP** — structured PR diffs, review comments, CI/CD visibility. Needs GitHub token.
- **SonarQube MCP** — comprehensive SAST + code quality metrics. Needs SonarQube instance.
- **Snyk MCP** — dependency vulnerability scanning, supply chain security. Needs Snyk account.

**When to use:** For deep reviews and security-sensitive code, run Semgrep alongside manual review. For complexity concerns, use CodeScene to identify hotspots before reading code. For PR reviews, GitHub MCP provides structured diff access.

## Guidelines

- **Context before critique.** Understand what the change does and why before finding fault. Wrong context → wrong feedback.
- **Contracts are the highest-leverage review target.** If the API contract, type definitions, or data schema are wrong, nothing else matters. Review these first.
- **What's absent matters more than what's present.** Missing error handling, missing validation, missing tests — these are harder to spot and more dangerous than incorrect code.
- **Severity determines action.** Blocking issues get "request changes." Suggestions get "approve with comments." Don't block on preferences.
- **Be specific, be concrete.** Every issue needs a file:line reference and a suggested fix. "This is bad" helps nobody.
- **Don't invent issues.** If the code is good, say so. An empty "Suggestions" section is better than manufactured nitpicks.
