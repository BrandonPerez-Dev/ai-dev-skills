# Artifacts — exact formats

Reference for auto-low-level-design. Load when writing any output file.
Source: design record `/home/juiz/research/engineering-nodes-2026-10/nodes/low-level-design.md` §3.

## context/modules.md — the module map

At most one page per container. Holds only what an agent cannot discover from the code: context files cut
agent effort but repository overviews "are not helpful" (Gloaguen et al., arXiv 2602.11988, moderate).
Fixed fields, at most 6 lines per module. `design-check` parses the `##` headings and the **Entry** lines (G3).

```markdown
---
updated: 2026-10-05
lld-run: full            # full | lite | record
container: api-server    # from context/architecture.md
---
# Modules: api-server

## invoices
- **Owns:** invoice totals and the invoice line model. Nothing else writes invoice rows.
- **Entry:** `src/invoices/index.ts` (only public import path)
- **Public API:** snapshot at `api/invoices.api.md`
- **May depend on:** `money`, `ports/tax` · **Must not depend on:** `adapters/*`, `http/*`
- **Extension points:** `TaxPolicy` port; real variants: `FlatTax`, `RegionTableTax`
- **Hides:** rounding rules and tax-region lookup
- **Decision:** context/decisions/0007-invoice-totals-in-cents.md

## Shared building blocks — use these, do not re-create
| Need | Use | Not |
|---|---|---|
| Format a date for display | `formatDate` in `src/shared/dates.ts` | hand-rolled `getMonth()` strings |
| Money arithmetic | `Money` in `src/money/index.ts` | raw floats |
```

A module blocked on an architecture decision gets a line `- **blocked-on:** architecture (design-requests/<file>)`.
`## Shared building blocks` is not a module; `design-check` ignores headings without an **Entry** line.

## The skeleton

Signatures and interface doc comments first (Ousterhout, "write the comments first", opinion); bodies use the
stack's unimplemented marker (`references/per-stack.md`) so locked tests fail red, not on import errors (G6).

## api/ — public-API snapshots

One text file per module, package or crate. Each module's `snapshot_cmd` in `design.toml` rewrites its snapshot
file in place; `design-check` G5 regenerates it, compares with the committed bytes, and restores the original,
so the check never changes the tree. Additions fail too, not only breaking changes.

## contracts/

`*.proto`, `openapi.yaml` — only for calls across a process boundary architecture declared. The files are the
snapshot. `buf breaking` and `oasdiff breaking` catch breakage only; `oasdiff changelog` also lists additions.

## context/decisions/NNNN-<slug>.md

Architecture's MADR-minimal format plus `level: module` in front matter, with the rejected alternative from
"design it twice". Only when the choice is not obvious from the skeleton.

## Reuse decisions

In the run's record: the `## Reuse decisions` section of the design request, or of
`context/decisions/NNNN-initial-module-design.md` at project start. Lasting reuse targets move to the map's
shared-building-blocks table.

```markdown
| Planned public symbol | Decision | Evidence searched |
|---|---|---|
| `invoiceTotalCents` | new — no total/sum over invoice lines exists | `rg -n "total|subtotal" src/` (3 hits, all UI formatting); ctags kinds f,c |
| `formatInvoiceDate` | reuse `formatDate` in src/shared/dates.ts | ctags symbol `formatDate` |
| `CsvExporter` | extend existing `Exporter` port in src/export | rg "interface Exporter" |
```

An "extract shared X" row must cite 3 existing call sites (rule of three).

## design-requests/<yyyy-mm-dd>-<slug>.md

At the repo root, not in `context/`, so it is not loaded as architectural truth.

```markdown
---
from: build            # build | refactor | review | human | low-level-design
to: low-level-design   # low-level-design | architecture
kind: signature-change # signature-change | new-symbol | new-module | split | dedupe
modules: [invoices]
status: open           # open | applied | rejected
slice: spec/regional-tax.md
---
## Needed
`invoiceTotalCents(lines, region, tax)` must also take `currency: CurrencyCode`.
## Why the current interface cannot work
Locked test `regional_tax.test.ts:41` totals a EUR invoice; the module has no currency input.
## Tried within the current signature
Reading currency from `lines[0]` — rejected: an empty invoice has no currency.
## Proposed API diff
(the snapshot diff the requester expects)
```

## context/design.toml — what scripts/design-check reads

```toml
[stack]
language = "typescript"                  # typescript | python | rust
typecheck = "npx tsc --noEmit -p ."      # G1
boundary = "npx depcruise src --config .dependency-cruiser.cjs"   # G2: architecture's own command; optional

[map]
path = "context/modules.md"
source_root = "src"                      # G3: every code directory directly under it must hold a module's Entry

[[module]]
name = "invoices"
entry = "src/invoices/index.ts"
snapshot = "api/invoices.api.md"
snapshot_cmd = "npx tsc -p . && npx api-extractor run --local"   # rewrites the snapshot in place

[duplication]                            # G8
cmd = "npx jscpd --min-lines 5 --min-tokens 50 --reporters json --output .jscpd-report src"
report = ".jscpd-report/jscpd-report.json"
baseline = "context/baselines/duplication.json"   # {"percentage": 2.1, "measured": "2026-10-05"}
ratchet = "down-only"                    # refactor may lower it; only this node raises it

[size]
warn_lines = 8000                        # R6, warning only

[locked_paths]                           # enforced by the runner, like locked tests
paths = ["api/**", "contracts/**", "context/modules.md", "context/design.toml"]
```

Python module example: `snapshot_cmd = "python scripts/py_api_snapshot.py invoices src > api/invoices.api.txt"`.
Rust: `snapshot_cmd = "cargo +nightly-<pinned> public-api -p invoices -s > api/invoices.api.txt"`.
