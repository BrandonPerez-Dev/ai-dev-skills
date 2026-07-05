#!/usr/bin/env python3
"""
Log a skill-eval iteration workspace to MLflow using the GenAI data model.

Usage:
    python3 log_to_mlflow.py <workspace>/iteration-N --skill-name <name> \
        [--skill-path /path/to/skill/SKILL.md] [--tracking-uri http://127.0.0.1:5000]

Per (case x variant) this logs:
  - a nested MLflow run: params (case, variant, iteration, git sha) +
    metrics (assertions passed/total, pass_rate, tokens, duration) + artifacts
  - a TRACE whose root span carries the eval prompt as input and the answer as
    output, with one FEEDBACK assessment per grading expectation (passed +
    evidence rationale). This is what populates the GenAI view's run drawers,
    the Traces tab, and what Judges/datasets can attach to later.

With --skill-path, the skill's SKILL.md is registered in the MLflow Prompt
Registry as prompt "skill_<name>" (a new version is created only when the text
changed), giving versioned, diffable skill history alongside the eval runs.

Backend default: http://127.0.0.1:5000 (systemd user service mlflow.service);
falls back to a local file store if the server is unreachable.
"""
import argparse
import json
import os
import subprocess
import sys

import mlflow
from mlflow.entities import AssessmentSource, AssessmentSourceType


