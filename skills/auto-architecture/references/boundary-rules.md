# Boundary rules — per-stack formats, the mutation manifest, invariants, revisits

Reference for the auto-architecture skill. Load at the north-star freeze (to write rules) and in revisit mode.
Source of truth: the design record `/home/juiz/research/engineering-nodes-2026-10/nodes/architecture.md` Part B. Working examples of every config below are in
`/home/juiz/research/engineering-nodes-2026-10/nodes/architecture-proof/` (proven 8 of 8 rules across three stacks).

## Principles

- Rules protect the **north-star** boundaries from the first slice, firm and provisional alike.
- Rules arrive as **failing checks inside lint**, never as prompt text. Executable checks beat instructions
  (ContextCov, arXiv 2603.00822: 88.3% vs 67.0% compliance, moderate).
- **Budget: ≤ 7 active structural rules** per repo (gate G3). Stacked constraints cost agents functional pass
  rate (Dente et al., arXiv 2605.06445: −27.28 points stacked; −8.8 for layering alone). The budget is a measured
  setting; the paired run in the measurement plan tightens or loosens it.
- Every rule's message **cites its decision record and names the allowed path**, e.g. "ADR-0002: use cases
  depend on ports in app/ports, never on adapters". Showing the rule text with the failure resolved 79% of policy
  failures in an IaC loop (Jouini, arXiv 2607.20478, moderate, adjacent domain).
- The rule check runs inside the project's existing `lint` command. Build already requires lint to pass, so the
  rules enter the build loop without editing any skill.
- Rule files and `arch-mutations.toml` are **protected paths**, like locked tests. Build may not edit them; a
  `wall` revisit event is the legal escape.

## Per-stack formats

| Stack | Tool | Rule file | Lint command | Blind spot |
|---|---|---|---|---|
| TypeScript | dependency-cruiser 18.5 | `.dependency-cruiser.cjs` | `npx depcruise src --config .dependency-cruiser.cjs` | type-only imports unless `tsPreCompilationDeps: true`; computed dynamic `import()` |
| TS in Nx | `@nx/enforce-module-boundaries` | `eslint.config` + `project.json` tags | `nx lint` | project-level only, not folders (not run in the proof) |
| Python | import-linter 2.15 | `pyproject.toml` `[tool.importlinter]` | `lint-imports` | `importlib` / string imports |
| Rust | crate graph + cargo-deny 0.20 | workspace `Cargo.toml`, per-crate deps, `deny.toml` | `cargo check --workspace && cargo deny check bans` | module rules inside one crate — use `pub(crate)` |

### TypeScript (dependency-cruiser)

```js
module.exports = {
  forbidden: [
    { name: "domain-is-pure", severity: "error",
      comment: "ADR-0002: domain imports nothing from app, adapters, main, or npm packages",
      from: { path: "^src/domain/" }, to: { pathNot: "^src/domain/" } },
    { name: "app-not-adapters", severity: "error",
      comment: "ADR-0002: use cases depend on ports, never on concrete adapters",
      from: { path: "^src/app/" }, to: { path: "^src/(adapters/|main\\.ts)" } },
    { name: "no-circular", severity: "error",
      comment: "ADR-0002: module graph stays acyclic",
      from: {}, to: { circular: true } },
  ],
  options: { doNotFollow: { path: "node_modules" }, tsPreCompilationDeps: true,
             tsConfig: { fileName: "tsconfig.json" } },
};
```

### Python (import-linter)

```toml
[tool.importlinter]
root_package = "shop"
include_external_packages = true   # lets you ban third-party packages, even when not installed

[[tool.importlinter.contracts]]
id = "layers"
name = "ADR-0002 ports-and-adapters layering"
type = "layers"
layers = ["shop.adapters", "shop.app", "shop.domain"]

[[tool.importlinter.contracts]]
id = "domain-no-frameworks"
name = "ADR-0002 domain imports no third-party frameworks"
type = "forbidden"
source_modules = ["shop.domain"]
forbidden_modules = ["sqlalchemy", "httpx", "fastapi"]
allow_indirect_imports = true
```

Contract types: `layers`, `forbidden`, `independence`.

### Rust (crate graph + cargo-deny)

Prefer a crate split over any linter: rustc rejects an undeclared crate (`unresolved import`) and cargo rejects
the reverse dependency (`cyclic package dependency`). A new non-cyclic dependency is *not* caught by the graph;
that is what `deny.toml` wrappers are for.

