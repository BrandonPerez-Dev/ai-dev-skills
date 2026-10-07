# Decision card and decision record

Reference for the auto-architecture skill. Load for every heavy decision (rounds 2..n+1 and revisits).
Source of truth: the design record `/home/juiz/research/engineering-nodes-2026-10/nodes/architecture.md` §A3, §A5, §A8.

The **card** is the conversation on the page. The **record** is what gets locked in Cadre. The **north-star
brief** collects the records' one-sentence versions.

## The card

One screen: about 150–250 words plus a small table. No study validates the card as a whole; each part's
evidence is noted.

1. **Question and why now** — one line.
2. **Your read first** — on **high-stakes cards only**, and always on those (driver call 1, option A, settled at
   approval). Before your lean is shown, the person writes their pick and what they think would make it fail.
   Put your lean in a collapsed `<details>` the person opens after answering. Cognitive forcing functions cut
   over-reliance on AI advice more than explanations do, and people like them least (Buçinca et al. 2021,
   N=199, strong).
   A card is high-stakes when it is marked **firm**, or its exit cost is high, or it touches two or more of the
   top-3 qualities. Expect a handful per project.
3. **2–3 real options**, including the simplest thing that could work. Each with the one mechanism that drives
   its trade-off (Ousterhout, "design it twice").
4. **Trade-off table** — 3–4 criteria, the person's top-3 qualities first, written in words, not scores. One
   "flips if…" line. Weighted scores invite weight-tuning and rank reversal.
5. **Fit tags per option** — commodity or differentiator; spends an innovation token?; exit cost; agent
   proficiency. See `technology-selection.md`.
6. **Your lean, with a bias disclosure** — "I lean toward X; I am biased toward popular tools; the case against
   X is …". Keep the rationale short: written AI rationales alone increased over-reliance (Vasconcelos et al.,
   CSCW 2023, strong). The contrary case is mandatory.
7. **Reversibility and the revisit signal** — firm or provisional; what would reopen this.
8. **The person's one-sentence version** — after deciding, the person states it in their own words, in
   Y-statement shape. You correct only errors. This sentence goes into the record and the brief.
9. **Audience versions on request** — investor, contractor, agent brief.

### Y-statement shape

> In the context of *X*, facing *Y*, we chose *Z* over *W* to get *Q*, accepting *D*.

## Worked example

> **Where do background jobs run?** Needed now: invoice sending is the first slice's slow step.
>
> **Your read first** (high-stakes: firm, touches reliability and cost). Your pick, and what would make it fail?
>
> | | A. Postgres table as queue | B. Redis + queue library | C. Managed queue |
> |---|---|---|---|
> | Reliability (top-1) | Jobs commit in the same transaction as the invoice | Separate store; needs an outbox for atomicity | Separate service; needs an outbox |
> | Cost (top-3) | No new infrastructure | One more service to run | Per-message billing, no ops |
> | Throughput | Fine to thousands of jobs/min | High | High |
> | Fit | Commodity, no token, low exit cost | Commodity, no token, medium exit cost | Commodity, no token, vendor lock-in |
>
> Flips if: job volume passes what one Postgres comfortably handles, or jobs must fan out to other systems.
>
> <details><summary>My lean</summary>A. I am biased toward popular tools (which here favours B). The case
> against A: polling load on the primary database, and a migration later if volume grows. Seam that keeps B
> cheap: a `JobQueue` port with the table as its first adapter.</details>
>
> **Your version:** "In an invoicing app with low job volume, facing the need to send invoices reliably, we
> chose a Postgres job table over Redis to commit jobs atomically with invoices, accepting a migration if volume
> outgrows one database."

## The record (locked in Cadre)

MADR 4.0 minimal, plus three revisit fields. Gate G5 lints it.

```markdown
status: accepted | superseded by NNNN      firmness: firm | provisional
# NNNN <title>
<the person's one-sentence version — Y-statement shape>
## Options considered
1. <chosen> — chosen.
2. <alternative> — parked. Why not now · Reconsider if · Seam that keeps it cheap (+ rule protecting it) · Switch sketch
## Assumptions        | id | assumption | signal | invalid when |
## Confirmation       rules / invariants / manual checks that enforce it
## Revisit when       assumption invalid · rule blocks build twice in 10 slices · review date
```

Lint rules (G5): front-matter status; a Y-statement; at least 2 considered options; every parked option has
`Reconsider if`; at least one `Revisit when`. The only edit allowed to an accepted record is adding evidence to
its assumptions table; anything else is a superseding record.

## The north-star brief

About 600 words plus two diagrams (gate G7). Shown on the page first; where it is stored is decided later.

1. **North star** — 3–5 sentences: the system at full scale and the one or two dominant qualities.
2. **Why this shape** — the person's own one-sentence versions of the 3–5 heaviest decisions.
3. **Context and containers** — C4 levels 1 and 2; ports listed (they become test seams).
4. **Top three qualities** — scenario, numeric response measure, how it is checked.
5. **The slice path** — thinnest slice first, then the fill-in order, each step with an "advance when" condition.
6. **Firm vs provisional** — which decisions are expensive to reverse, and what would reopen each.
7. **Top risks** — at most five, each with what we do about it.
