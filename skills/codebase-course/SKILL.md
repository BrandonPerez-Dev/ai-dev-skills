---
name: codebase-course
description: >-
  Turns a mature codebase into an interactive single-file HTML course plus a
  flashcard deck (deck.json), teaching the mental model that makes the code
  predictable to an engineer who knows the craft but not this repo. ALWAYS
  invoke when asked to create a course, study guide, or onboarding curriculum
  from a codebase. Course layer only — single-PR study belongs to
  `pr-walkthrough`; Arboreus lesson prose belongs to `learning`.
when_to_use: >-
  Triggers: "make a course from this repo", "study guide for this codebase",
  "help me learn this codebase", "onboarding material for the team",
  "turn this project into a course". NOT for explaining one PR/diff
  (pr-walkthrough), reference docs/READMEs (readme), or graph-based lessons
  (learning).
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
argument-hint: "[repo path] [optional focus, e.g. 'the graph engine']"
effort: high
---

# Codebase Course

You are the senior engineer who has lived in this repo for years, giving the tour you wish you'd been given — not a file-by-file narration, but the mental model that makes the rest of the code predictable. The reader is a competent engineer with zero knowledge of *this* repo. Your goal: after the course, they can predict where a change goes, what it will break, and why the code is shaped the way it is.

The output is a self-contained `course.html` (interactive: quizzes, code↔English translations, glossary tooltips) plus a `deck.json` flashcard deck for spaced retrieval. Default location: `study/` at the repo root, unless told otherwise.

## Calibrate first (the header)

Write this before designing anything and keep it as an HTML comment at the top of `course.html`:

```
Repo:       <name @ shortsha>
Audience:   experienced engineer, new to this repo (or as user specified)
Floor:      general engineering + <stack familiarity you're assuming, stated explicitly>
Teach list: <repo-specific concepts/terms the course must build — each taught or cut>
Objective:  By the end, the reader can <doing verb — predict/place/trace/extend>
Shape:      <module list with the technique each one leans on, one line each>
```

The floor is a contract in the opposite direction from a beginner course: never explain what `async` is, always explain what a "tier" means *here*. Stack familiarity is the judgment call — assume fluency in the repo's primary language; state (and briefly teach) anything narrower the code leans on (e.g., Kahn's algorithm, RLS policies).

## Phase 1 — Analysis (read before you teach)

Explore the codebase before designing anything (spawn an `Explore` agent for large repos; direct reads for small ones):

1. **Architecture**: main components, how they connect, where the boundaries are enforced vs merely conventional.
2. **Entry points and one traceable flow**: pick a concrete input (a request, a CLI command, a job) you can follow end-to-end — this becomes a module.
3. **Core domain concepts**: the nouns the code invents. These ARE the teach list.
4. **Complexity map**: which parts are simple plumbing vs genuinely intricate. Intricate + central = deep-dive module; intricate + peripheral = collapsible deep-dive at most.
5. **Conventions and invariants**: what the repo does differently from the ecosystem default — the highest-value teaching material, because it's exactly what an experienced engineer will get wrong.
6. **Git history**: `git log --grep=fix` on central files. Real fixed bugs are real misconceptions — they become common-mistake callouts and quiz distractors.

Verify the README's claims against the code; teach what the code does, not what the docs say it does. Where they disagree, that disagreement is itself course material.

## Phase 2 — Curriculum

Design 4–6 modules (8 only if the repo genuinely has that many distinct load-bearing ideas). Order by dependency of understanding, not by directory listing: purpose and shape → domain model → one flow traced end-to-end → deep dives chosen by the complexity map → conventions and extension points. Each module states a doing-verb objective the quiz can test.

Choose the teaching technique per module by what the material is:

| The material is... | Reach for |
|---|---|
| A flow (request lifecycle, ingestion pipeline) | End-to-end trace of ONE concrete input, annotated at each hop |
| A design judgment (why this stack, why this boundary) | The decision + the rejected alternative + what would break under it |
| A domain concept the code encodes | Scenario where its absence hurts, then derive the concept as the fix |
| A confusable pair (two similar layers/services) | Contrasting case that forces the discrimination before naming it |
| Invisible machinery (DI, codegen, middleware chains) | Concrete instance first, then fade to the general form |
| A convention used everywhere | Worked example, then a faded variant the reader completes mentally |

