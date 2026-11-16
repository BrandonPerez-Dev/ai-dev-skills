"""The walkthrough belongs to the cadres that list it, not to every session.

setup-claude.sh links skills into ~/.claude, where every Claude Code session on
the machine loads them. A skill whose SKILL.md says `scope: cadre` is left out
(and a link left by an older run is removed); a cadre runner links it into its
own runs' folders instead.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SETUP = ROOT / "scripts" / "setup-claude.sh"


BARE_PATH = "/usr/bin:/bin"


def run_setup(home: Path) -> subprocess.CompletedProcess:
    # A bare PATH, so the script's plugin step (it needs `claude`) is skipped.
    env = {"HOME": str(home), "PATH": BARE_PATH}
    return subprocess.run(
        ["bash", str(SETUP)], env=env, capture_output=True, text=True, check=False
    )


@pytest.mark.skipif(
    shutil.which("claude", path=BARE_PATH) is not None,
    reason="claude is on the bare PATH, so setup-claude.sh would install real plugins",
)
def test_a_cadre_skill_is_not_linked_for_every_session(tmp_path):
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)
    os.symlink(ROOT / "skills" / "code-walkthrough", skills / "code-walkthrough")

    done = run_setup(tmp_path)
    assert done.returncode == 0, done.stderr
    assert not (skills / "code-walkthrough").exists(), "an older global link is removed"
    assert not (skills / "code-walkthrough").is_symlink()
    others = [p for p in skills.iterdir() if p.is_symlink()]
    assert others, "the other skills are still linked"
    assert "code-walkthrough" in done.stdout


@pytest.mark.skipif(
    shutil.which("claude", path=BARE_PATH) is not None,
    reason="claude is on the bare PATH, so setup-claude.sh would install real plugins",
)
def test_the_scope_is_read_from_frontmatter_metadata_only(tmp_path):
    """CRLF endings, quotes and a trailing comment still mean cadre; the same words
    outside `metadata`, or in the body, do not."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy(SETUP, repo / "scripts" / "setup-claude.sh")
    skills = {
        "crlf": '---\r\nname: crlf\r\nmetadata:\r\n  scope: "cadre"  # dev\r\n---\r\nbody\r\n',
        "elsewhere": "---\nname: elsewhere\nother:\n  scope: cadre\n---\nbody\n",
        "body": "---\nname: body\n---\n```yaml\nmetadata:\n  scope: cadre\n```\n",
    }
    for name, text in skills.items():
        (repo / "skills" / name).mkdir(parents=True)
        (repo / "skills" / name / "SKILL.md").write_bytes(text.encode())
    home = tmp_path / "home"
    home.mkdir()
    done = subprocess.run(
        ["bash", str(repo / "scripts" / "setup-claude.sh")],
        env={"HOME": str(home), "PATH": BARE_PATH},
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stderr
    linked = {p.name for p in (home / ".claude" / "skills").iterdir()}
    assert linked == {"elsewhere", "body"}
