---
name: pr-walkthrough
description: >-
  Builds a pre-merge study aid for a pull request: a self-contained HTML
  walkthrough (why the change exists, a map of touched areas, annotated key
  hunks, a quiz on the diff) plus a flashcard deck (deck.json) scoped to what
  the change teaches. ALWAYS invoke when asked to explain, study, or build
  review-prep material for a PR or diff. Teaching layer only — finding
  defects belongs to `code-review`; whole-repo courses belong to
  `codebase-course`.
when_to_use: >-
  Triggers: "walk me through PR 42", "study guide for this diff", "help me
  review this PR", "what should I understand before reviewing this", pipeline
  assembly phase (review aids). NOT for judging the change (code-review) or
  learning the whole repo (codebase-course).
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
argument-hint: "[PR number | branch | path/to/diff]"
effort: high
---

# PR Walkthrough

Teach the change; don't re-review it. A reviewer who understands what a change is *for* and where its weight sits catches the problems no linter can — a reviewer reading a cold diff top-to-bottom catches formatting. You are the change's author explaining it to a sharp colleague the way you'd want it explained to you: why first, then the load-bearing parts, then what deserves their skepticism.

The reader is the inverse of `codebase-course`'s: fluent in this repo, new to this *change*. The floor is repo fluency; the teach list is whatever the change introduces — a new invariant, a moved boundary, a new failure mode.

Output: one self-contained `pr-<n>-walkthrough.html` (interactive, using codebase-course's template) plus `deck.json` scoped to the change. Default location: `study/` at the repo root (or the path the invoker specifies — in the pipeline this is posted per the assembly workflow).

## Inputs

- **PR number**: `gh pr view <n>` + `gh pr diff <n>` (body, linked issues, commits, diff).
- **Branch**: `git diff <base>...<branch>` with the merge-base as base; commits via `git log`.
- **Pipeline mode**: if `.pipeline/state.json` exists, read it plus the change spec (`changes/<story-id>/change-spec.md`) or touched `spec/`/`context/` files — the spec's *why* and test contracts are the walkthrough's backbone, already written.

Read the touched files in full, not just hunks — a walkthrough written from hunks alone misattributes purpose. Read the tests the change adds or modifies; they state intent more honestly than the PR body.

## Structure (in teach order, not diff order)

1. **Why this change exists** — the problem, from the story/spec/commits. One paragraph. If the PR body and the code disagree about what this does, say so; that's the most valuable sentence in the walkthrough.
2. **The map** — a `filemap` of touched areas with one-line whys, `.hot` on the files where the real change lives (most diffs are 80% mechanical ripple; say which 20% isn't).
3. **The change as narrative** — 2–4 sections ordered by understanding: the core mechanism first, then what had to move to accommodate it. Annotated code↔English translations on the load-bearing hunks only (real diff content, verbatim, `file:line` at the head ref). Mechanical ripple gets one honest sentence and a collapsible, not annotation.
4. **What deserves reviewer skepticism** — 2–4 attention points phrased as questions to hold while reading ("does the recompute still run when the insert comes through the batch path?"). These are *comprehension* pointers. If while writing you find an actual defect, flag it in ONE clearly-marked callout and stop — hunting is code-review's job, and a walkthrough that turns into a review loses the reader's trust in both.
5. **Quiz** — 5–8 questions per [quiz-design.md](../codebase-course/references/quiz-design.md): at least one consequence question about an input the change handles differently, and at least one regression-shaped question (what previously-working behavior does this touch). Distractors come from the plausible misreadings of this diff.
6. **deck.json** — 2–5 cards per [deck-schema.md](../codebase-course/references/deck-schema.md), scoped to what the change *teaches*, not what it edits. A dependency bump or pure refactor honestly emits `cards: []`.

## Build

Copy `../codebase-course/references/course-template.html`, fill placeholders (kicker: `PR walkthrough · #<n>`), write sections as modules against the markup contract in [interactive-elements.md](../codebase-course/references/interactive-elements.md). Verify every `file:line` against the PR's head ref, not the default branch. Parse-check the HTML before handoff.

## Bias guards

| Thought mid-build | Reality | Do instead |
|---|---|---|
| "I'll go through the diff file by file" | Diff order is alphabetical, not conceptual | Teach the core mechanism first, ripple last |
| "I should point out this bug I noticed" | You're teaching, not reviewing — mixed modes erode both | One marked callout max, then back to teaching |
| "Every hunk deserves an annotation" | Annotating ripple buries the signal | Annotate the 20% that carries the change; collapse the rest |
| "The PR body says what it does" | Bodies drift from diffs, especially late-revision PRs | Read the code and tests; teach discrepancies out loud |
| "Big change, big quiz" | Quiz size follows what the change teaches, not its line count | 5–8 questions on mechanism; `cards: []` if nothing durable |
| "Reviewer knows the repo, skip the map" | Repo fluency ≠ knowing where THIS change sits | Always ship the map; it's 10 lines and orients everything |

## Self-review before handoff

- Why-section matches the code (not just the PR body); discrepancies surfaced
- Map present, `.hot` on the genuinely load-bearing files
- Annotations only on load-bearing hunks; all code verbatim from the head ref; `file:line` verified
- Attention points are questions, not findings; at most one defect callout
- Quiz has consequence + regression coverage; no trivia (rename-refactor test)
- deck.json ids stable; cards scoped to the durable lesson of the change

## References (shared with codebase-course, load on demand)

- [../codebase-course/references/interactive-elements.md](../codebase-course/references/interactive-elements.md) — markup contract
- [../codebase-course/references/quiz-design.md](../codebase-course/references/quiz-design.md) — question quality
- [../codebase-course/references/deck-schema.md](../codebase-course/references/deck-schema.md) — deck.json schema
- [../codebase-course/references/course-template.html](../codebase-course/references/course-template.html) — the asset to copy
- `../codebase-course/scripts/study.py` — the reviewer; `study.py sync <deck.json>` merges a PR's cards into the same store by stable id, so merged-PR decks accumulate into one living deck instead of a pile of files
