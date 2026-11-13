# Eval: can a newcomer follow the walkthrough text?

Run on every spec before it is rendered. One model call, read-only, about 20 s.

Reader: a competent engineer who has never seen this codebase and has only
the page. Reading order: primer (goal, model, prequestions, terms), the
top-level why, then each stop's title, does, why, question. The code for each
stop is visible on the page, so line references are fine.

Report per spec:
1. Undefined terms at first use (term, where, quote, the definition owed).
2. Forward references (relies on something explained only later).
3. For each stop question and primer prequestion: answerable from the page?
4. Score 1-5: "a newcomer could follow this without opening the code".

End with `SCORE <spec>: n/5` and `TERMS <spec>: a | b | ...`.

Gate: score 4 or more, and no term in TERMS that a stop's question depends on.
Fix by defining the term in the primer's terms (it is then marked where each
stop first uses it), not by adding prose to the stop.

History (13 Nov 2026, first two demos): review 3/5 -> 4/5 (3.5) after adding
the primer; tour 4/5 -> 4/5. "cursor" was the top undefined term in both
before, and gone after.
