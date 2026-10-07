# Technology selection — baseline, tokens, exit cost, bias

Reference for the auto-architecture skill. Load in round 0 (to state the baseline) and in any deep dive that
picks a product, framework or data store. Sources: McKinley, *Choose Boring Technology* (2015); Hohpe & Fowler
on exit cost (2019); Wardley evolution axis; arXiv 2503.17181 (2025) on LLM language bias; arXiv 2509.11132
(2025) on agent proficiency by stack.

## Start from a boring baseline

State it on the round-0 page as **the baseline to deviate from**. Every deviation is a decision card.

| Stack | Baseline (draft — confirm against the person's existing projects) |
|---|---|
| TypeScript | Node LTS, one HTTP framework already in use, PostgreSQL, a Postgres-backed job table before any broker, dependency-cruiser for boundaries |
| Python | CPython current, FastAPI or the framework already in use, PostgreSQL, a Postgres-backed job table, import-linter for boundaries |
| Rust | Stable toolchain, workspace of crates, tokio + axum in the adapters crate only, PostgreSQL via sqlx, cargo-deny for bans |

Draft status: these baselines were chosen by the implement round, not by the driver. The person's own default stack overrides them.

## Innovation tokens

The project gets about three innovation tokens (McKinley; the number is opinion). Spending one means choosing
something new to the person or to the team of agents. On every card, tag whether an option spends a token.
Spend tokens only on what differentiates the product.

## Build, buy or rent — by evolution stage

Tag each option on the card (Wardley evolution axis, weak evidence):

| Stage of the capability | Default |
|---|---|
| Commodity (auth, email, payments, queues, storage) | Rent or buy. Building it spends a token for no advantage. |
| Product (well understood, several vendors) | Buy or adopt open source; wrap behind a port. |
| Custom / differentiator (the reason the product exists) | Build. This is where tokens go. |

## Exit cost

Exit cost = migration cost − what you gain by staying (Hohpe & Fowler). Ask per option:
- What data or code would have to move, and in what format is it held?
- Which interfaces leak vendor concepts into the domain? (If any, put a port in front.)
- Is there a second vendor or open-source equivalent today?
- What is the switch sketch if we leave in a year?

Record the answers as the parked option's `Seam` and `Switch sketch` in the decision record.

## Agent proficiency

Ask: how well do coding agents handle this stack? Signals: size of public training corpus, stability of the
API across versions, strong types and clear module boundaries (which raise harnessability). Evidence that
proficiency varies by stack: arXiv 2509.11132 (weak–moderate).

## Your popularity bias — disclose it every time

LLMs favour popular tools: across 8 models, Python was chosen in 90–97% of tasks, and models contradicted their
own language recommendations 83% of the time at project start (arXiv 2503.17181, moderate–strong). So:
- Every card with a technology choice states: *"I lean toward X. I am biased toward popular tools. The case
  against X is …"*
- The contrary case is mandatory and not shorter than one sentence.
- Your recommendation is not a fit signal on its own; the person's top-3 qualities and exit cost are.

## A technology choice becomes a rule only when it protects a quality

Data-layer and framework mandates are the costliest constraints for agents (Dente et al., arXiv 2605.06445:
−20.4 points for a PostgreSQL mandate). Turn a technology choice into a boundary rule only when its decision
record names the quality it protects.
