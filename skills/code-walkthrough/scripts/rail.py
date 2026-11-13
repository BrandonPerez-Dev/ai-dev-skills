"""The rail layout: one long page with a file-map rail and a flow diagram.

A rail on the left maps every file and where each stop sits in it; the page
opens with the primer and the flow between stops, then every stop in turn.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from pathlib import Path

from pygments.token import Token

from core import RULINGS, count_lines, diff_lines, highlight, read_file
from primer import answered_here, mark_terms, primer_html
from steps import steps_html

TEMPLATE = Path(__file__).parent / "templates" / "rail.html"
esc = html.escape


@dataclass
class Rail:
    """One render: the spec and what is derived from it."""

    spec: dict
    tour: bool = field(init=False)
    repo: str = field(init=False)
    rev: str = field(init=False)
    parent: str | None = field(init=False)
    flow: dict | None = field(init=False)
    cache: dict = field(default_factory=dict)

    def __post_init__(self):
        self.tour = self.spec["mode"] == "tour"
        self.repo, self.rev = self.spec["repo"], self.spec["rev"]
        self.parent = self.spec.get("base")  # None: no earlier version
        self.flow = self.spec.get("flow")


def file_at(r, rev, path):
    return read_file(r.repo, rev, path) or ""


# ---------------------------------------------------------------- highlight


def tok_class(tt):
    for base, cls in [
        (Token.Comment, "c"),
        (Token.Literal.String, "s"),
        (Token.Literal.Number, "n"),
        (Token.Keyword.Type, "t"),
        (Token.Keyword, "k"),
        (Token.Name.Function, "f"),
        (Token.Name.Builtin, "t"),
        (Token.Name.Class, "t"),
        (Token.Name.Attribute, "m"),
        (Token.Name.Decorator, "m"),
        (Token.Comment.Preproc, "m"),
        (Token.Name.Namespace, "ns"),
        (Token.Operator, "o"),
        (Token.Punctuation, "p"),
    ]:
        if tt in base:
            return cls
    return ""


def highlighted(r, rev, path):
    """Per-line HTML for the whole file, and the raw lines beside it."""
    key = (rev, path)
    if key not in r.cache:
        text = file_at(r, rev, path)
        raw = text.split("\n")[: count_lines(text)]
        out = highlight(path, text, tok_class)[: len(raw)]
        r.cache[key] = (out, raw)
    return r.cache[key]


# --------------------------------------------------------------------- diff


def diff_rows(r, path):
    """Whole-file diff as a list of (kind, old_no, new_no), kind in ' -+'.

    A tour has no diff: every line is unchanged.
    """
    if r.tour:
        n = count_lines(file_at(r, r.rev, path))
        return [(" ", i, i) for i in range(1, n + 1)]
    return list(diff_lines(r.repo, r.parent, r.rev, path))


def added_ranges(r, path):
    added = sorted(n for k, _, n in diff_rows(r, path) if k == "+")
    return to_ranges(added)


def to_ranges(nums):
    out = []
    for n in nums:
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return out


def window(r, path, first, last):
    """Diff rows covering new lines first..last, plus deletions inside or just before."""
    rows = diff_rows(r, path)
    idx = [i for i, (k, o, n) in enumerate(rows) if n is not None and first <= n <= last]
    lo, hi = idx[0], idx[-1]
    while lo > 0 and rows[lo - 1][0] == "-":
        lo -= 1
    return rows[lo : hi + 1]


def pair(rows):
    """Side-by-side pairs: runs of deletions face the additions after them."""
    pairs, i = [], 0
    while i < len(rows):
        if rows[i][0] == " ":
            pairs.append((rows[i], rows[i]))
            i += 1
            continue
        dels, adds = [], []
        while i < len(rows) and rows[i][0] == "-":
            dels.append(rows[i])
            i += 1
        while i < len(rows) and rows[i][0] == "+":
            adds.append(rows[i])
            i += 1
        for j in range(max(len(dels), len(adds))):
            pairs.append((dels[j] if j < len(dels) else None, adds[j] if j < len(adds) else None))
    return pairs


# --------------------------------------------------------------- code cells


def line_div(r, path, no, side, kind, order, hl):
    """One annotatable line. After side: data-line=path:N. Before side uses
    git's own name for the old file, data-line=REV^:path:N."""
    if side == "new":
        code, cls, dl = hl[0][no - 1], {"+": "add", " ": "ctx"}[kind], f"{path}:{no}"
    else:
        code, cls, dl = (
            hl[0][no - 1],
            {"-": "del", " ": "ctx"}[kind],
            f"{r.parent}:{path}:{no}",  # escaped below with the rest
        )
    return (
        f'<div class="ln {cls} {side}" data-line="{esc(dl)}" style="order:{order}">'
        f'<span class="no">{no}</span><code>{code or " "}</code></div>'
    )


