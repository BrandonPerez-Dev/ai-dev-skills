---
name: chain-survey
description: >-
  L1 chain creator — Phase 1. Systematically surveys a target repository to
  extract language, build commands, test infrastructure, project structure,
  CI/CD, conventions, and patterns. Verifies commands by running them.
  Produces a structured survey document that downstream chain-* skills
  consume to generate repo-specific L2 agent chains.
when_to_use: >-
  Use as the first step of the L1 chain creator flow when setting up an
  autonomous agent chain for a new repo. Input is a path to the target repo
  (or a GitHub URL to clone). Do NOT use on repos that already have a
  complete L2 chain — use chain-verify to audit existing chains instead.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - Task
  - WebSearch
  - WebFetch
argument-hint: "[path/to/target-repo or github-url]"
effort: high
---

# Chain Survey

Read a repository systematically. Extract everything an autonomous agent chain needs to know. Verify by running, not guessing. Output a structured survey that chain-plan and chain-generate consume.

<HARD-GATE>
Do not write skills, CLAUDE.md, or chain config. This skill produces one
artifact: the survey document. chain-plan interprets it; chain-generate
writes from it.
</HARD-GATE>

<HARD-GATE>
Verify commands by running them. "The test command is cargo test" is a
guess until you've run `cargo test` and confirmed it works. A survey
built on guesses produces a chain built on guesses.
</HARD-GATE>

## Input

One of:
- **Repo path** — absolute path to a local repo
- **GitHub URL** — clone it first, then survey

If the repo doesn't exist locally, clone it and note the clone path in the survey.

## Process

### 0. Orient

Before extracting details, understand what kind of project this is:
1. Read the top-level directory listing
2. Read README.md (or equivalent)
3. Identify the primary language and build system from config files
4. Check if `.claude/` exists (existing agent setup)
5. Check if `context/` and `spec/` exist (existing knowledge layers)

Record a one-paragraph project summary. This frames all subsequent extraction.

### 1. Language & Runtime

| What | How to find | How to verify |
|---|---|---|
| Primary language | Config files: Cargo.toml, package.json, go.mod, pyproject.toml, etc. | File extensions match |
| Language version | Config files, CI config, tool-versions, .nvmrc, rust-toolchain.toml | Run version command (`rustc --version`, `node --version`, etc.) |
| Build system | Config files, Makefile, scripts/ | Run build command |
| Edition/standard | Language config (Rust edition, TypeScript target, etc.) | Config file value |

### 2. Build Commands

Find and **run** each command. Record exact output (success/failure, warnings, timing).

| Command | Where to find | Verification |
|---|---|---|
| Build | Config + Makefile + CI | Run it. Must succeed. |
| Test | Config + CI + test runner config | Run it. Record pass/fail count. |
| Lint | CI + config (.eslintrc, clippy.toml, etc.) | Run it. Record warning count. |
| Format check | CI + config | Run it. |
| Type check | CI + tsconfig, mypy.ini, etc. | Run it. |

If a command fails, record WHY — missing dependency, broken test, etc. The failure itself is survey data.

For large test suites, run a subset first (`cargo test --no-run`, `npm test -- --listTests`) to verify infrastructure without waiting for the full suite.

### 3. Test Infrastructure

Read 3-5 existing test files. Extract patterns, not just metadata.

| What | How |
|---|---|
| Test framework | Test config files, import statements in test files |
| Test runner | Scripts, CI config, package.json scripts |
| Naming convention | Existing test names — `test_*`, `it("should...")`, `When/Then`, etc. |
| File organization | Where test files live — alongside source? separate `tests/` dir? |
| Shared helpers | Common imports across test files, test utility modules |
| Fixture patterns | How tests set up data — factories, builders, files, env vars |
| Setup/teardown | beforeEach, afterEach, test containers, temp dirs |
| Container requirements | Docker, docker-compose, testcontainers usage |
| Integration test approach | How integration tests run — spawned process, HTTP client, in-process |

Record 2-3 representative test snippets (10-20 lines each) that show the dominant pattern.

### 4. Project Structure

```bash
# Get a clean view of project structure
find . -type f -not -path './.git/*' -not -path './target/*' -not -path './node_modules/*' | head -100
```

Extract:
- Source layout (src/, lib/, cmd/, crates/, packages/)
- Module organization (how code is grouped)
- Entry points (main, lib, bin)
- Crate/package/module boundaries
- Where new code would naturally go

### 5. CI/CD

