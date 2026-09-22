---
name: python-quality
description: Python style and quality guide — how clean, readable Python looks. Naming, functions, classes, structure, typing, errors, and tooling defaults. Injected into build context when writing or reviewing Python.
type: reference
---

# Python Quality

How pleasant-to-read Python looks. Optimize for the reader; the writer already understands the code.

## Philosophy

- **Readable beats clever.** If a construct needs a comment to explain *what* it does, rewrite it.
- **Style compliance is not quality** (Hettinger). PEP 8-clean code can still have a bad design. Spend attention on names and API shape, not formatting — the formatter owns formatting.
- **Duplication is cheaper than the wrong abstraction.** Abstract on the third use, not the second.
- **Small surface, real behavior.** A module or class should be usable without reading its source.

## Naming

Names carry the story.

- **Descriptiveness proportional to scope** (Google §3.16.1): `i` is fine in a 5-line loop; anything visible across a module or API needs a real name. Spend the most naming effort at signatures and public APIs — locals are recoverable from context, parameters aren't.
- **Never encode the type in the name** — `id_to_name_dict`, `user_list` → `names_by_id`, `users`.
- **When behavior changes, the name changes with it.** A `timeout` that became milliseconds or a `validate_user` that grew a mutation misleads every future reader — rename in the same change.
- Functions are verb phrases: `parse_invoice`, `retry_with_backoff`
- Booleans read as questions: `is_active`, `has_pending`, `should_retry`
- Values with units say the unit: `timeout_seconds`, `elapsed_ms`
- Collections are plural nouns: `users`, `failed_attempts`

Conventions: `snake_case` functions/variables/modules, `PascalCase` classes, `SCREAMING_SNAKE` constants, `_leading_underscore` for internal.

## Functions

