# AWS Constraints for AI Agent Workloads

What's genuinely different about hosting AI agent systems vs standard web apps.

## 1. Long-Running SSE Connections

Agent sessions stream responses over SSE for minutes, not milliseconds.

**ALB idle timeout:** Defaults to 60 seconds. An agent thinking for >60s with no data sent = 504 Gateway Timeout mid-stream.

**Fix:**
- Set ALB idle timeout to **300-600 seconds** (5-10 min)
- Send SSE heartbeat (`:` comment line) every **15 seconds** to reset intermediate proxy timeouts
- Set target group deregistration delay > longest expected stream duration
- Do NOT use ALB health checks on streaming endpoints — use a separate `/health` path

**CloudFront + SSE:** CloudFront has a 60-second origin response timeout (configurable to 180s max). For SSE, either bypass CloudFront for the streaming endpoint or use heartbeats aggressively.

**API Gateway:** Has a **29-second hard timeout** that cannot be increased. API Gateway is NOT viable for SSE streaming. Use ALB directly.

## 2. Stateful Sessions

Agent conversations maintain context across turns. Three patterns:

### Option A: Sticky Sessions (simplest)
- ALB routes all requests from same session to same container
- **Config:** Target group with stickiness enabled (app cookie or duration-based)
- **Pros:** Zero code changes, works today
- **Cons:** If container dies, session is lost. Scaling is coarse (can't rebalance). Max ~1000 concurrent sessions per instance
- **Best for:** MVP, <100 concurrent users, when fast iteration matters more than reliability

### Option B: External State Store (most scalable)
- Session state serialized to DynamoDB or Redis after each turn
- Any container can resume any session
- **Pros:** Infinitely scalable, survives container restarts, enables multi-region
- **Cons:** 2-3 weeks implementation, serialization complexity, latency on resume
- **Best for:** Production with >100 concurrent users, multi-region requirements

### Option C: Hybrid Checkpointing (pragmatic middle)
- Keep state in memory during active streaming
- Checkpoint to DynamoDB between turns (not mid-stream)
- On container failure, resume from last checkpoint
- **Pros:** Simple implementation (~1 week), handles most failure cases, scales to ~5000 concurrent
- **Cons:** Loses in-progress stream on container death (user retries), not zero-downtime
- **Best for:** Most teams. Good enough for production, simple enough for small teams

## 3. LiteLLM as Unified AI Gateway

LiteLLM is not just an LLM proxy — it's a unified AI gateway that routes both LLM API calls
AND MCP tool calls. This is the central architectural insight for agent infrastructure.

### What LiteLLM Does
- **LLM routing:** Proxies requests to Anthropic/OpenAI/Bedrock/etc. (100+ providers)
- **MCP gateway:** Connects to MCP servers, discovers their tools, routes tool calls from
  any LLM provider to the correct MCP server
- **Tool bridging:** Makes MCP tools available to non-MCP-native providers (any LLM can use
  your MCP tools through LiteLLM, even if the provider doesn't support MCP natively)
- **Permission control:** Restrict which tools different API keys/teams can access
- **Tool namespacing:** Prefixes tool names with server name (`gdrive-search_files`) to
  disambiguate across multiple MCP servers

### Architecture
```
Agent Runtime → LiteLLM Gateway → LLM Providers (Anthropic, OpenAI, etc.)
                                → MCP Servers (your tools)
                                    ├── Google MCP (Drive, Gmail, Ads)
                                    ├── QuickBooks MCP
                                    ├── Document Parser MCP
                                    ├── Twilio MCP
                                    └── Recipe Executor MCP
```

The agent runtime only talks to LiteLLM. LiteLLM handles:
1. Sending the prompt + available tools to the LLM
2. When the LLM requests a tool call, routing it to the correct MCP server
3. Returning tool results to the LLM for next-step reasoning
4. Repeating until the LLM produces a final response

### MCP Server Configuration in LiteLLM
LiteLLM supports three MCP transport types:
- **Streamable HTTP / SSE** — MCP servers exposed as HTTP endpoints
- **stdio** — LiteLLM spawns MCP servers as child processes

```yaml
# litellm config.yaml
mcp_servers:
  gdrive:
    url: "http://mcp-google:8080/mcp"
    transport: "sse"
  document_parser:
    url: "http://mcp-docparser:8080/mcp"
    transport: "sse"
  quickbooks:
    url: "http://mcp-quickbooks:8080/mcp"
    transport: "sse"
    auth_type: "bearer_token"
    auth_value: os.environ/QB_MCP_TOKEN
```

### Deployment: Shared Service (recommended)
- Single LiteLLM deployment as its own ECS service
- All agent instances route through it
- Enables: shared API key management, request caching, rate limit pooling, usage tracking,
  centralized MCP server management, tool access control
- **Config:** Internal ALB or Service Connect, private subnet only
- **Sizing:** 1 vCPU, 2 GB RAM handles ~100 req/sec

### Why Shared Service over Sidecar
Since LiteLLM manages MCP server connections, running it as a shared service means:
- MCP servers are configured once, centrally — not per-agent-instance
- Tool permissions managed in one place
- Usage tracking across all agents
- MCP servers can be independently deployed and scaled
- Adding a new MCP server = config change in LiteLLM, no agent redeployment

## 4. MCP Server Deployment

With LiteLLM as the gateway, MCP servers are standalone services, not sidecars.

### Deployment Options

**A) Individual services** — Each MCP server is its own ECS service with an HTTP endpoint.
- Independent deployment, scaling, and health monitoring
- Best when servers have different resource profiles or update frequencies
- More operational overhead

**B) Bundled by external dependency** — Group related MCP servers into one container
  exposing multiple endpoints (e.g., all Google integrations together).
