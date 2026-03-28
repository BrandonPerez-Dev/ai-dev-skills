---
name: git-ops
description: >-
  Git operations beyond staging, committing, and PR creation. Use for: pushing
  code, rebasing, merging branches, resolving merge conflicts, setting up remotes,
  branch management (create/delete/rename), recovering from bad state (reflog,
  detached HEAD, aborted rebase), validating git state before acting, force-push
  decisions, and any time git feels wrong or broken. NOT for staging, writing
  commit messages, or creating PRs — delegate those to commit-and-pr.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Skill
  - AskUserQuestion
---

# Git Ops

Verify state before mutation. Every time.

<HARD-GATE>
Before ANY git mutation (push, rebase, reset, merge, checkout with changes, branch delete), run `git status`, `git branch --show-current`, and `git remote -v`. The 3 seconds this takes prevents the 3-hour recovery. If you find a lock file (`.git/index.lock`), a merge in progress (`.git/MERGE_HEAD`), or a rebase in progress (`.git/rebase-merge/`) — resolve that state before doing anything else.
</HARD-GATE>

<HARD-GATE>
NEVER run interactive git commands. `git rebase -i`, `git add -i`, `git commit` without `-m`, and `git mergetool` expect stdin/editor input that hangs the session and can leave lock files. Use non-interactive equivalents listed in the AI Safety section.
</HARD-GATE>

<delegation>

**Skill boundaries — do not duplicate these:**

| Task | Owner |
|------|-------|
| Staging files, writing commit messages, creating PRs, basic push-before-PR | **commit-and-pr** |
| Parallel branch isolation via worktrees | **git-worktrees** |
| Verification before shipping | **verification** |
| Delivery decision (merge/PR/discard) | **ship** |
| Everything else in git | **This skill** |

</delegation>

## Push Safety

This is where code leaves your machine. The cross-check below catches wrong-repo pushes — a failure mode unique to AI agents working across multiple repos.

### Pre-Push Cross-Check

Before every push, verify these three things agree:

```
1. PROJECT IDENTITY — all three should be obviously related:
   - Project manifest name (package.json "name", Cargo.toml, go.mod)
   - Directory name
   - Remote URL repo name
   If they disagree (e.g., package.json says "agent-platform-ui"
   but remote is "incu-agent-platform"), STOP and investigate.

2. REMOTE DESTINATION
   - git remote -v → correct org and repo
   - Confirm repo exists: gh repo view <org/repo>

3. OUTBOUND COMMITS
   - git log origin/<branch>..HEAD --oneline
   - Do these commits belong in THIS repo?
```

### Push Execution

```bash
git fetch origin
# Check if behind — if yes, rebase or merge first
git log HEAD..origin/main --oneline
# Review outbound commits
git log origin/main..HEAD --oneline
# Push
git push -u origin HEAD
```

### Remote Setup (New Repos)

Verify project identity BEFORE adding the remote. After adding, run `git remote -v` and cross-check against the project manifest. Then push.

## Merge vs Rebase

### The Golden Rule

**Never rebase commits that have been pushed to a shared branch.** Rebase rewrites SHAs — anyone who pulled the originals must force-reconcile.

### Decision

| Situation | Use | Why |
|-----------|-----|-----|
| Update feature branch with latest main | **Rebase** | Linear history; your commits aren't public yet |
| Merge feature into main (via PR) | **Merge** | Preserves PR as merge point |
| Shared branch, multiple contributors | **Merge** | Rebase rewrites their commits |
| Clean up local commits before push | **Soft reset** + new commit | Non-interactive squash (see below) |
| Diverged branches, many conflicts | **Merge** | Rebase replays each commit — multiplies conflict resolution |
| Undo a merge | **Revert** the merge commit | Never rebase away merges |

### Safe Rebase

```bash
git branch --show-current    # Confirm you're on feature branch, NOT main
git fetch origin
git rebase origin/main
# If conflicts: resolve, git add <files>, git rebase --continue
# If it's a mess: git rebase --abort (returns to pre-rebase state)
```

### Non-Interactive Squash

Since `git rebase -i` hangs in AI sessions, use these:

```bash
# Squash last N commits
git reset --soft HEAD~N
git commit -m "combined message"

# Amend last commit with new staged changes
git add <files>
git commit --amend --no-edit

# Autosquash with fixup commits
git commit --fixup=<target-sha>
GIT_SEQUENCE_EDITOR=: git rebase --autosquash origin/main
```

## Conflict Resolution

### Process

```bash
# 1. See which files conflict
git status    # "both modified" entries

# 2. Read each conflicted file — understand BOTH sides before choosing
# 3. Edit to correct final state, remove ALL conflict markers
# 4. Stage resolved files
git add <resolved-file>

# 5. Continue
git merge --continue    # or git rebase --continue

# 6. Run tests — semantic conflicts won't show as markers
```

### Bulk Strategy Selection

