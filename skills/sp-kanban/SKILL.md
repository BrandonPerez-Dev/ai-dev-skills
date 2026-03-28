---
name: sp-kanban
description: Manage tasks on Brandon's Super Productivity kanban board. Understands SP's tag-based columns, macro task sizing for AI-assisted development, and the full MCP tool set. Use when creating, organizing, or discussing tasks and project work.
allowed-tools:
  - mcp__super-productivity__get_tasks
  - mcp__super-productivity__create_task
  - mcp__super-productivity__update_task
  - mcp__super-productivity__complete_task
  - mcp__super-productivity__get_projects
  - mcp__super-productivity__create_project
  - mcp__super-productivity__get_tags
  - mcp__super-productivity__create_tag
  - mcp__super-productivity__add_tag_to_task
  - mcp__super-productivity__remove_tag_from_task
---

# Super Productivity Kanban

Manage Brandon's personal task board in Super Productivity via MCP.

## How SP Kanban Works

SP's kanban board is **tag-driven**. Columns are filtered views — a task appears in a column because it has the right tag. Moving a task between columns means changing its tags.

**Key operations:**
- **Move task to a column:** `add_tag_to_task` with that column's tag ID
- **Remove from a column:** `remove_tag_from_task`
- **Mark done:** `complete_task` (not a tag — uses `isDone`)

Always `get_tags` first to discover what columns/tags exist before trying to move tasks.

## Organization Model

- **Projects** = workstreams (e.g., "Google Drive MCP Server", "Trades AI Interface")
- **Tags** = kanban columns / status markers (e.g., "in-progress", "blocked")
- **Parent tasks** = features or macro work items visible on the board
- **Subtasks** = implementation steps nested under a parent (use `parent_id` on `create_task`)
- **Notes** = specs, context, acceptance criteria — lives on the task, not as separate cards

## Task Sizing for AI-Assisted Work

Brandon works with AI agents that can implement large chunks in a single session. The board should reflect **what he's thinking about**, not every implementation step.

**Right-sized card (board-level):**
- "Build Google Drive MCP Server" — a feature or project milestone
- "Email integration — send and receive" — a capability to deliver
- "Spike: QuickBooks integration" — a question to answer

**Too granular for the board:**
- "Create TokenStorage interface" — this is a subtask or a line in the notes
- "Write unit tests for OAuth module" — implementation detail
- "Add .gitignore" — not a card

**Rule of thumb:** If an AI agent could finish it as part of a larger task in one session, it's a subtask or a note — not a board card.

### When to use subtasks vs. notes

**Subtasks** (create with `parent_id`): Discrete steps that benefit from individual completion tracking. Use when you want to check things off as you go — e.g., "Set up OAuth", "Implement file tools", "Write README".

**Notes** (put in parent task `notes` field): Context, specs, acceptance criteria, decisions, file lists. Use for information that guides work but isn't independently completable — e.g., architecture decisions, API schemas, "we chose X because Y".

## Process

### Adding new work

1. `get_projects` — find the right project (or create one)
2. `get_tags` — discover existing column tags
3. Create a **macro task** in the project with rich notes containing specs/context
4. Optionally create **subtasks** under it for trackable milestones
5. Tag it for the right column if not just "To Do" (default)

### Reorganizing the board

1. `get_tasks` — see everything
2. Identify tasks that are too granular → consolidate into parent + subtasks
3. Confirm changes with the user before modifying
4. Move tasks between columns via `add_tag_to_task` / `remove_tag_from_task`

### Extracting tasks from conversation

Follow the same principles as kanban-breakdown but target SP:

1. **Extract, don't invent** — only create tasks the user mentioned
2. **Capture the why** — decisions and context go in notes
3. **Confirm before creating** — always present the plan first
4. **Scale detail to complexity** — simple tasks get a title and one-line note, complex ones get structured notes

## Card Templates

**Feature / macro task:**
```
Title: [Capability to deliver]
Notes:
## What
[Description]

## Context
[Decisions, trade-offs, relevant background]

## Done when
- [Observable outcome]
```

**Spike / research:**
```
Title: Spike: [Question to answer]
Notes:
## Question
[What we need to figure out]

## Why it matters
[What depends on this answer]

## Done when
- [We can make a decision / proceed]
```

**Simple task:**
```
Title: [What to do]
Notes: [One line of context if needed]
```

## Anti-Patterns

| Don't | Do Instead |
|-------|-----------|
| Create 12 cards for one feature | Create 1 parent + subtasks if needed |
| Put implementation steps as board cards | Put them as subtasks or in notes |
| Create cards without confirming | Present the list, get approval first |
| Guess at tag IDs | Always `get_tags` first |
| Duplicate work across cards | Consolidate into parent tasks |
