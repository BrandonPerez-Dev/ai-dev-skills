# beacon — product intent

beacon is a local daemon that relays webhooks from SaaS services to machines behind NAT,
with delivery guarantees. Single operator persona ("the driver").

## Intent (rough order of importance)

1. **Failed-delivery replay** — an operator can see failed webhook deliveries and replay
   them, so a consumer outage doesn't mean lost events. *(no implementation path yet)*
2. **Auth token rotation** — relay tokens rotate without downtime. *(in progress)*
3. **Multi-tenant routing** — one beacon instance serves several consumers with isolated
   delivery queues. *(later — direction only)*
