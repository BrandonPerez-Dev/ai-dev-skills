# pipelines

The Cadre runner used to live here as `pipelines/runner`. It now has its own
repository:

**https://github.com/BrandonPerez-Dev/cadre-runner** — clone it, don't copy it.

Its history came with it (`git log` there covers the work done while it lived
in this repo). What stays here is what the runner *reads*, not what it runs:

- `skills/` — the crew members every stage session loads. The runner points at
  this directory through `skills_source` in its config.

Workflow nodes live in a third repo, `cadre-workflows`, reached through the
runner's `workflows_source`.
