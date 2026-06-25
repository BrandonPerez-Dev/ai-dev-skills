---
name: skill-creator
description: >-
  Create new skills, improve existing skills, and measure skill performance
  with baseline-vs-with-skill evals. ALWAYS invoke when the user wants to
  create a skill, turn a workflow into a skill, edit or optimize an existing
  skill, run or design skill evals, benchmark a skill, optimize a skill's
  description for triggering, or diagnose a skill that isn't activating or
  isn't being followed. Do not draft or edit SKILL.md files without this
  skill.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Agent
  - Skill
  - WebSearch
  - WebFetch
  - AskUserQuestion
effort: high
---

# Skill Creator

Create skills that measurably improve agent output, and prove it with evals.

## The core loop

Skill quality is established by measurement, not by authoring care. The loop:

1. **Capture intent** — what should the skill enable, when should it trigger, what does good output look like? If the current conversation already contains the workflow ("turn this into a skill"), extract from history first.
2. **Research the domain** — verify the methodology and facts the skill will encode before drafting. A skill built from unverified assumptions ships those assumptions to every future session.
3. **Draft minimal** — write the smallest skill that plausibly closes the gap.
4. **Run evals** — 3-5 realistic test prompts, each run twice in parallel: once with the skill, once baseline (no skill, or the old version when improving). Subagents, same turn.
5. **Review with the human** — show outputs side by side; collect per-case feedback.
6. **Improve and re-run** — generalize from feedback, keep the prompt lean, repeat until the user is satisfied or progress stalls.