def code_block(r, stop):
    path, (first, last) = stop["file"], stop["lines"]
    new_hl = highlighted(r, r.rev, path)
    old_hl = new_hl if r.tour or r.parent is None else highlighted(r, r.parent, path)
    rows = window(r, path, first, last)
    pairs = pair(rows)
    has_before = any(k != "+" for k, _, _ in rows)
    # Unified order: walk rows in diff order; each cell gets its position.
    uorder = {row: pos for pos, row in enumerate(rows)}
    cells = []
    for left, right in pairs:
        if left is None:
            cells.append('<div class="ln gap before" aria-hidden="true" style="order:0"></div>')
        elif left[0] == " ":
            cells.append(
                line_div(r, path, left[1], "old", " ", 0, old_hl).replace(
                    'class="ln ctx old"', 'class="ln ctx old twin"'
                )
            )
        else:
            cells.append(line_div(r, path, left[1], "old", "-", uorder[left], old_hl))
        if right is None:
            cells.append('<div class="ln gap after" aria-hidden="true" style="order:0"></div>')
        else:
            cells.append(line_div(r, path, right[2], "new", right[0], uorder[right], new_hl))
    added = sum(1 for k, _, _ in rows if k == "+")
    deleted = sum(1 for k, _, _ in rows if k == "-")
    tag = (
        "as it stands"
        if r.tour
        else "all new in this commit"
        if not has_before
        else f"+{added} −{deleted} in this range"
    )
    return (
        f'<div class="codebox{" newonly" if r.tour or not has_before else ""}">'
        f'<div class="codehead"><span class="path">{esc(path)}</span>'
        f'<span class="range">{first}–{last}</span>'
        f'<span class="tag">{tag}</span>'
        f'<span class="sides"><span>before · {esc(r.parent or "")}</span>'
        f"<span>after · {esc(r.rev)}</span></span></div>"
        f'<div class="lines">{"".join(cells)}</div></div>'
    )


# ------------------------------------------------- references inside prose

# "lines 295-296", "line 364", or "client.rs lines 1-4": an optional file
# name (any extension), then one line or a range.
REF = re.compile(r"(?:\b([\w./-]+\.\w+) )?\blines? (\d+)(?:[–-](\d+))?")


def resolve_ref(r, stop, m):
    """(path, a, b) for a reference, or None if it names no file in the spec
    or no line in that file. Unresolved references stay plain text."""
    short, a = m.group(1), int(m.group(2))
    b = int(m.group(3) or a)
    path = stop["file"]
    if short:
        path = next((f for f in all_paths(r) if f == short or f.endswith("/" + short)), None)
        if path is None:
            return None
    n = count_lines(file_at(r, r.rev, path))
    if not 1 <= a <= n:
        return None
    return path, a, min(max(a, b), n)


def refs_in(r, stop):
    """Line references in a stop's prose that resolve: (label, path, a, b)."""
    out = []
    for text in [*stop["does"], stop["why"], stop["question"]]:
        for m in REF.finditer(text):
            ref = resolve_ref(r, stop, m)
            if ref:
                out.append((m.group(0), *ref))
    return out


def linkify(r, text, stop):
    def sub(m):
        ref = resolve_ref(r, stop, m)
        if ref is None:
            return m.group(0)
        path, a, b = ref
        return f'<a href="#" class="lref" data-ref="{esc(path)}:{a}-{b}">{m.group(0)}</a>'

    # Escape first, then link: the pattern only matches word characters,
    # dots, slashes and digits, which escaping leaves alone.
    return REF.sub(sub, esc(text, quote=False))


# A tour has no diff, so it gets no diff toggle.
DIFF_TOGGLE = (
    '<div class="seg" role="group" aria-label="Diff view">'
    '<button type="button" data-view="inline" class="on">Inline diff</button>'
    '<button type="button" data-view="split">Before | after</button></div>'
)


def all_files(r):
    return list(dict.fromkeys(all_paths(r)))


def all_paths(r):
    return [f["path"] for f in r.spec.get("files", [])] + [s["file"] for s in r.spec["stops"]]


def step_ref(path, a, b, label):
    return f'<a href="#" class="lref" data-ref="{esc(path)}:{a}-{b}">{esc(label)}</a>'


