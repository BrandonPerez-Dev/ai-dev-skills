---
name: chain-plan
description: >-
  L1 chain creator — Phase 2. Reads chain-survey output, compares against
  what a complete autonomous agent chain requires, grills the survey for
  gaps and wrong conclusions, and produces a generation plan specifying
  which L2 skills to create and what repo-specific knowledge to inject.
  Posts open questions to GitHub when blocked.
when_to_use: >-
  Use after chain-survey has produced .claude/chain/survey.md in the
  target repo. Takes the survey and produces a plan for chain-generate.
  Do NOT use without a completed survey — planning without data produces
  guesswork.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
argument-hint: "[path/to/target-repo]"
effort: high
---

# Chain Plan

Read the survey. Compare against requirements. Grill the findings. Plan what to generate. This skill bridges raw survey data and actual L2 skill generation.

<HARD-GATE>
Do not write L2 skills, CLAUDE.md, or agent-chain.yaml. This skill
produces the plan. chain-generate writes from it.
</HARD-GATE>

<HARD-GATE>
Do not plan without reading the survey. If `.claude/chain/survey.md`
doesn't exist, stop and run chain-survey first.
</HARD-GATE>

## Input

Target repo path (same repo where chain-survey wrote `survey.md`).

## Process

### 0. Load Survey

Read `.claude/chain/survey.md`. Also re-read `context/` and `spec/` if they exist — the survey summarizes them, but the plan needs the detail.

### 1. Requirements Matrix

For each L2 skill the chain can produce, check what the survey provides vs what the skill needs:

#### Process Skills (from L0 auto-* templates)

| L2 Skill | Requires from survey | Found? |
|---|---|---|
| **plan-grill** | Project-specific constraint categories, commit/branch conventions, context/spec format, grill lenses relevant to this project's domain | |
| **test-planning** | Test framework, runner, naming convention, shared helpers, fixture patterns, mock boundaries, integration approach, platform requirements | |
| **test-writer** | Test file patterns (where tests go, how named), import boilerplate, assertion style, setup/teardown, how to run single test vs all | |
| **build** | Where new code goes, error handling pattern, API style, dependency management, lint rules, verification commands | |
| **foundation** | CI/CD presence, existing project scaffold, missing infrastructure | |

#### Domain Skills (repo-specific knowledge)

| L2 Skill | Requires from survey | Found? |
|---|---|---|
| **Language/runtime** | Language-specific patterns, idioms, library usage in THIS codebase | |
| **Data interaction** | Subsystem rules, data integrity constraints, storage patterns | |
| **Security** (if applicable) | Threat model, security-sensitive areas, credential handling, isolation | |

Fill in the "Found?" column from survey data. Missing data → gap.

### 2. Gap Analysis

For each gap:

