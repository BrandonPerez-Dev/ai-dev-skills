
---
name: data-modeling
description: >-
  Schema and data modeling decisions — choosing between relational, graph, document,
  and time-series paradigms based on workload analysis. Use when designing new schemas,
  evolving existing ones, choosing between modeling approaches, or optimizing schema
  for query performance. Covers graph modeling in relational databases (adjacency lists,
  CTEs, materialized paths, ltree). Not for ETL/pipeline design or ML data preparation.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
  - ToolSearch
---

# Data Modeling

Design for the query, not the entity. Schema decisions are workload decisions.

<HARD-GATE>
Do NOT design a schema without first understanding the workload — what queries will run, how often, read/write ratio, and expected data volume. A "clean" schema that can't serve the dominant queries is a failed schema.
</HARD-GATE>

## Method Selection

| Situation | Approach | Start At |
|-----------|----------|----------|
| **Greenfield schema** | Full process: workload → paradigm → design → validate | Phase 1 |
| **Schema evolution** | Understand existing workload + new requirements, then extend | Phase 1 (scoped) |
| **Performance problem** | Skip to validation — profile queries, identify bottlenecks, restructure | Phase 4 |
| **Paradigm question** | "Should this be a graph? Document store?" | Phase 2 |
| **Review existing schema** | Reverse-engineer the workload, check alignment | Phase 1 + 4 |

## Process

### Phase 1: Workload Analysis

Before touching schema design, answer these questions:

**Query patterns:**
- What are the 3-5 most frequent queries? (These drive everything.)
- What are the 1-2 most expensive/complex queries?
- Read/write ratio? (90/10 reads → denormalize aggressively. 50/50 → normalize.)

**Data characteristics:**
- Expected row counts per table (now and in 12 months)
- Relationship cardinality — 1:1, 1:N, M:N? How large is N typically?
- Does the data form hierarchies, graphs, or flat records?
- Time-series component? Event logs? Append-only patterns?

**Access patterns:**
- Point lookups vs range scans vs full-table aggregations?
- Do queries traverse relationships (joins, graph walks)?
- How deep do relationship traversals go? (1 hop vs unbounded)

**Checkpoint:** Present the workload summary. "Here's what I understand about your data and queries. Still accurate?"

### Phase 2: Paradigm Selection

Match the workload to the right modeling approach.

| Workload Signal | Paradigm | Why |
|----------------|----------|-----|
| Structured records, joins across entities, ACID required | **Relational (normalized)** | Postgres handles this natively; integrity guaranteed |
| Hierarchies, DAGs, prerequisite chains, network traversal | **Graph-in-relational** | Postgres recursive CTEs + adjacency lists; no separate DB needed |
| Read-heavy, few relationships, flexible schema per record | **Document / JSONB** | Postgres JSONB columns; avoid full document DB unless scale demands it |
| Append-only events, time-bucketed queries, retention policies | **Time-series** | TimescaleDB extension or partitioned tables |
| High-volume graph traversals (social networks, recommendations) | **Dedicated graph DB** | Only when Postgres CTEs hit performance limits at scale |

**Default to Postgres.** Most workloads don't need a separate database. Postgres with extensions (ltree, pgvector, TimescaleDB, JSONB) covers relational, graph, document, time-series, and vector search in one system.

**Checkpoint:** "Based on the workload, I recommend [paradigm]. Here's why."

### Phase 3: Schema Design

#### Normalization as a Spectrum

Normalization isn't a rule to follow — it's a tradeoff to manage.

| Normal Form | Use When | Skip When |
|-------------|----------|-----------|
| **3NF** (fully normalized) | Write-heavy, data integrity critical, moderate query complexity | Read-heavy dashboards, analytics, simple apps |
| **Partial denormalization** | Read-heavy with known query patterns, computed/cached fields | Schema still evolving, query patterns unknown |
| **Fully denormalized** | Read-only analytics, materialized views, reporting layers | Transactional systems with updates |

**Decision rule:** Fully normalize first. Denormalize only when you can name the specific query that benefits and accept the maintenance cost of keeping redundant data consistent.

#### Graph Modeling in Relational Databases

For hierarchies, DAGs, and network structures in Postgres:

| Pattern | Best For | Tradeoff |
|---------|----------|----------|
| **Adjacency list** (`parent_id` self-reference) | Simple trees, shallow hierarchies | Recursive queries for deep traversal; simple to maintain |
| **Recursive CTEs** | Arbitrary-depth traversal on adjacency lists | Postgres-native, no extensions; slower on very large graphs |
| **Materialized path** (`path TEXT = '/a/b/c'`) | Fast subtree queries, breadcrumb display | Path updates cascade on moves; works well for mostly-static hierarchies |
| **ltree extension** | Postgres-native hierarchical queries with operators | Powerful query syntax; requires extension; tree-only (not general graphs) |
| **Closure table** (ancestor_id, descendant_id, depth) | Fast ancestor/descendant lookups, DAGs | Storage grows O(n²) worst case; excellent read performance |
| **Edge table** (source_id, target_id + metadata) | General graphs, DAGs with weighted/typed edges | Most flexible; pair with recursive CTEs for traversal |