def stop_of(r, path, line):
    for i, s in enumerate(r.spec["stops"], 1):
        if s["file"] == path and s["lines"][0] <= line <= s["lines"][1]:
            return i
    return None


def peeks(r, stop):
    """Lines a stop's prose points at that no stop shows: quote them here."""
    blocks = []
    for _label, path, a, b in refs_in(r, stop):
        if stop_of(r, path, a):
            continue
        hl = highlighted(r, r.rev, path)
        if a == b:  # a single line: show the statement it starts
            b = min(a + 3, len(hl[0]))
        lines = "".join(
            f'<div class="ln ctx new" data-line="{esc(path)}:{n}"><span class="no">{n}</span>'
            f"<code>{hl[0][n - 1] or ' '}</code></div>"
            for n in range(a, b + 1)
        )
        blocks.append(
            f'<div class="peek" id="peek-{esc(path)}-{a}"><div class="codehead">'
            f'<span class="path">{esc(path)}</span><span class="range">{a}–{b}</span>'
            f'<span class="tag">referenced above, outside the stop</span></div>'
            f'<div class="lines">{lines}</div></div>'
        )
    return "".join(blocks)


# -------------------------------------------------------------------- stops


def ruling(i, stop):
    btns = "".join(
        f'<button type="button" class="rule r-{key}" data-ruling="{key}">{lab}</button>'
        for key, lab in RULINGS
    )
    return f'<div class="ruling" data-stop="{i}">{btns}</div>'


def stop_html(r, i, stop):
    kind = stop["kind"]
    verdict = f" · {esc(stop['verdict'].lower())}" if stop.get("verdict") else ""
    seen = set()

    def lk(text):
        return mark_terms(linkify(r, text, stop), r.spec, seen)

    does = "".join(f"<p>{lk(p)}</p>" for p in stop["does"])
    first, last = stop["lines"]
    return f'''<article class="stop" id="stop-{i}" data-stop="{i}" data-kind="{kind}">
<div class="notes">
  <div class="stophead"><span class="num">{i}</span>
    <span class="kind k-{kind}">{kind}{verdict}</span>
    <span class="loc">{esc(stop["file"])}:{first}–{last}</span></div>
  <h2>{esc(stop["title"])}</h2>
  <div class="blk does"><h3>What it does</h3>{does}</div>
  {steps_html(stop, lambda t: lk(t), step_ref)}
  <div class="blk why"><h3>Why it is a stop</h3><p>{lk(stop["why"])}</p></div>
  {answered_here(r.spec, i)}
  <div class="blk ask"><h3>Your call</h3><p class="question">{lk(stop["question"])}</p>
  {ruling(i, stop)}
  <p class="hint">Select any line or sentence and annotate it to ask; the agent answers in a thread.</p></div>
</div>
<div class="codecol">{code_block(r, stop)}{peeks(r, stop)}</div>
</article>'''


# ------------------------------------------------------------- change map


def stat_counts(stat):
    """(added, deleted) from a stat such as "+159 −15", "+3", "−12" or "-4"."""
    added = re.search(r"\+(\d+)", stat)
    deleted = re.search(r"[−-](\d+)", stat)
    return (int(added.group(1)) if added else 0, int(deleted.group(1)) if deleted else 0)


def bar(r, stat):
    a, d = stat_counts(stat)
    if not a and not d:
        return ""
    scale = max(sum(stat_counts(f["stat"])) for f in r.spec.get("files", [])) or 1
    return (
        f'<span class="bar"><i class="a" style="width:{a / scale * 100:.1f}%"></i>'
        f'<i class="d" style="width:{d / scale * 100:.1f}%"></i></span>'
    )


PX = 0.62  # minimap pixels per source line


def minimap(r, path):
    n = count_lines(file_at(r, r.rev, path))
    h = round(n * PX)
    parts = [f'<div class="strip" style="height:{h}px">']
    for a, b in added_ranges(r, path):
        parts.append(
            f'<i class="tick" style="top:{(a - 1) * PX:.1f}px;'
            f'height:{max(1.5, (b - a + 1) * PX):.1f}px"></i>'
        )
    labels = []
    for i, s in enumerate(r.spec["stops"], 1):
        if s["file"] != path:
            continue
        a, b = s["lines"]
        top = (a - 1) * PX
        parts.append(
            f'<a href="#stop-{i}" class="box" data-goto="{i}" data-ref-stop="{i}" '
            f'style="top:{top:.1f}px;height:{(b - a + 1) * PX:.1f}px" '
            f'title="Stop {i}: {esc(s["title"])}"></a>'
        )
        labels.append((top, i, s))
    parts.append("</div>")
    # Labels sit beside the strip at their stop's height, nudged apart.
    lab, last = [], -99
    for top, i, s in sorted(labels):
        y = max(top - 4, last + 22)
        last = y
        lab.append(
            f'<a href="#stop-{i}" class="mlabel" data-goto="{i}" data-ref-stop="{i}" '
            f'style="top:{y:.1f}px"><b>{i}</b> {esc(s["title"])}</a>'
        )
    tall = max(h, last + 24)
    return (
        f'<div class="mini" style="height:{tall}px">{"".join(parts)}'
        f'<div class="mlabels">{"".join(lab)}</div></div>'
    )


