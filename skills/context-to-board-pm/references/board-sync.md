# Three-way sync (`Sync`): hub ↔ board ↔ code

Read when auditing the board against reality — the on-request **deep** version of the standing
"keep the trio honest" habit. Drift flows in two directions at once: the **board drifts from the
hub** (stories built on decisions the hub has since superseded; intent with no path), and **both
drift from the code** (a co-developer merges a fix, band-aids something, closes or files an issue,
direct-pushes — often without announcing it). `Sync` detects the drift and proposes the writes to
close it.

## Reach — read-only

This skill reads to *detect* drift; it never fixes. Sources, cheapest first:

- **Hub** — recent commits to the context repo, new/changed decisions and research, intent docs.
- **Linear** — issue status/description, recent comments, attachments (PR links), relations,
  state history, `updatedAt`.
- **GitHub (read-only `gh` via Bash)** — open + recently-merged PRs, PR↔issue links, CI status,
  authors.
- **Repo (read-only `git`, `Read`, `Grep`)** — the actual code, to verify *"is this really
  done?"* (a green or closed signal can be a band-aid).

**Never commit, push, merge, or mutate anything.** Board fixes are proposed and green-lit; hub
corrections route through the Upward lane (interrogate → hub PR → driver merges). Code fixes are
the workflow's lane — this skill **flags, it does not fix**.

## Drift categories

Classify each issue with **evidence** (PR / commit / hub entry / comment / file) and
**attribution** (whose action caused it):

| Drift type | Signal | Proposed fix |
|---|---|---|
| **In-sync** | board matches hub and code | none |
| **Done-in-code** | merged PR / actual code already implements it; story still open | propose **close** |
| **Band-aided** | looks resolved but a workaround masks it | **keep open**, flag the real state |
| **Built-on-rotted-hub-entry** | a governing hub decision is contradicted by the code or superseded | **suspend** planning against the entry; flag for the driver's ruling; hub correction via Upward |
| **Unpathed intent** | hub intent or a fresh decision with no board path | feed the Plan agenda |
| **Duplicate / superseded** | another story (or merged work) covers it | propose `duplicateOf` / supersede |
| **Mis-filed** | wrong project, lane/status, or relations | propose the fix |
| **Stale** | code or hub moved on; no deliberate hold | propose defer / delete |
| **Desynced description** | story content no longer matches hub or code | propose update (respect locked AC) |

## Collision / overlap — forward-looking (flag, don't resolve)

- Two **active** stories touching the same area → recommend sequencing or merging before they
  conflict.
- A **recent merge or hub decision** that likely invalidates an **in-flight** story → flag for
  re-check.

## Output

A reconciliation queue, then the batched writes (board writes await green light; hub items route
Upward):

```
SYNC (hub ↔ board ↔ code):
  <story>  done-in-code    — PR #NN (merged) implements it              → close
  <story>  rotted-hub      — hub decision <name> superseded by <commit> → suspend + driver ruling
  <story>  band-aided      — workaround noted in <comment>              → keep open, flag
  INTENT:  <hub entry> has no path                                      → Plan agenda
  COLLISION: <A> & <B> both touch <area>                                → sequence / merge
PROPOSED WRITES (awaiting green light): ...
HUB: <corrections routed Upward>
```

## Scope & cost

Deep audits are **on-request** (or when the standing habit recommends one) — reading code and hub
across a whole board is heavy, so **scope it**: start from recent activity (hub commits and merges
since things were last obviously in sync) or a targeted set, never a blind full scan. The skill is
stateless per invocation; it gauges "a lot has changed" from observable recent activity.
