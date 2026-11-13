---
name: code-walkthrough
description: >-
  Walk a person through a code change or an unfamiliar codebase on an
  annotatable page: a primer first, then a few curated stops (code quoted from
  git beside what it does, why it matters, and a question), each ending in a
  ruling. ALWAYS invoke when asked to walk someone through a PR, commit,
  branch or diff with them, to review a change together, to show the hotspots
  or decisions in a change, or to give a guided tour of a codebase or module
  for someone new to it. Do not hand back a findings list or a prose summary
  instead. Not for whole-repo courses (codebase-course) or for fixing code.
when_to_use: >-
  "walk me through PR 42", "review this with me", "where are the decisions in
  this change", "I'm new to this repo, show me how X works", "tour the
  storage layer". NOT: "fix these bugs", "write a course", "summarize the PR".
argument-hint: "[commit | branch | PR | path] [question for a tour]"
---

# Code walkthrough

A reader who knows what to look for, why it matters, and the words it uses
understands a change in minutes; a reader handed a diff or a findings list
does not. You pick the few places that matter, explain each one in plain
words beside the real code, and leave every judgement to the person. You
never edit code: anything ruled "needs a fix" goes to another session.

## Choose the mode

| The ask | Mode | Stops are |
|---|---|---|
| A commit, branch, PR or diff | `change` | hotspots: likely defects, decisions worth seeing, load-bearing context |
| "How does X work", someone new to the code | `tour` | concepts and on-purpose decisions, in the order that builds understanding |

## Process

Write each step's result into the spec file as you go; the spec is the
visible artifact, and the renderer refuses one that points at missing code.

1. **Read before choosing.** For a change: the whole diff, each touched
   function in full, its callers, and the tests. For a tour: the entry
   points and the one interface everything goes through. Read the repo's
   recorded decisions (`context/`, ADRs); a choice already decided is a
   `decision` stop at most, never a finding.
2. **Find (change mode).** Look line by line (conditions, off-by-one,
   swallowed errors); at removed behaviour (what each deleted line
   guaranteed, and where that moved); across files (callers and callees);
   then reuse, simplification, efficiency, and fixes of a symptom rather
   than its cause. Add the person's focus list: the repo's
   `context/review-focus.md` and anything they named.
3. **Verify before it becomes a stop.** Try to refute each candidate against
   the code. What survives gets `"verdict": "CONFIRMED"` or `"PLAUSIBLE"`
   with a concrete failure scenario in `why`. Unverified suspicion is a
   question to the reader, never a claim.
4. **Curate.** Only what changes the reader's understanding or needs their
   call. There is no target count: a one-line fix may need one stop. Order
   for understanding (mechanism first), not by file. In change mode list
   every touched file in `files` (hot, decision, ripple) so nothing is
   hidden. Long stops get `steps`: a few lines at a time, each with its own
   sentence.
5. **Prime.** Write `primer`: the goal (what the reader can do at the end),
   the picture to hold in 2-3 sentences, one or two `prequestions` tied to the
   stop that answers them, and `terms` for every word a newcomer would not
   know. Define a term in the glossary rather than padding a stop.
6. **Check the text.** Run `evals/newcomer-reader.md` on the spec (one
   read-only subagent). Fix every undefined term a question depends on and
   re-run until it scores 4 or more. Note the score on your reply.
7. **Render.**
   `python3 scripts/walkthrough.py SPEC.json [--layout pages|rail] [--repo PATH]`.
   The layout is the reader's setting (`CODE_WALKTHROUGH_LAYOUT`), not yours.
8. **Serve and converse.** Open the page with review-surface and keep
   polling. An annotation is a question: answer it in its thread, from the
   code. Collect the rulings; hand "needs a fix" and "discuss later" stops
   to the next session with their file, lines and failure scenario.

## Spec format

See `examples/self-tour.json` for a complete spec: a tour of this skill's
own code, rendered by `make examples`. Required: `mode`,
`repo` (relative to the spec file, or `--repo`), `rev`, `title`, `stops`.
For a change, `base` is where it starts: the commit's parent by default; for
a branch or PR use its merge base (`git merge-base main HEAD`) so every
commit in it shows as changed.
Each stop: `file`, `lines` [first, last], `kind` (context, concept,
decision, finding), `title`, `does` (paragraphs), `why`, `question`, and
optionally `verdict`, `steps` [{`lines`, `text`}], and `anchor`: text the
stop's first line must contain, so a spec that drifted from the code is
refused instead of quoting the wrong lines. Optional page parts:
`subtitle`, `why`, `lenses`, `files`, `primer`, `flow` (the rail layout's
diagram of how stops connect).

All text is escaped when rendered: write plain sentences, not HTML. A line
reference in prose ("lines 12-14", "schema.sql line 2") becomes a link that
lights those lines up; one that names no file in the spec stays plain text.
A spec that fails any check is refused with every problem listed.

## Bias guards

| Thought mid-task | Counter |
|---|---|
| "Show everything, to be thorough" | The map lists every file; stops are for what needs attention. |
| "This finding is obviously right" | Refute it against the code first, or mark it PLAUSIBLE and ask. |
| "The reader will know this term" | The newcomer eval decides; add it to `terms`. |
| "I'll just fix it while I'm here" | Never edit code. Rule it "needs a fix" and hand it on. |
| "A summary would be quicker" | The page is the deliverable; a summary loses the code beside the words. |

## Checks

`make check` runs ruff and the tests on a fixture repository built on the
fly; CI runs the same on every change under `skills/code-walkthrough/`.
