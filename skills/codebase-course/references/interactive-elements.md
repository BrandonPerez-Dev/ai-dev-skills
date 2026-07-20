# Interactive Elements — Markup Contract

The template's CSS/JS expects these exact structures. Deviating breaks the interaction silently
(quizzes won't score, nav won't build). Copy the snippet, replace content, keep the classes.

## Contents
1. [Module section](#1-module-section)
2. [Code ↔ English translation](#2-code--english-translation)
3. [Quiz block](#3-quiz-block)
4. [Spot-the-bug question](#4-spot-the-bug-question)
5. [Callouts](#5-callouts)
6. [File map](#6-file-map)
7. [Glossary term tooltip](#7-glossary-term-tooltip)
8. [Collapsible deep-dive](#8-collapsible-deep-dive)
9. [Template placeholders](#9-template-placeholders)

## 1. Module section

Direct child of `<main id="course">`. The nav builds itself from these — `id` must be
`module-N` (sequential) and the `<h2>` text becomes the nav label (keep it ≤4 words).

```html
<section class="module" id="module-2">
  <p class="module-kicker">Module 2</p>
  <h2>The Graph Engine</h2>
  <p class="objective">By the end you can <b>trace an edge insert through cycle
  detection and explain why tier computation reruns</b>.</p>
  <!-- prose, translations, callouts, quiz -->
</section>
```

The objective uses a doing verb the reader could be tested on — never "understand" or
"be familiar with".

## 2. Code ↔ English translation

Real code from the repo, verbatim, with the source path shown. Wrap the load-bearing
line(s) in `<mark>` and make the English column explain *why those lines*, not narrate
every line. Escape `<`, `>`, `&` in code.

```html
<div class="translate">
  <div class="code"><pre><code>export function insertEdge(from, to) {
  <mark>if (wouldCycle(from, to)) throw new CycleError();</mark>
  db.edges.insert({ from, to });
  <mark>recomputeTiers();</mark>
}</code></pre></div>
  <div class="english">
    <p>Before anything touches the database, the engine asks whether this edge would
    make the graph circular — a cycle would make "prerequisite" meaningless.</p>
    <p>Tiers are derived data, so every accepted edge invalidates them: that's why the
    recompute is unconditional, not an optimization.</p>
  </div>
  <span class="src">src/graph/engine.ts:118–124</span>
</div>
```

## 3. Quiz block

One `.quiz` per module (3–5 `.q` items — see quiz-design.md for question quality).
The JS scores on `data-correct` (present = right answer, attribute value irrelevant).
Exactly one option per question carries it. `.explain` is revealed after answering —
it must teach, not just say "correct".

```html
<div class="quiz">
  <p class="quiz-title">Check yourself</p>
  <div class="q">
    <p class="stem">A client inserts an edge that would create a cycle. What state is
    the database left in?</p>
    <div class="opts">
      <button>The edge row exists but tiers are stale</button>
      <button data-correct>Unchanged — the cycle check runs before any write</button>
      <button>The edge row exists with a <code>quarantined</code> flag</button>
    </div>
    <p class="explain">The guard-then-write ordering in <code>insertEdge</code> is the
    invariant: validation happens entirely in memory, so a rejected edge leaves no
    trace. The distractors describe repair strategies this codebase deliberately
    avoided.</p>
  </div>
  <p class="quiz-score"></p>
</div>
```

## 4. Spot-the-bug question

A `.q` whose stem includes a *modified* version of real code. The mutation must be
plausible (a mistake this codebase's history or structure invites), and the stem must
say the code was altered — never present invented bugs as the real source.

```html
<div class="q">
  <p class="stem">This version of <code>insertEdge</code> has been altered to introduce
  a bug. Which line breaks an invariant?</p>
  <pre><code>A  if (wouldCycle(from, to)) throw new CycleError();
B  db.edges.insert({ from, to });
C  if (from.tier > to.tier) recomputeTiers();</code></pre>
  <div class="opts">
    <button>Line A — the cycle check should follow the insert</button>
    <button>Line B — the insert needs a transaction</button>
    <button data-correct>Line C — tiers must recompute on every accepted edge</button>
  </div>
  <p class="explain">Making the recompute conditional reintroduces the stale-tier bug:
  tier values depend on the whole ancestry, not on the two endpoints' current tiers.
  Real code: src/graph/engine.ts:123.</p>
</div>
```

## 5. Callouts

Four types: `key-concept`, `aha`, `warning`, `common-mistake`. A callout surfaces what
the prose already developed — if the callout is doing the teaching, move it into prose.

```html
<div class="callout common-mistake">
  <span class="label">Common mistake</span>
  <p>Calling the REST layer from inside a graph-engine function. The engine is
  import-pure by convention — three past bug fixes (see git log on engine.ts) came
  from breaking this.</p>
</div>
```

## 6. File map

An annotated tree of the files the module (or PR) touches. `.hot` marks files the
reader will open most; `.why` carries the one-line reason each file matters.

```html
<div class="filemap"><pre>src/graph/
├── <span class="hot">engine.ts</span>      <span class="why">← every mutation funnels through here</span>
├── tiers.ts        <span class="why">← Kahn's algorithm, pure functions only</span>
└── export.ts       <span class="why">← read-only projections for the API layer</span></pre></div>
```

## 7. Glossary term tooltip

On the FIRST use of a repo-specific term in each module. The definition must stand
alone (≤160 chars). Add `tabindex="0"` so keyboard users can trigger it.

```html
<span class="term" tabindex="0" data-def="A concept's depth in the prerequisite DAG —
tier 0 has no prerequisites. Computed, never stored by hand.">tier</span>
```

## 8. Collapsible deep-dive

Native `<details>` for material that's real but optional at first pass (full function
bodies, edge-case tables, migration history).

```html
<details>
  <summary>Full cycle-detection walk (12 lines)</summary>
  <pre><code>…</code></pre>
</details>
```

## 9. Template placeholders

Replace every HTML comment token in `course-template.html`:

| Token | Fill with |
|---|---|
| `<!--COURSE_TITLE-->` (×2: `<title>` + `<h1>`) | Course name |
| `<!--COURSE_KICKER-->` | e.g. "Codebase course" / "PR walkthrough · #42" |
| `<!--COURSE_LEDE-->` | One sentence: what the reader can do after finishing |
| `<!--MODULE_COUNT-->` / `<!--EST_MINUTES-->` | Actual counts |
| `<!--REPO_REF-->` | `repo@shortsha` the content was read from |
| `<!--DATE-->` | Generation date |
| `<!--GENERATOR-->` | `codebase-course` or `pr-walkthrough` |
| `<!-- MODULES: … -->` | The module sections (delete the comment) |

Optionally override the accent: add `<style>:root { --accent: #0e7490; }</style>` after
the main style block. Pick one accent per course; the template's warm default is fine.
