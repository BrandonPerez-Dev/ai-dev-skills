"""What both layouts share: reading git, highlighting, diffing, and the spec.

Code on a walkthrough page is always quoted from git at the spec's revision,
never retyped, so everything here starts from a repository and a revision.
"""

from __future__ import annotations

import html
import json
import subprocess
from functools import lru_cache
from pathlib import Path

from pygments.lexers import get_lexer_for_filename
from pygments.token import STANDARD_TYPES
from pygments.util import ClassNotFound

KINDS = ("context", "concept", "decision", "finding")
ROLES = ("hot", "decision", "ripple")
RULINGS = (("fine", "Fine"), ("fix", "Needs a fix"), ("later", "Discuss later"))


class SpecError(ValueError):
    """A spec that points at code that is not there, or is malformed."""


def git(repo: str, *args: str) -> str | None:
    """Run git in `repo`; its stdout, or None if git failed."""
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=False)
    return r.stdout if r.returncode == 0 else None


def count_lines(text: str) -> int:
    """Lines as git and the highlighter count them: split on newlines only."""
    return len(text.split("\n")) - (1 if text.endswith("\n") else 0)


@lru_cache(maxsize=256)
def read_file(repo: str, rev: str, path: str) -> str | None:
    """The file's text at `rev`, or None if it does not exist there."""
    return git(repo, "show", f"{rev}:{path}")


def standard_class(ttype) -> str:
    """Pygments' own short class name for a token type ("k", "s2", ...)."""
    while ttype not in STANDARD_TYPES:
        ttype = ttype.parent
    return STANDARD_TYPES[ttype]


def highlight(path: str, text: str, classify=standard_class) -> list[str]:
    """The file as a list of HTML lines, each token wrapped in a class.

    The whole file is lexed at once, so a multi-line string or comment is
    coloured correctly on every line it spans. Stripping the tags and
    unescaping gives back the file exactly (a test holds this).
    """
    try:
        lexer = get_lexer_for_filename(path, stripnl=False, ensurenl=False)
    except ClassNotFound:
        return [html.escape(line) for line in text.split("\n")]
    lines: list[str] = []
    current: list[str] = []
    for ttype, value in lexer.get_tokens(text):
        cls = classify(ttype)
        for i, piece in enumerate(value.split("\n")):
            if i:
                lines.append("".join(current))
                current = []
            if piece:
                esc = html.escape(piece)
                current.append(f'<span class="{cls}">{esc}</span>' if cls else esc)
    lines.append("".join(current))
    return lines


@lru_cache(maxsize=256)
def diff_lines(repo: str, base: str | None, rev: str, path: str) -> tuple:
    """The whole file as base..rev diff rows: (tag, old_no, new_no).

    tag is " " (unchanged), "-" (only before) or "+" (only after). `base` is
    where the change starts (a commit's parent, or a PR's merge base); None
    means the file had no earlier version. A file the change did not touch
    comes back as all unchanged rows.
    """
    if base is None:
        text = read_file(repo, rev, path) or ""
        return tuple(("+", None, n) for n in range(1, count_lines(text) + 1))
    out = git(repo, "diff", "-U1000000", "--no-color", base, rev, "--", path) or ""
    rows: list[tuple[str, int | None, int | None]] = []
    old = new = 0
    in_hunk = False
    for line in out.splitlines():
        if line.startswith("@@"):
            _, a, b, *_ = line.split()
            old = int(a[1:].split(",")[0]) - 1
            new = int(b[1:].split(",")[0]) - 1
            in_hunk = True
            continue
        # Header lines come only before the first hunk. Inside a hunk a line
        # such as "--- x" is a deleted line whose text starts with "-- ".
        if not in_hunk or line.startswith("\\"):
            continue
        tag = line[:1]
        if tag == "-":
            old += 1
            rows.append(("-", old, None))
        elif tag == "+":
            new += 1
            rows.append(("+", None, new))
        else:
            old, new = old + 1, new + 1
            rows.append((" ", old, new))
    if not rows:
        text = read_file(repo, rev, path) or ""
        rows = [(" ", n, n) for n in range(1, count_lines(text) + 1)]
    return tuple(rows)


