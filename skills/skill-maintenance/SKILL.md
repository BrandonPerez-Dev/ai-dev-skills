
---
name: skill-maintenance
description: Evolve skills based on real-world usage — reads LEARNINGS.md logs, validates findings with research, and applies targeted updates to skills. Use when a skill produced incorrect guidance, missed a pattern, or needs updating based on new information.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Task
---

# Skill Maintenance

Evolve skills based on real-world usage. Read learnings, validate them, and apply targeted updates. Skills are living documents — they improve through use, not just through initial authoring.

<HARD-GATE>
**Never update a skill based on a single anecdote.** Every change must be validated — either by research confirming the pattern, or by multiple independent occurrences in the learnings log. One bad experience is a data point, not a trend.
</HARD-GATE>

## When to Use

- A skill gave incorrect or outdated guidance during a build
- A pattern or tool has changed since the skill was written
- The same issue keeps appearing across projects (repeated learning entries)
- New best practices have emerged that a skill should reflect
- A skill is missing guidance for a common scenario

## LEARNINGS.md Format

Each project maintains a `LEARNINGS.md` file at the project root. Entries are appended during build or ship phases when something unexpected happens.

### Entry Format

```markdown
## [YYYY-MM-DD] Short description

**Skill:** skill-name
**Severity:** minor | moderate | critical
**Context:** What were you doing when this happened?
**Expected:** What should the skill have told you?
**Actual:** What actually happened or what the skill said?
**Resolution:** How did you fix it?
**Suggested change:** (Optional) What the skill should say instead.
```

### Severity Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **minor** | Inconvenience, easy workaround | Batch with other minor items, update when 3+ accumulate |
| **moderate** | Wasted significant time or produced wrong output | Validate and update within the session |
| **critical** | Caused a bug, security issue, or broken deployment | Validate and update immediately |

### Example Entry

