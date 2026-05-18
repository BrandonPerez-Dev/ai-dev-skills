
---
name: commit-and-pr
description: >-
  Stage changes, create commits, push, and create pull requests. Use when ready to
  commit or create a PR. Teaches surgical staging, meaningful commit messages, and
  reviewable PRs. Prevents common git mistakes: committing secrets, skipping hooks,
  force-pushing shared branches, giant unreviewable PRs.
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Skill
  - AskUserQuestion
---

# Commit and PR

Every commit tells a story. Every PR is a contract for review. Make both worth reading.

<HARD-GATE>
Read the diff before committing. Never stage blindly — `git add .` without reviewing what changed is how secrets get committed, generated files get tracked, and debug code ships. Run `git diff --stat` and `git diff` first.
</HARD-GATE>

## Commit Flow

### 1. Review What Changed

```bash
git status
git diff --stat
git diff
```

Before staging anything, understand the full picture:
- **How many files changed?** If 20+ files, consider whether this should be multiple commits.
- **What types of changes?** Feature code, tests, config, docs — these may be separate commits.
- **Anything unexpected?** Files you didn't intend to change, debug code left in, generated files.

### 2. Check for Problems

Scan the diff for things that should NOT be committed:

| Problem | How to Spot | Fix |
|---------|------------|-----|
| **Secrets/credentials** | `.env`, API keys, tokens, passwords in code | Add to `.gitignore`, remove from staging |
| **Generated files** | `node_modules/`, `dist/`, `.next/`, coverage reports | Add to `.gitignore` |
| **Debug code** | `console.log`, `debugger`, hardcoded test values | Remove before staging |
| **Large binaries** | Images, videos, compiled files over 1MB | Use Git LFS or exclude |
| **Merge conflict markers** | `<<<<<<<`, `=======`, `>>>>>>>` | Resolve conflicts first |

### 3. Stage Surgically

Stage specific files by name. Group related changes into logical commits.

```bash
# Stage specific files
git add src/tools/new-tool.ts src/server.ts

# Stage parts of a file (interactive)
git add -p src/server.ts
```

**Never use `git add .` or `git add -A`** unless you've verified every change should go together and nothing unwanted is in the working directory.

### 4. Write the Commit Message

**Format:** Conventional commits.

```bash
git commit -m "$(cat <<'EOF'
type(scope): short description (imperative mood)

Why this change was made, not what the code does.
The diff shows what changed — the message explains why.

- Bullet points for multiple related changes
- Reference issues: Fixes #123

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

**Types:**

| Type | When |
|------|------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change that doesn't fix a bug or add a feature |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Build process, dependencies, tooling |
| `ci` | CI/CD configuration |

**Good vs bad messages:**

| Bad | Good |
|-----|------|
| `fix stuff` | `fix(auth): prevent token refresh race condition` |
| `update server.ts` | `feat(tools): add detail_level param to reduce token usage` |
| `changes` | `refactor(provider): extract mapper to separate module for testability` |
| `WIP` | Don't commit WIP — finish or stash |

**Rules:**
- Subject line: imperative mood ("add", not "added" or "adds"), under 72 chars
- Body: explain WHY, not WHAT. The diff shows what.
- Reference issues when applicable: `Fixes #123`, `Closes #456`
- One logical change per commit. Two unrelated fixes = two commits.

### 5. Handle Pre-Commit Hook Failures

If a pre-commit hook fails:

1. **Read the error.** The hook is telling you something — linting failure, type error, test failure.
2. **Fix the issue.** Don't skip the hook.
3. **Stage the fix.**
4. **Create a NEW commit.** Do NOT use `--amend` — the original commit didn't happen, so amending would modify the *previous* commit.
5. **NEVER use `--no-verify`** unless the user explicitly asks. Skipping hooks hides real problems.

### 6. Verify

After committing:
```bash
git log --oneline -3    # Confirm the commit looks right
git status              # Confirm working directory is clean (or only has expected unstaged changes)
```

## PR Flow

### 1. Assess PR Readiness

