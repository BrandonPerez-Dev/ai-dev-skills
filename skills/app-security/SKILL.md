
---
name: app-security
description: >-
  Application and agent security auditing — OWASP Top 10, SAST, dependency
  vulnerabilities, MCP/agent-specific attack surfaces, and API security.
  Use when auditing applications you're building locally, reviewing code for
  security issues, hardening an API, or assessing agent/MCP server security.
  Covers web apps, APIs, AI agents, and MCP servers. Not for network scanning
  or OS hardening — use infra-security for those.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebSearch
  - WebFetch
  - Agent
  - ToolSearch
---

# App Security

Find the vulnerabilities before someone else does. Audit systematically, not randomly.

<HARD-GATE>
Do NOT run a security audit without first understanding the application's attack surface — what it exposes, what it trusts, and where data crosses boundaries. A checklist without context misses the vulnerabilities that matter.
</HARD-GATE>

## Method Selection

| Situation | Approach | Start At |
|-----------|----------|----------|
| **New app audit** | Full process: attack surface → static analysis → dependency check → manual review | Phase 1 |
| **Pre-deploy review** | Focused: OWASP Top 10 check + dependency audit | Phase 2 |
| **Agent/MCP audit** | Agent-specific: tool poisoning, prompt injection, excessive permissions | Phase 3 |
| **After a vulnerability report** | Targeted: reproduce, assess blast radius, patch, verify | Phase 4 |
| **Code review with security lens** | Overlay: run alongside code-review skill, focus on trust boundaries | Phase 2 (scoped) |

## Process

### Phase 1: Attack Surface Mapping

Before scanning anything, understand what you're protecting and what's exposed.

**Identify boundaries:**
- External entry points: API routes, webhooks, WebSocket handlers, form inputs
- Authentication/authorization mechanisms and their enforcement points
- Data flows: where does user input go? What touches the database?
- Third-party integrations: APIs called, SDKs used, MCP servers connected
- Secrets and credentials: how stored, how accessed, how rotated

**For AI agents/MCP servers, also map:**
- Tool descriptions (can they be manipulated by untrusted content?)
- Model context window (what untrusted data enters the prompt?)
- Tool permissions (what can the agent do? File system access? Network? DB?)
- Human-in-the-loop gates (where does the agent act autonomously vs ask?)

**Checkpoint:** "Here's the attack surface I've identified. Anything I'm missing?"

### Phase 2: Automated Analysis

Run static analysis and dependency checks. These catch the low-hanging fruit.

**Static analysis (SAST):**

```bash
# Semgrep — language-aware SAST with OWASP rules
# Install: pip install semgrep (or brew install semgrep)
semgrep --config=auto .                          # Auto-detect language, run default rules
semgrep --config=p/owasp-top-ten .               # OWASP Top 10 specifically
semgrep --config=p/typescript .                   # Language-specific rules
semgrep --config=p/nodejs .                       # Node.js-specific rules
semgrep --config=p/security-audit .               # Broader security audit
```

**Dependency vulnerabilities:**

```bash
# npm audit — check known vulnerabilities in dependencies
npm audit                                         # Summary
npm audit --json                                  # Machine-readable for parsing

# Snyk (if available) — deeper analysis with fix suggestions
snyk test                                         # Test dependencies
snyk code test                                    # SAST via Snyk
```

**Secrets scanning:**

```bash
# Check for hardcoded secrets
# gitleaks (if available)
gitleaks detect --source=. --no-git

# Manual patterns to grep for
# Look for: API keys, tokens, passwords, connection strings
```

Use Grep to search for common secret patterns:
- `password\s*=\s*['"]` (hardcoded passwords)
- `(sk|pk)[-_](live|test)[-_]` (API keys)
- `BEGIN (RSA |DSA |EC )?PRIVATE KEY` (private keys)
- `mongodb(\+srv)?://[^/\s]+` (connection strings with credentials)

**Checkpoint:** "Here are the automated findings. [N critical, N high, N medium]. Let me walk through the critical ones."

### Phase 3: Manual Review — OWASP Top 10 + Agent Security

Automated tools miss logic flaws, business logic vulnerabilities, and agent-specific attacks. Manual review covers what scanners can't.

**OWASP Top 10 (2021) checklist:**

| # | Category | What to Check |
|---|----------|---------------|
| A01 | **Broken Access Control** | Can users access resources they shouldn't? Are API endpoints enforcing authorization, not just authentication? |
| A02 | **Cryptographic Failures** | Sensitive data encrypted at rest and in transit? Proper hashing for passwords (bcrypt/argon2, not MD5/SHA)? |
| A03 | **Injection** | SQL injection, NoSQL injection, command injection, XSS? Is input validated and parameterized? |
| A04 | **Insecure Design** | Are there missing rate limits, missing abuse controls, or unsafe default configurations? |
| A05 | **Security Misconfiguration** | Default credentials, unnecessary features enabled, overly permissive CORS, verbose error messages? |
| A06 | **Vulnerable Components** | Are dependencies up to date? Any known CVEs? (Covered in Phase 2) |
| A07 | **Auth Failures** | Weak passwords allowed? Missing MFA? Session management issues? Token expiration? |
| A08 | **Data Integrity Failures** | CI/CD pipeline security? Unsigned updates? Deserialization vulnerabilities? |
| A09 | **Logging Failures** | Are security events logged? Are logs tamper-proof? Is sensitive data excluded from logs? |
| A10 | **SSRF** | Can user input cause the server to make requests to internal services? URL validation? |

