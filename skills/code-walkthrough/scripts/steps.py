"""Steps inside a stop: one stop's code, explained a few lines at a time.

A stop may carry "steps": [{"lines": [a, b], "text": "..."}]. Each step
focuses those lines and shows its own explanation. Both layouts render the
same list; how a step is focused is up to each layout's script.
"""

import html


def steps_html(stop, mark, link=None):
    """The step list for one stop, or "" when it has none.

    `mark` turns step text into HTML (glossary terms marked). `link`, when
    given, renders the "lines a-b" label as that layout's line reference.
    """
    steps = stop.get("steps")
    if not steps:
        return ""
    items = []
    for n, step in enumerate(steps, 1):
        a, b = step["lines"]
        where = f"line {a}" if a == b else f"lines {a}–{b}"
        label = link(stop["file"], a, b, where) if link else where
        # A button, not a bare list item: with annotate mode on, the page
        # server turns clicks on plain elements into annotations.
        items.append(
            f'<li data-from="{a}" data-to="{b}"><button type="button" class="stepbtn">'
            f'{n}</button><span class="steplines">{label}</span> '
            f"{mark(step['text'])}</li>"
        )
    return (
        f'<div class="steps" data-file="{html.escape(stop["file"])}"><h3>Step through '
        f'<span class="stepcount">{len(steps)} steps</span></h3>'
        f"<ol>{''.join(items)}</ol></div>"
    )
