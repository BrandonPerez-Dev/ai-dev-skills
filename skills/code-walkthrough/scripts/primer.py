"""Priming shared by both layouts: the "before you read" page and the
glossary that marks each defined term where a stop first uses it.

A reader who knows the goal, the mental model and the words before meeting
the code follows it better (advance organizers; questions asked before
reading, answered later). The spec carries all of it under "primer".
"""

import html
import re


def primer_html(spec):
    """The opening block: goal, mental model, questions to hold, terms.

    Returns "" for a spec without a primer.
    """
    p = spec.get("primer")
    if not p:
        return ""
    model = "".join(f"<p>{html.escape(m)}</p>" for m in p.get("model", []))
    qs = "".join(
        f'<li>{html.escape(q["q"])} <span class="muted">(answered at stop {q["stop"]})</span></li>'
        for q in p.get("prequestions", [])
    )
    terms = "".join(
        f'<dt id="term-{slug(t["term"])}">{html.escape(t["term"])}</dt><dd>{html.escape(t["def"])}</dd>'
        for t in p.get("terms", [])
    )
    return (
        f'<div class="primer"><div class="phead"><p class="where">Before you read</p>'
        f"<h2>{html.escape(p['goal'])}</h2></div>"
        f'<div class="pblk"><h3>The picture to hold</h3>{model}</div>'
        + (
            f'<div class="pblk"><h3>Keep these questions in mind</h3><ol class="preq">{qs}</ol></div>'
            if qs
            else ""
        )
        + (
            f'<div class="pblk"><h3>Words you will meet</h3><dl class="terms">{terms}</dl></div>'
            if terms
            else ""
        )
        + "</div>"
    )


def slug(term):
    return re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")


def define_terms(text, spec, seen):
    """Escape `text` and mark the first use of each glossary term in it."""
    return mark_terms(html.escape(text, quote=False), spec, seen)


def mark_terms(markup, spec, seen):
    """Mark the first use of each glossary term in already-escaped HTML.

    `seen` is shared across one stop, so a term is marked once per stop:
    a reader who jumps straight to a stop still gets the definition.
    Text inside tags is never touched.
    """
    # Longest first, so "idempotency key" is marked before "key" can match
    # inside it. A capitalised term (a type name such as Store) matches
    # case-sensitively, so it does not mark the plain word "store".
    terms = sorted(spec.get("primer", {}).get("terms", []), key=lambda t: -len(t["term"]))
    for t in terms:
        term = t["term"]
        if term in seen:
            continue
        flags = 0 if term[:1].isupper() else re.IGNORECASE
        word = re.escape(html.escape(term, quote=False))
        pat = re.compile(rf"(?<![\w-])({word})(?![\w-])", flags)
        # Tags, and anything already marked, are never searched.
        pieces = re.split(r"(<dfn[^>]*>.*?</dfn>|<[^>]+>|&#?\w+;)", markup)
        for k, piece in enumerate(pieces):
            if piece.startswith(("<", "&")):
                continue
            m = pat.search(piece)
            if m:
                tip = html.escape(t["def"], quote=True)
                pieces[k] = (
                    piece[: m.start()] + f'<dfn title="{tip}">{m.group(1)}</dfn>' + piece[m.end() :]
                )
                seen.add(term)
                break
        markup = "".join(pieces)
    return markup


def answered_here(spec, stop_no):
    """The primer questions this stop answers, as a callout."""
    qs = [q["q"] for q in spec.get("primer", {}).get("prequestions", []) if q["stop"] == stop_no]
    if not qs:
        return ""
    items = "".join(f"<li>{html.escape(q)}</li>" for q in qs)
    return f'<div class="answers"><p class="where">You can now answer</p><ul>{items}</ul></div>'