**Agent/MCP-specific attack surfaces:**

| Attack | Description | Mitigation |
|--------|-------------|------------|
| **Prompt injection** | Untrusted data in the model's context manipulates behavior | Separate trusted instructions from untrusted data; validate model outputs before executing |
| **Tool poisoning** | Malicious tool descriptions influence the agent's behavior | Review all tool descriptions; don't trust tools from untrusted sources |
| **Excessive permissions** | Agent has more access than needed (file system, network, DB) | Principle of least privilege; scope tool permissions tightly |
| **Rug pull** | MCP server changes behavior after initial trust establishment | Pin server versions; monitor for behavioral changes |
| **Data exfiltration** | Agent leaks sensitive context via tool calls to external services | Audit outbound tool calls; restrict network access |
| **Cascading trust** | Agent A trusts Agent B which trusts untrusted input | Map the full trust chain; validate at every boundary |

**For each finding, record:**
- Severity: Critical / High / Medium / Low
- Location: file:line or component
- Description: what's wrong and why it matters
- Exploit scenario: how could this be exploited? (1-2 sentences)
- Fix: recommended remediation

**Checkpoint:** Present findings grouped by severity. Critical first, one at a time.

### Phase 4: Remediation

Fix vulnerabilities in priority order. Verify each fix.

**Priority order:**
1. **Critical** — Remote code execution, authentication bypass, SQL injection with data access
2. **High** — Privilege escalation, stored XSS, sensitive data exposure
3. **Medium** — CSRF, open redirects, information disclosure
4. **Low** — Missing headers, verbose errors, minor misconfigurations

**For each fix:**
- Implement the smallest change that eliminates the vulnerability
- Write a test that verifies the vulnerability is fixed (regression test)
- Verify the fix doesn't introduce new issues

**Supabase/Postgres specific:**
- Row Level Security (RLS) policies: verify they exist and are correct for every table
- Service role key: never exposed to client; only used server-side
- Anon key: only grants access RLS allows
- Edge Functions: validate input, check auth, handle errors without leaking info

### Phase 5: Report

Compile findings into a structured report.

```markdown
## Security Audit Report

**Application:** [name]
**Date:** [date]
**Scope:** [what was audited]

### Summary
- Critical: [N] | High: [N] | Medium: [N] | Low: [N]
- [1-2 sentence overall assessment]

### Critical Findings
[One section per finding with description, location, exploit scenario, fix]

### High Findings
[...]

### Recommendations
[Prioritized list of next steps]

### Out of Scope
[What wasn't covered — network, infrastructure, etc. → route to infra-security]
```

## Bias Guards

| Trap | Reality | Do Instead |
|------|---------|------------|
| "We use a framework so we're safe" | Frameworks prevent some classes of bugs, not all. Business logic flaws, misconfigurations, and agent-specific attacks aren't covered | Audit the application logic, not just the framework |
| "No vulnerabilities found = secure" | Absence of evidence ≠ evidence of absence. Tools miss logic flaws | Combine automated + manual review; acknowledge coverage gaps |
| "It's internal so it doesn't matter" | Internal apps get compromised via lateral movement, insider threats, supply chain attacks | Apply defense in depth regardless of exposure |
| "We'll add security later" | Security debt compounds. Retrofitting auth and access control is 10x harder | Security is a design constraint, not a feature to add |
| "The agent only does what I tell it" | Prompt injection means the agent does what ANYONE tells it if untrusted data enters context | Treat all model outputs as untrusted; validate before executing |

## Anti-Patterns

| Anti-Pattern | What Goes Wrong | Prevention |
|--------------|----------------|------------|
| **Checklist without context** | Running OWASP checklist without understanding the app; misses the real risks | Phase 1 attack surface mapping is mandatory |
| **Tool-only audit** | Running Semgrep and calling it done; misses logic flaws and agent attacks | Automated + manual review always |
| **Fix without verify** | Patching a vulnerability without testing the fix works | Every fix gets a regression test |
| **Severity inflation** | Everything marked critical to get attention; creates alert fatigue | Use consistent severity criteria; critical = exploitable + high impact |
| **Security theater** | Adding headers and CSP but ignoring broken auth | Focus on impact, not compliance checkboxes |

## MCP Tools

Use `ToolSearch` to discover available security MCP tools at the start of any audit.

**pentestMCP** — If available, provides 20+ security testing tools including nmap, SQLMap, directory busting, subdomain enumeration, and vulnerability scanning. Valuable for active testing in Phases 2-3.

**Semgrep MCP** — If available, enables SAST analysis directly through MCP tools rather than CLI.

If neither is available, fall back to Bash with CLI tools (semgrep, npm audit, gitleaks) or manual Grep-based pattern matching.

## Guidelines

- **Attack surface first.** Understanding what's exposed is more valuable than running every scanner. A targeted review of 5 critical endpoints beats a surface-level scan of 100.
- **Automate the boring parts.** Dependency checks and pattern-based SAST are mechanical — automate them. Save human attention for logic flaws and design issues.
- **Agent security is application security.** MCP servers are APIs. Prompt injection is input validation. Tool permissions are access control. Apply the same principles with agent-specific awareness.
- **Fix the root cause, not the symptom.** If you find SQL injection, the fix isn't escaping that one query — it's ensuring all queries use parameterized statements.