def test_map(r, path):
    """A hot file with no stop: where each #[test] sits."""
    raw = file_at(r, r.rev, path).split("\n")
    tests = []
    for i, line in enumerate(raw):
        if line.strip() != "#[test]":
            continue
        # The function may follow other attributes (#[should_panic]) or be async.
        for j in range(i + 1, min(i + 6, len(raw))):
            m = re.search(r"\bfn (\w+)", raw[j])
            if m:
                tests.append((j + 1, m.group(1)))
                break
    items = "".join(
        f'<li data-line="{esc(path)}:{n}"><span class="no">{n}</span><code>{esc(name)}</code></li>'
        for n, name in tests
    )
    return f'<ul class="tests">{items}</ul>' if items else ""


def change_map(r):
    hot, ripple = [], []
    files = r.spec.get("files") or [
        {"path": p, "stat": "", "role": "hot", "note": ""}
        for p in dict.fromkeys(s["file"] for s in r.spec["stops"])
    ]
    for f in files:
        stops = [i for i, s in enumerate(r.spec["stops"], 1) if s["file"] == f["path"]]
        head = (
            f'<div class="fhead"><code class="fp">{esc(f["path"])}</code>'
            f'<span class="stat">{esc(f["stat"])}</span>{bar(r, f["stat"]) if f["stat"] else ""}</div>'
        )
        if f["role"] == "hot":
            body = minimap(r, f["path"]) if stops else test_map(r, f["path"])
            hot.append(
                f'<div class="file hot">{head}<p class="fnote">{esc(f["note"])}</p>{body}</div>'
            )
        else:
            ripple.append(
                f'<li class="file {esc(f["role"])}" title="{esc(f["note"])}">{head}'
                f'<span class="fnote">{esc(f["note"])}</span></li>'
            )
    return "".join(hot), "".join(ripple)


# ------------------------------------------------------------------ flow map

# The flow diagram comes from the spec ("flow"): lanes, nodes (stops or
# plain waypoints naming the code between them) and edges. Positions are in
# viewBox units. A spec without a flow gets no diagram.
LANE_TOP, LANE_STEP = 16, 76


def lane_y(i):
    return LANE_TOP + LANE_STEP * i


NODE_H = 46


