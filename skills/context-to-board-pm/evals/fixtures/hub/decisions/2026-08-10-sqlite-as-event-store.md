# SQLite is the event store

Date: 2026-08-10

All delivery state — pending, delivered, failed events and their payloads — lives in a
single SQLite database. It is the one durable store; any feature that needs event history
reads it rather than growing a parallel record.

Rejected alternatives:
- Flat JSONL append logs (no atomic queries across state transitions; compaction and
  partial-write corruption become our problem; two sources of truth the moment any other
  feature also needs state).
- An embedded KV store (weaker ad-hoc querying for operator tooling).