| Gap | Impact | Resolution |
|---|---|---|
| [what's missing] | [which L2 skill is degraded without it] | [can chain-generate infer it? needs human input? skip the skill?] |

Classify each gap:

- **Fillable** — chain-generate can infer from codebase patterns even though the survey didn't capture it explicitly. (e.g., "assertion style not recorded" → chain-generate reads test files directly)
- **Needs human** — can't be derived from code. (e.g., "which APIs have test environments?" → open question)
- **Skip** — the gap means a specific domain skill isn't warranted. (e.g., "no security-critical patterns" → no security domain skill)
- **Foundation trigger** — the gap is infrastructure that needs to be created. (e.g., "no CI" → foundation skill creates it)

### 3. Grill the Survey

Before planning the generation, grill the survey findings. The survey extracted data; the grill challenges whether that data is correct and complete.

#### Lens 1: Extraction Accuracy

- Did the survey correctly identify the test framework? (run a test to double-check)
- Are the build commands the RIGHT commands? (does CI run something different?)
- Are the "representative" code snippets actually representative? (or outliers?)
- Did the survey miss a second language or build system? (monorepo concern)

#### Lens 2: Coverage Gaps

- Are there whole categories the survey skimmed? (e.g., "no dependencies listed" for a project with 50 deps)
- Did the survey read enough test files to capture the dominant pattern? (3 files might show 3 different patterns)
- Are there subsystems the survey didn't reach? (e.g., a `tools/` directory with its own build system)
- Are there test environments the survey couldn't see? (CI-only containers, cloud sandboxes)

#### Lens 3: Assumption Risks

- Where did the survey assume a convention from limited evidence?
- Which survey conclusions would be EXPENSIVE to get wrong in a generated skill? (mock boundaries, error handling patterns)
- Does the project have unusual patterns that a generic L0 template would get wrong?

#### Grill Output

Each finding becomes an ADR in the plan:

```markdown
### [Finding Title]
- **Status:** resolved | assumption | blocking
- **Context:** [What part of the survey this challenges]
- **Decision:** [Resolution or assumption]
- **Confidence:** high | medium | low
- **Consequences:** [What changes in the generation plan]
- **Alternatives considered:** [Other interpretations]
```

### 4. Plan the L2 Skills

For each skill that passed the requirements matrix (has enough data):

```markdown
### L2: [skill-name]
- **Base L0:** auto-[name] (or "no L0 base" for domain skills)
- **Confidence:** high | medium
- **Key customizations:**
  - [What repo-specific knowledge to inject]
  - [What generic guidance to replace]
  - [What new sections to add]
- **Survey sources:** [Which survey sections feed this skill]
- **Gaps:** [What's missing but inferrable] or "none"
```

For domain skills without an L0 base, describe the skill's purpose and what knowledge it captures.

### 5. Plan Foundation Work

If the survey found infrastructure gaps:

```markdown
## Foundation Work
- **CI/CD:** [missing / partial / complete]
  - Action: [what foundation skill creates]
- **CLAUDE.md:** [missing / incomplete / complete]
  - Action: [what to generate or update]
- **context/:** [missing / exists]
  - Action: [bootstrap or skip]
- **spec/:** [missing / exists]
  - Action: [bootstrap or skip]
```

### 6. Plan the Agent Chain Config

```markdown
## Chain Config
- **Chain name:** [project]-agent
- **Trigger sources:** [issues, manual, scheduled]
- **Build command:** [from survey, verified]
- **Test command:** [from survey, verified]
- **Lint command:** [from survey, verified]
- **Format check:** [from survey, verified]
- **Branch prefix:** agent/
- **Commit style:** [from survey git conventions]
- **PR labels:** [standard set]
```

### 7. Open Questions

Collect all medium and low-confidence items:

```markdown
## Open Questions

### Blocking
- [Question] — blocks: [which L2 skills affected]

### Assumptions
- [Assumption] — affects: [which L2 skills affected]
```

### 8. Save and Push

1. Write `.claude/chain/plan.md` to the target repo
2. Commit to the chain setup branch
3. Post open questions as PR comments if a PR exists

## Plan Format

```markdown
# Chain Plan: [project-name]

> Date: YYYY-MM-DD
> Survey: .claude/chain/survey.md
> Status: planning

## Requirements Matrix

### Process Skills
[Table from step 1]

### Domain Skills
[Table from step 1]

## Gaps
[Table from step 2]

## Grill

### Extraction Accuracy
[ADRs]

### Coverage Gaps
[ADRs]

### Assumption Risks
[ADRs]

## L2 Skills to Generate

### Process Skills
[Entries from step 4]

### Domain Skills
[Entries from step 4]

## Foundation Work
[From step 5]

## Chain Config
[From step 6]

## Open Questions
[From step 7]

## Generation Order

The recommended order for chain-generate:
1. Foundation (if needed) — infrastructure first
2. CLAUDE.md — project-level knowledge
3. Domain skills — codebase knowledge that process skills reference
4. Process skills — plan-grill → test-planning → test-writer → build
5. agent-chain.yaml — ties it all together
```

## Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| **Planning without a survey** | Hard gate. Run chain-survey first. |
| **Marking all gaps as blocking** | Most gaps are fillable from code. Block only when wrong answers are expensive. |
| **Skipping the grill** | The grill catches survey errors before they become skill errors. |
| **Planning skills for things the project doesn't need** | No security skill for a static site. No data interaction skill for a CLI tool with no persistence. |
| **Ignoring the survey's failed commands** | A failing test suite shapes the plan — maybe foundation needs to fix it first. |
| **Writing L2 skills in this step** | Plan only. chain-generate writes. |

## Handoff

After this skill completes:
- **chain-generate** reads plan.md + survey.md + L0 templates and produces L2 skills
- The human can review the plan before generation starts
- Open questions may need answers before certain L2 skills can be generated with confidence
