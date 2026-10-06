# Review-load sizing — the `Duration` term for CD3

Read when sizing a story or setting CD3's `Duration`. Cadre's binding constraint is **human review**,
not agent code-generation — so "size" here means **expected human-review load**, not effort-to-write.
This score is CD3's denominator (`CD3 = CoD ÷ Duration`).

**Central idea:** drop velocity/effort points. Size a story by how much scarce human review it will
consume. **Coarse and judged, not computed** — Cadre stories vary too much in nature for one formula
to fit fairly.

## The read

Produce a **coarse review-load tier** (S / M / L, or 1–5) for the story, **shown with its reasoning**
and **naming which driver drove it**. It is a *pre-planning estimate* — planning's actual slice count
refines it later; realized review data (someday) calibrates it (see Calibration).

Three drivers — a **lens menu, no fixed weights**:

1. **Blast-radius / reversibility — the anchor** (the signal pm can judge honestly at story-time).
   Does the change touch a public contract, a shared invariant, a root config, a security/billing
   path? High blast-radius / low reversibility → careful, expensive review. A local, reversible,
   internal change → cheap review. Read it straight off the story's Constraints / Context.
2. **Expected scope — rough.** How much surface does the outcome touch? Bigger surface → more to
   review. No real diff exists yet, so this is a gauge, not a measurement.
3. **Slice / PR count — rough** (planning owns the real number). Each slice lands as a PR = one
   discrete review event; one-slice vs many → few vs many review events. pm estimates "one slice or
   several?"; planning's count updates it.

**Name the driver.** Because story types vary, say which one dominated: *"L — high blast-radius (touches
the merge gate's public contract), though scope is small."* The justification is the point; a bare tier
isn't auditable, and naming the driver is what keeps the read honest across wildly different stories.

## Don't double-count risk

Risk appears in CD3 twice, meaning two different things — keep them distinct:

- **CoD numerator** (risk-reduction / opportunity-enablement) = the **value of *retiring*** risk (doing
  this makes future incidents / blockers go away).
- **Review-load denominator** (blast-radius) = the **review attention *this change* consumes**.

A change can be high on one and low on the other:

- Config flag disabling a dangerous feature → high de-risk **value** (CoD ↑), tiny reversible change
  (review-load ↓) → **CD3 high, do first.**
- Large public-API refactor for cleanliness → little risk retired (CoD low), huge blast-radius
  (review-load ↑) → **CD3 low, defer.**

Never let "it's risky" inflate both for the same reason.

## Calibration — anchor by analogy (cold-start)

No statistical model yet: Cadre has too few completed items for reference-class forecasting or Monte
Carlo to mean anything, and measuring realized review *effort* needs board↔code reach the pm doesn't
have yet. So anchor the tier against a few **realized reference stories**:

| Anchor | ~Review-load |
|---|---|
| a small isolated fix (a CI/config one-liner) | **S** |
| a mid single-outcome feature | **M** |
| a multi-slice skeleton touching many modules (PIPE-1-scale) | **L** |

Judge the new story *relative* to these — "heavier review than the skip-gate fix, lighter than the
skeleton." That is reference-class forecasting in its simplest sparse-data form: comparison, not
statistics.

**Graduation path (deferred, not built):** once Cadre has more completed items *and* pm can read
realized PR review data (comment rounds, re-review churn — review **effort**, not raw latency, which is
mostly queue-wait), the anchors become data-backed and the method can adopt bucketed RCF / Monte Carlo.
That reach arrives with the board↔code sync capability.

## What this replaces

The old "`Duration` = person-days" hand-wave. And it is **not** velocity story points / Fibonacci —
those estimate effort-to-write, which isn't what costs when an agent implements in hours.

## Evidence & caveats

- **Strong (2025–26, multiply-sourced):** human review is the binding constraint under AI-accelerated
  output; size-by-review-load feeds CD3's `Duration`; PR size + description length are the top
  review-latency predictors; blast-radius / reversibility tiering (HARD/SOFT/AUTO) and per-change risk
  scoring are established governance signals.
- **Thin / synthesis (hence *judge, don't compute*):** the exact weighting of the three drivers is not
  empirically fixed; review *latency* ≠ review *effort*; raw line-count does **not** predict rejection
  (use slice count + blast-radius, not line thresholds); much of the multiplier data is
  vendor-published; the whole thesis is recent — revisit if AI review-assist matures and relaxes the
  constraint.
