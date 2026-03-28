# Team Capacity Right-Sizing

Infrastructure complexity must match team capacity. Overbuilding kills small teams.

## The Rule

Every infrastructure component has an operational cost beyond its setup cost. A 2-person team adding Kubernetes, Istio, and Terraform Cloud will spend 60% of their time on platform operations instead of product development.

## Capacity Tiers

### Tier 1: 1-3 Person Team (Startup / Innovation)

**Can manage:**
- Single AWS account, single region
- 1 VPC, 2-3 subnets (public + private)
- ECS Fargate (2-5 services)
- ALB (1-2 load balancers)
- RDS (1 instance, single-AZ for dev, multi-AZ for prod)
- Secrets Manager (standard usage)
- CloudWatch (logs + basic dashboards)
- GitHub Actions (CI/CD)
- Terraform or CDK (simple stacks)

**Should avoid:**
- Kubernetes (EKS) — operational overhead is enormous
- Service mesh (Istio, App Mesh) — not needed under 10 services
- Multi-region — doubles everything for marginal benefit at low scale
- Custom observability stack — CloudWatch is good enough
- GitOps with ArgoCD/Flux — GitHub Actions is sufficient

**Key principle:** Use managed services for everything. Pay AWS to operate, don't operate yourself.

### Tier 2: 4-8 Person Team (Growth)

**Can add:**
- Multiple environments (dev/staging/prod) with separate accounts
- ECS with auto-scaling policies
- ElastiCache (Redis) for shared state
- DynamoDB for high-throughput data
- More sophisticated CI/CD (environment promotion, canary deploys)
- Datadog or equivalent (if CloudWatch isn't sufficient)
- Infrastructure modules (reusable Terraform/CDK constructs)

**Still avoid:**
- Kubernetes (unless mandated by platform team)
- Multi-region active-active
- Custom service mesh
- Building your own deployment platform

### Tier 3: 9+ Person Team (Scale)

**Can consider:**
- EKS if container orchestration complexity justifies it
- Service-to-service auth (mutual TLS, service mesh)
- Multi-region for HA or data residency
- Dedicated SRE/platform function
- Custom internal developer platform
- Advanced observability (distributed tracing, custom metrics)

## How to Use This

When the user describes their team size:

1. Identify which tier they're in
2. Filter recommendations to that tier's "can manage" list
3. Explicitly flag anything in "should avoid" if it comes up
4. If the user pushes for a higher-tier pattern, ask: "Who will operate this at 2 AM when it breaks?"

## Common Mistakes by Tier

### Tier 1 teams that act like Tier 3
- **Symptom:** Kubernetes + Terraform Cloud + Datadog + multi-account setup
- **Result:** 2 engineers spend 70% of time on infrastructure, 30% on product
- **Fix:** ECS Fargate + CloudWatch + GitHub Actions. Ship product, not infrastructure.

### Tier 2 teams that skip automation
- **Symptom:** Manual deployments, no staging environment, production debugging
- **Result:** Slow releases, frequent outages, fear of deploying
- **Fix:** Invest in CI/CD pipeline and environment parity before adding features

### Any team that builds before buying
- **Symptom:** Custom auth system, custom log aggregation, custom secret rotation
- **Result:** Months of engineering on solved problems
- **Fix:** Cognito/Okta for auth, CloudWatch/Datadog for logs, Secrets Manager for secrets