```toml
# Cargo.toml — the crate graph IS the rule set. domain <- app <- adapters.
[workspace]
resolver = "3"
members = ["crates/domain", "crates/app", "crates/adapters"]

# deny.toml — frameworks only as direct dependencies of the adapters crate.
[bans]
multiple-versions = "allow"
deny = [
  { crate = "tokio", wrappers = ["adapters"] },
  { crate = "axum",  wrappers = ["adapters"] },
  { crate = "sqlx",  wrappers = ["adapters"] },
]
```

## The rule-mutation manifest — proving every rule bites

One `arch-mutations.toml` per repo. Run by `scripts/rule_mutation.py <dir>` (in this skill): the baseline must
pass; each mutant must fail with the expected text; the tree is restored; any declared rule that killed no
mutant fails the gate as **toothless** (gate G2).

```toml
check = "npx depcruise src --config .dependency-cruiser.cjs"   # the same command lint runs
snapshot = []              # files the tool rewrites as a side effect (Rust: ["Cargo.lock"])
rules = ["domain-is-pure", "app-not-adapters", "no-circular"]   # every active rule id

[[mutation]]
rule = "domain-is-pure"
expect = "domain-is-pure"                                       # text the failure must contain
edits = [{ file = "src/domain/order.ts", append = 'import "node:fs";' }]
```

Write one mutation per rule: the smallest edit an agent might plausibly make that violates it. The proof's
negative control (a typo'd path `^src/domian/`) was reported as toothless with exit 1.

## Architecture invariants — `spec/architecture-invariants.md`

Uses the test-planning skill's invariant-spec format, with one added `fitness:` tag per rule.

```markdown
---
status: planned
---
# Architecture invariants

## Rules
- R1 Domain imports nothing outside domain — ADR-0002. fitness: structural (lint: domain-is-pure)
- R2 Use cases never import adapters — ADR-0002. fitness: structural (lint: app-not-adapters)
- R3 Place-order p95 < 300 ms at 50 rps on the reference box — Q1, ADR-0004. fitness: test (k6 threshold)
- R4 Payment provider outage returns 503 within 2 s, order stays pending — Q2, ADR-0005. fitness: test (integration, error case)
- R5 Exactly-once order creation under client retry — Q3. fitness: manual (LLM judge at review; no cheap test yet)

## Tests that enforce these rules
- R1, R2: `npm run lint` (proven by arch-mutations.toml)
- R3: <filled by test-writer>
- R4: `spec/place-order.md` § Error cases
```

- `structural` → lint; build's full-suite gate runs it.
- `test` → test planning writes the contract, test writing locks it, build makes it green. Latency and load go
  to the verification-planning check catalogue.
- `manual` → a named review question, kept visible as a gap.

Known gap: the autonomous `auto-test-planning` skill does not yet document the invariant format, so it may skip
this file.

## Machine gate before hand-off

| # | Check | Built? |
|---|---|---|
| G1 | Boundary rules pass on the current tree (or empty skeleton) | yes |
| G2 | Every active rule kills its mutant | yes |
| G3 | ≤ 7 structural rules, ≤ 3 quality scenarios | spec only |
| G4 | Every quality scenario has a numeric measure and an invariants row | spec only |
| G5 | Decision-record lint (see `decision-card.md`) | spec only |
| G6 | Every record named exists; every rule cites an existing record | spec only |
| G7 | North-star brief ≤ 600 words excluding diagrams | spec only |
| G8 | Every C4 L2 container maps to a path/package/crate in a rule, or is marked `external` | spec only |

## Revisits

Any node raises an `architecture.revisit` event when a trigger fires:

| Kind | Fires when | Raised by |
|---|---|---|
| `wall` | Build cannot pass a locked test without breaking a rule, twice for the same rule within 10 slices; or a `test` fitness check fails and the fix is structural | build |
| `assumption` | A record's "invalid when" signal is observed | any node, ops, the driver |
| `requirement` | A spec needs a new container, integration, data store or dependency direction; or the top-3 qualities change | spec / interrogate |
| `stage` | The slice path's next "advance when" condition is met | driver or macro node |
| `split` | Low-level design files a `kind: split` request | low-level design |
| `dependency` | A new third-party framework appears without a record | review |
| `scheduled` | A record's review date passes | timer |

```yaml
kind: architecture.revisit
trigger: wall | assumption | requirement | stage | split | dependency | scheduled
decisions: [ADR-0002]
evidence:
  - "npm run lint → app-not-adapters: src/app/checkout.ts → src/adapters/stripe.ts"
raised_by: build
note: "<one line>"
```

Handling is in `design-process.md` § Revisit mode. Each parked alternative names a seam protected by a rule,
so the rules hold today's structure and keep tomorrow's option open.
