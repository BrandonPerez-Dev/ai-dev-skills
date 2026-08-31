# context-to-board-pm — tracked items

- **Install step (when this replaces `pm` locally):** retire/disable the installed v1 `pm`
  skill in the same act (router collision otherwise — both claim "prioritize the backlog"),
  and add a routing-graph node for `context-to-board-pm` (run skill-graph). Note: installs
  are symlinks into the live ai-dev-skills working tree — keep `main` checked out there
  (feature work in a git worktree) or installed skills dangle on branch switch.
- **Calibration:** sizing anchors pending first real workflow runs (see
  `references/sizing.md`); the calibration loop's signals feed them.
- **Deliberate deviations, confirmed:** two HARD-GATEs (distinct irreversibles: hub-truth
  contamination vs. unchecked plans); non-gerund name (driver-mandated).

## Done

- ~~Executor-context guard~~ — bias-guard row added (floor is executor-relative; craft
  travels, economics don't). From first non-Cadre use (NEX-194).
- ~~Pre-publish trim~~ — v1 meta-narrative removed from SKILL.md, sizing.md,
  story-standard.md (2026-08-31).
- ~~Eval assertion tightening~~ — the five grader-suggested changes applied to
  `evals/evals.json` (32 expectations total). The changes encode behaviors the iteration-1
  graders directly observed in the outputs; a discrimination re-check against those outputs
  wasn't possible (the run artifacts lived in session scratchpad and were cleaned up —
  lesson: log eval runs to MLflow / commit the benchmark, never leave the record in temp).
  Next full eval run verifies discrimination empirically.
