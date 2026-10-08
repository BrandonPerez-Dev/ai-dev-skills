# Machine gate and review heuristics

Reference for auto-low-level-design. Load at step 5 of every run.
Source: design record §5, §9.

## Gate

A full run passes all nine; a lite run passes G1, G2, G5, G6, G7 for the touched symbols.
`scripts/design-check` automates G1, G2, G3, G5, G8 and the R6 size warning; the rest you check and list on the
page as pass or fail.

| # | Check | How |
|---|---|---|
| G1 | Skeleton type-checks | `design-check` runs `stack.typecheck` |
| G2 | Architecture's boundary rules pass on the skeleton | `design-check` runs `stack.boundary` |
| G3 | Map and tree agree: each module's Entry exists; each code directory under `source_root` holds a module | `design-check` parses the map |
| G4 | Every public symbol has a doc comment | per-stack check (`per-stack.md`) |
| G5 | Snapshots regenerate identical to the committed files | `design-check` runs each `snapshot_cmd`, compares, restores |
| G6 | If test-writer ran: locked tests compile and fail with the unimplemented marker, not import or type errors | run the tests; grep the failures for the marker |
| G7 | Every new public symbol has a reuse row; every `new` row shows what was searched | read the table |
| G8 | Duplication at or below baseline | `design-check` runs `duplication.cmd`, reads `report`, compares to `baseline` |
| G9 | Each extension point names ≥2 real variants or links an ADR | read **Extension points**; in Rust also count `impl Trait for` |

```
python3 scripts/design-check            # all automated checks, exit 1 on any failure
python3 scripts/design-check --only G5  # one check
```

**Build's lock.** Build's full-suite gate runs `design-check`, so G5 fails any widened or changed signature.
The locked paths stop build editing a snapshot to make G5 pass.

**Setting the baseline.** On a full run, after the skeleton is written:
`python3 scripts/design-check --write-baseline` records the current duplication percentage. Only this node runs it.

## Which design heuristics are automatable

| Heuristic | Verdict | Why |
|---|---|---|
| One public entry, no deep imports | Gate | lint plus compiler |
| Every public symbol documented | Gate (G4) | api-extractor flags undocumented members (observed) |
| Pass-through methods | Advisory only | `py_design_smells.py` found the real case plus 1 false positive in 2 flags (observed) |
| Premature extension point | Gate in Rust; map check in TS and Python (G9) | structural types are never named by implementers |
| Rule of three | Doc check at design time | an extract-shared row cites 3 call sites |
| Deep vs shallow module | Judgement | ask: is the interface smaller than what it hides? |
| Information leakage | Judgement | LLM smell detection recall 0.41 (arXiv 2504.16027, moderate) |

The advisory report goes on the page and to the review node. It never fails a run or a build.
