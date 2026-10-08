# Reuse scan — find existing code before naming a new public symbol

Reference for auto-low-level-design. Load at step 2 of every full or lite run.
Source: design record §8, plus the index-structure research of 2026-10-06 (below).

## Procedure (default — no index)

1. Symbol inventory: `ctags -R --output-format=json` (universal-ctags), or the language server, filtered to
   public symbols.
2. For each planned public symbol, search by name, synonyms and signature shape (`rg` for parameter and return
   types).
3. Check dependency manifests for a library that already does it.
4. Read the duplication report for clone clusters near the change.
5. Record one row per planned symbol (`artifacts.md` § Reuse decisions). A `new` row must show what was searched.

This is a hypothesis to measure, not a proven benefit: agent PRs "frequently disregard code reuse
opportunities" (Huang et al., MSR 2026, moderate), but no study tests a retrieval step's effect on reuse.

## Upgrade path, only if measurement shows grep missing existing code

Step up one rung at a time; each rung keeps the ones below it.

| Rung | What | Open-source parts |
|---|---|---|
| 1 | Symbol units table: one row per function/class/method from a tree-sitter parse — path, content hash, signature, docstring | tree-sitter; sqlite |
| 2 | Lexical ranking (BM25) over names, signatures, docstrings | sqlite FTS5, or tantivy |
| 3 | Embeddings per symbol unit, cached by content hash; brute-force cosine or sqlite-vec | sqlite-vec, usearch |
| — | Adopt instead of build: cocoindex-code (local, AST-aware, incremental, MCP; Python/TS/Rust) | cocoindex |

**Change detection: a per-file manifest, not a Merkle tree.** Check mtime and size, hash content only when they
changed, key cached units by content hash (Continue's indexer does this, sqlite tag catalog). A branch switch or a
revert then re-embeds nothing. Cursor's Merkle tree earns its keep on client/server sync, sharing one index across
a team and proving which files a client holds (cursor.com/blog/secure-codebase-indexing); for one local repo of
~1,000 files a full stat pass takes milliseconds, and embedding — not change detection — is the cost.

**Embeddings find candidates, they do not prove equivalence.** Dense embedders ranked near-identical buggy
variants above the correct function in 67–78% of queries (ExecRetrieval, arXiv 2609.01865, moderate). The agent
reads each candidate before choosing `reuse`.

Avoid: github/stack-graphs (archived 2025-09); google/zoekt (archived; sourcegraph/zoekt is live but unneeded at
this size); content-defined chunking (FastCDC) — byte boundaries do not line up with functions.
