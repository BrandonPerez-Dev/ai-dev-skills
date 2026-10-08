---
name: auto-low-level-design
description: Low-level design specialist for the Cadre pipeline. Fixes a project's module boundaries and public interfaces before code exists, records them as a module map, a compiling skeleton and locked public-API snapshots, and installs design-check so build, refactor and review keep the design holding without re-running this node. Use at project start after auto-architecture, when a design request lands in design-requests/, when design-check reports a duplication or size trigger, or when a spec names a module not in context/modules.md. Not for containers, data stores or cross-container dependency directions (auto-architecture owns those), and not on ordinary changes behind existing public signatures.
---

# Auto-low-level-design — module boundaries and interfaces that compile and stay locked

You decide modules and their public interfaces, write them down as code and config, and install checks that
fail when later work drifts. Prose prompts did not change agents' structural quality (Zhu et al., arXiv
2605.02741, moderate); compiled skeletons and checks in the build loop do. So the rule behind everything here:

**Every design decision either compiles, becomes a check in build's loop, or is marked human judgement.**

Design record this skill implements (evidence, sources, measurement plan, proof run):
`/home/juiz/research/engineering-nodes-2026-10/nodes/low-level-design.md`.

## Mode — pick one before anything else

| Mode | When | Scope |
|---|---|---|
| **Full** | Project start, after architecture has containers and boundary rules. Also triggers R2, R3, R5, R6. | Module map, skeleton, snapshots, reuse decisions, baselines — for the affected modules only on a reassess |
| **Full, record mode** | Brownfield project with no recorded design | Snapshot today's API, write the map from the tree, set the duplication baseline at today's value. No redesign unless the person asks. |
| **Lite** | Triggers R1 (a design request) and R4 (duplication above baseline) | One signature change: skeleton edit, snapshot update, map line, reuse row |
| **Skip** | Change stays behind existing public signatures; prototype or spike | Say so on the page in two lines. Build runs `design-check`. |

Triggers R1–R7 and how each is detected: `references/triggers-and-scope.md`.

## What a run leaves in the project repo

All outputs are files in the project; nothing lives only in a session. Exact formats: `references/artifacts.md`.

1. `context/modules.md` — the module map, fixed schema, at most 6 lines per module, one page per container.
2. The skeleton — public signatures and interface doc comments, bodies left unimplemented with the stack's marker.
3. `api/<module>.api.*` — one public-API snapshot per module. Locked to build.
4. `contracts/` — proto/OpenAPI, only for calls across a process boundary architecture declared.
5. `context/decisions/NNNN-*.md` with `level: module` — only when a choice is not obvious from the skeleton.
6. Reuse decisions — one row per planned public symbol: new, reuse or extend, with what was searched.
7. `context/design.toml` — the check manifest — and `scripts/design-check`, copied from this skill.
8. `context/baselines/duplication.json` — the duplication baseline; refactor may lower it, only this node raises it.

## Each run

1. **Read inputs directly**, never through a summary: `context/architecture.md`, `context/decisions/*.md`,
   architecture's boundary-rule config, the in-scope `spec/*.md`, existing `api/*`, open `design-requests/*.md`.
2. **Reuse scan** before naming any new public symbol (`references/reuse-scan.md`). A `new` row with no search
   evidence fails G7.
3. **Write the skeleton and map** using the stack's conventions (`references/per-stack.md`). Decompose by the
   decision most likely to change. Each port names two or more real variants, or links an ADR (G9).
4. **Generate snapshots and the manifest.** Copy `scripts/design-check` into the project's `scripts/`, and
   `scripts/py_api_snapshot.py` too for Python projects.
5. **Run the gate** (`references/gate.md`): all of G1–G9 for a full run; G1, G2, G5, G6, G7 for a lite run.
   Paste the output on the page.
6. **Run the advisory smell report** (`scripts/py_design_smells.py` for Python). It never fails a run.
7. **Write the page** to `$CADRE_SURFACE_OUT` with the **auto-surface** skill. Lead with the snapshot files — they
   are the review surface, not prose. Budgets: full run ≤15 min for ~8 modules; one module ≤5 min; lite ≤3 min.
   Ask, per interface: *is it smaller than what it hides?*

## Settled calls (driver, 2026-10-06)

- **Two nodes.** Architecture and this node stay separate and hand off through files. Merge exit: if more than 1
  in 5 full runs file a `kind: split` request back to architecture, revisit.
- **Lite runs auto-approve purely additive changes** — a new parameter with a default, or a new symbol the reuse
  scan found no match for. Everything else goes to the person. Backstop: R5 (3 lite runs on one module within 10
  slices forces a full reassess).
- **Rust: pin one nightly toolchain for `cargo public-api` only**; everything else builds on stable.

## Non-negotiables

- **Code and config over prose.** If a decision can be a type, a visibility rule or a check, it is one.
- **api/, contracts/, context/modules.md, context/design.toml are locked paths** for build and refactor — the same
  mechanism as locked tests. A snapshot changes only when this node runs.
- **Escalate, do not decide, anything cross-container**: a new deployable, separate repo, external consumers, a
  third-party plugin API, or a new dependency direction between containers. Write a `kind: split` design request
  addressed to architecture, mark the modules `blocked-on: architecture` in the map, and stop.
- **Simplest shape first.** A separate package or crate only for a compiler-enforced boundary, an R6 size trigger,
  or a dependency set the rest must not inherit. A plugin point only with two real variants now.

## Neighbours

| Neighbour | Takes from this node | Gives this node |
|---|---|---|
| Architecture | `kind: split` requests | Containers, ADRs, boundary-rule config (read directly) |
| Spec / test-planning | Module names and public entry points | Behavioural contracts; R2 when a contract names an unmapped module |
| Test-writer | The skeleton; tests import public entries only | Red tests, checked by G6 |
| Build | `design-check` in its full-suite gate, locked paths, the map entry it touches, shared building blocks | Design requests (R1) |
| Refactor | Shared-building-blocks table; the baseline it may only lower | Design requests |
| Review | `design-check` output: API diff, duplication delta, smell advisory | Design requests; design/structure findings |
