
---
name: git-worktrees
description: Creating isolated workspaces with git worktrees. Use when you need parallel branches, isolated feature work, or subagent isolation without context-switching.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
---

# Git Worktrees

Isolated workspaces for parallel work. No stashing, no context-switching, no lost state.

<HARD-GATE>
Always use `git worktree remove` for cleanup. Never `rm -rf` a worktree directory — it leaves orphaned metadata in `.git/worktrees/` that causes confusing errors later.
</HARD-GATE>

## When to Use

Use the decision framework:

```
Need to work on two things simultaneously?
├─ Yes, need both codebases available at once? → WORKTREE
├─ Yes, but switching back and forth is fine? → BRANCH
└─ No, just saving context temporarily? → STASH

Need isolation for parallel agents? → WORKTREE (isolation: worktree)
Need to test a fix without losing current work? → WORKTREE
Need to review a PR while mid-feature? → WORKTREE
```

| Scenario | Use Worktree | Use Branch | Use Stash |
|----------|:---:|:---:|:---:|
| Parallel feature + bugfix | X | | |
| Quick one-file fix | | X | |
| Save WIP for 5 minutes | | | X |
| PR review while coding | X | | |
| Parallel agent isolation | X | | |
| Long-running experiment | X | | |
| Compare two approaches | X | | |

## Creating a Worktree

### Using Claude Code's Built-In Tool

Claude Code has a native `EnterWorktree` tool:

```
claude --worktree feature-auth       # Named worktree
claude --worktree                    # Auto-generated name
```

**Default location:** `.claude/worktrees/<name>/`
**Branch naming:** `worktree-<name>`
**Auto-cleanup:** Removes automatically if no changes were made on exit.

### Using Git Directly

```bash
# Create worktree with new branch
git worktree add ../feature-auth -b feature/auth

# Create worktree from existing branch
git worktree add ../bugfix-123 bugfix/123

# Create worktree from a specific commit
git worktree add ../experiment abc1234

# List all worktrees
git worktree list
```

### Post-Creation Setup

Worktrees share `.git` but NOT:
- `node_modules` / `vendor` / `venv`
- Build artifacts
- IDE settings (`.vscode/`, `.idea/`)
- Environment files (`.env`, `.env.local`)

**After creating a worktree, always run setup:**

```bash
cd <worktree-path>

# Node.js
npm install  # or yarn / pnpm / bun install

# Python
pip install -e .  # or poetry install

# Rust
cargo build

# Go
go mod download
```

**Copy environment files if needed:**

```bash
cp ../<main-repo>/.env .env
```

### Safety Checks

Before creating:

```
1. □ Verify the worktree directory will be gitignored
   (check .gitignore for the parent directory pattern)
2. □ List existing worktrees: git worktree list
   (avoid creating duplicates)
3. □ Confirm the branch name is available
   (git won't allow the same branch in two worktrees)
```

## Cleanup

This is where most people get burned. Follow these rules exactly.

### Normal Removal

```bash
# Always use git worktree remove — NEVER rm -rf
git worktree remove <path>

# If changes exist and you want to discard them
git worktree remove --force <path>

# Delete the branch after removing the worktree (if done with it)
git branch -d feature/auth
```

### Orphaned Worktree Recovery

If someone (or a crashed process) deleted the worktree directory without using `git worktree remove`:

```bash
# Check for orphaned references
git worktree list
# You'll see entries pointing to non-existent directories

# Clean up orphaned metadata
git worktree prune

# Verify
git worktree list
```

### Lock/Unlock (External Drives)

If the worktree is on a removable drive or network mount:

```bash
# Lock before unmounting — prevents git from pruning it
git worktree lock <path> --reason "On external drive"

# Unlock when remounted
git worktree unlock <path>
```

### Cleanup Checklist

When done with a worktree:

```
1. □ Commit or stash any remaining changes
2. □ Push the branch if it needs to be preserved
3. □ git worktree remove <path> (not rm -rf!)
4. □ git branch -d <branch> (if branch is merged/done)
5. □ Verify: git worktree list (should not show removed worktree)
```

## Parallel Agent Patterns

### Subagent Isolation

The Claude Code Task tool supports worktree isolation:

```
Task tool with isolation: "worktree"
```

Each agent gets its own worktree automatically. Changes are isolated. If the agent makes changes, the worktree path and branch are returned in the result.

**Use this when:** Parallel agents need to modify the same files without conflicts.

### Parallel Implementation (Compare Approaches)

```
Main Agent
  ├─ dispatch Agent 1 (isolation: worktree) → Approach A
  ├─ dispatch Agent 2 (isolation: worktree) → Approach B

  [wait for both]

  Review both approaches → pick winner or merge best parts
  Clean up losing worktree
```

### Feature + Bugfix Parallel

```
Main worktree: continue feature work
  └─ dispatch Agent (isolation: worktree) → fix bug on separate branch

  [agent returns with fix]

  Review fix → merge bugfix branch → continue feature
```

## Common Pitfalls

| Pitfall | What Happens | Prevention |
|---------|-------------|------------|
| **rm -rf instead of git worktree remove** | Orphaned metadata in `.git/worktrees/` | Always use `git worktree remove` |
| **Same branch in two worktrees** | `fatal: 'branch' already checked out` | Create a new branch: `git worktree add <path> -b new-branch` |
| **Missing dependencies** | Build/test failures in new worktree | Run install command immediately after creation |
| **Shared stash confusion** | Stash entries visible across ALL worktrees | Use branches or commits for WIP, not stash across worktrees |
| **Forgetting cleanup** | Disk space waste, branch clutter | Check `git worktree list` periodically |
| **Shared git hooks** | Hooks with relative paths break in worktrees | Use absolute paths or `core.hooksPath` |

## Troubleshooting

### "fatal: 'branch' is already checked out"

Git prevents the same branch from being checked out in two worktrees.

```bash
# Option A: Create a new branch from the target
git worktree add <path> -b my-branch origin/target-branch

# Option B: Check what's using the branch
git worktree list  # Find which worktree has it
```

### "fatal: is a linked worktree" (during prune)

The worktree directory still exists. Remove it properly first:

```bash
git worktree remove <path>
# Then prune if needed
git worktree prune
```

### Worktree shows in list but directory is gone

```bash
git worktree prune  # Cleans up stale references
git worktree list   # Verify it's gone
```

## Guidelines

- **Worktrees for parallel work, branches for sequential work, stash for quick saves.** Use the decision framework, don't default to worktrees for everything.
- **Always `git worktree remove`, never `rm -rf`.** This is the single most common mistake. It leaves orphaned metadata that causes confusing errors later.
- **Run setup after creation.** Dependencies aren't shared between worktrees. Install immediately.
- **Clean up when done.** `git worktree list` should only show active work. Remove what you're not using.
