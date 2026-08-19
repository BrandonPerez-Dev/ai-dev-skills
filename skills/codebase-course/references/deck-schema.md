# deck.json — Flashcard Deck Schema

Both skills emit a `deck.json` next to the HTML output. This is the layer no existing
tool ships (verified 2026-07-14, ~/research/codebase-study-guide-ci-flashcards-2026.md):
generation is solved everywhere; carrying the material into spaced retrieval is not.
The deck is that carrier — Anki-convertible today, Arboreus-importable later, and
merge-friendly so a CI step can accumulate per-PR decks into a living repo deck.

## Schema

```json
{
  "version": 1,
  "source": {
    "type": "codebase | pr",
    "repo": "arboreus-api",
    "ref": "20a02f9",
    "pr": 42
  },
  "generated_by": "codebase-course | pr-walkthrough",
  "generated_at": "2026-07-14",
  "cards": [
    {
      "id": "graph-engine--cycle-guard-ordering",
      "concept": "edge insertion invariant",
      "module": "02-graph-engine",
      "type": "qa | scenario | rationale",
      "front": "In arboreus-api, an edge insert would create a cycle. What state is the database left in, and why?",
      "back": "Unchanged. wouldCycle() runs entirely in memory before any write — validation-then-write ordering is the invariant, so rejected edges leave no trace.",
      "files": ["src/graph/engine.ts:118"],
      "tags": ["graph-engine", "invariant"]
    }
  ]
}
```

## Field rules

- **`id`** — stable slug: `<module-or-change-area>--<concept-slug>[-n]`. Stability is
  what makes decks mergeable: a regenerated deck for the same repo state must produce
  the same ids, so a CI merge step can upsert instead of duplicate. Never include line
  numbers or dates in ids.
- **`front`** — must be answerable *without the codebase open*, and must name the repo
  or subsystem (cards get studied months later, mixed with cards from other repos —
  "what does insertEdge do" is meaningless in a shuffled deck).
- **`back`** — the mechanism in ≤3 sentences, then nothing. A back that needs scrolling
  is a lesson, not a card.
- **`files`** — pointers for verification, not part of the answer. Line numbers are
  allowed here (they're a courtesy, expected to rot).
- **`type`** — `qa` (direct mechanism recall), `scenario` (input → consequence),
  `rationale` (why this design over the alternative). Same quality bar as
  quiz-design.md §1: if a rename-only refactor changes the answer, cut the card.
- **`concept`** — human-readable concept name, shared across cards that test the same
  idea from different angles. This is the future Arboreus join key.

## Card selection

Derive cards from the module objectives and the quiz questions — the quiz is the
generator, the card is the distilled retrieval form (no distractors, no code block
unless the code IS the answer). Per module: 3–6 cards. Per PR: 2–5 cards, scoped to
what the change teaches (a new invariant, a moved boundary, a new failure mode) — not
to the mechanical edits.

Skip cards entirely for modules/changes that taught nothing durable (pure refactors,
dependency bumps). An empty `cards: []` deck is honest; padded decks poison the review
queue and are why people abandon SRS.

## The study hub (default workflow)

Generated guides and decks collect in **one hub folder** (default `~/study`,
override with `$STUDY_HUB`), not in scattered per-repo `study/` dirs:

```
~/study/
├── index.html          the reviewer — dashboard, card-flip review, links to every guide
├── decks.js            generated: every deck bundled so index.html can auto-load them
├── arboreus-api/       course.html + deck.json (course gets a "← Study hub" backlink)
└── <other subjects>/
```

Build or refresh it with:

```
study.py hub --add path/to/generated/study    # copy a new guide+deck into the hub
study.py hub                                  # re-bundle after any deck regenerates
```

Two reasons the hub is the default rather than a nicety:

1. **One store.** Over `file://` the browser scopes localStorage per page path,
   so N scattered copies of the reviewer means N separate progress stores. One
   hub page = one path = one unified history across every subject.
2. **Auto-loading.** `fetch()` of a sibling `deck.json` is CORS-blocked on
   `file://`, but a `<script src>` tag is not — so the hub bundles decks into
   `decks.js` and the reviewer loads them with no file picker. Re-opening after
   a deck regenerates folds in the new cards automatically (the merge below is
   idempotent and keeps earned scheduling).

Decks may still live in their source repo for CI to regenerate; `hub --add`
copies them in. The two locations aren't in conflict — the repo is where a deck
is *produced*, the hub is where it's *studied*.

## The terminal reviewer (scripts/study.py)

The same store, headless — for scripting, automation, or when a browser isn't
handy. Stdlib-only Python, single file, no installs:

```
study.py sync study/deck.json    # upsert into ~/.study/state.json (or $STUDY_DIR)
study.py review                  # terminal loop over what's due
study.py stats                   # due / new / upcoming, per deck
study.py rebuild                 # replay review-log.jsonl into state.json
```

Note the terminal and browser reviewers keep **separate** stores (a filesystem
JSON file vs browser localStorage); both compute identical schedules, but they
don't sync. Pick one as your daily driver — the hub for studying, `study.py`
for automation.

It splits content from schedule the way this schema implies: `state.json` holds
scheduling keyed by card id (plus a content snapshot, so review works with the
source repo absent), and `review-log.jsonl` is an append-only event stream.
Scheduling is FSRS-6, ported from ts-fsrs 5.4.1 and held to it by a differential
test (`scripts/test_fsrs_parity.mjs` + `.py`, 634 cases, bit-exact). Fuzz is
disabled deliberately — determinism is what makes `rebuild` faithful and
parameter retraining possible later, the same reasoning as arboreus-api's
`src/lib/srs.ts`.

Sync semantics are exactly the id-stability contract above: unknown id → new card,
known id + changed content → content replaced, **schedule kept**, known id absent
from the deck → `status: orphaned` (history preserved, skipped in review).

## Downstream targets

- **Anki (today)**: `front`/`back` map directly to a Basic note; `tags` carry over;
  `concept` becomes a tag. Any genanki/anki-llm one-liner converts it.
- **Arboreus (later)**: `concept` → concept node (or match against an existing graph),
  `card` → problem of type retrieval, `files` → source refs, `source.repo` → domain.
  This mapping is why `concept` granularity matters — one concept per idea, not one
  per card.
- **CI accumulation (pipeline, later)**: merged-PR decks upsert into `study/deck.json`
  on the default branch keyed by `id`; a card regenerated with new content replaces its
  predecessor, cards whose `files` all vanish get flagged for review, everything else
  appends.