| What | Where |
|---|---|
| CI system | .github/workflows/, .gitlab-ci.yml, Jenkinsfile, etc. |
| What runs on PR | CI config — which checks, which OS/versions |
| Required checks | Branch protection rules (if accessible via gh api) |
| Deploy pipeline | CI config, deploy scripts |
| CI secrets / env | CI config references (don't extract values) |

If no CI exists, record this as a gap — foundation skill will need to create it.

### 6. Existing .claude/ Setup

| What | Check |
|---|---|
| CLAUDE.md | Exists? Content? Build/test commands documented? |
| .claude/settings.json | Permissions, allowed tools |
| .claude/skills/ | Any existing skills? What do they do? |
| .claude/commands/ | Any existing commands? |

### 7. context/ and spec/ Docs

If they exist:
- List all files with one-line summaries
- Note the format conventions (frontmatter style, section structure)
- Note what topics are covered (architecture, testing, security, etc.)
- Check for gaps (architecture documented but not testing strategy? etc.)

If they don't exist, record "no existing knowledge layers" — chain-generate may bootstrap them.

### 8. Git Conventions

```bash
# Recent commit messages
git log --oneline -20

# Branch patterns
git branch -a | head -20

# Tags
git tag | tail -5
```

Extract:
- Commit message style (conventional commits? scope? imperative?)
- Branch naming (feature/, fix/, kebab-case?)
- PR conventions (if visible from merged PRs: `gh pr list --state merged --limit 5`)
- Release/tag pattern

### 9. Dependencies

| What | How |
|---|---|
| Key libraries | Lock file + config file — focus on the 5-10 most important |
| External services | Config files, env vars, connection strings (note service type, not credentials) |
| API clients | Import statements, SDK references |
| Database | Config, migration files, schema |

Don't catalog every transitive dependency. Focus on what shapes the architecture.

### 10. Code Conventions

Sample 3-5 source files (not tests). Extract:
- Error handling pattern (Result<T, E>, try/catch, anyhow, thiserror, custom)
- Module organization (one file per type? grouped by feature? by layer?)
- API style (builder pattern, struct literals, trait objects)
- Naming conventions (snake_case, camelCase, PascalCase — for functions, types, files)
- Documentation style (doc comments? inline? none?)

Record 1-2 representative code snippets (10-15 lines each).

### 11. Mock/Test Patterns

From the test files read in step 3, specifically extract:
- What's tested against real instances (database, queue, etc.)
- What's mocked and HOW (mock library, manual mocks, test doubles)
- Where the mock boundary sits (HTTP client? adapter interface? in-memory?)
- Container usage (testcontainers, docker-compose, etc.)

### 12. Security Posture

| What | How |
|---|---|
| Security docs | SECURITY.md, context/security.md, threat model docs |
| Credential handling | How secrets are loaded, vault integration, env vars |
| Sandbox/isolation | Namespace usage, container isolation, capability restrictions |
| Auth patterns | JWT, OAuth, API keys — how auth works in this project |
| Security-sensitive areas | Code that handles user input, network boundaries, file system access |

If the project has a security model documented in context/, summarize it. If not, note what appears security-relevant from the code.

## Output

Write the survey to `.claude/chain/survey.md` in the target repo.

### Survey Format

```markdown
# Chain Survey: [project-name]

> Date: YYYY-MM-DD
> Repo: [path or URL]
> Primary language: [language]

## Summary
[One paragraph: what this project is, what it does, current state]

## Language & Runtime
- **Language:** [name] [version]
- **Build system:** [tool]
- **Edition/standard:** [value]

## Commands
| Command | Invocation | Status | Notes |
|---|---|---|---|
| Build | `cargo build --workspace` | ✅ | 23s, 0 warnings |
| Test | `cargo test --workspace` | ✅ | 45 tests, 0 failures |
| Lint | `cargo clippy --workspace` | ⚠️ | 3 warnings |
| Format | `cargo fmt --check` | ✅ | — |

## Test Infrastructure
- **Framework:** [name]
- **Runner:** [command]
- **Naming:** [convention]
- **File organization:** [pattern]
- **Helpers:** [list of shared test utilities]
- **Fixtures:** [pattern]
- **Integration approach:** [how integration tests work]
- **Containers:** [yes/no, what kind]

### Representative test (excerpt)
```[lang]
[10-20 lines of a typical test]
` ` `

## Project Structure
[Directory tree with annotations]

## CI/CD
- **System:** [GitHub Actions / GitLab CI / none]
- **PR checks:** [list]
- **Required checks:** [list or "unknown"]
- **Gaps:** [what's missing]

## Existing .claude/ Setup
- **CLAUDE.md:** [exists/missing, summary if exists]
- **Skills:** [list or "none"]
- **Settings:** [summary or "default"]

## Knowledge Layers
### context/
[List of files with one-line summaries, or "does not exist"]

### spec/
[List of files with one-line summaries, or "does not exist"]

## Git Conventions
- **Commit style:** [pattern]
- **Branch naming:** [pattern]
- **PR conventions:** [pattern]

## Key Dependencies
| Dependency | Purpose | Version |
|---|---|---|
| [name] | [what it does] | [version] |

## Code Conventions
- **Error handling:** [pattern]
- **Module organization:** [pattern]
- **API style:** [pattern]
- **Naming:** [convention]

### Representative code (excerpt)
```[lang]
[10-15 lines of typical source code]
` ` `

## Mock/Test Boundaries
- **Real:** [what's tested against real instances]
- **Mocked:** [what's mocked and how]
- **Mock boundary:** [where it sits]
- **Containers:** [usage]

## Security
- **Security docs:** [exist/missing]
- **Credential handling:** [pattern]
- **Isolation:** [pattern]
- **Auth:** [pattern]
- **Security-sensitive areas:** [list]

## Gaps
[List of things that are missing or broken, mapped to which chain-* skill addresses them]
```

## Timing

The survey should take 2-5 minutes for a typical repo. Most time is spent running commands. Don't over-read — sample source files, don't read every one.

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Guessing commands without running them** | Hard gate. Run every command. |
| **Reading every source file** | Sample 3-5 representative files. Time is finite. |
| **Cataloging every dependency** | Focus on the 5-10 that shape architecture. |
| **Skipping the .claude/ check** | Existing setup changes what chain-generate produces. |
| **Writing skills or CLAUDE.md** | Survey only. One artifact: survey.md. |
| **Ignoring failing commands** | A failing test suite IS the survey data. Record why. |

## Handoff

After this skill completes:
- **chain-plan** reads survey.md and produces a gap analysis + generation plan
- The human can review the survey if desired (it's committed to the repo)
- If the survey reveals the repo is too complex (monorepo, multi-language), note this for chain-plan to handle
