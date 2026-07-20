#!/usr/bin/env python3
"""Check study.py's FSRS-6 port against reference output from the real ts-fsrs.

    node test_fsrs_parity.mjs > /tmp/fsrs-ref.jsonl
    python3 test_fsrs_parity.py /tmp/fsrs-ref.jsonl

Exits non-zero on any mismatch. Tolerance is 1e-8 on the roundTo(_, 8) values
(last-ULP differences between JS and Python transcendentals are expected);
intervals must match exactly.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from study import next_state, next_interval, forgetting_curve  # noqa: E402

TOL = 1e-8


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/fsrs-ref.jsonl"
    rows = [json.loads(l) for l in open(path) if l.strip()]
    if not rows:
        print("no reference rows — did the node side run?", file=sys.stderr)
        return 1

    fails = []
    max_dd = max_ds = max_dr = 0.0
    for i, r in enumerate(rows):
        if r["kind"] == "curve":
            got = forgetting_curve(r["t"], r["s"])
            diff = abs(got - r["er"])
            max_dr = max(max_dr, diff)
            if diff > TOL:
                fails.append(f"curve t={r['t']} s={r['s']}: got {got}, want {r['er']}")
            continue

        gd, gs = next_state(r["d"], r["s"], r["t"], r["g"])
        gi = next_interval(gs)
        dd, ds = abs(gd - r["ed"]), abs(gs - r["es"])
        max_dd, max_ds = max(max_dd, dd), max(max_ds, ds)
        ctx = f"{r['kind']} d={r['d']} s={r['s']} t={r['t']} g={r['g']}"
        if dd > TOL:
            fails.append(f"{ctx}: difficulty got {gd}, want {r['ed']}")
        if ds > TOL:
            fails.append(f"{ctx}: stability got {gs}, want {r['es']}")
        if gi != r["ei"]:
            fails.append(f"{ctx}: interval got {gi}, want {r['ei']}")

    print(f"{len(rows)} reference cases")
    print(f"max abs diff — difficulty {max_dd:.2e}, stability {max_ds:.2e}, retrievability {max_dr:.2e}")
    if fails:
        print(f"\nFAIL ({len(fails)} mismatches):")
        for f in fails[:20]:
            print("  " + f)
        if len(fails) > 20:
            print(f"  … and {len(fails) - 20} more")
        return 1
    print("PASS — Python port matches ts-fsrs on every case")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
