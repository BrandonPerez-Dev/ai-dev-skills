"""The pages layout: one stop per page, turned left and right.

The first page primes the reader and maps the walkthrough; each stop after
it puts code on the left and its explanation on the right.
"""

from __future__ import annotations

import html
from pathlib import Path

from core import RULINGS, aligned, diff_lines, highlight, read_file
from primer import answered_here, define_terms, primer_html
from steps import steps_html

TEMPLATE = Path(__file__).parent / "templates" / "pages.html"
GAP = '<div class="ln gap"><span class="num"></span><code> </code></div>'
esc = html.escape


def highlighted(spec, rev, path):
    text = read_file(spec["repo"], rev, path)
    return None if text is None else highlight(path, text)


def line_div(path, n, code, cls="ln"):
    return (
        f'<div class="{cls}" data-line="{esc(path)}:{n}"><span class="num">{n}</span>'
        f"<code>{code or ' '}</code></div>"
    )


def after_view(path, lines, first, last, added):
    return "".join(
        line_div(path, n, lines[n - 1], "ln add" if n in added else "ln")
        for n in range(first, last + 1)
    )


def split_view(path, old_lines, new_lines, rows, first, last):
    """Before on the left, after on the right, aligned row by row."""
    inside = [i for i, (_, n, _) in enumerate(rows) if n and first <= n <= last]
    if not inside:
        return ""
    left, right = [], []
    for o, n, kind in rows[inside[0] : inside[-1] + 1]:
        left.append(line_div(f"{path}@before", o, old_lines[o - 1], f"ln {kind}") if o else GAP)
        right.append(line_div(path, n, new_lines[n - 1], f"ln {kind}") if n else GAP)
    return (
        f'<div class="split"><div class="lines side">{"".join(left)}</div>'
        f'<div class="lines side">{"".join(right)}</div></div>'
    )


def code_pane(spec, stop):
    rev = spec["rev"]
    path, (first, last) = stop["file"], stop["lines"]
    lines = highlighted(spec, rev, path)
    toggle, split, added = "", "", set()
    if spec["mode"] == "change":
        base = spec.get("base")
        rows = aligned(diff_lines(spec["repo"], base, rev, path))
        added = {n for _, n, k in rows if n and k in ("add", "chg")}
        old_lines = highlighted(spec, base, path) if base else None
        changed_here = any(k != "ctx" for _, n, k in rows if n and first <= n <= last)
        if old_lines is not None and changed_here:
            split = split_view(path, old_lines, lines, rows, first, last)
        if split:
            toggle = (
                '<span class="views"><button type="button" data-view="after" class="on">'
                'After</button><button type="button" data-view="split">Before | after'
                "</button></span>"
            )
        elif old_lines is None:
            toggle = '<span class="muted">new file</span>'
    return (
        f'<div class="code"><div class="codehead"><span>{esc(path)}:{first}-{last} '
        f'<span class="muted">at {esc(rev)}</span></span>{toggle}</div>'
        f'<div class="lines after">{after_view(path, lines, first, last, added)}</div>'
        f"{split}</div>"
    )


def ruling(i):
    buttons = "".join(
        f'<button type="button" data-ruling="{r}">{label}</button>' for r, label in RULINGS
    )
    return f'<div class="ruling" data-stop="{i}">{buttons}</div>'


def stop_page(spec, i, n, stop):
    kind = stop["kind"]
    seen: set[str] = set()

    def mark(text):
        return define_terms(text, spec, seen)

    notes = "".join(f"<p>{mark(p)}</p>" for p in stop["does"])
    verdict = f" · {esc(stop['verdict'])}" if stop.get("verdict") else ""
    return f"""<section class="stop" id="stop-{i}">
{code_pane(spec, stop)}
<aside class="notes">
<p class="where">Stop {i} of {n} · <span class="kind {kind}">{kind}{verdict}</span></p>
<h2>{esc(stop["title"])}</h2>
<h3>What it does</h3>{notes}
{steps_html(stop, mark)}
<h3>Why it is a stop</h3><p>{mark(stop["why"])}</p>
{answered_here(spec, i)}
<h3>Your call</h3><p class="question">{mark(stop["question"])}</p>
{ruling(i)}
<p class="muted hint">Select any line or sentence and annotate it to ask the agent; it answers in a thread.</p>
</aside></section>"""


def map_page(spec):
    stops = spec["stops"]
    toc = "".join(
        f'<tr><td>{i}</td><td>{esc(s["title"])}</td><td><span class="kind {s["kind"]}">'
        f"{s['kind']}</span></td><td><code>{esc(s['file'])}:{s['lines'][0]}-{s['lines'][1]}"
        "</code></td></tr>"
        for i, s in enumerate(stops, 1)
    )
    files = ""
    if spec.get("files"):
        rows = "".join(
            f'<tr class="{esc(f["role"])}"><td><code>{esc(f["path"])}</code></td>'
            f"<td>{esc(f['stat'])}</td><td>{esc(f['role'])}</td><td>{esc(f['note'])}</td></tr>"
            for f in spec["files"]
        )
        files = (
            "<h3>Every file the change touches</h3><table><thead><tr><th>File</th>"
            f"<th>Lines</th><th>Role</th><th>Note</th></tr></thead><tbody>{rows}</tbody></table>"
        )
    lenses = "".join(f"<li>{esc(lens)}</li>" for lens in spec.get("lenses", []))
    where = f"{len(spec['files'])} files, " if spec.get("files") else ""
    return f"""<section class="stop map" id="stop-0">
<div class="mapmain">
{primer_html(spec)}
<p class="where">The map · {where}{len(stops)} stops</p>
<h2>{esc(spec["title"])}</h2>
<p>{esc(spec.get("why", ""))}</p>
<h3>The path</h3>
<table><thead><tr><th>#</th><th>Stop</th><th>Kind</th><th>Where</th></tr></thead><tbody>{toc}</tbody></table>
{files}
</div>
<aside class="notes">
<h3>How to read this</h3>
<p>One stop per page. Use the arrow keys, the numbered dots, or swipe, to move left and right. On a stop with steps, the arrows walk its steps first.</p>
<p>{esc(spec.get("reading", ""))}</p>
<h3>Looked for</h3><ul>{lenses}</ul>
</aside></section>"""


def render(spec: dict) -> str:
    """The whole page for a checked spec (see core.load_spec)."""
    stops = spec["stops"]
    pages = [map_page(spec)] + [stop_page(spec, i, len(stops), s) for i, s in enumerate(stops, 1)]
    return (
        TEMPLATE.read_text(encoding="utf-8")
        .replace("{{TITLE}}", esc(spec["title"]))
        .replace("{{SUBTITLE}}", esc(spec.get("subtitle", "")))
        .replace("{{PAGES}}", "\n".join(pages))
    )
