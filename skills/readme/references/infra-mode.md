# Infrastructure / Extension README Patterns

Patterns for GitHub Actions, Terraform modules, Helm charts, plugins, VS Code extensions, and other infrastructure-as-code or extension artifacts.

## What Makes Infrastructure READMEs Different

Infrastructure artifacts are consumed declaratively — the user copies a YAML/HCL/JSON block into their config, not a function call into their code. The README is a configuration reference with enough context to make the right choices. Inputs, outputs, and defaults are the core content.

## Key Patterns

### Copy-Pasteable Usage Block First

The first thing the reader sees should be a complete, working configuration block they can paste:

**GitHub Action:**
```markdown
## Usage

\```yaml
- uses: org/my-action@v2
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    config-path: '.github/my-config.yml'
\```
```

**Terraform Module:**
```markdown
## Usage

\```hcl
module "vpc" {
  source  = "org/vpc/aws"
  version = "~> 3.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"
}
\```
```

**Helm Chart:**
```markdown
## Usage

\```bash
helm repo add myrepo https://charts.example.com
helm install my-release myrepo/my-chart
\```
```

### Inputs / Outputs Tables

The core documentation. Every input and output gets a table row:

```markdown
## Inputs

| Name | Description | Required | Default |
|------|-------------|----------|---------|
| `token` | GitHub token for API access | Yes | — |
| `config-path` | Path to config file | No | `.github/config.yml` |
| `dry-run` | Preview changes without applying | No | `false` |

## Outputs

| Name | Description |
|------|-------------|
| `result` | JSON object with operation results |
| `changed` | Whether any changes were made (`true`/`false`) |
```

For Terraform modules, use the standard `terraform-docs` format:
```markdown
## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.3 |
| aws | >= 5.0 |

## Providers

| Name | Version |
|------|---------|
| aws | >= 5.0 |
```

### Versioning and Pinning

Infrastructure users need to pin versions. Document the versioning strategy:

```markdown
## Versioning

This action uses [semantic versioning](https://semver.org/).

- Pin to a major version: `uses: org/action@v2`
- Pin to a specific version: `uses: org/action@v2.3.1`
- Pin to a commit SHA: `uses: org/action@abc123` (most secure)
```

### Examples Section

Infrastructure READMEs benefit from multiple configuration examples showing common scenarios:

```markdown
## Examples

### Basic Usage
\```yaml
[minimal config]
\```

### With Custom Configuration
\```yaml
[config with optional fields]
\```

### Advanced: Multi-Environment Setup
\```yaml
[production-grade config]
\```
```

Each example should be a complete, working configuration — not a fragment.

### Permissions / Security

Infrastructure artifacts often need specific permissions. Document them:

```markdown
## Permissions

This action requires the following GitHub token permissions:

\```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
\```
```

For Terraform: document the IAM permissions or roles required.
For Helm: document RBAC requirements, PodSecurityPolicy, or SecurityContext needs.

### Compatibility Matrix

Document what versions of the parent platform are supported:

```markdown
## Compatibility

| This Version | Terraform | AWS Provider | Kubernetes |
|-------------|-----------|-------------|------------|
| v3.x | >= 1.3 | >= 5.0 | — |
| v2.x | >= 1.0 | >= 4.0 | — |
| v1.x | >= 0.14 | >= 3.0 | — |
```

## Section Order (Infrastructure-Specific)

```
1. Badges (version, CI, Terraform Registry, Marketplace link)
2. Title + one-liner ("A [Terraform module / GitHub Action / Helm chart] that [capability]")
3. Usage (copy-pasteable config block)
4. Inputs table
5. Outputs table
6. Examples (basic → advanced, each complete and working)
7. Permissions / Security requirements
8. Compatibility matrix
9. Versioning strategy
10. Requirements / Dependencies
11. Contributing
12. License
```

## Infrastructure-Specific Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Incomplete usage example (fragment, not full config) | Every example should be paste-and-run |
| Missing defaults in inputs table | Always show the default value, even if it's `""` or `false` |
| No version pinning guidance | Document how to pin safely — major, exact, SHA |
| Permissions undocumented | List every permission/role required, with minimum scope |
| Single example only | Show basic, intermediate, and advanced configurations |
| terraform-docs not integrated | Use `terraform-docs` for auto-generated input/output tables |