def aligned(rows):
    """Diff rows paired for a side-by-side view: (old_no, new_no, kind).

    A run of deletions faces the additions that follow it, row by row, so the
    old and new version of a statement sit side by side. kind is ctx, del,
    add or chg (a deleted line paired with an added one).
    """
    out, dels, adds = [], [], []

    def flush():
        for i in range(max(len(dels), len(adds))):
            o = dels[i] if i < len(dels) else None
            n = adds[i] if i < len(adds) else None
            out.append((o, n, "chg" if o and n else ("del" if o else "add")))
        dels.clear()
        adds.clear()

    for tag, o, n in rows:
        if tag == "-":
            if adds:
                flush()
            dels.append(o)
        elif tag == "+":
            adds.append(n)
        else:
            flush()
            out.append((o, n, "ctx"))
    flush()
    return out


def _is_str(v) -> bool:
    return isinstance(v, str) and v != ""


def _is_lines(v) -> bool:
    return (
        isinstance(v, list)
        and len(v) == 2
        and all(isinstance(n, int) and not isinstance(n, bool) for n in v)
    )


def load_spec(path: Path, repo: str | None = None) -> dict:
    """Read a spec and check it against the code it describes.

    Raises SpecError listing every problem: a missing or mistyped field, a
    stop, step or question pointing at lines that are not there, a flow that
    refers to nodes or stops that do not exist. Rendering a spec that loaded
    cleanly does not fail.
    """
    try:
        spec = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SpecError(f"cannot read the spec: {e}") from e
    if not isinstance(spec, dict):
        raise SpecError("the spec must be a JSON object")
    spec.setdefault("mode", "change")
    problems: list[str] = []
    if spec["mode"] not in ("change", "tour"):
        problems.append(f'mode must be "change" or "tour", not {spec["mode"]!r}')
    for key in ("repo", "rev", "title"):
        if not _is_str(spec.get(key)):
            problems.append(f"{key!r} must be a non-empty string")
    if not isinstance(spec.get("stops"), list) or not spec["stops"]:
        problems.append("'stops' must be a non-empty list")
    if problems:
        raise SpecError("; ".join(problems))
    # A relative repo is relative to the spec file, so a spec can travel
    # with the repository it describes. `repo` overrides it for one run.
    root = Path(repo) if repo else Path(path).parent / spec["repo"]
    spec["repo"] = str(root.resolve())
    if not _commit(spec["repo"], spec["rev"]):
        raise SpecError(f"no commit {spec['rev']} in a git repository at {spec['repo']}")
    if spec["mode"] == "change":
        if "base" in spec and not _commit(spec["repo"], spec["base"]):
            problems.append(f"no commit {spec['base']} for 'base'")
        spec.setdefault(
            "base", f"{spec['rev']}^" if _commit(spec["repo"], f"{spec['rev']}^") else None
        )
    for key in ("subtitle", "why", "reading"):
        if key in spec and not isinstance(spec[key], str):
            problems.append(f"{key!r} must be a string")
    if "lenses" in spec and not all(isinstance(x, str) for x in spec["lenses"]):
        problems.append("'lenses' must be a list of strings")
    n_stops = len(spec["stops"])
    for i, stop in enumerate(spec["stops"], 1):
        problems += _stop_problems(spec, i, stop)
    problems += _primer_problems(spec.get("primer"), n_stops)
    problems += _files_problems(spec)
    problems += _flow_problems(spec.get("flow"), n_stops)
    if problems:
        raise SpecError("; ".join(problems))
    return spec


def _commit(repo: str, rev: str) -> bool:
    return git(repo, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}") is not None


