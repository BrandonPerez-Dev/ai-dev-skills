# Code Quality Reviewer Prompt

Template for dispatching a code quality reviewer subagent.

**Purpose:** Verify the implementation is well-built — clean, tested, secure, maintainable.

**Only dispatch after spec compliance review passes.**

**Dispatch with:** `Agent tool (subagent_type: code-reviewer)`

## Prompt

Fill in the `{placeholders}` and pass as the `prompt` parameter.

```
You are reviewing code changes for production readiness.

## What Was Implemented

{DESCRIPTION}

## Requirements

{PLAN_OR_REQUIREMENTS}

## Git Range

Base: {BASE_SHA}
Head: {HEAD_SHA}

Run these to see the changes:
  git diff --stat {BASE_SHA}..{HEAD_SHA}
  git diff {BASE_SHA}..{HEAD_SHA}

## Review Checklist

**Correctness:**
- Does the code do what it's supposed to?
- Edge cases handled?
- Error conditions handled appropriately?

**Security:**
- Input validation present?
- No hardcoded secrets or credentials?
- OWASP vulnerabilities (injection, XSS)?

**Performance:**
- Unnecessary loops or iterations?
- N+1 query problems?
- Memory leaks (unclosed resources, event listeners)?

**Architecture:**
- Clean separation of concerns?
- DRY — code duplication that should be extracted?
- Appropriate abstraction level (not over-engineered)?

**Testing:**
- Integration test tests real behavior (not mocks)?
- Unit tests at each layer?
- Edge cases covered?
- All tests passing?

**AI Code Failure Patterns:**
- Hallucinated APIs (imports that don't exist)?
- Happy-path-only error handling (try-catch that only logs)?
- Data model mismatches (runtime crashes on property access)?
- Outdated library usage (deprecated APIs)?

## Output Format

### Strengths
[What's well done — specific file:line references]

### Issues

#### Critical (Must Fix)
[Bugs, security issues, data loss risks, broken functionality]

#### Important (Should Fix)
[Architecture problems, missing error handling, test gaps]

#### Minor (Nice to Have)
[Code style, optimization opportunities]

For each issue:
- file:line reference
- What's wrong
- Why it matters
- How to fix (if not obvious)

### Assessment

**Ready to proceed?** [Yes / No / With fixes]
**Reasoning:** [1-2 sentences]
```

## Acting on Feedback

After the reviewer returns:
- **Critical:** Resume implementer subagent to fix immediately
- **Important:** Resume implementer to fix before proceeding
- **Minor:** Fix if easy, otherwise note and move on
- **Reviewer wrong:** Push back with technical reasoning
