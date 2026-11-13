import html
import re

import pytest

from conftest import LIB_V1, LIB_V2
from core import SpecError, aligned, count_lines, diff_lines, highlight, load_spec, read_file


def plain(markup: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", markup))


def test_highlighting_quotes_the_file_exactly():
    lines = highlight("src/lib.rs", LIB_V2)
    assert [plain(line) for line in lines] == LIB_V2.split("\n")
    assert any('class="k"' in line for line in lines)


def test_unknown_file_types_are_escaped_not_highlighted():
    assert highlight("notes.unknownext", "a < b") == ["a &lt; b"]


def test_a_missing_file_reads_as_none(repo, head):
    assert read_file(str(repo), head, "nope.rs") is None


def test_diff_lines_cover_both_versions_in_order(repo, head):
    rows = diff_lines(str(repo), f"{head}^", head, "src/lib.rs")
    assert [o for _, o, _ in rows if o] == list(range(1, len(LIB_V1.splitlines()) + 1))
    assert [n for _, _, n in rows if n] == list(range(1, len(LIB_V2.splitlines()) + 1))


def test_a_deleted_line_starting_with_dashes_is_kept(repo, head):
    rows = diff_lines(str(repo), f"{head}^", head, "schema.sql")
    assert ("-", 3, None) in rows


def test_a_rewritten_line_sits_beside_its_replacement(repo, head):
    rows = aligned(diff_lines(str(repo), f"{head}^", head, "src/lib.rs"))
    old, new = LIB_V1.splitlines(), LIB_V2.splitlines()
    _old_no, n, kind = next(r for r in rows if r[0] and "pub fn bump" in old[r[0] - 1])
    assert kind == "chg"
    assert "limit: u64" in new[n - 1]


def test_a_valid_spec_loads(write_spec):
    spec = load_spec(write_spec())
    assert spec["stops"][0]["title"] == "bump stops at the limit"


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"lines": [3, 99]}, "outside src/lib.rs"),
        ({"file": "gone.rs"}, "does not exist"),
        ({"kind": "<b>"}, "kind must be one of"),
        ({"steps": [{"lines": [1, 2], "text": "x"}]}, "step 1: lines 1-2 outside the stop"),
    ],
)
def test_a_spec_pointing_at_missing_code_fails_loudly(write_spec, repo, head, change, message):
    from conftest import base_spec

    stop = {**base_spec(repo, head, "change")["stops"][0], **change}
    with pytest.raises(SpecError, match=re.escape(message)):
        load_spec(write_spec(stops=[stop]))


def test_a_question_for_a_missing_stop_fails(write_spec):
    primer = {"goal": "g", "prequestions": [{"q": "?", "stop": 4}]}
    with pytest.raises(SpecError, match="stop 4"):
        load_spec(write_spec(primer=primer))


def test_a_spec_whose_repo_is_missing_says_so(write_spec, tmp_path):
    with pytest.raises(SpecError, match="no commit"):
        load_spec(write_spec(repo=str(tmp_path / "nowhere")))


def test_the_repo_can_be_overridden_for_one_run(write_spec, repo, tmp_path):
    path = write_spec(repo="does/not/matter")
    assert load_spec(path, str(repo))["repo"] == str(repo.resolve())


def test_lines_are_counted_as_git_counts_them():
    assert count_lines("a\x0cb\nc\n") == 2
    assert count_lines("a\nb") == 2


def test_a_base_covers_every_commit_in_the_change(tmp_path):
    from conftest import make_repo, run

    repo = make_repo(tmp_path / "r")
    first = run(repo, "rev-list", "--max-parents=0", "HEAD")
    (repo / "src/lib.rs").write_text((repo / "src/lib.rs").read_text() + "// more\n")
    run(repo, "commit", "-qam", "more")
    rows = diff_lines(str(repo), first, "HEAD", "src/lib.rs")
    added = [n for tag, _, n in rows if tag == "+"]
    assert len(added) >= 5  # the limit change and the new comment, two commits


BAD = [
    ({"does": "one string"}, "'does' must be a non-empty list"),
    ({"does": None}, "'does' must be a non-empty list"),
    ({"lines": [3, 4, 5]}, "'lines' must be [first, last]"),
    ({"title": ""}, "'title' must be a non-empty string"),
    ({"verdict": "MAYBE"}, "verdict must be CONFIRMED or PLAUSIBLE"),
]


@pytest.mark.parametrize(("change", "message"), BAD)
def test_malformed_stops_are_spec_errors(write_spec, repo, head, change, message):
    from conftest import base_spec

    stop = {**base_spec(repo, head, "change")["stops"][0], **change}
    with pytest.raises(SpecError, match=re.escape(message)):
        load_spec(write_spec(stops=[stop]))


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        ({"primer": {"model": []}}, "primer: needs a 'goal'"),
        ({"primer": {"goal": "g", "prequestions": [{"q": "?", "stop": "1"}]}}, "does not exist"),
        ({"files": [{"path": "src/lib.rs", "role": "hot", "note": ""}]}, "needs 'path', 'stat'"),
        (
            {"files": [{"path": "src/lib.rs", "stat": "+1", "role": "x", "note": ""}]},
            "role must be",
        ),
        (
            {"files": [{"path": "nope.rs", "stat": "+1", "role": "hot", "note": ""}]},
            "not in the change",
        ),
        (
            {
                "flow": {
                    "title": "t",
                    "lanes": ["a"],
                    "nodes": [],
                    "edges": [{"from": "x", "to": "y", "label": "", "dir": "v"}],
                }
            },
            "must join two known nodes",
        ),
        (
            {
                "flow": {
                    "title": "t",
                    "lanes": ["a"],
                    "nodes": [
                        {
                            "id": "n",
                            "lane": 0,
                            "x": 1,
                            "w": 2,
                            "stop": 99,
                            "title": "t",
                            "ref": "r",
                            "text": "x",
                        }
                    ],
                }
            },
            "stop 99",
        ),
        ({"rev": "nosuchcommit"}, "no commit nosuchcommit"),
    ],
)
def test_malformed_page_parts_are_spec_errors(write_spec, extra, message):
    with pytest.raises(SpecError, match=re.escape(message)):
        load_spec(write_spec(**extra))


def test_an_anchor_catches_code_that_moved(write_spec, repo, head):
    from conftest import base_spec

    stop = base_spec(repo, head, "change")["stops"][0]
    assert load_spec(write_spec(stops=[{**stop, "anchor": "/// Add one"}]))
    with pytest.raises(SpecError, match="no longer contains"):
        load_spec(write_spec(stops=[{**stop, "anchor": "fn name"}]))
