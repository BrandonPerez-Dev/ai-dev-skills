# Prioritization frameworks — formulas, scales, sources

Read this before applying RICE or WSJF, or when asked to justify a scale. Formulas below were
adversarially verified (3-0 confirmation) against originator-traceable sources on 2026-08-02; the
refuted variants are listed so they don't creep back in.

## ICE (quick-triage fallback)

The ready-lane **default is CD3 / WSJF** (below) — Cost of Delay ÷ Duration, with **Duration =
review-load** (`references/sizing.md`). ICE is the fast rough-cut when a full CoD estimate isn't worth
it.

```
ICE = Impact × Confidence × Ease
```

- Each factor rated ~1–10. **Multiplicative, not an average.**
- No Reach term — a change touching 100 users and one touching 100,000 score equally if per-unit
  impact and ease match. That's the gap RICE closes; accept it as the price of ICE's speed.
- Popularized by Sean Ellis. Best for a single scorer with no tooling.
- ⚠️ **Refuted variant (do not use):** `ICE = (Impact + Confidence + Ease) / 3` (arithmetic mean) —
  refuted 0-3. ICE multiplies.
- Sources: productplan.com/glossary/ice-score, fygurs.com, productlift.dev.

## RICE (escalate: reach varies widely)

```
RICE = (Reach × Impact × Confidence) / Effort
```

- **Reach** — units (users/consumers) affected in a defined period.
- **Impact** — fixed scale: Massive 3, High 2, Medium 1, Low 0.5, Minimal 0.25.
- **Confidence** — percentage: 100% / 80% / 50%.
- **Effort** — originator uses person-months; **for Cadre use person-days** (agent cycle time is
  hours/days). Effort is the divisor → lower effort raises the score.
- Originator: Intercom (Sean McBride, 2016/2018), built by adding Reach to ICE.
- Sources: intercom.com/blog/rice-simple-prioritization-for-product-managers, kayako.com,
  centercode.com, pmtoolkit.ai, fygurs.com, productlift.dev.

## WSJF / CD3 (default — ready-lane sequencing)

```
WSJF = Cost of Delay / Job Size          (CD3 = the same arithmetic: CoD ÷ Duration)
Cost of Delay = User/Business Value + Time Criticality + Risk Reduction / Opportunity Enablement
```

- **CD3 is the WSJF arithmetic** (CoD ÷ Duration). Cadre uses it as the **ready-lane default for
  individual stories**, with **Duration = review-load** (`references/sizing.md`) rather than effort. At
  the initiative level the same formula sequences projects with coarser inputs.
- SAFe scores each CoD input on a **modified Fibonacci** scale (1,2,3,5,8,13,20); **Cadre deliberately
  uses a 1–10 relative scale** for the three CoD components (a house simplification — a design choice,
  not the SAFe prescription). Job Size / Duration is the denominator, NOT part of CoD.
- Originator: SAFe (framework.scaledagile.com/wsjf).
- ⚠️ **What was refuted (0-3):** the *claim that SAFe prescribes a 1–10 scale* — SAFe uses Fibonacci.
  (Cadre's 1–10 is a deliberate house simplification, not a claim about SAFe.)

## Framework routing — author-decided, NOT cited

The claim that "RICE fits small-team feature decisions, WSJF fits portfolio/multi-team decisions" was
**refuted 0-3** — there is no citable boundary for when to switch frameworks. The routing in SKILL.md
(default ICE; RICE only on wide reach variance; WSJF only at initiative level) is a deliberate design
choice for this shop, not a sourced rule. Revisit with the driver if it stops fitting.

## Evidence caveats

- Framework details rest largely on PM blogs, but every formula traces cleanly to its originator
  (Intercom for RICE/ICE, SAFe for WSJF) and is cross-corroborated — high confidence on the math.
- The frameworks are stable (2016–2018); low time-sensitivity.
- The Linear MCP surface is fast-moving ("more functionality on the way") — introspect the live tool
  schema rather than hard-coding capabilities.