def git_sha(path):
    try:
        return subprocess.check_output(
            ["git", "-C", path, "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "unknown"


def register_skill_prompt(skill_name, skill_path):
    """Register SKILL.md as a versioned prompt; skip if unchanged."""
    pname = f"skill_{skill_name}"
    text = open(skill_path).read()
    try:
        latest = mlflow.genai.load_prompt(f"prompts:/{pname}@latest")
        if latest.template == text:
            return pname, latest.version, False
    except Exception:
        pass
    v = mlflow.genai.register_prompt(
        name=pname, template=text,
        commit_message=f"snapshot at eval time (sha {git_sha(os.path.dirname(skill_path))})")
    try:
        mlflow.genai.set_prompt_alias(pname, alias="latest", version=v.version)
    except Exception:
        pass
    return pname, v.version, True


GRADER_SOURCE = AssessmentSource(source_type=AssessmentSourceType.LLM_JUDGE, source_id="skill-creator-grader")


def slug(text, n=60):
    return "".join(c if c.isalnum() else "_" for c in text.lower())[:n].strip("_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iteration_dir")
    ap.add_argument("--skill-name", required=True)
    ap.add_argument("--skill-path", default=None,
                    help="Path to SKILL.md to register in the prompt registry")
    ap.add_argument("--tracking-uri", default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    args = ap.parse_args()

    it_dir = os.path.abspath(args.iteration_dir)
    iteration = os.path.basename(it_dir)

    try:
        mlflow.set_tracking_uri(args.tracking_uri)
        mlflow.set_experiment(f"skill-evals/{args.skill_name}")
    except Exception:
        fallback = os.path.expanduser("~/mlflow/mlruns")
        os.makedirs(fallback, exist_ok=True)
        mlflow.set_tracking_uri(f"file://{fallback}")
        mlflow.set_experiment(f"skill-evals/{args.skill_name}")
        print(f"tracking server unreachable; using file store {fallback}", file=sys.stderr)

    sha = git_sha(it_dir)

    prompt_ref = None
    if args.skill_path:
        pname, version, created = register_skill_prompt(args.skill_name, args.skill_path)
        prompt_ref = f"{pname}/v{version}"
        print(f"prompt registry: {prompt_ref} ({'new version' if created else 'unchanged'})")

    cases = [d for d in sorted(os.listdir(it_dir))
             if os.path.isdir(os.path.join(it_dir, d)) and
             os.path.exists(os.path.join(it_dir, d, "eval_metadata.json"))]

    variant_totals = {}
    n_traces = 0
    with mlflow.start_run(run_name=f"{args.skill_name}-{iteration}") as parent:
        mlflow.log_params({"skill": args.skill_name, "iteration": iteration, "git_sha": sha})
        if prompt_ref:
            mlflow.set_tag("skill_prompt", prompt_ref)

        for case in cases:
            case_dir = os.path.join(it_dir, case)
            meta = json.load(open(os.path.join(case_dir, "eval_metadata.json")))
            for variant in sorted(os.listdir(case_dir)):
                vdir = os.path.join(case_dir, variant)
                if not os.path.isdir(vdir):
                    continue
                grading_p = os.path.join(vdir, "grading.json")
                timing_p = os.path.join(vdir, "timing.json")
                answer_p = os.path.join(vdir, "outputs", "answer.md")
                if not os.path.exists(grading_p):
                    continue

                grading = json.load(open(grading_p))
                exps = grading.get("expectations", [])
                passed = sum(1 for e in exps if e.get("passed"))
                total = len(exps)
                timing = json.load(open(timing_p)) if os.path.exists(timing_p) else {}
                answer = open(answer_p).read() if os.path.exists(answer_p) else ""

                with mlflow.start_run(run_name=f"{case}/{variant}", nested=True):
                    mlflow.log_params({"case": case, "variant": variant,
                                       "iteration": iteration, "git_sha": sha})
                    if prompt_ref:
                        mlflow.set_tag("skill_prompt", prompt_ref)
                    mlflow.log_metrics({
                        "assertions_passed": passed,
                        "assertions_total": total,
                        "pass_rate": passed / total if total else 0.0,
                        "total_tokens": timing.get("total_tokens", 0),
                        "duration_seconds": timing.get("total_duration_seconds", 0.0),
                    })
                    mlflow.log_artifact(grading_p)
                    if os.path.exists(answer_p):
                        mlflow.log_artifact(answer_p)

                    # Trace: prompt in, answer out, one assessment per expectation.
                    with mlflow.start_span(name=f"{case}/{variant}", span_type="AGENT") as span:
                        span.set_inputs({"task_prompt": meta.get("prompt", ""),
                                         "case": case, "variant": variant})
                        span.set_outputs({"answer": answer})
                        trace_id = span.trace_id
                    for e in exps:
                        try:
                            mlflow.log_feedback(
                                trace_id=trace_id,
                                name=slug(e.get("text", "assertion")),
                                value=bool(e.get("passed")),
                                rationale=e.get("evidence", ""),
                                source=GRADER_SOURCE,
                            )
                        except Exception as ex:
                            print(f"  feedback log failed ({case}/{variant}): {ex}", file=sys.stderr)
                    if grading.get("notes"):
                        try:
                            mlflow.log_feedback(trace_id=trace_id, name="grader_notes",
                                                value=grading["notes"], source=GRADER_SOURCE)
                        except Exception:
                            pass
                    n_traces += 1

                agg = variant_totals.setdefault(variant, {"passed": 0, "total": 0, "tokens": 0})
                agg["passed"] += passed
                agg["total"] += total
                agg["tokens"] += timing.get("total_tokens", 0)

        for variant, agg in variant_totals.items():
            rate = agg["passed"] / agg["total"] if agg["total"] else 0.0
            mlflow.log_metrics({f"{variant}_pass_rate": rate, f"{variant}_tokens": agg["tokens"]})
        variants = list(variant_totals)
        if len(variants) == 2 and "with_skill" in variant_totals:
            other = [v for v in variants if v != "with_skill"][0]
            w, o = variant_totals["with_skill"], variant_totals[other]
            delta = (w["passed"] / w["total"] if w["total"] else 0) - (o["passed"] / o["total"] if o["total"] else 0)
            mlflow.log_metric("pass_rate_delta", delta)

        print(f"Logged {len(cases)} cases, {n_traces} traces with assessments, "
              f"parent run {parent.info.run_id[:8]} (experiment skill-evals/{args.skill_name})")


if __name__ == "__main__":
    main()
