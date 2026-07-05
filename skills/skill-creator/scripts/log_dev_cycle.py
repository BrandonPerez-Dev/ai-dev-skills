#!/usr/bin/env python3
"""
Log one design->build->ship cycle to MLflow so dev-skill versions correlate
with real outcomes. Called at ship time (the ship skill's post-flight), or
manually after a cycle completes.

Usage:
    python3 log_dev_cycle.py --project remote-terminal --slice 004-blackboard-reads \
        [--spec path/to/spec.md] [--grill path/to/grill.md] \
        [--iterations-to-green 3] [--locked-test-violations 0] \
        [--review-findings 2] [--tokens 1250000] [--notes "..."]

Logs to experiment "dev-cycles/<project>": params capture the registry version
of every core dev skill at cycle time (the correlation substrate for evolving
skills later), metrics capture the outcome, artifacts capture the spec and
grill transcript.

Every metric is optional — log what you measured, skip what you didn't.
"""
import argparse
import os

import mlflow

DEV_SET = ["engineering", "slicing", "test-planning", "test-writer", "build", "tdd", "ship", "code-review"]


def skill_versions():
    out = {}
    for name in DEV_SET:
        pname = "skill_" + name.replace("-", "_")
        try:
            p = mlflow.genai.load_prompt(f"prompts:/{pname}@latest")
            out[f"v_{name}"] = str(p.version)
        except Exception:
            out[f"v_{name}"] = "unregistered"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--slice", required=True, dest="slice_name")
    ap.add_argument("--spec", default=None)
    ap.add_argument("--grill", default=None, help="grill/interrogation transcript file")
    ap.add_argument("--iterations-to-green", type=int, default=None)
    ap.add_argument("--locked-test-violations", type=int, default=None)
    ap.add_argument("--review-findings", type=int, default=None)
    ap.add_argument("--tokens", type=int, default=None)
    ap.add_argument("--notes", default=None)
    ap.add_argument("--tracking-uri", default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    args = ap.parse_args()

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(f"dev-cycles/{args.project}")

    with mlflow.start_run(run_name=args.slice_name) as run:
        mlflow.log_params({"project": args.project, "slice": args.slice_name, **skill_versions()})
        metrics = {k: v for k, v in {
            "iterations_to_green": args.iterations_to_green,
            "locked_test_violations": args.locked_test_violations,
            "review_findings": args.review_findings,
            "total_tokens": args.tokens,
        }.items() if v is not None}
        if metrics:
            mlflow.log_metrics(metrics)
        if args.notes:
            mlflow.set_tag("notes", args.notes)
        for f in (args.spec, args.grill):
            if f and os.path.exists(f):
                mlflow.log_artifact(f)
        print(f"Logged cycle {args.project}/{args.slice_name} (run {run.info.run_id[:8]}) "
              f"with skill versions {[v for k, v in run.data.params.items() if k.startswith('v_')]}")


if __name__ == "__main__":
    main()
