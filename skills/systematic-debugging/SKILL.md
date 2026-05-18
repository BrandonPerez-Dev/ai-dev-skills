
---
name: systematic-debugging
description: Use when encountering any bug, test failure, unexpected behavior, or performance problem — before proposing fixes. Root cause first, always.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Task
  - WebSearch
  - WebFetch
---

# Systematic Debugging

Find the root cause before you touch the code. Random fixes waste time and create new bugs.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes. No exceptions.

## When to Use

Use for ANY technical issue:
- Test failures
- Production bugs
- Unexpected behavior
- Performance problems
- Build or CI failures
- Integration issues
- Configuration mysteries

**Use this ESPECIALLY when:**
- Under time pressure — rushing guarantees rework
- "Just one quick fix" seems obvious — obvious fixes mask root causes
- You've already tried a fix and it didn't work
- You don't fully understand the system
- The bug is in unfamiliar code

## Select Your Investigation Method

Different bugs need different approaches. Choose before diving in:

| Bug Type | Start With | Why |
|----------|-----------|-----|
| **Regression** (worked before, broke recently) | `git-bisect.md` — temporal search | "When did it break?" is easier than "where in code?" |
| **Test failure** (clear error, known code) | Phase 1 below — standard investigation | You have a reproduction and a stack trace |
| **"Works locally, fails in CI"** | `environment-debugging.md` — env checklist | Almost always config, secrets, or env differences |
| **Performance problem** | Profiling first — measure, don't guess | Intuition about performance is usually wrong |
| **Flaky / intermittent** | Reproduce first, then Phase 1 | If you can't trigger it reliably, you can't debug it |
| **Unfamiliar codebase** | Phase 0 below — orient first | You need a map before you can navigate |
| **Distributed / cross-service** | Trace the request across boundaries | Find which service is the source of the problem |

## Phase 0: Orient (Unfamiliar Code)

**Skip this if you already know the codebase.** Use when entering cold.

Before debugging code you don't understand:

1. **Map the system** — What are the main components? Where are the entry points? Read the README, architecture docs, directory structure.
2. **Locate the error** — Use the error message as a breadcrumb. Find the file and line. Read the surrounding function.
3. **Trace one level out** — What calls this function? What does it call? Read the types/interfaces, not the implementation details.
4. **Find related tests** — Tests document expected behavior. Read the test for the failing code to understand what it's supposed to do.

Use the **research** skill if the system is complex enough to warrant full investigation. Phase 0 is a quick orientation, not a deep dive.

**Exit criteria:** You understand enough about the system's structure to form hypotheses about what might be wrong.

## Phase 1: Investigate

**BEFORE attempting ANY fix:**

### Read the Error

Don't skim. Read the full error message, stack trace, and any warnings.

- Note exact line numbers and file paths
- Read the error message literally — it often contains the answer
- Check for multiple errors — the first one is usually the root cause
- Warnings before the error may be related

### Reproduce Consistently

- Can you trigger it reliably?
- What are the exact steps?
- If not reproducible: gather more data, add logging, don't guess

### Check Recent Changes

- `git diff` and `git log` on relevant files
- New dependencies, config changes, env variable changes
- Did someone else's change affect this area?

### Gather Evidence in Multi-Component Systems

**When the system has multiple layers (CI → build → deploy, API → service → database):**

Add diagnostic instrumentation at each component boundary BEFORE proposing fixes:

```
For EACH layer boundary:
  - Log what data enters
  - Log what data exits
  - Verify config/env propagation
  - Check state

Run once to see WHERE it breaks.
THEN investigate that specific component.
```

This reveals which layer fails. Fix the right layer, not the one that reports the error.

### Trace Data Flow

When the error is deep in the call stack, trace backward to find the original trigger. See `root-cause-tracing.md` for the complete technique.

**Quick version:** Where does the bad value originate? What called this with the bad value? Keep tracing up until you find the source. Fix at source, not at symptom.

## Phase 2: Reproduce and Reduce

### Reproduce

If you don't have a reliable reproduction yet, create one:
- Isolate the failing case into the simplest possible trigger
- Automate it (test case, script, curl command)
- Confirm it fails consistently

### Reduce

**Minimize the reproduction to its essence.** Remove everything that isn't necessary to trigger the bug:

- Remove unrelated code, data, and configuration
- Simplify inputs to the smallest failing case
- Strip out irrelevant dependencies

A minimal reproduction focuses your investigation and often reveals the root cause directly. If the bug disappears when you remove something, that something is involved.

## Phase 3: Hypothesize and Test

