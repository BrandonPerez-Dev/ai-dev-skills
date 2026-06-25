# Chain Creator Design

> Date: 2026-06-24
> Status: Draft
> Related: [autonomous-github-flow.md](2026-06-24-autonomous-github-flow.md)

## What This Is

A skill that reads a repo and produces a **repo-specific agent chain** — a customized set of skills and a CLAUDE.md that an autonomous agent uses to plan, test, and build in that particular codebase. The auto-* skills (auto-plan-grill, auto-test-planning, auto-build) are the generic templates (L0). The chain creator (L1) adapts them into repo-specific skills (L2) that know the project's language, conventions, test infrastructure, and architectural patterns.

## Why Not Just Use Generic Skills

Generic skills work but produce mediocre results because they guess at:
- Build/test/lint commands (is it `cargo test`, `npm test`, `pytest`?)
- Test patterns (integration via spawned process? HTTP client? in-process?)
- Mock boundaries (what's real, what's stubbed?)
- Naming conventions (commit style, file naming, code naming)
- Project structure (where does new code go? what crate/module?)
- Spec/context format (does the project already have these? what format?)
- Error handling patterns (anyhow? thiserror? custom? exceptions?)
- CI expectations (what checks must pass before merge?)

An agent that guesses gets corrected, which costs human time — the exact thing the autonomous loop is meant to save. A repo-specific chain knows these answers on day one.

## What the Chain Creator Reads

### From the repo (automated survey)

