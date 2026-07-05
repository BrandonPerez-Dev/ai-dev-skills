#!/usr/bin/env python3
"""
Register skills in the MLflow Prompt Registry as versioned prompts.

Usage:
    python3 register_skills.py [skill-name ...]      # specific skills
    python3 register_skills.py --all-dev             # the core dev pipeline set

Each skill's SKILL.md is registered as prompt "skill_<name>" (hyphens -> underscores).
A new version is created only when the text changed since the latest version, so
this is safe to run repeatedly (e.g., after any skill edit, or from a cron).
"""
import argparse
import os
import subprocess
import sys

import mlflow

SKILLS_ROOT = os.path.expanduser("~/dev-config/ai-workflow-config/skills")

DEV_SET = [
    "engineering", "slicing", "test-planning", "test-writer", "build", "tdd",
    "ship", "code-review", "coding-standards", "investigating",
    "skill-creator", "refactor" ,
]


def git_sha(path):
    try:
        return subprocess.check_output(["git", "-C", path, "rev-parse", "--short", "HEAD"],
                                       stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "unknown"


def register(name):
    path = os.path.join(SKILLS_ROOT, name, "SKILL.md")
    if not os.path.exists(path):
        print(f"  {name}: SKILL.md not found, skipped", file=sys.stderr)
        return
    text = open(path).read()
    pname = "skill_" + name.replace("-", "_")
    try:
        latest = mlflow.genai.load_prompt(f"prompts:/{pname}@latest")
        if latest.template == text:
            print(f"  {pname}: v{latest.version} unchanged")
            return
    except Exception:
        pass
    v = mlflow.genai.register_prompt(name=pname, template=text,
                                     commit_message=f"snapshot (repo sha {git_sha(SKILLS_ROOT)})")
    try:
        mlflow.genai.set_prompt_alias(pname, alias="latest", version=v.version)
    except Exception:
        pass
    print(f"  {pname}: v{v.version} registered")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="*")
    ap.add_argument("--all-dev", action="store_true")
    ap.add_argument("--tracking-uri", default=os.environ.get("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    args = ap.parse_args()

    mlflow.set_tracking_uri(args.tracking_uri)
    names = list(args.skills)
    if args.all_dev:
        names.extend(s for s in DEV_SET if s not in names)
    if not names:
        ap.error("give skill names or --all-dev")
    for n in names:
        register(n)


if __name__ == "__main__":
    main()