Before creating a PR, invoke **verification** to confirm:

- [ ] All tests pass locally
- [ ] Types check, lint is clean
- [ ] No secrets or debug code in the diff
- [ ] All commits have meaningful messages
- [ ] Changes are focused — one concern per PR

**Size check:** `git diff --stat main...HEAD | tail -1`

| Lines Changed | Verdict |
|--------------|---------|
| < 200 | Good — easy to review |
| 200-400 | Acceptable — reviewer can handle it |
| 400-800 | Large — consider splitting if logically separable |
| 800+ | Too large — split into smaller PRs unless it's a single coherent change (migration, generated code) |

If the PR is too large, ask the user: "This PR is ~X lines. Want to split it, or is it one coherent change?"

### 2. Push

```bash
git fetch origin
git rebase origin/main    # Rebase onto latest main (or merge if user prefers)
git push -u origin HEAD
```

If push is rejected (remote has changes):
- `git pull --rebase origin main` — rebase your changes on top
- Resolve any conflicts
- Push again

**Never force push to main/master.** For feature branches, only force push if you've rebased and the branch is yours alone.

### 3. Create PR

```bash
gh pr create --title "type(scope): description" --body "$(cat <<'EOF'
## Summary
- [What this PR does and why, 1-3 bullets]

## Changes
- [Specific changes, grouped by concern]

## Test Plan
- [ ] [How to verify this works]

## Notes for Reviewer
- [Anything the reviewer should know — areas of uncertainty, decisions to validate, files to focus on]

---
Generated with Claude Code
EOF
)"
```

**PR title:** Same format as commit messages. Under 72 chars.

**PR description must include:**
- **Summary:** What and why (not how — the code shows how)
- **Test plan:** How the reviewer can verify correctness
- **Notes for reviewer:** Where to focus attention, what trade-offs were made

**Options:**
- `--draft` — work in progress, not ready for review
- `--reviewer @username` — request specific reviewer
- `--base develop` — target branch if not main
- `--label "type: bug"` — add labels

### 4. Return the PR URL

Always show the user the PR URL when done so they can review it in the browser.

## Decision Guide

| Situation | Action |
|-----------|--------|
| Multiple unrelated changes in working directory | Stage and commit separately — one logical change per commit |
| Change touches tests + implementation | Usually one commit — tests and code for the same feature belong together |
| Pre-commit hook fails | Fix the issue. Never `--no-verify`. |
| PR is 800+ lines | Ask user if it can be split. If not, note in PR description why it's large. |
| Unsure about target branch | Ask the user. Don't assume `main`. |
| Merge conflicts during rebase | Resolve them. Don't `--skip` or `--abort` without asking. |
| Commit already pushed, need to change | New commit with the fix, not `--amend` (unless user explicitly asks to amend + force push) |

## Anti-Patterns

| Anti-Pattern | What Happens | Instead |
|--------------|-------------|---------|
| `git add .` | Secrets, debug code, generated files get committed | Stage specific files by name |
| `--no-verify` | Real lint/type/test errors ship | Fix the hook failure |
| `--amend` after hook failure | Modifies the wrong commit (previous one, not the failed one) | New commit — the failed commit never happened |
| Giant PRs | Nobody reviews 1000 lines carefully | Split into focused PRs |
| "fix stuff" messages | Future you can't understand the history | Explain WHY in the message body |
| Force push to shared branch | Overwrites teammates' work | Only force push your own feature branches after rebase |

## Guidelines

- **Read the diff first.** The hard gate is non-negotiable. Understand what you're committing before you commit it.
- **One logical change per commit.** A feature + its tests = one commit. A feature + an unrelated fix = two commits.
- **Messages explain WHY.** The diff shows what changed. The message explains why it was necessary.
- **Stage surgically.** Name the files. Review the diff. Don't blanket-add.
- **Never skip hooks.** Pre-commit hooks exist to catch problems. Fix the problem, don't bypass the check.
- **PRs are for reviewers.** Write the description for the person reviewing, not for yourself. What should they look at? What decisions did you make?