def flow_svg(r):
    nodes = {
        n["id"]: (n["id"], n["lane"], n["x"], n["w"], n.get("stop"), n["title"], n["ref"])
        for n in r.flow.get("nodes", [])
    }
    g = []
    for i, name in enumerate(r.flow["lanes"]):
        y = lane_y(i)
        g.append(
            f'<rect class="lane" x="0" y="{y - 8}" width="1000" height="{NODE_H + 16}" rx="8"/>'
            f'<text class="lanelab" x="12" y="{y + NODE_H / 2 + 4}">{esc(name)}</text>'
        )
    for a, b, label, side in (
        (e["from"], e["to"], e["label"], e["dir"]) for e in r.flow.get("edges", [])
    ):
        na, nb = nodes[a], nodes[b]
        ya, yb = lane_y(na[1]), lane_y(nb[1])
        if side == "v":
            x = max(na[2], nb[2]) + 34
            y1, y2 = (ya + NODE_H, yb) if ya < yb else (ya, yb + NODE_H)
            g.append(
                f'<path class="edge" d="M{x},{y1} L{x},{y2 + (-4 if ya < yb else 4)}" marker-end="url(#arr)"/>'
                f'<text class="elab" x="{x + 6}" y="{(y1 + y2) / 2 + 4}">{esc(label)}</text>'
            )
        else:
            if na[2] < nb[2]:
                x1, x2 = na[2] + na[3], nb[2] - 4
            else:
                x1, x2 = na[2], nb[2] + nb[3] + 4
            y = ya + NODE_H / 2
            g.append(
                f'<path class="edge" d="M{x1},{y} L{x2},{y}" marker-end="url(#arr)"/>'
                f'<text class="elab mid" x="{(x1 + x2) / 2}" y="{y - 6}">{esc(label)}</text>'
            )
    for _nid, lane, x, w, stop, title, ref in nodes.values():
        y = lane_y(lane)
        if stop:
            g.append(
                f'<a href="#stop-{stop}" class="fnode stop" data-goto="{stop}" data-ref-stop="{stop}">'
                f'<rect x="{x}" y="{y}" width="{w}" height="{NODE_H}" rx="7"/>'
                f'<circle cx="{x + 20}" cy="{y + NODE_H / 2}" r="12"/>'
                f'<text class="nnum" x="{x + 20}" y="{y + NODE_H / 2 + 5}">{stop}</text>'
                f'<text class="ntitle" x="{x + 40}" y="{y + 20}">{esc(title)}</text>'
                f'<text class="nref" x="{x + 40}" y="{y + 36}">{esc(ref)}</text></a>'
            )
        else:
            g.append(
                f'<g class="fnode way"><rect x="{x}" y="{y}" width="{w}" height="{NODE_H}" rx="7"/>'
                f'<text class="ntitle" x="{x + 12}" y="{y + 20}">{esc(title)}</text>'
                f'<text class="nref" x="{x + 12}" y="{y + 36}">{esc(ref)}</text></g>'
            )
    height = lane_y(len(r.flow["lanes"]) - 1) + NODE_H + 16
    return (
        f'<svg class="flow" viewBox="0 0 1000 {height}" role="img" '
        f'aria-label="{esc(r.flow["title"])}">'
        f'<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>'
        f"{''.join(g)}</svg>"
    )


def flow_list(r):
    """The same flow as a list, for screens too narrow for the diagram."""
    nodes = {n["id"]: n for n in r.flow.get("nodes", [])}
    items = []
    for nid in r.flow.get("order") or list(nodes):
        n = nodes[nid]
        num = (
            f'<a href="#stop-{n["stop"]}" class="fnum" data-goto="{n["stop"]}" '
            f'data-ref-stop="{n["stop"]}">{n["stop"]}</a>'
            if n.get("stop")
            else '<span class="fnum way">·</span>'
        )
        items.append(f"<li>{num}<span>{esc(n['text'])} <code>{esc(n['ref'])}</code></span></li>")
    return f'<ol class="flowlist">{"".join(items)}</ol>'


def flow_block(r):
    if not r.flow:
        return ""
    return (
        f'<div class="flowwrap"><h2 class="lbl">{esc(r.flow["title"])} · click a stop</h2>'
        f"{flow_svg(r)}{flow_list(r)}</div>"
    )


# ------------------------------------------------------------------- page


def render(spec: dict) -> str:
    """The whole page for a checked spec (see core.load_spec)."""
    r = Rail(spec)
    stops = r.spec["stops"]
    hot, ripple = change_map(r)
    lenses = "".join(f"<li>{esc(lens)}</li>" for lens in r.spec.get("lenses", []))
    pips = "".join(
        f'<a href="#stop-{i}" class="pip" data-goto="{i}" data-ref-stop="{i}" '
        f'title="Stop {i}: {esc(s["title"])}">{i}</a>'
        for i, s in enumerate(stops, 1)
    )
    body = "\n".join(stop_html(r, i, s) for i, s in enumerate(stops, 1))
    return (
        TEMPLATE.read_text(encoding="utf-8")
        .replace("{{TITLE}}", esc(r.spec["title"]))
        .replace("{{SUBTITLE}}", esc(r.spec.get("subtitle", "")))
        .replace("{{WHY}}", esc(r.spec.get("why", "")))
        .replace("{{PIPS}}", pips)
        .replace("{{N}}", str(len(stops)))
        .replace("{{HOT}}", hot)
        .replace(
            "{{RIPPLEBLOCK}}",
            f'<h4>Ripple and decision files</h4><ul class="ripple">{ripple}</ul>' if ripple else "",
        )
        .replace("{{LENSES}}", lenses)
        .replace("{{FLOWBLOCK}}", flow_block(r))
        .replace("{{PRIMER}}", primer_html(r.spec))
        .replace("{{DIFFTOGGLE}}", "" if r.tour else DIFF_TOGGLE)
        .replace("{{MAPLABEL}}", "Files on this tour" if r.tour else "Change map")
        .replace("{{MAPCOUNT}}", f"{len(all_files(r))} files")
        .replace("{{STOPS}}", body)
    )
