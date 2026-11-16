"""The walkthrough belongs to the cadres that list it, not to every session.

setup-claude.sh links skills into ~/.claude, where every Claude Code session on
the machine loads them. A skill whose SKILL.md says `scope: cadre` is left out
(and a link left by an older run is removed); a cadre runner links it into its
own runs' folders instead.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SETUP = ROOT / "scripts" / "setup-claude.sh"


def run_setup(home: Path) -> subprocess.CompletedProcess:
    # A bare PATH, so the script's optional plugin step (needs `claude`) is skipped.
    env = {"HOME": str(home), "PATH": "/usr/bin:/bin"}
    return subprocess.run(
        ["bash", str(SETUP)], env=env, capture_output=True, text=True, check=False
    )


def test_a_cadre_skill_is_not_linked_for_every_session(tmp_path):
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)
    os.symlink(ROOT / "skills" / "code-walkthrough", skills / "code-walkthrough")

    done = run_setup(tmp_path)
    assert done.returncode == 0, done.stderr
    assert not (skills / "code-walkthrough").exists(), "an older global link is removed"
    assert not (skills / "code-walkthrough").is_symlink()
    assert (skills / "architecture").is_symlink(), "every other skill is still linked"
    assert "code-walkthrough" in done.stdout
