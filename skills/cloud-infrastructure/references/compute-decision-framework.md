# Compute Decision Framework

## The Decision: Lambda vs Fargate vs EC2

Don't present all three equally. Use the workload classification to narrow to 2 options, then discuss trade-offs.

## Quick Filter

| If the workload is... | Eliminate | Discuss |
|----------------------|-----------|---------|
| Long-running (>15 min) | Lambda | Fargate vs EC2 |
| Stateful with sidecars | Lambda | Fargate vs EC2 |
| Event-driven, short bursts | EC2 | Lambda vs Fargate |
| Needs GPU | Lambda, Fargate | EC2 (or SageMaker) |
| Team has no container experience | Fargate, EC2 | Lambda (or managed services) |

## Detailed Comparison

| Aspect | Lambda | Fargate | EC2 |
|--------|--------|---------|-----|
| **Max runtime** | 15 minutes | Unlimited | Unlimited |
| **Cold start** | 100ms-2s | 35s-2min | N/A (always on) |
| **Scaling speed** | Instant (1000 concurrent) | 30s-2min per task | Minutes (ASG) |
| **Min cost** | $0 (pay per invocation) | ~$15/mo (1 task always-on) | ~$8/mo (t4g.nano) |
| **Container support** | Yes (image-based) | Yes (native) | Yes (ECS agent) |
| **Sidecar support** | No | Yes (multi-container tasks) | Yes |
| **SSE/WebSocket** | No (29s API GW timeout) | Yes (via ALB) | Yes |
| **Sticky sessions** | No | Yes (via ALB) | Yes |
| **Operational overhead** | Lowest | Low | Medium-High |

## Downstream Implications (the part people miss)

Choosing compute cascades into 4-5 other decisions:

### If you choose Lambda:
- Networking: VPC-attached Lambda adds cold start (2-6s)
- State: Must be externalized (DynamoDB/Redis)
- API: Must use API Gateway or Function URLs (29s timeout limit)
- Secrets: Environment variables or Secrets Manager extension
- Logging: CloudWatch Logs (automatic)
- **Cannot do:** SSE streaming, long-running sessions, sidecar processes

### If you choose Fargate:
- Networking: Task in private subnet, ALB in public subnet
- State: In-memory (with sticky sessions) or externalized
- API: ALB with configurable timeouts (up to 4000s)
- Secrets: Injected from Secrets Manager into container env
- Logging: CloudWatch via awslogs driver, or FireLens for Datadog/Splunk
- Service discovery: ECS Service Connect or Cloud Map
- **Can do:** SSE, WebSocket, sidecars, long-running sessions

### If you choose EC2:
- Networking: Full VPC control, can run in any subnet
- State: Full disk, full memory, any storage pattern
- Patching: YOU own OS patching and security updates
- Scaling: ASG with launch templates, slower than Fargate
- **Only choose when:** GPU needed, specific OS requirements, or cost optimization at scale (Savings Plans)

## For AI Agent Workloads

**Recommendation: Fargate** for almost all AI agent use cases.

Why:
- Long-running SSE streams eliminate Lambda
- Sidecar containers (MCP servers, LiteLLM) need multi-container support
- Operational overhead of EC2 not justified unless GPU needed
- ALB with 300s+ timeout handles agent streaming

**Exception:** Use Lambda for:
- Webhook receivers (Twilio callbacks, OAuth redirects)
- Scheduled tasks (token rotation, cleanup jobs)
- Event processing (S3 triggers, SQS consumers)

These are complementary — Fargate for the agent runtime, Lambda for event-driven peripherals.

## Cost Examples (us-east-1, March 2026)

### Low traffic (MVP): 5 concurrent agent sessions
- **Fargate:** 1 task (2 vCPU, 4 GB), always-on = ~$60/month
- **Lambda:** N/A (can't do SSE)
- **EC2:** 1 t4g.medium = ~$30/month (but you own patching)

### Medium traffic: 50 concurrent agent sessions
- **Fargate:** 5 tasks auto-scaling = ~$300/month
- **EC2:** 3 t4g.large with ASG = ~$180/month (but operational overhead)

### Note: LLM token costs at 50 concurrent sessions likely = $2,000-5,000/month
Compute is 5-15% of total cost. Don't over-optimize it.
