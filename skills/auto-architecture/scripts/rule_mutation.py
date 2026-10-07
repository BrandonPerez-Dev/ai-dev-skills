#!/usr/bin/env python3
"""Rule-mutation gate: proves every architecture boundary rule bites.

For each rule declared in arch-mutations.toml:
  1. the boundary check passes on the untouched tree (baseline),
  2. a deliberate violating edit is applied,
  3. the check must exit non-zero AND its output must contain `expect`,
  4. the edit is reverted (always, even on crash).
A rule with no killing mutation fails the gate: it is decoration, not a sensor.

Usage: rule_mutation.py <project-dir>   (reads <project-dir>/arch-mutations.toml)
Exit 0 = every rule killed its mutant; 1 = at least one rule is toothless.
"""
import pathlib
import subprocess
import sys
import tomllib


def run(cmd: str, cwd: pathlib.Path) -> tuple[int, str]:
    p = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def main() -> int:
    root = pathlib.Path(sys.argv[1]).resolve()
    spec = tomllib.loads((root / "arch-mutations.toml").read_text())
    check = spec["check"]

    code, out = run(check, root)
    if code != 0:
        print(f"BASELINE FAIL: `{check}` must pass on the untouched tree\n{out}")
        return 1
    print(f"baseline: `{check}` passes")

    declared = set(spec["rules"])
    killed: set[str] = set()
    for m in spec["mutation"]:
        originals = {}
        try:
            for name in spec.get("snapshot", []):  # files tools rewrite as a side effect
                f = root / name
                originals[f] = f.read_text() if f.exists() else None
            for e in m["edits"]:
                f = root / e["file"]
                originals.setdefault(f, f.read_text() if f.exists() else None)
                f.write_text((originals[f] or "") + e["append"] + "\n")
            code, out = run(check, root)
        finally:
            for f, text in originals.items():
                f.unlink() if text is None else f.write_text(text)
        bit = code != 0 and m["expect"] in out
        print(f"{'KILLED' if bit else 'SURVIVED'}  {m['rule']:<24} exit={code} expect={m['expect']!r}")
        if bit:
            killed.add(m["rule"])

    code, _ = run(check, root)
    if code != 0:
        print("RESTORE FAIL: tree no longer passes after mutations")
        return 1

    toothless = sorted(declared - killed)
    print(f"{len(killed)}/{len(declared)} rules proven; toothless: {toothless or 'none'}")
    return 1 if toothless else 0


if __name__ == "__main__":
    sys.exit(main())
