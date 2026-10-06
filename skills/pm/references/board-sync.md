# Board↔code reconciliation (`Reconcile`)

Read when auditing the board against reality — the on-request **deep** version of the standing
"keep the board honest" habit. Cadre's board drifts from the code: a co-developer merges a fix,
band-aids a runner, closes or files an issue, direct-pushes — often without announcing it. `Reconcile`
detects that drift and proposes the Linear writes to close it.

## Reach — read-only

pm reads code to *detect* drift; it never writes code. Sources, cheapest first:

- **Linear** — issue status/description, recent comments, status updates, attachments (PR links),
  relations, state history, `updatedAt`.
- **GitHub (read-only `gh` via Bash)** — open + recently-merged PRs (`gh pr list` / `gh pr view`), the
  PR↔issue links, CI status, PR authors.
- **Repo (read-only `git`, `Read`, `Grep`)** — `git log` / `git show`, and the actual code /
  `.pipeline` state, to verify *"is this really done?"* (the NEX-128 lesson: a green or closed signal
  can be a band-aid).

**Never commit, push, merge, or mutate anything.** The only writes pm makes are to Linear, and only
after confirmation (the HARD-GATE). Code fixes and merge-conflict *resolution* are other members'
lanes (engineer; the pipeline's reconcile stage) — pm **flags, it does not fix**.

## Drift categories

Classify each issue against reality, with **evidence** (the PR# / commit / comment / file that shows
it) and **attribution** (which dev's action caused it):

| Drift type | Signal | Proposed fix |
|---|---|---|
| **In-sync** | board matches reality | none |
| **Done-in-code** | a merged PR / the actual code already implements it; issue still open | propose **close** |
| **Band-aided** | looks resolved but a workaround masks it — not actually fixed | **keep open**, flag the real state + the band-aid |
| **Duplicate / superseded** | another issue (or a merged one) covers it | propose `duplicateOf` / supersede |
| **Mis-filed** | wrong project, lane/status, or relations | propose the fix |
| **Stale** | code moved on; no longer relevant; no deliberate hold | propose defer / delete |
| **Desynced description** | content no longer matches the code / plan | propose update |

## Collision / overlap — forward-looking (flag, don't resolve)

Beyond reconciling the past, surface where the two devs may collide:

- Two **active** stories touching the same area/files → recommend sequencing or merging them before
  they conflict.
- A **recent merge** that likely invalidates or affects an **in-flight** story → flag for a re-check.

Resolving an actual merge conflict is the pipeline's reconcile stage, not pm's job.

## Output

A reconciliation queue, then the batched Linear writes (confirmed before writing):

```
RECONCILE (board vs code):
  NEX-xxx  done-in-code  — PR #NN (merged, @codev) implements it     → close
  NEX-yyy  band-aided    — "band-aid applied to fedora-1" (comment)  → keep open, flag
  NEX-zzz  duplicate     — same scope as NEX-www                     → duplicateOf NEX-www
  COLLISION: NEX-aaa & NEX-bbb both touch runner/github.py cursor    → sequence / merge
PROPOSED WRITES (awaiting confirm): ...
```

## Scope & cost

The deep audit is **on-request** (or when the standing habit recommends it) — reading code across a
board is heavy, so **scope it**: recent activity first (what changed since things were last obviously
in sync), or a targeted set, not a blind full-repo scan. The always-on cheap probe (Linear signals) is
the continuous version; this is the deep one. pm can't track "time since last sync" (it's stateless per
invocation) — it gauges "a lot has changed" from observable recent activity.
