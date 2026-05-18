
---
name: kanban-breakdown
description: Break down loose conversation, meeting notes, or task lists into well-structured kanban cards. Extracts action items, captures decision context, validates task quality, and confirms with the user before creating anything. Uses kanban-mcp tools.
allowed-tools:
  - mcp__kanban-mcp__create-kanban-board
  - mcp__kanban-mcp__add-task-to-board
  - mcp__kanban-mcp__move-task
  - mcp__kanban-mcp__delete-task
  - mcp__kanban-mcp__get-board-info
  - mcp__kanban-mcp__get-task-info
  - mcp__kanban-mcp__list-boards
---

# Kanban Breakdown

The context around a task is more valuable than the task itself. Decisions made, options rejected, and dependencies discovered — that's what gets lost between sessions. Capture it or lose it.

<HARD-GATE>
Never create cards without presenting them to the user first. Extract, validate, confirm, then create.
</HARD-GATE>

## When to Use

- User shares meeting notes, task lists, or describes work in conversation
- User wants to add items to an existing kanban board
- User wants to reorganize or re-scope existing board items
- User dumps a stream of things that need doing and wants them tracked

## Core Principles

**Extract, don't invent.** Pull tasks from what the user said. Don't add tasks they didn't mention. Don't flesh out scope they didn't describe.

**Capture the why, not just the what.** When the user shares context around a task — decisions, trade-offs, things deprioritized and why — that goes in the card. This is the context that gets lost between sessions.

**Confirm before creating.** Always present the extracted tasks back to the user before writing them to the board. The user may have misspoken, changed their mind, or you may have misunderstood.

**Right-size the card.** Not everything needs acceptance criteria. Match the card detail to the task complexity.

## Process

### Step 1: Listen and Extract

Parse the user's input for:

1. **Action items** — things someone needs to do
2. **Owners** — who's responsible (may be unnamed)
3. **Status signals** — "in progress", "waiting on", "blocked by", "done"
4. **Decision context** — "we discussed X but decided Y because Z"
5. **Dependencies** — "need X before we can Y"
6. **Spikes/unknowns** — "we need to figure out how to..."

Don't force structure that isn't there. If the user said "fix the button," the card is "fix the button" — not a three-paragraph user story.

### Step 2: Validate with INVEST

Quick mental check on each extracted task. Don't lecture the user about INVEST — just use it to catch problems:

| Criterion | Check | If it fails |
|-----------|-------|-------------|
| **Independent** | Can this be done without finishing another task first? | Flag the dependency, don't block creation |
| **Negotiable** | Is the approach locked or flexible? | Note constraints if mentioned |
| **Valuable** | Does completing this deliver something useful? | If it's pure process overhead, ask if it's needed |
| **Estimable** | Could someone roughly size this? | If too vague, suggest a spike task first |
| **Small** | Can this be done in 1-2 weeks? | Suggest splitting only if obviously too large |
| **Testable** | Will you know when it's done? | Add a simple "done when" if ambiguous |

**Don't over-apply this.** A task like "add the logo" doesn't need INVEST analysis. Reserve it for tasks that feel vague or oversized.

### Step 3: Suggest Splits (Only When Needed)

Split a task only when it clearly has multiple independent pieces. Use these patterns:

- **Workflow steps** — "build and deploy X" → build X, deploy X
- **CRUD** — "manage users" → create, read, update, delete
- **Spike + execute** — "figure out how to do X, then do X" → research spike, implementation
- **By owner** — "Brandon and Geo do X" where each person's part is independent

**Don't split for the sake of splitting.** Three similar lines of work is fine as one card.

### Step 4: Write the Cards

Card content scales with complexity:

**Simple task** (clear, small, obvious owner):
```
**Owner:** [name]

[One sentence describing what to do.]
```

**Medium task** (some context or ambiguity):
```
**Owner:** [name]

[What to do and why.]

[Any decisions or context that would be lost between sessions.]
```

**Complex task** (multiple parts, dependencies, or unknowns):
```
**Owner:** [name]

## What
[Description of the work]

## Context
[Decisions made, things deprioritized and why, relevant background]

## Done when
- [Observable outcome 1]
- [Observable outcome 2]

## Dependencies
- [Blocked by / waiting on]
```

**Spike / research task:**
```
**Owner:** [name]

## Question
[What we need to figure out]

## Why it matters
[What decision or task depends on this answer]

## Done when
- We have enough information to [make decision / proceed with implementation]
```

### Step 5: Present for Confirmation

Show the user what you'll create **before creating it**. Group by owner if multiple people are involved, or by status if there are items in different states.

**Max 4 tasks per group.** If there are more, cluster them into named groups.

For each task, show:
- Title
- Owner
- Column (To Do / In Progress / On Hold)
- One-line summary of what's in the card

End with: **"Validate — anything to change, add, or drop before I create these?"**

### Step 6: Create and Organize

After confirmation:
1. Create all cards on the board
2. Move items to the correct column based on status signals
3. Report back with a summary of what was created

**FYI format:** "Created X tasks. Y in To Do, Z in Progress, W on Hold. Board is up to date."

## Handling Updates to Existing Boards

When the user wants to modify existing items:

1. **Pull current board state** — `get-board-info` first so you know what's already there
2. **Match updates to existing cards** — don't create duplicates
3. **Confirm deletions** — if something sounds like it replaces an existing card, confirm before deleting the old one
4. **Preserve context** — when updating a card, keep existing context and append new information

## Column Mapping

Map status signals from conversation to columns:

| Signal | Column |
|--------|--------|
| No status mentioned | To Do |
| "working on", "in progress", "started" | In Progress |
| "waiting on", "blocked", "need X first" | On Hold |
| "done", "finished", "shipped" | Done (only if user confirms) |

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Create cards without confirming | Present the list, wait for approval |
| Add acceptance criteria to every card | Scale detail to complexity |
| Split simple tasks into sub-tasks | Keep it as one card |
| Invent tasks the user didn't mention | Only extract what was said |
| Drop decision context from cards | Capture why, not just what |
| Assume owner when not stated | Ask, or mark as unassigned |
