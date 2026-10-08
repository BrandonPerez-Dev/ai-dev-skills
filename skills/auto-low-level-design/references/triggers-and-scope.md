# Triggers, skip and scale, and what to escalate

Reference for auto-low-level-design. Load when deciding the mode of a run.
Source: design record `/home/juiz/research/engineering-nodes-2026-10/nodes/low-level-design.md` §1, §7, §10.

## Reassess triggers

Each trigger is a file or a check result another node can see. Thresholds marked *opinion* are starting values
for the measurement plan (design record §12) to calibrate.

| # | Trigger | Detected by | Runs |
|---|---|---|---|
| R1 | Build, refactor or review needs a public signature changed, or a new public symbol | That node writes `design-requests/<date>-<slug>.md` | Lite |
| R2 | A spec needs a module, package, plugin point or cross-process contract not in the map | A spec names a path missing from `context/modules.md`, or a request with `kind: new-module` | Full, that module |
| R3 | Architecture changed a boundary that affects modules | An ADR with non-empty `affects-modules:` lands in `context/decisions/` | Full, affected modules |
| R4 | Duplication above baseline, or a new clone spans two modules | `design-check` G8 fails | Lite (a reuse decision) |
| R5 | One module's interface keeps moving: ≥3 lite runs within 10 slices (opinion) | Count of `applied` requests naming the module | Full, that module |
| R6 | A module outgrows one agent: over ~8k lines (opinion; Team Topologies cognitive load) | `design-check` size warning | Full, as a split proposal |
| R7 | A human asks | Directly | As asked |

Why running rarely is safe: Liu et al. (arXiv 2604.12147, ASE 2026, 21,120 trajectories) found a poor plan hurts
more than no plan and that inserted early phases can degrade performance (moderate-strong). This node adds no
per-change phase; per change, later nodes only run `design-check` and read one map entry.

## Skip and scale

| Situation | Action |
|---|---|
| Change stays behind existing public signatures | Do not run. Build runs `design-check`. |
| Build needs one new parameter or symbol | Lite, from a design request |
| New module, package, plugin point or cross-process contract | Full, for that module |
| Greenfield project start | Full. Replaces build's V0a boundary-scaffold phase; build keeps V0b, the walking skeleton. |
| Brownfield, no recorded design | Full in record mode. No redesign unless asked (R7). |
| Prototype or spike | Skip entirely: no snapshot, no lock |

## Lite-run approval

Auto-approve when the snapshot diff only adds: a parameter with a default, or a symbol whose reuse row is `new`
with search evidence. Anything that removes or changes an existing line goes to the person (≤3 min: the request's
*Why* and *Tried* sections plus the snapshot diff).

## Packages, plugins, repos — who decides

| Decision | Owner | Rule |
|---|---|---|
| Module (one directory, one entry) inside a container | This node | Default unit. Decompose by the decision likely to change (Parnas 1972). |
| Separate package or crate, same repo and deployable | This node | Only for (a) a compiler-enforced boundary, (b) R6, (c) a dependency set the rest must not inherit |
| Internal plugin point (core plus registry) | This node | Only with ≥2 real variants now (G9) |
| New deployable, separate repo, external consumers, third-party plugin API, new cross-container dependency direction | **Architecture** | Write `kind: split`, `to: architecture`; mark modules `blocked-on: architecture`; stop |

Split repos only for independent release cadence, ownership, licensing or security boundaries, or external
consumers. For one developer plus agents, a monorepo keeps refactors atomic (Fowler, MonolithFirst, opinion).
