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

This governs written artifacts, not conversational pacing, and it is not a template.
