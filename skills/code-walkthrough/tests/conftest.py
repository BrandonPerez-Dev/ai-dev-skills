"""A small git repository built fresh for each test session.

The tests never depend on a repository outside this one: the fixture makes a
two-commit history with a Rust file whose function changes, and a SQL file
that loses a "-- " comment line (the case a naive diff parser drops).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

LIB_V1 = """//! A tiny counter.

/// Add one.
pub fn bump(n: u64) -> u64 {
    n + 1
}

pub fn name() -> &'static str {
    "counter"
}
"""

LIB_V2 = """//! A tiny counter.

/// Add one, never past the limit.
pub fn bump(n: u64, limit: u64) -> u64 {
    if n >= limit {
        return limit;
    }
    n + 1
}

pub fn name() -> &'static str {
    "counter"
}
"""

SQL_V1 = "-- the events table\nCREATE TABLE events (seq INTEGER);\n-- old note\n"
SQL_V2 = "-- the events table\nCREATE TABLE events (seq INTEGER);\n"


def run(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


def make_repo(root: Path) -> Path:
    """The two-commit history described above, in `root`."""
    root.mkdir(parents=True, exist_ok=True)
    run(root, "init", "-q", "-b", "main")
    run(root, "config", "user.email", "test@example.com")
    run(root, "config", "user.name", "Test")
    (root / "src").mkdir()
    (root / "src/lib.rs").write_text(LIB_V1)
    (root / "schema.sql").write_text(SQL_V1)
    run(root, "add", ".")
    run(root, "commit", "-q", "-m", "first")
    (root / "src/lib.rs").write_text(LIB_V2)
    (root / "schema.sql").write_text(SQL_V2)
    run(root, "commit", "-qam", "bump takes a limit")
    return root


@pytest.fixture(scope="session")
def repo(tmp_path_factory) -> Path:
    """Shared and read-only: a test that needs more history makes its own."""
    return make_repo(tmp_path_factory.mktemp("repo"))


@pytest.fixture
def head(repo) -> str:
    return run(repo, "rev-parse", "--short", "HEAD")


def base_spec(repo: Path, rev: str, mode: str) -> dict:
    return {
        "mode": mode,
        "repo": str(repo),
        "rev": rev,
        "title": "A counter",
        "subtitle": "fixture",
        "why": "bump now stops at a limit.",
        "lenses": ["correctness"],
        "primer": {
            "goal": "Explain what bump does at the limit.",
            "model": ["bump adds one."],
            "prequestions": [{"q": "What does bump return at the limit?", "stop": 1}],
            "terms": [{"term": "limit", "def": "the largest value bump returns"}],
        },
        "stops": [
            {
                "file": "src/lib.rs",
                "lines": [3, 9],
                "kind": "decision",
                "title": "bump stops at the limit",
                "does": ["It returns the limit instead of going past it."],
                "why": "Callers now pass a limit.",
                "question": "Should it be an error instead?",
                "steps": [
                    {"lines": [4, 4], "text": "The new limit argument."},
                    {"lines": [5, 7], "text": "At the limit, return it."},
                ],
            }
        ],
    }


@pytest.fixture
def write_spec(tmp_path, repo, head):
    def write(mode: str = "change", **changes) -> Path:
        spec = base_spec(repo, head, mode)
        spec.update(changes)
        path = tmp_path / f"{mode}.json"
        path.write_text(json.dumps(spec))
        return path

    return write
