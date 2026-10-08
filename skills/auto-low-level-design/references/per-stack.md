# Per-stack conventions — TypeScript, Python, Rust

Reference for auto-low-level-design. Load when writing the skeleton, snapshots or `design.toml`.
Source: design record §4; every *observed* entry was run in
`/home/juiz/research/engineering-nodes-2026-10/nodes/lld-gate-demo/` (re-run with its `run.sh`).

| | TypeScript | Python | Rust |
|---|---|---|---|
| Public entry | One `index.ts` per module; TSDoc `@public` | `__init__.py` with `__all__`, plus `py.typed` | `lib.rs` with `pub use`; `pub(crate)` by default; one crate per hard boundary |
| Port / extension point | `interface` | `typing.Protocol` | `trait` |
| Unimplemented body | `throw new Error("unimplemented")` | `raise NotImplementedError` | `todo!("<fn name>")` |
| Type-check (G1) | `tsc --noEmit -p .` (observed PASS) | `mypy --strict src`, `pyright src` (observed clean) | `cargo check --all-targets` (observed PASS) |
| API snapshot (G5) | `api-extractor run --local` writes `api/<pkg>.api.md` (observed: CI mode exits 1 on an added export) | `scripts/py_api_snapshot.py <pkg> src > api/<pkg>.api.txt` (observed: diff fails on a name added to `__all__`) | `cargo +nightly-<pinned> public-api -s > api/<crate>.api.txt` — pinned nightly, decided 2026-10-06; not yet run |
| Release breakage (separate concern) | api-extractor report diff | `griffe check --against <tag>` | `cargo semver-checks` (stable) |
| Doc comments (G4) | no `// (undocumented)` in the report (observed) | griffe docstring field | `#![deny(missing_docs)]` |
| Deep-import ban | dependency-cruiser (architecture's config) | import-linter (architecture's config) — **mandatory** | compiler visibility |
| Duplication (G8) | jscpd | jscpd | jscpd (observed: one tool, all three languages) |

## Caveats found by running the tools

1. **api-extractor bundles its own TypeScript** (5.9.3 while the project's tsc was 7.0.2, observed). Pin both and
   prove the pair with a G5 run at project start.
2. **Python's surface is `__all__`.** A function left out of it is invisible to the snapshot (observed: empty
   diff). That only holds if deep imports are banned, so architecture's import-linter rule is required.
3. **jscpd matches tokens; agents mostly produce semantic clones** it misses (Huang et al., MSR 2026, moderate).
   The baseline is a floor sensor; the design record's measurement plan adds sampled semantic checks.
4. **Structural typing defeats implementation counting.** Python Protocols and TS interfaces are not named by
   implementers, so G9 is a map check (variants named in **Extension points**) outside Rust; in Rust also count
   `impl Trait for`.