Most modules combine two. Record the choice in the header's Shape line — if every module of every course comes out the same shape, the format is driving instead of the repo.

Design internally; don't present the curriculum for approval unless the user asked to be in the loop. For large repos where modules build in parallel (via Agent), write a brief per module first (teaching arc, pre-extracted code with paths/lines, elements checklist) so builders never re-read the codebase.

## Phase 3 — Build

1. Copy `references/course-template.html` to the output location; fill every placeholder (interactive-elements.md §9).
2. Write modules against the markup contract in [interactive-elements.md](references/interactive-elements.md). Per module: ≥1 code↔English translation (real code, verbatim, `file:line` shown), ≥1 quiz (3–5 questions per [quiz-design.md](references/quiz-design.md)), glossary tooltips on first use of repo-specific terms, callouts only for what the prose already developed.
3. All code shown is real code from the repo at the stated ref — never reconstructed from memory. Spot-the-bug mutations are labeled as altered. Every `file:line` reference is verified with a Read/Grep before it ships.
4. Emit `deck.json` per [deck-schema.md](references/deck-schema.md): derive cards from objectives + quiz questions, 3–6 per module, mechanism only.
5. Tell the reader how to review it: `python3 <skill>/scripts/study.py sync <path>/deck.json` then `study.py review` (stdlib-only, no installs). The course teaches; the deck plus reviewer is what makes it stick.

## Phase 4 — Verify

- Open-or-parse check: the HTML parses (e.g. `python3 -c "import html.parser..."` or a browser open) — an unclosed `<div>` breaks scroll-nav silently.
- Spot-check three `file:line` references at random against the repo.
- Run the self-review below; fix before handoff, not after.

## Bias guards

| Thought mid-build | Reality | Do instead |
|---|---|---|
| "I'll walk the directory tree top to bottom" | Directory order is storage order, not learning order | Order modules by dependency of understanding |
| "The reader might not know what a promise is" | The floor is an experienced engineer | Spend teaching budget on what's specific to THIS repo |
| "I'll narrate what each function does" | Narration reads as understanding but doesn't transfer | Teach the invariant/decision; let code excerpts carry the how |
| "The README explains the architecture, I'll adapt it" | READMEs drift; teaching stale claims is worse than none | Verify against code; teach the discrepancy if there is one |
| "More modules = more thorough" | Coverage isn't the goal; predictability is | 4–6 modules on load-bearing ideas; the rest is collapsible or cut |
| "I'll write the quiz from what I remember writing" | Memory-derived questions drift to trivia | Write questions from invariants and git-mined misconceptions |

## Self-review before handoff

- Header present; every teach-list term taught at first use or cut; floor consistent with what the prose assumes
- Each module: doing-verb objective, ≥1 real-code translation, quiz per quiz-design.md, technique per the table (Shape line justifies it)
- No trivia questions or trivia cards (rename-refactor test)
- deck.json validates against the schema; ids stable; empty modules honestly card-less
- Would this course look meaningfully different from the last one this skill produced? If not, justify why both repos genuinely called for the same shape

## References (load on demand)

- [references/interactive-elements.md](references/interactive-elements.md) — exact markup contract; load before writing any module HTML
- [references/quiz-design.md](references/quiz-design.md) — question types, distractor mining, explanation rules
- [references/deck-schema.md](references/deck-schema.md) — deck.json schema, card selection, downstream targets
- [references/course-template.html](references/course-template.html) — the asset to copy; never regenerate its CSS/JS from scratch
- `scripts/study.py` — the reviewer decks feed (sync/review/stats/rebuild); stdlib-only, copyable to a locked-down machine. Its FSRS port is pinned to ts-fsrs by `scripts/test_fsrs_parity.{mjs,py}` — run that after touching the scheduling math.
