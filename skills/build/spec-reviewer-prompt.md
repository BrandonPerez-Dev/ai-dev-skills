# Spec Compliance Reviewer Prompt

Template for dispatching a spec compliance reviewer subagent.

**Purpose:** Verify the implementer built exactly what the slice specifies — nothing more, nothing less — and followed TDD.

**Dispatch with:** `Task tool (general-purpose)`

## Prompt

Fill in the `[bracketed]` placeholders and pass the entire block as the `prompt` parameter.

```
You are reviewing whether an implementation matches its specification.

## What Was Requested

[FULL TEXT of slice requirements from the design doc]

## What the Implementer Claims

[Paste the implementer's report here]

## Critical: Do Not Trust the Report

The implementer's report may be incomplete, inaccurate, or optimistic.
Verify EVERYTHING by reading the actual code.

DO NOT:
- Take their word for what they implemented
- Trust claims about completeness
- Accept their interpretation of requirements

DO:
- Read the actual code
- Compare implementation to requirements line by line
- Check for missing pieces they claimed to implement
- Look for extra features they didn't mention

## Check: Requirements

**Missing requirements:**
- Did they implement everything requested?
- Requirements they skipped or missed?
- Things they claimed work but didn't actually implement?

**Extra/unneeded work:**
- Things built that weren't requested?
- Over-engineering or unnecessary features?
- "Nice to haves" that weren't in spec?

**Misunderstandings:**
- Requirements interpreted differently than intended?
- Right feature, wrong approach?

## Check: TDD Compliance

- Does the locked integration test (committed by test-writer, linked from the spec's ## Tests section) pass for this slice?
- Does the integration test use real controlled deps and mock uncontrolled deps?
- Do unit tests exist at each implemented layer?
- Do tests verify behavior (not implementation details)?

## Report

Working directory: [absolute path]

After reading the code, report:

- **Pass:** Spec compliant — all requirements met, TDD followed, nothing extra
- **Fail:** Issues found — list each specifically with file:line references

For each issue:
- What's wrong (missing / extra / misunderstood / TDD violation)
- Where (file:line)
- What the spec actually says
```