def _stop_problems(spec, i, stop) -> list[str]:
    if not isinstance(stop, dict):
        return [f"stop {i} must be an object"]
    out = []
    for key in ("file", "title", "why", "question"):
        if not _is_str(stop.get(key)):
            out.append(f"stop {i}: {key!r} must be a non-empty string")
    if not (
        isinstance(stop.get("does"), list)
        and stop["does"]
        and all(isinstance(p, str) for p in stop["does"])
    ):
        out.append(f"stop {i}: 'does' must be a non-empty list of paragraphs")
    if stop.get("kind") not in KINDS:
        out.append(f"stop {i}: kind must be one of {', '.join(KINDS)}")
    if "verdict" in stop and stop["verdict"] not in ("CONFIRMED", "PLAUSIBLE"):
        out.append(f"stop {i}: verdict must be CONFIRMED or PLAUSIBLE")
    if not _is_lines(stop.get("lines")):
        out.append(f"stop {i}: 'lines' must be [first, last]")
        return out
    if not _is_str(stop.get("file")):
        return out
    text = read_file(spec["repo"], spec["rev"], stop["file"])
    if text is None:
        out.append(f"stop {i}: {stop['file']} does not exist at {spec['rev']}")
        return out
    a, b = stop["lines"]
    if not 1 <= a <= b <= count_lines(text):
        out.append(f"stop {i}: lines {a}-{b} outside {stop['file']}")
    elif "anchor" in stop and stop["anchor"] not in text.split("\n")[a - 1]:
        # The stop's first line no longer says what the spec expects: the
        # code moved since the spec was written.
        out.append(f"stop {i}: line {a} of {stop['file']} no longer contains {stop['anchor']!r}")
    for k, step in enumerate(stop.get("steps", []), 1):
        if not (
            isinstance(step, dict) and _is_lines(step.get("lines")) and _is_str(step.get("text"))
        ):
            out.append(f"stop {i} step {k}: needs 'lines' [first, last] and 'text'")
            continue
        sa, sb = step["lines"]
        if not a <= sa <= sb <= b:
            out.append(f"stop {i} step {k}: lines {sa}-{sb} outside the stop")
    return out


def _primer_problems(primer, n_stops) -> list[str]:
    if primer is None:
        return []
    if not isinstance(primer, dict) or not _is_str(primer.get("goal")):
        return ["primer: needs a 'goal'"]
    out = []
    if not all(isinstance(m, str) for m in primer.get("model", [])):
        out.append("primer: 'model' must be a list of sentences")
    for q in primer.get("prequestions", []):
        stop = q.get("stop") if isinstance(q, dict) else None
        if not (isinstance(q, dict) and _is_str(q.get("q"))):
            out.append("primer: each prequestion needs 'q' and 'stop'")
        elif not (isinstance(stop, int) and 1 <= stop <= n_stops):
            out.append(f"prequestion points at stop {stop}, which does not exist")
    for t in primer.get("terms", []):
        if not (isinstance(t, dict) and _is_str(t.get("term")) and _is_str(t.get("def"))):
            out.append("primer: each term needs 'term' and 'def'")
    return out


def _files_problems(spec) -> list[str]:
    out = []
    for f in spec.get("files", []):
        if not (
            isinstance(f, dict) and all(isinstance(f.get(k), str) for k in ("path", "stat", "note"))
        ):
            out.append("files: each entry needs 'path', 'stat' and 'note'")
            continue
        if f.get("role") not in ROLES:
            out.append(f"files: {f['path']}: role must be one of {', '.join(ROLES)}")
        before = spec.get("base")
        exists = read_file(spec["repo"], spec["rev"], f["path"]) is not None or (
            before is not None and read_file(spec["repo"], before, f["path"]) is not None
        )
        if not exists:
            out.append(f"files: {f['path']} is not in the change")
    return out


def _flow_problems(flow, n_stops) -> list[str]:
    if flow is None:
        return []
    if not (
        isinstance(flow, dict)
        and _is_str(flow.get("title"))
        and isinstance(flow.get("lanes"), list)
        and flow["lanes"]
        and all(isinstance(x, str) for x in flow["lanes"])
    ):
        return ["flow: needs a 'title' and a list of 'lanes'"]
    out, ids = [], set()
    for n in flow.get("nodes", []):
        ok = isinstance(n, dict) and all(_is_str(n.get(k)) for k in ("id", "title", "ref", "text"))
        ok = ok and all(isinstance(n.get(k), (int, float)) for k in ("x", "w"))
        ok = ok and isinstance(n.get("lane"), int) and 0 <= n["lane"] < len(flow["lanes"])
        if not ok:
            out.append("flow: each node needs id, lane, x, w, title, ref and text")
            continue
        if n.get("stop") is not None and not (
            isinstance(n["stop"], int) and 1 <= n["stop"] <= n_stops
        ):
            out.append(f"flow: node {n['id']} points at stop {n['stop']}, which does not exist")
        ids.add(n["id"])
    for e in flow.get("edges", []):
        if not (
            isinstance(e, dict)
            and e.get("from") in ids
            and e.get("to") in ids
            and e.get("dir") in ("v", "h")
            and isinstance(e.get("label"), str)
        ):
            out.append(f"flow: edge {e!r} must join two known nodes, with dir v or h")
    if any(x not in ids for x in flow.get("order", [])):
        out.append("flow: 'order' names a node that does not exist")
    return out