```bash
# Accept all theirs (your changes are outdated)
git checkout --theirs <file> && git add <file>

# Accept all ours (their changes should be discarded)
git checkout --ours <file> && git add <file>

# Auto-resolve entire merge favoring one side
git merge -X theirs <branch>
git merge -X ours <branch>
```

### Rerere

```bash
git config rerere.enabled true
```

Git remembers how you resolved each conflict and auto-applies the same resolution on repeated rebases. Enable this in every repo with long-running branches.

## Recovery Patterns

### Wrong Branch Commits

```bash
git log --oneline -N                # Note the SHAs
git checkout -b correct-branch      # Branch from current position
git checkout wrong-branch
git reset --soft HEAD~N             # Undo commits, keep changes staged
git restore --staged .              # Unstage
git stash                           # Park the changes
```

### Undo a Pushed Commit

```bash
# Safe: creates a new commit that undoes the change
git revert <sha>
git push
```

Do NOT use reset + force-push on shared branches. For solo branches only, and only with `--force-with-lease` (see approval gates below).

### Reflog Recovery ("Lost" Commits)

The reflog tracks every HEAD movement for ~30 days. Commits are almost never truly lost.

```bash
git reflog --oneline -20
git cherry-pick <sha>       # Apply to current branch
# or: git branch recovery <sha>   # Recover as new branch
```

### Bad Rebase State

```bash
# Mid-rebase and it's a mess:
git rebase --abort    # Returns to pre-rebase state

# Already completed the rebase and want to undo:
git reflog            # Find pre-rebase SHA
git reset --hard <pre-rebase-sha>    # Local only!
```

### Detached HEAD

```bash
git symbolic-ref -q HEAD || echo "DETACHED HEAD"
# If uncommitted work: stash, checkout branch, pop
# If committed in detached state: git branch save-my-work, then checkout and merge
```

## AI-Specific Safety

<approval-required>

**Always ask the user before running these.** Show what will happen (dry-run output) and why.

| Command | Risk | Show First |
|---------|------|------------|
| `git push --force-with-lease` | Overwrites remote history (but aborts if remote has unseen commits) | `git log origin/branch..HEAD` |
| `git reset --hard` | Destroys uncommitted work permanently (reflog only tracks commits) | `git status` + `git diff --stat` |
| `git clean -f` | Deletes untracked files permanently | `git clean -n` (dry run) |
| `git branch -D` | Force-deletes unmerged branch | `git log main..branch --oneline` |
| `git checkout .` / `git restore .` | Discards all unstaged changes | `git diff --stat` |

Never use `git push --force` — always `--force-with-lease`, which aborts if the remote has commits you haven't fetched.

</approval-required>

### Non-Interactive Alternatives

| Command That Hangs | Why | Use Instead |
|-------------------|-----|-------------|
| `git rebase -i` | Opens editor | `git reset --soft` + new commit, or `GIT_SEQUENCE_EDITOR=:` |
| `git add -i` / `git add -p` | Interactive staging | `git add <specific-files>` |
| `git commit` (no `-m`) | Opens editor | `git commit -m "..."` with heredoc |
| `git mergetool` | Opens visual diff | Edit conflict markers directly |
| `git stash pop` (with conflicts) | Waits for input | `git stash apply`, resolve, then `git stash drop` |

### Timeout Recovery

If a git command times out, it may leave state artifacts:

1. `.git/index.lock` — remove if no git process is running (`ps aux | grep git`)
2. `.git/rebase-merge/` — `git rebase --abort`
3. `.git/MERGE_HEAD` — `git merge --abort`
4. Run `git status` to assess

## Bias Guards

| Thought | Reality | Do Instead |
|---------|---------|------------|
| "I'll just force-push, it's my branch" | Someone may have pulled it | Ask the user; use `--force-with-lease` |
| "The remote is probably fine" | You may be in the wrong repo | Cross-check `git remote -v` against project manifest |
| "I'll skip the state check" | Lock files, in-progress ops, detached HEAD | Always check. 3 seconds. |
| "Reset --hard is fine, reflog has it" | Uncommitted work is gone forever | Stash or commit WIP first |
| "The conflict is obvious, take theirs" | Semantic conflicts hide behind clean markers | Read both sides, test after resolving |

Follow the communication-protocol skill for all user-facing output and interaction.

## Guidelines

- **State before action.** The 3-second trinity (status, branch, remote) prevents the 3-hour recovery.
- **Cross-check identity before pushing.** Package name, directory name, remote URL must agree. This is the #1 AI-specific push failure.
- **Rebase local, merge shared.** If anyone else has seen the commits, don't rebase them.
- **Recovery is always possible.** Reflog keeps 30 days of history. Don't panic — find the SHA.
- **Ask before destroying.** Force-push, reset --hard, clean -f, branch -D are one-way doors. Show dry-run output, get approval.
- **Delegate staging/commits/PRs.** Those belong to commit-and-pr. This skill handles everything else.
