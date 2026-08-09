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
  file/function references, parenthesized at the end as verification anchors. The
  reference supports the sentence; it is never the sentence.
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

This governs written artifacts, not conversational pacing, and it is not a template.
