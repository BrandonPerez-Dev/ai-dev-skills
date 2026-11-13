import html
import json
import re

import pytest

import pages
import rail
import walkthrough
from core import load_spec
from primer import mark_terms
from steps import steps_html

LAYOUTS = {"pages": pages.render, "rail": rail.render}


@pytest.mark.parametrize("layout", sorted(LAYOUTS))
@pytest.mark.parametrize("mode", ["change", "tour"])
def test_both_layouts_render_both_modes(write_spec, layout, mode):
    page = LAYOUTS[layout](load_spec(write_spec(mode)))
    assert "Before you read" in page
    assert 'data-line="src/lib.rs:5"' in page
    assert "<dfn" in page
    assert 'class="stepbtn"' in page
    assert ('data-view="split"' in page) == (mode == "change")


@pytest.mark.parametrize("layout", sorted(LAYOUTS))
def test_spec_text_cannot_inject_markup(write_spec, layout):
    path = write_spec(title="<script>x()</script>", why="<img src=x onerror=y>")
    page = LAYOUTS[layout](load_spec(path))
    assert "<script>x()" not in page
    assert "<img src=x" not in page
    assert html.escape("<script>x()</script>") in page


def test_the_cli_writes_the_page_and_rejects_a_bad_spec(write_spec, tmp_path, capsys):
    out = tmp_path / "out.html"
    assert walkthrough.main([str(write_spec()), "--layout", "rail", "-o", str(out)]) == 0
    assert "data-line=" in out.read_text()
    bad = write_spec(stops=[])
    bad_spec = re.sub(
        r'"stops": \[\]', '"stops": [{"file": "x", "lines": [1, 1]}]', bad.read_text()
    )
    bad.write_text(bad_spec)
    assert walkthrough.main([str(bad)]) == 1
    assert "does not exist" in capsys.readouterr().err


def test_the_layout_setting_comes_from_the_environment(write_spec, monkeypatch):
    monkeypatch.setenv("CODE_WALKTHROUGH_LAYOUT", "rail")
    path = write_spec()
    assert walkthrough.main([str(path)]) == 0
    assert path.with_name(f"{path.stem}-rail.html").exists()


def test_terms_are_marked_once_per_stop_and_never_inside_tags():
    spec = {"primer": {"terms": [{"term": "cursor", "def": "last seq seen"}]}}
    seen: set[str] = set()
    first = mark_terms('<a data-x="cursor">cursor</a> then cursor', spec, seen)
    assert first.count("<dfn") == 1
    assert 'data-x="cursor"' in first
    assert mark_terms("cursor again", spec, seen) == "cursor again"


def test_longer_terms_win_and_type_names_match_case():
    terms = [
        {"term": "key", "def": "what it is about"},
        {"term": "idempotency key", "def": "dedup label"},
        {"term": "Store", "def": "the trait"},
    ]
    out = mark_terms(
        "an idempotency key, store-assigned, then Store", {"primer": {"terms": terms}}, set()
    )
    assert '<dfn title="dedup label">idempotency key</dfn>' in out
    assert out.count("<dfn") == 2
    assert "store-assigned" in out


def test_steps_render_their_ranges_and_vanish_when_absent():
    stop = {
        "file": "a.rs",
        "steps": [{"lines": [3, 5], "text": "x"}, {"lines": [7, 7], "text": "y"}],
    }
    out = steps_html(stop, html.escape)
    assert out.count('class="stepbtn"') == 2
    assert 'data-from="3" data-to="5"' in out
    assert steps_html({"file": "a.rs"}, html.escape) == ""


def test_a_test_function_after_other_attributes_is_listed(tmp_path):
    import json

    from conftest import base_spec, make_repo, run

    repo = make_repo(tmp_path / "own")
    (repo / "tests").mkdir()
    (repo / "tests/t.rs").write_text(
        "#[test]\n#[should_panic]\nfn panics() {}\n\n#[test]\nasync fn waits() {}\n#[test]\n"
    )
    run(repo, "add", ".")
    run(repo, "commit", "-qm", "tests")
    spec = base_spec(repo, run(repo, "rev-parse", "--short", "HEAD"), "change")
    spec["files"] = [
        {"path": "src/lib.rs", "stat": "+1", "role": "hot", "note": ""},
        {"path": "tests/t.rs", "stat": "+7", "role": "hot", "note": "no stop here"},
    ]
    path = tmp_path / "with-tests.json"
    path.write_text(json.dumps(spec))
    page = rail.render(load_spec(path))
    assert "<code>panics</code>" in page
    assert "<code>waits</code>" in page


def test_prose_line_references_never_crash_and_resolve_any_file(write_spec):

    spec_path = write_spec()
    stop = json.loads(spec_path.read_text())["stops"][0]
    stop["does"] = [
        "See main.rs line 2, which is not in this walkthrough.",
        "The last line is line 13, and line 400 does not exist.",
        "The table is in schema.sql line 2.",
    ]
    files = [{"path": "schema.sql", "stat": "−1", "role": "ripple", "note": "dropped a note"}]
    page = rail.render(load_spec(write_spec(stops=[stop], files=files)))
    assert "See main.rs line 2" in page  # left as plain text
    assert 'data-ref="schema.sql:2-2"' in page
    assert "line 400" in page and 'data-ref="src/lib.rs:400' not in page


def test_flow_text_is_escaped_and_any_number_of_lanes_fits(write_spec):
    node = {
        "id": "n",
        "lane": 4,
        "x": 10,
        "w": 100,
        "stop": 1,
        "title": "t",
        "ref": "r",
        "text": "x",
    }
    flow = {
        "title": "<b>flow</b>",
        "lanes": ["<i>a</i>", "b", "c", "d", "e"],
        "nodes": [node],
        "edges": [],
    }
    page = rail.render(load_spec(write_spec(flow=flow)))
    assert "<i>a</i>" not in page and html.escape("<i>a</i>") in page
    assert 'aria-label="&lt;b&gt;flow&lt;/b&gt;"' in page


def test_a_deletions_only_stat_draws_a_bar(write_spec):
    files = [
        {"path": "src/lib.rs", "stat": "+4 −1", "role": "hot", "note": ""},
        {"path": "schema.sql", "stat": "−1", "role": "ripple", "note": ""},
    ]
    page = rail.render(load_spec(write_spec(files=files)))
    assert page.count('class="bar"') == 2


def test_terms_never_mark_inside_html_entities():
    spec = {"primer": {"terms": [{"term": "amp", "def": "an amplifier"}]}}
    assert mark_terms("a &amp; b", spec, set()) == "a &amp; b"


def test_the_bundled_examples_still_match_the_code():
    """Every example points at real code in this repository (see `anchor`)."""
    from pathlib import Path

    examples = sorted((Path(__file__).parent.parent / "examples").glob("*.json"))
    assert examples
    for path in examples:
        spec = load_spec(path)
        for layout in LAYOUTS.values():
            assert "data-line=" in layout(spec)