The eval mechanics, schemas, and viewer live in `harness/` (vendored from Anthropic's official skill-creator). Usage in "Running the harness" below.

## Is the skill worth it? Measure, don't guess

Judge a skill by its **measured delta over baseline**, weighed against its context cost. Don't ask "can the model already do this?" — capability is a guess, and that question systematically rejects skills whose value is consistency rather than capability. A Python-conventions skill fails the capability test (the model can write Python) and passes the delta test (output quality and consistency measurably improve). The baseline runs in step 4 answer the worth-it question empirically: no delta after honest iteration means cut it; a real delta justifies the tokens regardless of what the model "could" do alone.

The same logic governs every paragraph inside a skill: content earns its place by changing behavior, not by being true. The context window is shared; prefer the smallest set of high-signal tokens.

## Two failure modes, two different fixes

Skills fail silently — no error, the agent just proceeds without the skill and output looks plausible. The failures split into two distinct problems. Diagnose which one you have before fixing anything.

**Activation failure: the skill never triggers.** Triggering is decided entirely by the frontmatter description, and Claude under-triggers by design — it skips skills for tasks it believes it can handle alone. Empirical data (650-trial community study, 2026): directive descriptions ("ALWAYS invoke when… Do not X directly") reached 100% activation; passive "Use when…" descriptions reached 37-77%. Write descriptions pushy:

- Name the domain, then the trigger contexts, then the bypass to forbid: `<What it does>. ALWAYS invoke when <concrete trigger phrases and situations>. Do not <do the thing> directly.`
- Put the most important trigger first — the skill listing shares a budget (~1% of context window) and over-budget descriptions get silently dropped (check `/doctor`).
- Also rule out the mundane causes: wrong directory, no restart after adding a new top-level skills dir, name collision with a bundled skill.

**Execution failure: the skill loads but steps get skipped.** The skill body is one frozen message — it is not re-read during the session — and the user's latest request always has the attention advantage. Steps that delay output without producing visible content get rationalized away. Fixes that hold:

- **Make procedural steps emit visible artifacts.** "Verify the output" gets skipped; "write a verification block mapping each requirement to where the output satisfies it" doesn't, because skipping it is now visible.
- **Write standing instructions, not one-time steps.** "Throughout this task, run the linter after each edit" survives; "Step 3: run the linter" decays once step 3 scrolls past.
- **Push must-not-skip behavior into scripts and hooks.** A bundled script runs the same way every time and costs no attention. Hooks enforce at the tool-call layer — but verify them; they can fail silently.
- **Front-load durable rules.** On compaction, each skill keeps only its first ~5,000 tokens (25,000 combined across skills, most-recent-first), and summarization dilutes prose constraints ("when preconditions hold, plan the work" becomes "plans work"). Anything load-bearing past the first 5k can vanish mid-session. A skill can be re-invoked after compaction to restore it.

## Prescriptiveness: split by layer

- **Description field**: directive emphasis, including ALWAYS — empirically justified for triggering.
- **Single structural gates**: one hard gate that produces an artifact (a failing test, a written plan, a checklist file) is effective.
- **Body behavior**: explain the why instead of stacking MUSTs. Models generalize from motivated rules to cases the skill didn't enumerate; bare imperatives don't survive compaction and read as noise to skip. Scattered all-caps in the body is a yellow flag — reframe with reasoning.
- **Fragile deterministic steps**: don't explain, script. Exact commands, "run this, don't modify."

Match freedom to fragility: open-field judgment gets principles; narrow-bridge operations get scripts.

## Designing the skill

A skill is an agent definition: the body is its system prompt, `allowed-tools` its grants, `references/` its knowledge base, `scripts/` its deterministic tools. Design accordingly:

- **One central thesis.** The single sentence that survives if everything else is cut. A skill without one is a tip list.
- **Method selection over uniform process.** If different inputs need different approaches, lead with a decision table; don't let the model default to one path for everything. Output homogeneity is the tell: when every output of a skill has the same shape regardless of input, the skill is over-prescribing — convert mandates into a technique menu with selection criteria, and make the output justify its choice.
- **Bias guards for the skill's domain.** The rationalizations the model actually produces mid-task ("this case is simple, skip the process"), each paired with the counter-move. Specific beats generic.
- **Output format.** Show what done looks like; it anchors quality.
- **References one level deep**, with a line in SKILL.md saying when to read each. Files over ~100 lines get a table of contents. Nested references get half-read and missed.
- **Scripts for repeated work.** If eval transcripts show every run independently writing the same helper, bundle it in `scripts/` and point to it.
- **Structure budget**: SKILL.md under 500 lines, ideally well under; durable rules in the first 5k tokens; gerund naming (`processing-pdfs`); no time-sensitive facts in the body.
- **`allowed-tools` is a grant, not a fence.** It pre-approves tools; it does not restrict unlisted ones. To actually block, use `disallowed-tools` or permission deny rules.
- **No meta-narrative.** State the rule and its reason. Project history and audit stories belong in planning docs, not skills.

## Writing evals

Save cases to `evals/evals.json` inside the skill directory (schema: `references/eval-schemas.md`). 3-5 cases to start; expand once the loop stabilizes.

- **Realistic prompts** — what a user would actually type, with file paths, messy phrasing, concrete detail. Not abstract task descriptions.
- **Substantive tasks** — simple one-step prompts won't trigger skills at all and test nothing.
- **Write cases the baseline visibly fails.** If baseline and with-skill both clear every assertion, the eval measures nothing — the discriminating signal hides in qualities the assertions didn't capture. Calibrate difficulty until the baseline fails at least some assertions, and prefer assertions that encode the skill's specific behavioral rules (artifacts produced, sourcing discipline) over generic quality bars both versions meet.
- **Assertions objectively verifiable** where possible, with descriptive names and a short id (the id becomes the assessment column name in MLflow). Check programmatically (a script) over eyeballing.
- **Subjective-quality skills** (writing style, pedagogy, design): assertions cover the structural floor (format, required elements, banned patterns); real quality judgment comes from human review of outputs against **golden references** — exemplar outputs the user has personally vetted. Build the golden set as the user reviews; it compounds.
- Keep per-case results as a score plus textual feedback. That format feeds both human review now and automated optimization later.

When a skill failure surfaces in real use, add it as an eval case before fixing it. The suite accretes regression coverage the same way a test suite does.

## Running the harness

All commands run from the skill-creator directory; the harness lives in `harness/`.

**1. Spawn runs — all cases, with-skill AND baseline, same turn:**

For each case, two subagents in parallel: one pointed at the skill, one at the baseline (no skill for new skills; a snapshot copy of the old version for improvements — `cp -r <skill> <workspace>/skill-snapshot/` before editing). Outputs to `<skill-name>-workspace/iteration-N/<eval-name>/{with_skill,without_skill|old_skill}/outputs/`. Write `eval_metadata.json` per case. Capture `total_tokens` and `duration_ms` from each task notification into `timing.json` immediately — the notification is the only place that data exists.

**2. While runs execute, draft or review assertions.** Update `evals/evals.json`.

**3. Grade and aggregate:**

- Grade each run against assertions per `harness/agents/grader.md`; results to `grading.json` (fields: `text`, `passed`, `evidence` — the viewer depends on these exact names).
- Aggregate: `cd harness && python -m scripts.aggregate_benchmark <workspace>/iteration-N --skill-name <name>` → `benchmark.json` with pass rate, time, tokens, mean ± stddev, delta vs baseline.
- Analyst pass per `harness/agents/analyzer.md`: non-discriminating assertions, high-variance cases, time/token tradeoffs.

**4. Log to MLflow (canonical record), then human review:**

```bash
python3 scripts/log_to_mlflow.py <workspace>/iteration-N --skill-name <name> \
  --skill-path <skill>/SKILL.md
```

Logs to the local tracking server (`http://127.0.0.1:5000`, systemd user service `mlflow.service`):
- one nested run per case x variant (pass rates, tokens, duration, answer/grading artifacts)
- one **trace** per run (eval prompt in, answer out) with a per-assertion **assessment** (pass/fail + evidence) — this populates the GenAI view's Traces tab and run drawers
- with `--skill-path`, the SKILL.md is registered in the **Prompt Registry** as `skill_<name>` (new version only when the text changed) — the versioned, diffable evolution ledger GEPA later reads

The user reviews in the MLflow UI: the experiment's Traces tab shows answers with per-assertion pass columns, and they can attach their own feedback to traces there. Note the UI's two view modes (GenAI vs Model training toggle in the sidebar): traces/assessments live in GenAI view; classic run tables in Model training view. The vendored HTML viewer (`harness/eval-viewer/generate_review.py --static`) remains a fallback for offline side-by-side review.

**5. Improve:** generalize from feedback rather than patching the specific case; read the transcripts, not just outputs — cut skill content that sends runs down unproductive paths; bundle scripts for work repeated across runs; explain the why behind new rules. Then re-run into `iteration-N+1`.

**Description optimization** (after the body stabilizes): generate ~20 trigger eval queries (8-10 should-trigger across phrasings, 8-10 near-miss should-NOT-trigger — adjacent domains and keyword overlaps, not obviously-irrelevant strawmen). Review the set with the user (`harness/assets/eval_review.html`), then:

```bash
cd harness && python -m scripts.run_loop --eval-set <eval.json> \
  --skill-path <skill> --model <current-session-model-id> --max-iterations 5 --verbose
```

Train/test split is built in; apply `best_description` (selected on held-out score, which resists overfitting).

**Blind A/B** (optional, "is v2 actually better?"): `harness/agents/comparator.md` + `analyzer.md`.

## Continuous improvement and GEPA

The loop above run by hand — score, read feedback, propose an edit, accept only what improves held-out cases — is manual reflective iteration, and it's the right default. A skill graduates to automated optimization — `mlflow.genai.optimize_prompts()` with the GEPA optimizer (tracked on the same local MLflow server), or the standalone `gepa` library — only when all three hold:

1. Its metric is trustworthy (assertions plus a reference-anchored judge that has tracked the user's actual judgments).
2. Manual iteration has plateaued.
3. Someone will diff and approve the winning candidate — never auto-merge an optimized skill.

Guardrails from the optimization literature: mutate on train cases, select on held-out validation; penalize length (optimizers bloat instructions with edge cases); keep a frozen set of human-judged outputs and reject the run if judge scores stop correlating with them.

## Self-review before shipping a skill

- Description: directive, trigger-first, under budget, near-miss negatives considered
- Central thesis stated; every section serves it
- Why explained for judgment rules; scripts for fragile steps; no all-caps stacking in the body
- Procedural/verification steps emit visible artifacts; standing-instruction phrasing
- Durable rules in the first 5k tokens
- References one level deep; TOCs on long files; scripts bundled for repeated work
- `evals/evals.json` exists with realistic cases; baseline delta measured, not assumed
- No meta-narrative, no time-sensitive facts, no content that merely restates model knowledge

## References

- `references/eval-schemas.md` — exact JSON schemas for evals, grading, benchmark files (read before writing any harness file)
- `references/scoring-methodology.md` — scoring rubric for auditing existing skills
- `harness/agents/{grader,comparator,analyzer}.md` — subagent instructions for grading, blind A/B, analysis (read when spawning each)
