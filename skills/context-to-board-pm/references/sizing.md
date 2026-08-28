# Driver-attention sizing — the `Duration` term for CD3

Read when sizing a chunk/story or setting CD3's `Duration`. The binding constraint is **driver
attention**, not agent code-generation — so "size" means the scarce human attention a story will
consume across its two touchpoints: the **spec interrogation** at the front and the **evidence
review** at the end. This score is CD3's denominator (`CD3 = CoD ÷ Duration`).

**Central idea:** drop velocity/effort points. Size by driver attention, **coarse and judged, not
computed** — stories vary too much in nature for one formula to fit fairly.

## The read

Produce a **coarse attention tier** (S / M / L, or 1–5), **shown with its reasoning** and **naming
which driver drove it**. It is a pre-run estimate; realized run data calibrates it (see
Calibration).

Three drivers — a **lens menu, no fixed weights**:

1. **Blast-radius / reversibility — the anchor.** Does the change touch a public contract, a
   shared invariant, a root config, a security/billing path? High blast-radius / low
   reversibility → careful, expensive review of the evidence and a warier interrogation. Local,
   reversible, internal → cheap on both ends. Read it off the story's Constraints / Context.
2. **Interrogation weight.** How much intent must the driver hold and answer questions about in
   one sitting? A story whose spec raises many genuine driver-decisions (product trade-offs,
   irreversible choices) is heavier than a large-but-settled one. This is also the **ceiling
   check**: if the spec can't fit one coherent interrogation, the chunk is over the bar — recut.
3. **Evidence surface.** How much demonstrated acceptance must be reviewed at the end — how many
   AC demonstrations, how much of the outcome must be seen working? An MVP with five observable
   behaviors reviews heavier than one with two, whatever their diff sizes. Diff size itself is
   *not* a driver — results are reviewed by evidence, not by reading the diff.

**Name the driver.** *"L — high blast-radius (touches the merge gate's contract), though the
evidence surface is small."* A bare tier isn't auditable; naming the driver keeps the read honest
across wildly different stories.

## Don't double-count risk

Risk appears in CD3 twice, meaning two different things — keep them distinct:

- **CoD numerator** (risk-reduction / opportunity-enablement) = the **value of retiring** risk.
- **Duration denominator** (blast-radius) = the **attention this change consumes**.

A config flag disabling a dangerous feature: high de-risk value (CoD ↑), tiny reversible change
(Duration ↓) → CD3 high, do first. A large public-API refactor for cleanliness: little risk
retired (CoD low), huge blast-radius (Duration ↑) → CD3 low, defer. Never let "it's risky"
inflate both for the same reason.

## Calibration — anchors are pending, and that's the honest state

**The v1 anchors are retired** (they measured per-slice PR review in the retired pipeline shape)
and **v2 has no realized runs yet** — so until the first real workflow runs land, sizing is pure
relative judgment: rank the increment's chunks against each other and against the floor/ceiling,
and say so plainly in the artifact.

The calibration loop replaces folklore with data: each workflow run feeds back a signal —

- **blew up mid-run** (chunk too big or spec too thin → tighten ceiling / interrogation weight),
- **stalled on ambiguity** (interrogation missed a decision → lens gap, not size),
- **finished trivially** (below the MVP floor → floor set too low or chunk mis-cut),
- **run wasted on a spec gap** the path check should have caught (check lens gap),

and those signals establish the realized reference stories that become the anchor table here.
Record anchors as they emerge; a tier judged against a realized anchor beats any formula at this
data volume (reference-class forecasting in its sparsest form: comparison, not statistics).

## What this replaces

Velocity story points / Fibonacci (effort-to-write isn't what costs when an agent implements),
and v1's per-slice review-load read (slice count no longer reaches the driver — fine slicing is
workflow-internal, and review happens on evidence at the story level).

## Evidence & caveats

- **Strong (2025–26, multiply-sourced):** human review is the binding constraint under
  AI-accelerated output; size-by-review-attention feeds CD3's `Duration`; blast-radius /
  reversibility tiering is an established governance signal.
- **Thin / synthesis (hence judge, don't compute):** driver weighting is not empirically fixed;
  the interrogation-weight and evidence-surface lenses are v2 constructs awaiting realized data;
  the whole thesis is recent — revisit if AI review-assist matures and relaxes the constraint.
