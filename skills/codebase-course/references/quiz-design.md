# Quiz Design — Question Quality

Shared by `codebase-course` and `pr-walkthrough`. A quiz question is worth including only
if getting it wrong would change how the reader works in this codebase. Everything here
serves that filter.

## Contents
1. [What to quiz — and what never to](#1-what-to-quiz--and-what-never-to)
2. [Question types](#2-question-types)
3. [Distractor design](#3-distractor-design)
4. [Explanations](#4-explanations)
5. [Count and placement](#5-count-and-placement)

## 1. What to quiz — and what never to

Quiz **mechanism and consequence**: what happens, what breaks, who owns what, why the
design is the way it is. These survive refactors and transfer to real work.

Never quiz **trivia**: file names, line numbers, function names, counts ("how many
tools does the MCP server expose"), dates, versions. Trivia questions are easy to write
and teach nothing — a reader can ace them and still be unable to make a safe change.
The test: if the answer changes under a rename-only refactor, cut the question.

One tell you're drifting into trivia: the stem starts with "What is the name of…" or
"Which file contains…". A file-location question is only legitimate when the *location
is the lesson* (e.g., the module taught that all mutations funnel through one file).

## 2. Question types

| Type | Shape | Use when |
|---|---|---|
| **Consequence** | "X happens / arrives / fails. What state results?" | The module taught an invariant or ordering |
| **What-would-happen-if** | "If you removed/reordered line X…" | The code has a guard or sequence whose purpose is the lesson |
| **Boundary/ownership** | "Which layer is responsible for Y?" | The architecture assigns responsibilities readers will misassign |
| **Contrasting case** | "These two calls look alike — which one Z, and why?" | A confusable pair exists (two similar services, sync/async variants) |
| **Spot-the-bug** | Altered real code; find the broken invariant | The invariant is concrete enough that a plausible mutation violates it (markup rules: interactive-elements.md §4) |
| **Design rationale** | "Why does this repo do X instead of the more common Y?" | A grill-worthy decision was taught with its rejected alternative |

Mix at least three types per course; a quiz that is all one type is testing pattern
recognition of the quiz format, not the material.

## 3. Distractor design

Every wrong option must be a **real, plausible misconception** — something a competent
engineer skimming the code would actually believe. The best sources:

- **Git history**: bugs that were actually fixed are misconceptions someone actually
  held. `git log --grep=fix` on the module's files is a distractor mine.
- **The more common convention**: what this repo does *differently* from the ecosystem
  default — the default IS the natural wrong answer.
- **The adjacent layer**: attributing a responsibility to the layer that would own it
  in a naive design.

Never pad with throwaway options ("the code crashes", "nothing happens") that no one
would pick — a 3-option question with three live options beats a 4-option question with
one dead one. Keep options parallel in length and register; the longest option being
correct is the oldest tell in test design.

## 4. Explanations

The `.explain` block is where wrong answers become learning. It must:

- State *why* the right answer is right in terms of the mechanism, not by restating it.
- Name what makes the strongest distractor attractive and where that model breaks.
- Point back into the code (`file:line`) so the reader can verify rather than trust.

"Correct — see module text" is a bug. The explanation is often the highest-value prose
in the module because it lands exactly at the moment of surprise.

## 5. Count and placement

- **codebase-course**: one quiz per module, 3–5 questions, placed after the module's
  final concept (not mid-development of an idea). Difficulty ramps within the quiz:
  first question answerable from the module alone; last question may require combining
  the module with a prerequisite module.
- **pr-walkthrough**: one quiz, 5–8 questions, after the annotated hunks. At least one
  consequence question about an input the change now handles differently, and at least
  one regression-shaped question ("what previously-working behavior does this touch?").
- Every question maps to a flashcard in `deck.json` (deck-schema.md) — write the quiz
  first, derive cards from it, not the reverse: quiz questions have distractor context,
  cards are the distilled retrieval form.