- Fewer services to manage
- Deploy and scale together
- Best for small teams

**C) Hybrid** — Bundle small/related servers, keep heavy ones standalone.
- Document Parser standalone (CPU-intensive)
- Google bundle (Drive + Gmail + Ads — all use same OAuth tokens)
- QuickBooks standalone (different auth, different scaling)
- Twilio standalone (webhook receiver needs different networking)

### Recommendation for 2-person team
Start with **bundled by dependency** (Option B). Split out individual services only if
one bundle needs different scaling or deployment cadence.

### HTTP Adapters for Stdio MCP Servers
Stdio MCP servers need an HTTP adapter for production deployment behind LiteLLM:
- Use `mcp-proxy` or similar tools to wrap stdio servers in HTTP
- Or rewrite servers to use HTTP/SSE transport natively
- The adapter adds minimal overhead but enables network-based routing

## 5. Cost Model

AI agent workloads have an unusual cost profile:

| Category | % of Total | Driven By |
|----------|-----------|-----------|
| LLM inference (tokens) | 60-75% | Prompt length, model choice, tool call volume |
| Compute (Fargate/EC2) | 10-20% | Task count, always-on vs auto-scaling |
| External APIs (Google, Twilio) | 5-15% | Tool invocation frequency |
| Data transfer + storage | 2-5% | Cross-AZ traffic, session persistence |
| Secrets Manager | <1% | Per-secret, per-API-call pricing |

**Implication:** Optimizing compute without optimizing prompts is optimizing the wrong thing. A 20% reduction in prompt tokens saves more than a 50% reduction in Fargate costs.

**Key levers:**
- Model selection (Haiku vs Sonnet vs Opus = 10x cost range)
- Prompt caching (Claude supports automatic caching for repeated context)
- Tool call efficiency (fewer round-trips = fewer tokens)
- Auto-scaling Fargate tasks to zero during off-hours (if workload allows)

## 6. OAuth Credential Management

Multi-tenant systems where each customer connects their own Google/QuickBooks/Twilio accounts.

### Secrets Manager (per-customer secrets)
- Store OAuth refresh tokens as individual secrets: `customer/{id}/google-oauth`
- Rotation: Lambda function that refreshes tokens before expiry
- **Pricing:** $0.40/secret/month + $0.05 per 10K API calls
- At 100 customers × 3 integrations = $120/month for secrets alone

### DynamoDB (if Secrets Manager cost is prohibitive)
- Store encrypted tokens in DynamoDB with KMS encryption
- Custom rotation logic in the credential vault service
- **Pricing:** Negligible at small scale (<$5/month)
- **Downside:** You own the encryption and rotation logic

### Recommendation
- Use Secrets Manager if platform team mandates it (most do for compliance)
- Use DynamoDB + KMS if cost-sensitive and team is comfortable owning rotation
- Either way, tokens should never be in environment variables in production