- One job, named precisely. If the name needs "and", split it.
- **Prefer small, focused functions. Past ~50 lines, split it unless splitting harms the structure** (Google's guide says ~40; pylint/Ruff enforce 50 statements). This is a strong default, not a hard gate — a flat, linear 60-line function can be fine.
- **Nesting is the real limit, not length**: max ~4 levels deep, and keep guard clauses / early returns doing the flattening. A deeply nested 15-line function is worse than a flat 50-line one (this is the argument behind cognitive complexity — extraction that removes nesting always pays; extraction that just relocates lines doesn't).
- The extraction test is **entanglement**: after extracting a helper, can each piece be understood without reading the other? If not, inline it back.
- An extracted function must simplify its call site. Helpers that just relocate five lines are noise.
- Up to ~5 parameters is normal Python (the linter default); past that, reach for a dataclass or keyword-only args.
- **No boolean positional parameters** — make them keyword-only (`fetch(url, *, verify=True)`), split the function, or use an Enum. `fetch(url, 3, True)` tells the reader nothing.
- **Guard clauses over nesting; no `else` after `return`.** Handle the edge cases early and let the happy path read straight down.
- Walrus (`:=`) only when it removes genuine repetition; when a plain assignment works, prefer it (PEP 572's own guidance).
- Never use mutable default arguments. `def f(items=None): items = items or []`.

## Comments and docstrings

- **Docstring every public function, class, and module** — one summary line, then Args/Returns/Raises (Google style) when the signature isn't self-explanatory. The docstring is the interface contract.
- Inside function bodies, comments explain **why**, never what: business rules, workarounds with links, non-obvious performance choices.
- No commented-out code. No section-divider comments — if you need dividers, split the module.

## Classes and the data model

- **A class with `__init__` and one other method is probably a function.** Modules are already namespaces; don't build a class to hold two functions.
- When you do write a class, use the protocols instead of Java idioms:
  - `__repr__` on everything — it pays for itself in every debugging session
  - `__len__` / `__getitem__` / `__iter__` instead of `get_size()` / `get_by_index()`
  - properties instead of getters/setters — you can add them after the fact, so start with plain attributes
  - prefer public attributes over private; a single `_underscore` marks internal, and `__double_underscore` name-mangling hurts readability and testability
  - context managers (`__enter__`/`__exit__` or `@contextmanager`) for any recurring setup/teardown pair
- **Inheritance:** subclass for specialization (exceptions, genuinely "is-a with more") — never for code sharing. Sharing via subclassing leads to subclass explosion; use composition or plain functions.
- **Interfaces you consume:** define a `typing.Protocol` next to the consumer. Don't force providers to inherit your ABC. ABCs are for when you're also sharing implementation or need runtime `isinstance` enforcement.

## Data holders — the layering rule

| Need | Use |
|---|---|
| Internal/domain data | `@dataclass` (add `frozen=True`, `slots=True` when it fits) |
| Untrusted input at the boundary (API bodies, config, LLM output) | Pydantic |
| Bag of named values crossing a function boundary | `NamedTuple` or `TypedDict` |

Validate at the edge, then pass trusted plain objects inward. Don't make Pydantic models your domain layer — re-validating data you already trust, and letting your API schema shape your business objects, are both design pressure in the wrong direction.

## Errors

- **Raise exceptions rather than returning `None`** to signal failure — `None` returns silently become `TypeError`s three frames later.
- EAFP is the culture: try the operation and catch the failure, rather than pre-checking (`try: ... except KeyError` over `if key in d`). LBYL is fine when the check is clearer or the failure is expensive.
- Keep `try` blocks as short as possible — one risky statement, not a paragraph.
- Catch **narrowly** and close to where you can actually handle it. Bare `except:` never; `except Exception:` only at top-level boundaries that log and continue.
- One base exception per package (`class AppError(Exception)`), a handful of specific subclasses. Don't mint an exception type per failure; reuse `ValueError`/`TypeError`/`KeyError` when they say it.
- Error messages carry context: `f"failed to parse invoice {invoice_id}: {reason}"`, never `"parse error"`.

## Idioms

- f-strings for all formatting; `pathlib.Path` over `os.path`; `enumerate`/`zip` over index loops.
- Comprehensions: **at most two control subexpressions** (`for`/`if` combined — Google and Effective Python converge on this exact line). Beyond that, write a loop.
- **Long `if`/`elif` chains become dict lookups**, not class hierarchies — `handlers[kind](payload)`. This is modern Python's answer to branching.
- Generators when the consumer might not need everything or the data is large; lists when you'll iterate twice or need `len`.
- `match/case` only for real structural dispatch (tagged unions, AST-like data). It's not a switch replacement for two branches — `if/elif` reads better there.
- `__slots__`, descriptors, metaclasses: you almost never need them. Reach for them only with a measured reason, and expect to justify it in review.

## Typing

- **Annotate every public signature.** Internal helpers can rely on inference.
- Modern syntax: `list[str]`, `str | None`, `def f[T](x: T) -> T` (3.12+). Never `typing.List`/`Optional` in new code.
- `Any` is a design smell — use `object` or a `Protocol` and narrow.
- Type-check with `strict = true` **on new code**, per-module overrides exempting legacy (the Dropbox model: new files must be typed; don't chase a global percentage). `disallow_untyped_defs` is the floor.

## Structure

- **src layout**: `src/package/`, `tests/` as a sibling. Install editable (`uv pip install -e .`).
- `__init__.py` defines the public API: explicit re-exports (`from ._core import parse as parse` or an `__all__` list). Implementation lives in `_underscore` modules.
- One module per cohesive topic. Split when a file holds two unrelated topics, not at a line count. Don't nest packages until flat modules actually collide — premature package trees are noise.
- Break import cycles with `if TYPE_CHECKING:` for type-only imports; a runtime cycle means the dependency direction is wrong — fix the design, don't defer imports to hide it.
- Constants and exceptions live near their users; a dedicated `exceptions.py` only once several modules share them.

## Tooling (2026)

- **Ruff** for lint + format (replaces Black/isort/flake8). The 0.16+ default rule set is already broad (F, E-core, B, UP, SIM, RUF, import sorting); add `C4` and `PTH` on top. Leave `E501` off — the formatter owns line length.
- On greenfield code, enable `C90` with `max-complexity = 10` (relax per-file for legacy). Don't gate CI on function line count — no respected project does; keep the ~50-line rule a review conversation.
- Line length: 88–100. Pick one, stop discussing it.
- **uv** for packaging/venvs; everything configured in `pyproject.toml`.
- **pytest**: plain functions, fixtures over setup classes, `parametrize` for case tables. Shared fixtures in `conftest.py`. Mock at your system's boundary (HTTP, clock, filesystem), not your own internals.
- CI gates that pay: `ruff format --check`, `ruff check` at defaults with zero tolerance, the type checker, and **coverage on changed lines** (~90% via diff-cover or codecov patch) instead of a whole-repo percentage. Whole-repo coverage is a non-blocking ratchet: floor it at the current value, raise it only upward.
- Don't gate on maintainability index, docstring coverage, or duplication — measured against real codebases they're noise generators. Complexity warnings (cognitive ≤15) inform review; they never block.
- Every deviation from a lint default gets an inline comment saying why — that's the expert convention, not silent config.
