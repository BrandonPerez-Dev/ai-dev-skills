#!/usr/bin/env python3
"""Render a code walkthrough spec as an annotatable page.

One spec, two layouts:
  pages  one stop per page, turned left and right
  rail   one long page with a file-map rail and a flow diagram

The layout is a reader setting, not part of the spec. It comes from
--layout, else $CODE_WALKTHROUGH_LAYOUT, else "pages".

    walkthrough.py spec.json                      # writes spec-pages.html
    walkthrough.py spec.json --layout rail -o out.html
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pages
import rail
from core import SpecError, load_spec

LAYOUTS = {"pages": pages.render, "rail": rail.render}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("spec", type=Path)
    ap.add_argument("--layout", choices=sorted(LAYOUTS))
    ap.add_argument("-o", "--out", type=Path)
    ap.add_argument("--repo", help="the repository, overriding the spec's repo for this run")
    args = ap.parse_args(argv)
    layout = args.layout or os.environ.get("CODE_WALKTHROUGH_LAYOUT", "pages")
    if layout not in LAYOUTS:
        ap.error(f"unknown layout {layout!r}; choose from {', '.join(sorted(LAYOUTS))}")
    try:
        spec = load_spec(args.spec, args.repo)
    except SpecError as e:
        print(f"{args.spec}: {e}", file=sys.stderr)
        return 1
    out = args.out or args.spec.with_name(f"{args.spec.stem}-{layout}.html")
    page = LAYOUTS[layout](spec)
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out}: {spec['mode']} mode, {layout} layout, {len(spec['stops'])} stops")
    return 0


if __name__ == "__main__":
    sys.exit(main())
