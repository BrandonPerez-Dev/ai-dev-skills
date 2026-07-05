# Skill Scoring Methodology

Two-phase scoring eliminates false negatives by separating objective detection from subjective evaluation.

## Phase 1: Structural Fact Sheet (Automated)

Before any subjective scoring, generate an objective fact sheet for the skill. These markers can be detected by scanning the file — no judgment needed.

### Markers to detect

| Category | What to scan | How to detect |
|---|---|---|
| **Frontmatter** | `allowed-tools` list | YAML between `---` markers |
| **Frontmatter** | `Skill` in allowed-tools | `- Skill` in the YAML block |
| **Frontmatter** | Other tools listed | Each `- ToolName` entry |
| **Hard gates** | `<HARD-GATE>` tags | Literal tag scan |
| **Anti-patterns** | Anti-patterns section/table | `## Anti-Patterns` or `Anti-Pattern` in table headers |
| **Delegation** | Explicit skill invocations | Patterns: `invoke **name**`, `Invoke **name**`, `delegates to **name**` |
| **Which skills** | Named skills referenced | Extract skill names from bold markers after invoke/delegate |
| **Central thesis** | Opening sentence after `# Title` | First non-empty line after the H1 heading |
| **Guidelines** | `## Guidelines` section | Heading scan |
| **When to Use** | `## When to Use` section | Heading scan |
| **Decision tables** | Tables with conditional routing | Pipe-delimited rows with When/If/Scenario columns |
| **References** | `references/` directory | Directory existence + file count |
| **Line count** | Total lines in SKILL.md | `wc -l` |
| **Sections** | All H2/H3 headings | Heading scan |

### Fact sheet format

```
SKILL: <name>
LINES: <count>

FRONTMATTER:
  allowed-tools: [Bash, Read, Glob, Grep, Skill]
  other-fields: ...

STRUCTURAL MARKERS:
  hard-gates: <count> — "<text of each gate>"
  anti-patterns: <yes/no> — <count of anti-patterns listed>
  guidelines: <yes/no> — <count of guideline bullets>
  when-to-use: <yes/no>
  decision-tables: <count>
  references-dir: <count of files>

DELEGATION:
  has-Skill-tool: <yes/no>
  explicit-invocations:
    - invoke **verification** (line N)
    - invoke **commit-and-pr** (line N)
    - delegates to **architecture** (line N)

CENTRAL THESIS:
  opening-line: "<first sentence after H1>"

SECTIONS:
  - ## When to Use
  - ## Process
  - ## Anti-Patterns
  - ## Guidelines
```

## Phase 2: Subjective Quality Evaluation (LLM)

