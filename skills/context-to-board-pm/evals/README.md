# Evals — v2 suite

`evals.json` holds 5 cases against a self-contained fixture (`fixtures/`): the invented
**beacon** project — a mini hub (intent doc, three governing decisions, one research
finding) plus a board snapshot. The fixture plants traps the assertions check for:

1. **Plan increment** — agenda-not-full-plan, MVP-grade chunks, coverage map citing the
   three governing decisions, proposed-writes discipline.
2. **Story writing** — six-section standard + context manifest; the deliberately
   unsettled question (replay ordering) must surface as interrogation/hub-debt, never be
   silently decided.
3. **Sync** — BEA-2 is rotted (contradicted by newer retry-storm research): flag with
   evidence, suspend, no silent correction.
4. **Too-small** — a solo `--version`-flag story must be refused in favor of
   ride-along/batch (MVP floor).
5. **Subordination** — the driver asks to plan against a recorded hub decision: surface
   the conflict, offer the amendment path, never plan around the hub (and never flatly
   refuse).

Baseline for A/B: the v1 `pm` skill (snapshot from `origin/main:skills/pm`). The Linear
MCP is offline in eval runs — the board snapshot file stands in, and writes are asserted
as *proposals* (which is the skill's contract anyway).

The v1 `evals.json` was removed rather than carried: its cases tested v1 flows, and stale
passing cases are a lying gate, not coverage.