```markdown
## [2026-02-15] Biome v2 changed config schema

**Skill:** boilerplate-cicd
**Severity:** moderate
**Context:** Scaffolding a new project using the boilerplate-cicd skill's biome.json template.
**Expected:** The config should work with Biome v2.3.
**Actual:** Biome rejected the `$schema` URL — v2.0 path changed to `https://biomejs.dev/schemas/2.0/schema.json`.
**Resolution:** Updated the schema URL manually. Config worked after that.
**Suggested change:** Update the biome.json example to use the v2.0 schema URL.
```

## Maintenance Process

### 1. Read Learnings

Scan LEARNINGS.md files across projects for entries targeting the skill:

```bash
# Find all learning entries for a specific skill
grep -r "**Skill:** skill-name" /path/to/projects/*/LEARNINGS.md
```

Or read a specific project's file to review all recent entries.

### 2. Triage

Group entries by pattern:

| Pattern | Count | Severity | Action |
|---------|-------|----------|--------|
| Biome schema URL outdated | 3 | moderate | Update example |
| Missing ESM guidance | 1 | minor | Monitor — not enough data yet |
| Security scanning missed CVE | 1 | critical | Research and update immediately |

**Decision rules:**
- 3+ entries on the same pattern → update the skill
- 1 critical entry → validate and update immediately
- 1-2 minor entries → log for future review, don't update yet
- Conflicting entries → research before deciding

### 3. Validate

Before changing a skill, confirm the learning is correct and generalizable:

**For tool/API changes:**
- Check the official documentation (WebSearch/WebFetch)
- Verify the new behavior with a test (Bash)
- Confirm the old guidance is actually wrong, not a local config issue

**For pattern changes:**
- Search for the pattern in multiple codebases (Grep/Glob)
- Check if the community has shifted (WebSearch for current best practices)
- Verify the suggestion doesn't break other guidance in the skill

**For missing guidance:**
- Research the topic — is there established best practice?
- Check if other skills cover this and the learning is a skill boundary issue
- Determine if the guidance belongs in this skill or a different one

### 4. Draft the Change

Write the specific change to the skill:

- **Identify the exact section** to modify
- **Make the minimum change** that addresses the learning
- **Preserve the skill's voice and structure** — don't rewrite sections for one fix
- **Add, don't just replace** — if the old guidance was sometimes right, add the nuance rather than removing it

### Change Types

| Type | When | Example |
|------|------|---------|
| **Correction** | Skill says something wrong | Fix the incorrect config value |
| **Addition** | Skill is missing guidance | Add a new row to a table, new bullet to a list |
| **Nuance** | Skill is too absolute | Add "unless X, in which case Y" |
| **Deprecation** | Tool or pattern is outdated | Replace with current alternative, note migration path |
| **Reorganization** | Section has grown unwieldy | Split or restructure for clarity |

### 5. Apply and Verify

1. **Edit the skill file** — use Edit tool for targeted changes
2. **Read the modified section** — verify the change reads correctly in context
3. **Check for contradictions** — does the change conflict with other parts of the skill?
4. **Update the changelog entry** in the learnings log (mark as resolved)

### 6. Mark Learnings Resolved

After applying changes, update the LEARNINGS.md entries:

```markdown
## [2026-02-15] Biome v2 changed config schema

**Skill:** boilerplate-cicd
**Severity:** moderate
**Status:** ✅ Resolved — skill updated 2026-02-16
...
```

## Versioning

Skills don't use formal semantic versioning — they're documents, not APIs. But track changes:

### Changelog Section

Add a changelog to the bottom of skill files when changes accumulate:

```markdown
## Changelog

- **2026-02-16:** Updated Biome config to v2.0 schema URL (3 learnings)
- **2026-02-10:** Added ESM/CJS decision guidance (research-driven)
- **2026-02-01:** Initial version
```

### When to Bump vs Rewrite

| Signal | Action |
|--------|--------|
| 1-3 targeted fixes | Edit specific lines |
| 5+ fixes in same section | Rewrite that section |
| 10+ fixes across skill | Full skill revision (re-research) |
| Underlying technology changed fundamentally | Full skill rewrite |

## Proactive Maintenance

Don't only react to failures. Schedule periodic reviews:

### Quarterly Review Checklist

- [ ] Read all LEARNINGS.md entries for the skill
- [ ] WebSearch for "[tool/framework] changes [current year]" for each major tool referenced
- [ ] Check if referenced library versions are still current
- [ ] Verify linked documentation URLs still work
- [ ] Look for patterns in entries that suggest a deeper issue

### Signals That a Skill Needs Attention

- **Same workaround appearing in multiple projects** — the skill is missing something
- **Users skip a recommended step** — the step may be wrong or unnecessary
- **A new tool has become the default** — the skill references the old one
- **The skill contradicts another skill** — boundary issue, needs alignment

## Cross-Skill Consistency

When updating one skill, check related skills for consistency:

| Skill Updated | Also Check |
|---------------|-----------|
| boilerplate-cicd | build (verification commands), ship (CI references) |
| architecture | design (architecture section), build (component references) |
| test-planning | design (test strategy section) |
| tdd | build (test execution) |
| eval-driven-dev | ai-agent-building (agent evals) |
| architecture-diagram | design (diagrams in design docs), architecture (data flow diagrams) |
| ai-agent-building | build (agent-specific patterns), architecture (orchestration) |

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Updating on one data point** | Overfits to a single experience | Wait for 3+ occurrences or validate with research |
| **Rewriting when editing suffices** | Churn, loses tested guidance | Make the minimum effective change |
| **Ignoring minor entries** | Minor issues accumulate into major gaps | Review minors quarterly, batch when 3+ cluster |
| **Changing without validation** | Introduces new errors | Always research before changing |
| **Updating the skill but not the learnings log** | Entries stay open, causing re-investigation | Mark entries resolved when addressed |
| **Silent fixes** | No audit trail of why something changed | Always add a changelog entry |

## Guidelines

- **Validate before changing.** One anecdote is not a pattern. Research confirms or denies.
- **Minimum effective change.** Edit the line that's wrong, not the whole section.
- **Preserve what works.** Most of a skill is correct most of the time. Don't destabilize proven guidance for an edge case.
- **Log everything.** Changelog entries, resolved learnings, research findings. Future maintainers need context.
- **Cross-check related skills.** A change in one skill may create contradictions in another.
- **Batch minor fixes.** Don't update a skill for every papercut. Wait for patterns to emerge.