Score each of the 8 dimensions using the rubric from skill-creator. The scorer receives:
1. The full SKILL.md content
2. The Phase 1 fact sheet (so structural markers can't be missed)

### Scoring rules

For each dimension, the scorer MUST:

1. **Quote the specific evidence** — cite the line or section that supports the score
2. **Reference the fact sheet** — if the fact sheet says `hard-gates: 2` and the scorer gives failure-prevention = 0, that's a contradiction that must be explained
3. **Explain the gap** — if scoring below 2, state what's missing to reach 2

### Dimension-specific anchors

These prevent drift in scoring standards.

#### Additive value (0-2)
- **0**: Reformatted version of something Claude already knows (e.g., generic git commands, standard library API)
- **1**: Adds team conventions, specific decision frameworks, or domain context Claude doesn't have
- **2**: Teaches a methodology Claude doesn't do by default. Apply the **deletion test** to each instruction block: "Would removing this cause Claude to make a mistake?" If no, cut.

#### Description quality (0-2) — NEW DIMENSION (2026-05-14)
- **0**: Missing trigger info; mixed POV ("I'll do X" / "you should..."); time-sensitive; over the 1,536-char combined cap with truncation; vague
- **1**: Third-person, includes both what the skill does and when to use it, fits in budget
- **2**: Third-person, **key use-case phrase first** (routing scores against the start), includes what + when, uses `when_to_use` field for additional triggers if useful, fits within 1,536-char combined cap, NOT time-sensitive
- **IMPORTANT**: Mixed POV is an automatic 0. Anthropic explicitly: "inconsistent point-of-view can cause discovery problems."

#### Entry-point clarity (0-2) — REVISED FROM "Central thesis" (2026-05-14)
Measures whether Claude, once the skill is loaded, can find the anchoring concept fast — within a 5-second scroll. Broader than the old "central thesis" criterion: a quick-reference table near the top counts equally with a prose thesis statement.
- **0**: No anchoring concept anywhere near the top. The reader must scan the whole skill to figure out what's load-bearing
- **1**: Has an anchor (thesis or table) but it's buried mid-document, OR it's generic ("do good work" / "follow best practices")
- **2**: Any of: (a) clear opinionated prose thesis in the first non-empty line after the H1 (typical for methodology skills like research / systematic-debugging / verification), (b) quick-reference table mapping tasks → tools/files/approach near the top (typical for utility skills like pdf / docx / pptx), (c) both. Quote the anchor.
- **IMPORTANT**: A skill's *form* of entry-point clarity depends on its type. Methodology skills usually use prose theses; utility skills usually use quick-ref tables. Neither is inherently superior — score whether the anchor is *fast to find and load-bearing*, not whether it's in the form you expected.

#### Failure prevention (0-2) — REVISED
Mechanism-agnostic — scores whether failures are prevented, not whether `<HARD-GATE>` tags are present. (Zero of six analyzed Anthropic-authored skills use `<HARD-GATE>` tags.)
- **0**: No verification mechanisms, no critical-failure callouts, no validation scripts/hooks, no domain-specific anti-patterns
- **1**: Has ONE mechanism: verification loop OR critical callouts (`⚠️ CRITICAL`/**bold**) OR validation scripts OR subagent QA pattern OR `<HARD-GATE>` blocks OR domain anti-patterns table
- **2**: Multiple mechanisms appropriate to the domain. Could include: verification loops ("assume there are problems"), bold/critical prose callouts on specific failure modes, scripts/hooks for fragile operations, subagent delegation for fresh-eyes review, bias guards table, anti-patterns table. Positive directives with motivation count equally with negation gates.
- **IMPORTANT**: If the fact sheet shows `hard-gates: >= 1`, the minimum score is 1 (still a valid mechanism, just not Anthropic's canonical pattern).

#### Decision support (0-2) — BROADENED
- **0**: Linear "do these steps" with no branching or conditional logic
- **1**: Some conditional logic (if X then Y) or a sizing table
- **2**: Any of: quick-reference table mapping situations → approach, conditional workflow branching, domain-partitioned references with explicit routing instructions, method selection table

#### Structure (0-2) — BROADENED
- **0**: Wall of text, no progressive disclosure, references nested >1 level deep
- **1**: Organized sections, references one level deep, but linear flow without entry/exit criteria
- **2**: Progressive disclosure done well: SKILL.md as index, references loaded on demand, all reference files one level deep from SKILL.md, files >100 lines have a TOC. For methodology skills, phased process with entry/exit criteria. For user-facing skills, output paced per communication-protocol.

#### Tool design (0-2) — UPDATED FOR 2026
- **0**: No `allowed-tools` AND no delegation AND no MCP/script usage
- **1**: `allowed-tools` appropriate to the task, OR delegates to other skills
- **2**: 2026 patterns applied: `allowed-tools` treated as grant (not fence), MCP tools use fully qualified names (`Server:tool_name`), Skill/Task used for delegation where appropriate, `context: fork` + `agent:` for subagent routing where helpful, `effort:` / `model:` calibration where intelligence-sensitive, scoped `hooks:` for deterministic enforcement where the operation is fragile
- **IMPORTANT**: If the fact sheet shows `has-Skill-tool: yes` AND `explicit-invocations` lists delegations, the minimum score is 1.

#### Context efficiency (0-2) — REVISED FOR 2026 COMPACTION BUDGET
- **0**: Exceeds 500-line SKILL.md cap, OR padded with explanations Claude already knows
- **1**: Under 500 lines, but some filler — sections that could be trimmed without losing value
- **2**: Under 500 lines, **critical instructions in first ~350 lines** (the 5,000-token per-skill compaction-durable zone), references/ used for variant/domain detail loaded on demand, no explanations of standard-library behavior, deletion test applied throughout. Density over completeness.
- **IMPORTANT**: Anthropic's official cap is 500 lines (not 300 as the old anchor stated). The 5K-token compaction budget makes the *first* ~350 lines load-bearing — a 480-line skill with critical content up front beats a 280-line skill that buried the load-bearing rules.

### Output format

```
SKILL: <name>

SCORES:
  additive-value:      X/2 — "<evidence quote>" [gap if < 2]
  description-quality: X/2 — "<evidence quote>" [gap if < 2]
  entry-point-clarity: X/2 — "<evidence quote>" [gap if < 2]
  failure-prevention:  X/2 — "<evidence quote>" [gap if < 2]
  decision-support:    X/2 — "<evidence quote>" [gap if < 2]
  structure:           X/2 — "<evidence quote>" [gap if < 2]
  tool-design:         X/2 — "<evidence quote>" [gap if < 2]
  context-efficiency:  X/2 — "<evidence quote>" [gap if < 2]

TOTAL: XX/16

FACT SHEET CONFLICTS: [any cases where the score contradicts the fact sheet — must be explained]

TOP IMPROVEMENTS:
1. [Most impactful improvement to raise the score]
2. [Second most impactful]
```

## Scoring at scale

When scoring multiple skills:
1. Generate fact sheets for all skills first (batch)
2. Score skills in small batches (5-8) to maintain calibration
3. After each batch, check for scoring drift by comparing similar skills
4. Flag any score that contradicts the fact sheet

## Known bias patterns

| Bias | How it manifests | Countermeasure |
|---|---|---|
| **Missed structural markers** | Scoring 0 on failure-prevention when `<HARD-GATE>` exists | Fact sheet makes markers impossible to miss |
| **Missed delegation** | Scoring 0 on tool-design when `Skill` is in allowed-tools | Fact sheet explicitly lists delegation targets |
| **Inflation** | Scoring 2 on everything because "it seems good" | Require quoted evidence for every score |
| **Context recency** | Last skill scored gets harsher treatment | Score in small batches, calibrate between batches |
| **Halo effect** | Well-written prose gets high structure score | Check structural elements independently of prose quality |
