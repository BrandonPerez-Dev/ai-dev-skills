
---
name: ship
description: Review and delivery phase — verification gate, build summary, then the user chooses how to finish (merge, PR, keep working, or discard), and the cycle is logged to MLflow. ALWAYS invoke when a build completes its slices, when the user says "ship it" / "let's merge" / "wrap this up", or before delivering any completed feature. Do not merge or PR completed build work without it.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Skill
---

# Ship

Shipping is a decision, not a formality. The user reviews the completed work, chooses how to deliver it, and you execute their choice. Never auto-ship.

<HARD-GATE>
Run the full verification gate before presenting options. Broken work is not ready to ship — go back to build.
</HARD-GATE>

## When to Use

- After the build skill completes all vertical slices
- After all tests pass, types check, lint is clean

## Process

### 1. Final Simplify

Invoke **refactor** on the full set of changes (all verticals). This is the final polish pass — catching cross-vertical redundancy, naming inconsistencies, or patterns that emerged during build that can now be consolidated. Commit any changes: `refactor(scope): final cleanup`.

If build already ran refactor after each vertical (which it should), this pass is typically light. Skip if the diff is empty.

### 2. Verification Gate

Invoke **verification** to confirm everything works:
- All integration tests pass
- All unit tests pass
- TypeScript compiles clean (or equivalent type check)
- Linter clean
- The feature works (run the server, try it)

**If verification fails, stop.** Go back to build. Don't present options.

### 3. Present Summary

Show the user what was built:
- Completed vertical slices (what each delivers)
- Key files changed/created
- Test results (integration + unit counts)
- Design doc deviations (what changed from the plan and why)

Keep it concise — they've been in the loop during build.

### 4. User Decision

Present the completion options. **Wait for the user to choose — never auto-select.**

```
Tests pass. Work is ready. How would you like to finish?

1. Push & create PR — push branch, open PR for team review
2. Merge locally    — squash/merge into base branch, delete feature branch
3. Keep working     — leave branch as-is, continue later
4. Discard          — delete branch and all changes
```

| Option | Commits | Pushes | Creates PR | Cleans Up |
|--------|:---:|:---:|:---:|:---:|
| 1. Push & PR | Yes | Yes | Yes | No |
| 2. Merge locally | Yes | No | No | Yes |
| 3. Keep working | No | No | No | No |
| 4. Discard | No | No | No | Yes |

### 5. Execute Choice

#### Option 1: Push & Create PR

Invoke **commit-and-pr** to handle staging, commit messages, push, and PR creation.

**Keep the worktree alive** — the user may need it for review feedback.

Return the PR URL to the user.

#### Option 2: Merge Locally

Invoke **commit-and-pr** for staging and commit messages, then:

```bash
# Determine base branch
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'

# Merge into base branch
git checkout <base-branch>
git merge --squash <feature-branch>
git commit -m "feat(scope): description"

# Delete feature branch
git branch -d <feature-branch>

# Verify merge is clean — use the project's test command
```

Then clean up worktree if applicable (Step 6).

#### Option 3: Keep Working

Report the current state:

```
Branch: <feature-branch>
Location: <worktree-path or repo path>
Status: N files changed, M commits ahead of <base-branch>

Resume anytime with: cd <path>
```

No commits, no push, no cleanup.

#### Option 4: Discard

**This is destructive. Require explicit confirmation.**

```
This will permanently delete:
  - Branch: <feature-branch>
  - Commits: N commits with M files changed
  - Worktree: <path> (if applicable)

Type "discard" to confirm:
```

Only proceed after explicit confirmation. Then:

```bash
git checkout <base-branch>
git branch -D <feature-branch>
```

Then clean up worktree if applicable (Step 6).

### 6. Worktree Cleanup (if applicable)

For Options 2 and 4 only — Options 1 and 3 keep the worktree alive.

```bash
cd <main-worktree-path>
git worktree remove <worktree-path>   # NEVER rm -rf
git worktree list                      # Verify cleanup
```

### 7. Log the Cycle (Options 1 and 2)

Every shipped slice is a data point correlating dev-skill versions with real outcomes — the substrate for evolving the skills over time. After push/merge, log it:

```bash
python3 ~/dev-config/ai-workflow-config/skills/skill-creator/scripts/log_dev_cycle.py \
  --project <repo-name> --slice <spec-name> \
  --spec spec/<name>.md \
  --iterations-to-green <N red→green build loops> \
  --review-findings <count from code-review, if run> \
  --notes "<one line: anything that fought you this cycle>"
```

Capture iterations-to-green from the build phase (how many runs before the locked tests passed); skip any metric you didn't measure rather than guessing. If a dev skill misbehaved this cycle, the note is the seed of its next eval case — record it while it's fresh.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **Ship without verification** | Broken code gets merged or PR'd | Hard gate: verification first, always |
| **Auto-selecting an option** | User didn't consent to the action | Present all options, wait for explicit choice |
| **Skipping the summary** | User can't make an informed decision | Show what was built before asking how to finish |
| **"Tests are probably passing"** | Probably is not evidence | Run them. Every time. |
| **Force push to shared branch** | Overwrites teammates' work | Only force push your own feature branches after rebase |
| **rm -rf a worktree** | Orphaned metadata causes confusing errors | Always `git worktree remove` |
| **Discard without confirmation** | Permanent data loss | Require typed confirmation for destructive actions |

## Guidelines

- **Verification before options.** The gate is non-negotiable.
- **User chooses, you execute.** Never auto-select a delivery method.
- **Delegate to commit-and-pr.** Don't duplicate commit/PR logic — invoke the skill.
- **Destructive actions need confirmation.** Option 4 requires explicit typed confirmation.