### Form a Single Hypothesis

- State clearly: "I think X is causing Y because Z"
- Be specific, not vague
- Write it down before testing

### Test Minimally

- Make the SMALLEST possible change to test the hypothesis
- One variable at a time
- Don't fix multiple things at once

### Verify

- Did it confirm the hypothesis? → Phase 4
- Didn't confirm? → Form a NEW hypothesis
- DON'T layer fixes on top of each other

### Cognitive Load Check

If you've been debugging for a while:

- **10-minute rule:** If the current approach hasn't yielded progress in 10 minutes, switch methods. Try a different investigation angle.
- **Tunnel vision check:** Are you fixated on one theory? Actively seek disconfirming evidence.
- **Rubber duck it:** Explain the problem out loud (or in text). Articulating the issue often reveals the gap in your understanding.
- **Step back:** If you're going in circles, summarize what you know vs. what you don't. The gap usually points to the next investigation.

### When You Don't Know

- Say "I don't understand X" — don't pretend
- Ask for help
- Use the **research** skill to investigate unfamiliar APIs, patterns, or libraries

## Phase 4: Fix and Verify

### Create a Failing Test

- Simplest possible reproduction as an automated test
- Use the **tdd** skill for writing proper failing tests
- MUST have a failing test before implementing the fix
- The test documents the bug for future developers

### Implement a Single Fix

- Address the root cause identified in Phase 3
- ONE change at a time
- No "while I'm here" improvements
- No bundled refactoring

### Verify the Fix

- Test passes now?
- No other tests broken?
- Issue actually resolved, not just masked?
- Use the **verification** skill before claiming done

### If the Fix Doesn't Work

Count your attempts:

- **< 3 attempts:** Return to Phase 1 with new information
- **≥ 3 attempts: STOP.** You likely have an architectural problem, not a bug.

### When 3+ Fixes Fail: Question the Architecture

**Patterns that indicate an architectural problem:**
- Each fix reveals new coupling or shared state in a different place
- Fixes require "massive refactoring" to implement
- Each fix creates new symptoms elsewhere

**STOP and question fundamentals:**
- Is this pattern sound, or are we persisting through inertia?
- Should we refactor the architecture instead of patching symptoms?

**Discuss with the user before attempting more fixes.** This is not a failed hypothesis — this is a wrong architecture.

### After Fixing

Consider adding defense-in-depth validation. See `defense-in-depth.md` — add checks at multiple layers to make the bug structurally impossible to recur.

## Red Flags — STOP and Follow the Process

If you catch yourself thinking any of these, return to Phase 1:

- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- "One more fix attempt" (when you've already tried 2+)
- Each fix reveals a new problem in a different place

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check. |
| "Just try this first, then investigate" | The first fix sets the pattern. Do it right from the start. |
| "I'll write the test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question the pattern. |

## Supporting Techniques

Available in this directory:

- **`root-cause-tracing.md`** — Trace bugs backward through the call stack to find the original trigger
- **`defense-in-depth.md`** — Add validation at multiple layers after finding root cause
- **`condition-based-waiting.md`** — Replace arbitrary timeouts with condition polling (fixes flaky tests)
- **`git-bisect.md`** — Binary search through commit history to find when a regression was introduced
- **`environment-debugging.md`** — Systematic approach to config, CI, and "works on my machine" issues
- **`find-polluter.sh`** — Bisection script to find which test creates unwanted state

## Quick Reference

| Phase | Key Activities | Exit Criteria |
|-------|---------------|---------------|
| **0. Orient** | Map system, locate error, read tests | Understand enough to hypothesize |
| **1. Investigate** | Read errors, reproduce, check changes, gather evidence | Know WHAT and WHERE |
| **2. Reproduce & Reduce** | Isolate, minimize, automate | Have minimal reliable reproduction |
| **3. Hypothesize & Test** | Form theory, test minimally, verify | Confirmed root cause |
| **4. Fix & Verify** | Failing test, single fix, verify | Bug resolved, tests pass, no regressions |

## Guidelines

- **Root cause first, always.** Symptom fixes are failure.
- **One change at a time.** Multiple changes at once make it impossible to isolate what worked.
- **Select the right method.** Regression → git bisect. Env issue → environment checklist. Performance → profile. Don't default to code inspection for everything.
- **Reduce before deep-diving.** A minimal reproduction is worth more than hours of code reading.
- **Manage your cognitive load.** 10-minute rule. Rubber duck. Step back. Debugging is mentally expensive.
- **3 strikes = architectural problem.** Don't keep patching. Question the design.
