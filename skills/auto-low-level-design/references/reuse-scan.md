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
| 3 | Hybrid: add one embedding per symbol unit (cached by content hash; brute-force cosine or sqlite-vec), fuse with the BM25 list by reciprocal rank fusion, rerank the top 30–50 with a local cross-encoder | sqlite-vec, usearch; any local cross-encoder reranker |
| 4 | Graph expansion: from the top hits, walk AST-derived edges (calls, imports, inheritance) one or two hops to pull in the helpers a hit uses and the wrappers around it | tree-sitter edges in sqlite; the LocAgent pattern (BM25 plus multi-hop traversal, arXiv 2503.09089) |
| — | Adopt instead of build: cocoindex-code (local, AST-aware, incremental, MCP; Python/TS/Rust) | cocoindex |

**Change detection: a per-file manifest, not a Merkle tree.** Check mtime and size, hash content only when they
changed, key cached units by content hash (Continue's indexer does this, sqlite tag catalog). A branch switch or a
revert then re-embeds nothing. Cursor's Merkle tree earns its keep on client/server sync, sharing one index across
a team and proving which files a client holds (cursor.com/blog/secure-codebase-indexing); for one local repo of
~1,000 files a full stat pass takes milliseconds, and embedding — not change detection — is the cost.

BM25 and embeddings find different candidates: lexical wins where names repeat, dense where intent does (CoIR).
Fusing then reranking is why rung 3 is one rung, not two (Anthropic Contextual Retrieval, 2024: missed top-20
retrievals fell 49% against plain embeddings once contextual embeddings were fused with BM25, and 67% once a
reranker was added; measured on documents, not code).

**Retrieval is the agent's tool; the agent makes the call.** Scores rank candidates, they do not prove two
functions do the same thing: dense embedders ranked near-identical buggy variants above the correct function in
67–78% of queries (ExecRetrieval, arXiv 2609.01865, moderate), and a reranker judges text similarity too. So never
set a `reuse` or `new` row from a score threshold. The agent reads the top candidates and records its reason.

Avoid: github/stack-graphs (archived 2025-09); google/zoekt (archived; sourcegraph/zoekt is live but unneeded at
this size); content-defined chunking (FastCDC) — byte boundaries do not line up with functions.
