# Rightsizing a skill for the Claude 5 generation

The repeatable recipe for converting an over-constrained skill (written for older models)
into a lean one that suits Claude 5 generation models (the Claude 5 family, Opus 4.8,
Haiku 4.5). Read this before rightsizing any existing skill; it is the standard the
`skill-maintenance` rightsizing operation applies.

Source: Anthropic, "The new rules of context engineering for Claude 5 generation models"
(claude.com/blog, 2026). Anthropic removed >80% of Claude Code's system prompt for this
generation with no performance loss. The old constraint-heavy authoring style now *hurts*:
it spends context, dilutes the real gates, and reads as noise the model skips.

## The reframe

Older models needed rules and repetition. Claude 5 rewards **judgment** and **single
statement**. A skill's job shifts from "fence every path" to "state the thesis, explain the
why once, and trust the model to generalize." This does not mean gutting the skill — it
means cutting what no longer changes behavior. As always: **measured delta decides, not
authoring taste** (see the core loop). Rightsizing is a hypothesis until an eval confirms it.

## The dominant anti-pattern: restatement + gate inflation

Two signatures account for most over-constraint. Hunt them first.

1. **Triple-table restatement.** The same directive appears in a `<HARD-GATE>`, then again in
   an "Anti-Patterns" table, then again in a "Guidelines" table (sometimes a "Bias Guards"
   table too). Three-to-five copies of one rule. Detection: pick any load-bearing rule and
   grep it across the file — if it recurs in the closing tables, collapse to one statement in
   the most relevant place.
2. **`<HARD-GATE>` inflation.** Most gates guard *quality or process discipline*, not a
   safety/money/irreversible/trust boundary. A skipped grill or an unrun linter is
   recoverable; those are not gates. Emphatic framing on recoverable steps is decorative —
   demote it to a motivated principle.

## KEEP list — the only places emphatic gates survive

Rightsizing must not strip a real safety gate. Across the corpus, genuine critical-area gates
reduce to a short, stable set. Keep these firm (once each); treat everything else as principle:

- **Propose-before-write / no external mutation without approval** — anything that writes to a
  user's board, repo, or account.
- **No commit/push/merge/PR or other outward, hard-to-reverse action without explicit go-ahead.**
- **Locked-test immutability** and **no implementation before a failing test** (test-first skills).
- **Irreversible git operations** — force-push, `reset --hard`, `clean -f`.
- **Checker must not fix** — a verifier that also edits can't be trusted (verification skills).
- **Never auto-merge an optimized/generated artifact** — a human diffs and approves.

If a gate isn't protecting one of these, it's emphasis, not a gate.

## The procedure

1. **Inventory directives.** List every rule, gate, and table row. Mark each: KEEP-gate (on the
   list above), or candidate-principle (everything else).
2. **Collapse duplicates to one.** For each rule stated more than once, keep the single clearest
   instance in the most relevant section; delete the rest. The three closing tables usually
   merge into at most one short bias-guard list of the *domain-specific* rationalizations.
3. **Demote non-critical gates to motivated principles.** Replace "NEVER do X / MUST do Y" with
   the reason, stated once: "do Y, because Z." Models generalize from a motivated rule to cases
   the skill never enumerated; a bare imperative does not, and does not survive compaction.
4. **Progressive disclosure.** Move depth only some runs need — long templates, per-work-type
   checklists, domain catalogs, dated tool picks — into `references/`, named from SKILL.md with
   a line saying when to read each. Keep the interface (output format, decision table) inline.
5. **De-duplicate across siblings.** If several skills restate the same lore (e.g. mock-boundary
   rules, or an `auto-*` variant near-duplicating its interactive sibling), extract it to one
   shared reference both load; each SKILL keeps only its distinctive posture.
6. **Run skill-creator's self-review checklist** against the result.
7. **Measure before trusting the recipe at scale.** Rightsize ONE skill, then run a baseline A/B
   (new vs a snapshot of the old) through the harness. Require: no regression on the skill's
   behaviors, at equal-or-lower token cost. Only after one skill validates do you roll the same
   recipe across a batch — don't mass-edit on the theory alone.

## Done looks like

- Central thesis intact and stated once; every remaining section serves it.
- Emphatic language survives only on KEEP-list gates; elsewhere, motivated principles.
- No rule stated more than once; at most one closing bias-guard list.
- Run-specific depth lives in `references/`, not inline.
- A baseline A/B shows the lean version holds behavior at equal-or-lower tokens.
