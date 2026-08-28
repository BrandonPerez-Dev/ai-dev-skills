# Retry-storm findings

Date: 2026-08-20

Load testing showed naive fixed-interval retry causes synchronized retry storms: when a
consumer recovers, every failed delivery fires at once and knocks it back over. Two
design-partner incidents reproduced this exactly.

Conclusion: any retry or replay mechanism must use exponential backoff with jitter and a
per-consumer concurrency cap. Fixed-interval retry is ruled out by evidence.
