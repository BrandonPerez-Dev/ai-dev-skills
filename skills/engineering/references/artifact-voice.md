# Artifact voice

Planning artifacts — specs, change-specs, test contracts, interrogation threads,
PR bodies — are read by a human driving the session, whose reading time is the hard
limit on how much gets done in a day. Optimize for how fast they can grasp the
change, not for completeness of the record.

Grounded in Anthropic's Claude Opus 5 guidance ("written deliverable length"): Claude 5
models write longer files than prior models by default, so length must be *deliberately*
calibrated — the default is too long.

## The rules

- **Match length to the change.** Cover the substance; do not pad with filler sections,
  redundant summaries, or boilerplate. A one-spec change is a few tight sentences; a
  large change earns more. The change decides the length, never a template.
- **Orient before detail.** Open with what this change is and why — a few sentences that
  let the reader know what follows before they hit it. This is the *function* of a paper's
  abstract, not a mandated "Abstract" heading.
- **Let structure follow the material.** No fixed section skeleton. A migration, a new
  endpoint, and a refactor should not come out the same shape. Impose only the structure
  this specific change needs — imposing sections it doesn't is as much a failure as bloat.
- **Say each thing once.** No restating a point in different words, no summary that repeats
  the body. Put conclusions in the artifact; leave out the analysis that produced them.
- **Readable beats short.** Cut what doesn't change what the reader would do next — not by
  compressing into fragments, arrow-chains, or jargon. If forced to choose, choose clear.

## Driver-facing decisions (open questions, low-confidence flags, driver calls)

The reader is a competent but busy tech lead reviewing many stories at once. They will
read your block, make a call, and move to the next of a hundred like it — optimize for
comprehension and decision speed. They approved this work weeks ago and do NOT remember
the codebase's function names; write so no memory of it is required.

- **Claim → conflict → decision → anchors, in that order.** What's true in plain words,
  what it collides with, the question with a recommendation — and only then the
  file/function references, at the end as verification anchors. The reference supports
  the sentence; it is never the sentence.
- **Anchors are self-contained and clickable.** The reader must be able to decide without
  opening a second tab, so bring the evidence to them: quote the two or three lines that
  actually matter (fenced, with the path above them), and link every reference as a
  GitHub permalink — `[path/file.py:88](https://github.com/<owner>/<repo>/blob/<commit-sha>/path/file.py#L88)`,
  pinned to a commit SHA (a branch link rots as the branch moves). A bare `file.py:88`
  with no quoted content is the failure mode: it makes the reader do the lookup you
  already did. If the evidence is too long to quote, quote the decisive fragment and say
  what the rest contains.
- **Intent and effect, not mechanism.** "An already-locked test says a config without a
  fallback model is valid — this contract says it isn't; both can't hold" beats
  "contradicts `test_load_config_returns_structured_object_for_valid_toml`, whose
  `_valid_toml()` fixture…". Name what a thing is *for*, not what it is called.
- **Price the choice.** Say what approving wrongly costs ("these become locked tests —
  a wrong call here is expensive to unwind") so urgency is calibrated without the reader
  reconstructing it.
- **One decision per block, recommendation first.** Three sentences a reviewer can read,
  agree with, and move past.

Worked example — the same blocker, both ways:

> ❌ the contract's "`[models] default` required unconditionally" error case directly
> contradicts the already-locked `tests/test_config.py::test_load_config_returns_structured_object_for_valid_toml`,
> whose `_valid_toml()` fixture has the five standard steps and no `default`…

> ✅ This contract makes a fallback model mandatory in every config. An already-locked
> test says a config without one is valid — both can't be true. Recommend: only require
> the fallback when custom flows exist, since that's the only case that needs it; the
> alternative is authorizing an edit to a locked test. (contract §error-cases; locked:
> `test_config.py::test_load_config…`)

## Report shape (BLUF)

Every artifact is a report to a busy manager. Reports earn fast reading through
ordering, not headings:

- **Bottom line up front.** The first line states the outcome or the ask — what
  happened, or what's needed from the reader — before any context. A reader who
  stops after one line should leave with the verdict. ("All six slices merged; this
  PR ships the story" / "Blocked: two contracts contradict — decision needed.")
- **Pyramid order.** Governing conclusion first, then the few points that support
  it, then evidence. Never narrative order ("first I looked at… then I found…") —
  the reader gets your conclusions, not your journey.
- **Status updates read done / issues / next.** What completed, what's wrong or
  waiting, what happens next — in that order, nothing else.
- **Titles follow the pipeline grammar** — `[planning] <STORY-ID>: <title>`,
  `[<slug>][<stage>][<k>/<N>] <slice>`, `[story] <STORY-ID>: <title>`. The runner
  lints these and blocks auto-merge on violations; a title is the one line most
  readers ever see, so it carries story, stage, and review order on its own.

These are ordering principles layered onto the rules above — BLUF does not add
sections, and pyramid order composes with "let structure follow the material."

This governs written artifacts, not conversational pacing, and it is not a template.
