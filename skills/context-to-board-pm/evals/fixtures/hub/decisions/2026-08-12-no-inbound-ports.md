# No inbound ports

Date: 2026-08-12

beacon makes outbound connections only (long-poll / streaming to the relay hub). It never
opens an inbound listening port — that is the entire security story for machines behind
NAT, and several design partners adopted beacon specifically for it. Operator interaction
happens through the CLI against local state, not through a served endpoint.

Rejected alternatives:
- A local HTTP admin endpoint (an inbound port, however "local"; breaks the promise and
  the firewall posture audits rely on).
