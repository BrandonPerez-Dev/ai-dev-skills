# beacon ships as a single static binary

Date: 2026-08-05

beacon is distributed as one static binary — no sidecar services, no separate admin
server, no runtime dependencies. Operators install it with one copy and run it with one
command; that simplicity is the product's core promise.

Rejected alternatives:
- A separate admin/UI service (operational surface doubles; breaks the one-binary install).
- Plugin architecture with dynamic loading (deferred until a real second consumer exists).