**For DAGs specifically** (like prerequisite graphs): Use an **edge table** with recursive CTEs. Store edge metadata (type, weight, threshold) on the edge. Compute derived properties (tier/depth) via Kahn's algorithm and cache on the node. Validate acyclicity on write, not read.

#### Schema Design Checklist

Before finalizing, verify:
- [ ] Every frequent query can be served with ≤ 2 joins (or has a denormalized path)
- [ ] Indexes exist for every WHERE clause and JOIN condition in frequent queries
- [ ] Composite indexes match query column order (leftmost prefix rule)
- [ ] Foreign keys enforce referential integrity at the DB level
- [ ] Timestamps use `TIMESTAMPTZ`, not `TIMESTAMP`
- [ ] UUIDs for primary keys if records may cross system boundaries
- [ ] Nullable columns are intentionally nullable, not by default

**Checkpoint:** Present the schema. "Here's the proposed schema with rationale for key decisions."

### Phase 4: Validation

Verify the schema serves the workload. This is where most schema designs fail — they look right but perform wrong.

**Query plan analysis:**
```sql
EXPLAIN ANALYZE <your frequent query>;
```

Check for:
- Sequential scans on large tables (missing index?)
- Nested loop joins on large result sets (wrong join strategy?)
- High row estimates vs actual rows (stale statistics?)

**Stress test with realistic data:**
- Generate data at expected 12-month volume
- Run the top 5 queries and measure latency
- Check that indexes are actually used (not just defined)

**Schema evolution safety:**
- Can the schema accommodate the next 2-3 known features without breaking changes?
- Are migrations additive (ADD COLUMN) or destructive (DROP/RENAME)?
- Is there a path to denormalize later if read performance demands it?

## Bias Guards

| Trap | Reality | Do Instead |
|------|---------|------------|
| "Normalize everything" | Over-normalization creates join-heavy queries that kill read performance | Normalize first, then selectively denormalize for proven bottlenecks |
| "Denormalize for speed" | Premature denormalization creates update anomalies and maintenance burden | Only denormalize when you can name the query and accept the consistency cost |
| "We need a graph database" | Postgres recursive CTEs handle most graph workloads under 1M edges | Benchmark with CTEs first; dedicated graph DB only when Postgres proves insufficient |
| "The schema looks clean" | Clean schema ≠ performant schema | Validate against actual queries with EXPLAIN ANALYZE |
| "JSONB for flexibility" | Schemaless is maintenance debt — you lose constraints, indexes are partial, migrations are invisible | Use JSONB for genuinely variable data; use columns for known fields |
| "Add an index for every query" | Too many indexes slow writes and consume storage | Index selectively for frequent queries; composite indexes cover multiple patterns |

## Anti-Patterns

| Anti-Pattern | What Goes Wrong | Prevention |
|--------------|----------------|------------|
| **Entity-first design** | Schema models the domain perfectly but can't serve the queries | Start with workload analysis, not an ER diagram |
| **Premature optimization** | Denormalized schema for queries that may never exist | Normalize first; denormalize with evidence |
| **Implicit graph in relational** | Category → subcategory → item chains via multiple tables instead of proper graph pattern | Recognize graph structures; use edge table + CTEs |
| **Stringly-typed enums** | `status TEXT` with no validation; typos create phantom states | Use CHECK constraints or Postgres ENUMs for small, stable sets; text + app validation for evolving sets |
| **Missing migration strategy** | Schema works today, no path to evolve | Design for additive changes; avoid painting yourself into corners |

## MCP Tools

Use `ToolSearch` to discover available database MCP tools at the start of any data modeling session.

**Supabase MCP** (`supabase` server) — If available, use it for schema introspection, migration generation, and querying existing tables. Especially valuable in Phase 1 (workload analysis) and Phase 4 (validation) where you can inspect live schema and run EXPLAIN ANALYZE directly.

**Postgres MCP** (`@modelcontextprotocol/server-postgres`) — Lighter alternative for read-only schema inspection and query testing against any Postgres database.

If neither is available, fall back to Bash with `psql` commands or reading Drizzle/migration files directly.

## Guidelines

- **Workload drives everything.** A schema is correct only relative to its queries. Different queries for the same data → different schemas.
- **Postgres first.** Extensions (ltree, pgvector, TimescaleDB, JSONB) cover most paradigms. Add a separate database only when Postgres demonstrably can't handle the workload.
- **Normalize, then denormalize.** Start with 3NF. Denormalize only with evidence (slow query, known read pattern). Document why each denormalization exists.
- **Graph patterns are common.** Hierarchies, DAGs, prerequisite chains, org charts — recognize these early. An edge table + recursive CTEs is the default pattern.
- **Validate with EXPLAIN ANALYZE.** Theory is not performance. Run your queries against realistic data before shipping the schema.