| Category | What to extract | How |
|---|---|---|
| **Language & runtime** | Language, edition/version, build tool | Cargo.toml, package.json, go.mod, pyproject.toml, etc. |
| **Build commands** | Build, test, lint, format, type-check | Build config + Makefile/scripts + CI config |
| **Test infrastructure** | Framework, runner, naming conventions, shared helpers, fixture patterns, container requirements | Test files + test config + test helpers |
| **Project structure** | Source layout, module organization, crate/package boundaries | Directory tree + entry points |
| **CI/CD** | What checks run, what triggers them, required checks for merge | .github/workflows/, .gitlab-ci.yml, etc. |
| **Existing .claude/** | CLAUDE.md, settings, existing skills, permissions | .claude/ directory |
| **context/ and spec/** | Existing architectural docs and behavioral specs, their format | context/, spec/ directories |
| **Git conventions** | Commit message style, branch naming, PR conventions | git log, .gitignore, branch patterns |
| **Dependencies** | Key libraries, external services, APIs | Lock files, imports, config |
| **Code conventions** | Error handling, module organization, API style, naming | Source code sampling |
| **Mock/test patterns** | How existing tests handle mocking, what's real vs stubbed | Test files |
| **Security posture** | Any security-sensitive patterns, credential handling, sandbox requirements | Security docs, config, code patterns |

### From the human (kickoff or existing docs)

Some things can't be derived from code:
- What the project does (high-level purpose)
- What work is planned or in-progress
- Team conventions not captured in code (review process, deploy cadence)
- External service access (which APIs have test environments?)
- Quality bar expectations (how thorough should testing be?)

If `context/` already documents these, the chain creator reads them directly. If not, these become the chain creator's first open questions.

## What the Chain Creator Produces

### 1. CLAUDE.md (if missing or incomplete)

A project-level CLAUDE.md with:
- Build/test/lint commands (verified by running them)
- Project structure overview
- Key conventions the agent must follow
- Links to context/ and spec/ docs

### 2. Repo-specific skills (L2)

Customized versions of the L0 auto-* templates, living in the repo's `.claude/skills/`:

#### `.claude/skills/plan-grill/SKILL.md`
Auto-plan-grill adapted with:
- Project-specific constraint categories (e.g., for Ostia: "namespace isolation requirements", "Landlock compatibility", "binary resolution strategy")
- Project-specific grill lenses (e.g., for Ostia: "does this change affect the security model?", "does this require new Landlock rules?")
- Known mock boundaries from context/testing-strategy.md
- Commit message format and branch naming
- Context/ and spec/ format conventions from the project

#### `.claude/skills/test-planning/SKILL.md`
Auto-test-planning adapted with:
- Test framework and runner commands
- Test naming conventions (from existing tests)
- Shared test helpers and how to use them (e.g., Ostia's `McpClient::spawn()`)
- Fixture patterns (e.g., Ostia's `tempfile::TempDir` + YAML config writers)
- Mock boundary decisions (from context/testing-strategy.md)
- Integration test choreography (e.g., Ostia: "each test spawns a real ostia serve process")
- Platform requirements (e.g., Ostia: "tests require Linux + unprivileged namespaces")

#### `.claude/skills/test-writer/SKILL.md`
Auto-test-writer adapted with:
- Exact test file patterns (where tests go, how they're named)
- Import boilerplate (what test helpers to use)
- Assertion style (from existing tests)
- Setup/teardown patterns
- How to run a single test vs all tests

#### `.claude/skills/build/SKILL.md`
Auto-build adapted with:
- Where new code goes (which crate, which module, how modules are organized)
- Error handling pattern (anyhow? thiserror? what's the convention)
- API style (builder pattern? direct construction? trait-based?)
- How to add dependencies (workspace-level vs crate-level)
- Linting rules to follow
- How to verify (cargo check, cargo clippy, cargo test)

#### `.claude/skills/foundation/SKILL.md` (conditional)
For greenfield or major structural changes:
- Project initialization steps
- CI/CD setup
- Config scaffolding
- Dependency installation
- Context/ and spec/ bootstrapping

### 3. Agent chain config

A manifest that ties the skills together and defines the execution order:

```yaml
# .claude/agent-chain.yaml
name: ostia-agent
description: Autonomous dev agent for Ostia (Rust MCP sandbox)

chain:
  - skill: plan-grill
    triggers: [issue-created, manual]
    outputs: [plan, open-questions, spec-stubs]
    
  - skill: test-planning
    triggers: [plan-complete, slice-unblocked]
    inputs: [plan, spec-stubs]
    outputs: [test-contracts]
    condition: "slice has no test contract yet"
    
  - skill: test-writer
    triggers: [contract-validated]
    inputs: [test-contracts]
    outputs: [locked-tests]
    condition: "slice has validated contract but no committed test"
    
  - skill: build
    triggers: [tests-committed]
    inputs: [locked-tests, spec]
    outputs: [implementation]
    condition: "slice has committed red test"
    
  - skill: refactor
    triggers: [slice-built]
    inputs: [implementation-diff]
    outputs: [refactored-code]
    
  - skill: foundation
    triggers: [greenfield, structural-change]
    inputs: [plan]
    outputs: [project-scaffold]
    condition: "no existing test infrastructure or major structural addition"

github:
  branch_prefix: "agent/"
  commit_style: "feat(scope): description"
  pr_labels: [agent-in-progress, needs-answer, ready-for-review]
  
verification:
  build: "cargo build --workspace"
  test: "cargo test --workspace"
  lint: "cargo clippy --workspace -- -D warnings"
  format_check: "cargo fmt --check"
```

## How the Chain Creator Works

### Phase 1: Survey (automated, ~2-5 min)

Read the repo systematically. For each category in the "What to extract" table above:
1. Find the relevant files (build config, test files, CI config, etc.)
2. Extract the specific information
3. Verify by running commands (e.g., `cargo test --workspace` to confirm it works)
4. Record findings in a survey document

### Phase 2: Gap Analysis

Compare what was found against what a complete agent chain needs:

| Required | Found | Gap |
|---|---|---|
| Build commands | ✅ cargo build/test | — |
| Test infrastructure | ✅ integration tests, McpClient helper | — |
| CI/CD | ❌ No GitHub Actions | Agent needs to know there's no CI to check |
| CLAUDE.md | ❌ Missing | Chain creator will generate one |
| context/ docs | ✅ 6 files | — |
| spec/ docs | ✅ 8 files | — |
| Mock boundaries | ✅ Documented in testing-strategy.md | — |

Gaps become either:
- Things the chain creator fills (CLAUDE.md, skill files)
- Open questions for the human (external service access, team conventions)
- Foundation skill triggers (CI setup, missing infrastructure)

### Phase 3: Generate (skills + config)

For each L2 skill:
1. Start from the corresponding L0 template (auto-plan-grill, auto-test-planning, etc.)
2. Inject repo-specific knowledge into the relevant sections
3. Remove generic guidance that's now covered by specific guidance
4. Validate that the skill references real files, real commands, real patterns

### Phase 4: Verify

Run a lightweight smoke test:
- Can the build command succeed?
- Can the test command succeed?
- Do the referenced test helpers exist?
- Do the referenced context/ and spec/ files exist?
- Does the generated CLAUDE.md match reality?

### Phase 5: Push and Report

- Commit generated files to the repo (on a branch if configured for GitHub flow)
- Report what was generated, what gaps remain, what open questions need human input

## The Foundation Skill

The "untestable vertical" — project initialization and structural scaffolding. This is conditional: it runs when the chain detects greenfield or major structural additions.

What it handles:
- **Greenfield:** cargo init / npm init, directory structure, CI config, initial context/ and spec/ setup, dependency installation, linting config
- **Structural addition:** new crate in workspace, new service, new test infrastructure (e.g., adding testcontainers for the first time)
- **CI bootstrapping:** GitHub Actions for build/test/lint if missing

Why it's separate: these steps don't have natural integration test contracts. You can't write "when I create Cargo.toml, then the project builds" as a spec slice — it's infrastructure, not behavior. The foundation skill's success criteria are: "build passes, test runner works, project structure matches conventions."

The foundation skill runs BEFORE plan-grill when triggered, and its output is the infrastructure that plan-grill assumes exists.

## Evolution Strategy

### What to evolve via GEPA

The chain creator itself is the primary GEPA target. Evolving it improves every chain it produces.

**Eval tasks for the chain creator:**
- **Input:** A repo (or a snapshot of one)
- **Grader:** Does the produced chain work? (build passes, test commands work, skill files reference real patterns, CLAUDE.md is accurate)
- **Feedback:** LLM judge comparing the produced chain to an expert-written chain for the same repo

**What GEPA optimizes:** The chain creator's survey strategy (what to look at, in what order), its gap analysis (what counts as a gap), and its generation templates (how to adapt L0 skills to L2).

### What to evolve via gskill (later)

Once repos have clean commit history from autonomous work:
- gskill produces repo-specific coding skills (not planning/testing skills)
- These complement the L2 chain by adding "how to write code in this specific codebase" knowledge
- gskill evolves the build skill; the chain creator evolves the planning/testing skills

### Correction feedback loop

When the human corrects an L2 skill:
- If the correction is repo-specific → update the L2 skill in the repo
- If the correction reveals a gap in the L0 template → update the L0 auto-* skill
- If the correction reveals a gap in the chain creator → update the chain creator's survey/generation logic

This three-level correction routing is what makes the system self-improving across projects, not just within one.

## What This Does NOT Do

- **Run the chain.** The chain creator produces skills and config. The supervisor/trigger system runs them.
- **Replace interactive skills.** The chain creator only produces autonomous L2 skills. Interactive skills remain for when you're pair-programming.
- **Guess at business logic.** The chain creator extracts conventions and infrastructure patterns. It doesn't decide what features to build — that comes from the kickoff/issue.
- **Skip human review of generated chains.** The first chain for a repo always gets human review. GEPA optimization reduces the need for corrections over time, but the human gate stays.

## Open Questions

1. **Where does the agent-chain.yaml live?** Options: `.claude/agent-chain.yaml` in the repo (versioned, visible), or in the skill config system (centralized, not repo-versioned).
2. **How much of the L0 template shows through in L2?** Should L2 skills be fully self-contained (copy everything from L0 + add repo-specific), or should they reference L0 and only override the repo-specific parts? Self-contained is more robust but harder to update when L0 improves.
3. **How does the chain creator handle multi-language repos?** (e.g., remote-terminal: Go + TypeScript + Proto). Does it produce one chain with language-specific steps, or multiple chains?
4. **Should the foundation skill be part of the chain or a pre-chain step?** If it's in the chain, the chain config handles triggering. If it's pre-chain, the chain creator runs it during initial setup.
