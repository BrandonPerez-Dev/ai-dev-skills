# Platform Standards (Institutional Knowledge)

This file accumulates organizational constraints as they're discovered. Update it when you learn
new information from the user, platform team, Confluence, or AWS account inspection.

Last updated: 2026-03-06

## Status: Partially Known

Discovered through conversation with Brandon (2026-03-06). Platform team has a framework
called "Fabric" — need to find docs (Confluence or shared docs). Some gaps remain.

## Team
- **Size:** 2 people (Brandon + 1 semi-technical) — Tier 1 capacity
- **Intent:** Close-to-production dev environment, rigorous infrastructure proof-of-concept
- **Strategy:** Infrastructure designed to generalize as a shared AI platform — reusable AI gateway, MCP servers, and composable agent runtimes for use across products and teams
- **Note:** Small team but want production patterns, not throwaway infra

## Cloud Provider
- **Provider:** AWS
- **Region:** Unknown — ask user
- **Account structure:** Unknown — ask about Fabric, may define this

## Platform Framework: Fabric
- **What it is:** GitOps-based provisioning platform for infrastructure config (NOT a deployment/compute platform)
- **How it works:** Declarative config in `fabric-id-configuration` repo → custom Terraform provider → API → async provisioners → target systems
- **What it manages:** Vault namespaces/secrets, GitHub repos/runners, Artifactory repos/permissions, K8s namespaces (future)
- **What it does NOT manage:** Application deployment, compute orchestration, ALB/networking config
- **Implication:** Use Fabric to provision supporting infra (Vault, Artifactory, GitHub runners). Application deployment is our own Terraform + GitHub Actions.
- **Source:** Confluence WF space, confirmed by user 2026-03-06

## Compute
- **Preferred:** Unknown — need Fabric docs to confirm
- **Other AI teams:** Using "Agent Core" — but not relevant for Claude Agent SDK
- **Container registry:** Artifactory / JFrog (Fabric-managed, not ECR) — confirmed via Fabric docs
- **Known constraint:** Agent workloads need long-running SSE (rules out Lambda for streaming)

## Networking
- **VPC strategy:** Platform team providing a /22 VPC (1024 IPs) (user, 2026-03-06)
- **Transit gateway:** Unknown
- **VPN/DirectConnect:** Unknown
- **DNS:** Unknown — Route 53? External DNS?

## Auth & Identity
- **User auth:** Okta seen in org, unclear if mandated for apps (user, 2026-03-06)
- **Service-to-service auth:** Unknown — IAM roles? Mutual TLS?
- **OAuth for customer integrations:** Need to store customer OAuth tokens (Google, QuickBooks, Twilio)

## Secrets Management
- **Preferred store:** HashiCorp Vault (user, 2026-03-06)
- **Rotation policy:** Unknown
- **Note:** This means Vault agent sidecar or API calls, not AWS Secrets Manager

## Logging & Observability
- **Log aggregation:** CloudWatch + Splunk (user, 2026-03-06)
- **Metrics:** Unknown
- **Tracing:** Unknown
- **Alerting:** Unknown

## CI/CD
- **Pipeline tool:** GitHub Actions (user, 2026-03-06)
- **Deployment strategy:** Unknown — rolling? blue-green? canary?
- **IaC tool:** Terraform (user, 2026-03-06)

## Security & Compliance
- **Compliance requirements:** Unknown
- **Data residency:** Unknown
- **Encryption standards:** Unknown — KMS? Customer-managed keys?
- **Security scanning:** Unknown — what tools does the security team use?

## Data
- **Preferred database:** Unknown — RDS (Postgres/MySQL)? DynamoDB? Aurora?
- **Caching:** Unknown — ElastiCache? DAX?
- **Object storage:** S3 (assumed, nearly universal)

---

## How to Update This File

When the user provides platform team information:
1. Replace "Unknown" with the actual value
2. Add any constraints or reasoning
3. Update the "Last updated" date
4. Note the source (user said, Confluence doc, AWS CLI output)

Example:
```
## Compute
- **Preferred:** ECS Fargate (platform team standard, confirmed by user 2026-03-06)
- **Container registry:** ECR (standard, private repos only)
- **Known constraint:** Agent workloads need long-running SSE (rules out Lambda for streaming)
```
