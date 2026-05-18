
---
name: infra-security
description: >-
  Network and system security — host hardening, network assessment, firewall
  auditing, CIS benchmarks, and service exposure analysis. Use when assessing
  your home/office network security, hardening a local system, checking for
  exposed services, or auditing system configurations against security baselines.
  Not for application code review or agent security — use app-security for those.
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

# Infra Security

Know what's running, what's exposed, and what's misconfigured. Your network is only as secure as its weakest host.

<HARD-GATE>
Do NOT run network scans or active probes without explicit authorization from the network owner. Scanning networks you don't own is illegal in most jurisdictions. For home/office networks — confirm with the user that they own or are authorized to test the target network before proceeding.
</HARD-GATE>

## Method Selection

| Situation | Approach | Start At |
|-----------|----------|----------|
| **Home/office network assessment** | Full process: discovery → service audit → host hardening | Phase 1 |
| **System hardening** | Host-focused: Lynis audit → CIS benchmark check → remediation | Phase 3 |
| **"What's exposed?"** | Quick scan: nmap the network, identify unexpected services | Phase 1 (scoped) |
| **After an incident** | Targeted: check for indicators of compromise, review logs, lock down | Phase 4 |
| **New machine setup** | Baseline: harden before connecting to production networks | Phase 3 |

## Process

### Phase 1: Network Discovery

Map what's on the network and what's exposed.

**Host discovery:**

```bash
# Find live hosts on the local network
# Requires: nmap (install: sudo dnf install nmap / brew install nmap)
nmap -sn 192.168.1.0/24                    # Ping sweep — find live hosts
nmap -sn -oG - 192.168.1.0/24 | grep Up    # Grep-friendly output
```

**Port scanning (authorized targets only):**

```bash
# Quick scan — top 1000 ports
nmap -sV 192.168.1.0/24                    # Service version detection

# Thorough scan — specific host
nmap -sV -sC -p- <target-ip>               # All ports + default scripts

# UDP scan (slower, often overlooked)
sudo nmap -sU --top-ports 100 <target-ip>  # Top 100 UDP ports
```

**For each discovered host, record:**
- IP address and hostname
- Open ports and services
- Service versions (outdated versions = vulnerabilities)
- Expected vs unexpected (is this service supposed to be running?)

**Checkpoint:** "Here's what I found on the network. [N] hosts, [N] open services. These [N] look unexpected — want to investigate?"

### Phase 2: Service Assessment

For each exposed service, assess the risk.

**Service risk evaluation:**

| Service Type | Key Questions | Common Issues |
|-------------|---------------|---------------|
| **SSH** | Key-only auth? Root login disabled? Non-standard port? | Password auth enabled, root login allowed |
| **HTTP/HTTPS** | What's serving? TLS version? Certificate valid? | Self-signed certs, outdated TLS, default pages exposed |
| **Database** | Bound to localhost only? Auth required? | Listening on 0.0.0.0, default credentials |
| **SMB/NFS** | Shares properly ACL'd? Guest access disabled? | Open shares, guest access enabled |
| **DNS** | Recursive queries restricted? Zone transfers disabled? | Open resolver, zone transfer to any |
| **Docker** | API bound to localhost? No --privileged containers? | Docker socket exposed, containers running as root |

**Check for default credentials** on any admin interfaces found. Common culprits: routers, NAS devices, IoT, printer admin panels.

**SSL/TLS assessment:**

```bash
# Check TLS configuration (if testssl.sh is available)
testssl.sh <target>:443

# Quick check with nmap
nmap --script ssl-enum-ciphers -p 443 <target>
```

**Checkpoint:** Present findings grouped by risk. "These [N] services need attention. Here's what's wrong with each."

### Phase 3: Host Hardening

Assess and harden individual systems against security baselines.

**Lynis — system audit:**

```bash
# Install: sudo dnf install lynis / brew install lynis
# Full system audit
sudo lynis audit system

# Review results
cat /var/log/lynis.log                     # Full log
cat /var/log/lynis-report.dat              # Machine-readable report
```

**Key Lynis sections to review:**
- Hardening index (overall score)
- Warnings (immediate action needed)
- Suggestions (improvements to consider)
- Vulnerable packages

**CIS Benchmark areas** (manual checks when Lynis doesn't cover):

| Area | What to Check |
|------|---------------|
| **Filesystem** | Separate partitions for /tmp, /var, /home? noexec/nosuid on /tmp? |
| **Boot** | Boot loader password set? Single-user mode requires auth? |
| **Services** | Unnecessary services disabled? (avahi, cups, bluetooth if not needed) |
| **Network** | IP forwarding disabled? ICMP redirects ignored? TCP SYN cookies enabled? |
| **Firewall** | Default deny policy? Only required ports open? Logging enabled? |
| **SSH** | Protocol 2 only? MaxAuthTries ≤ 4? PermitRootLogin no? Key auth only? |
| **Logging** | auditd running? rsyslog configured? Log rotation set up? |
| **Updates** | Auto-updates enabled? Unattended security patches? |
| **Users** | No accounts with empty passwords? Unused accounts locked? sudo limited? |

**Firewall audit:**

```bash
# Check firewall status and rules
# firewalld (Fedora/RHEL)
sudo firewall-cmd --list-all
sudo firewall-cmd --list-all-zones

# iptables/nftables
sudo iptables -L -n -v
sudo nft list ruleset

# ufw (Ubuntu)
sudo ufw status verbose
```

**SSH hardening check:**

```bash
# Review SSH config
cat /etc/ssh/sshd_config | grep -v '^#' | grep -v '^$'
```

Key settings to verify:
- `PermitRootLogin no`
- `PasswordAuthentication no` (key-only)
- `MaxAuthTries 3`
- `X11Forwarding no` (unless needed)
- `AllowUsers` or `AllowGroups` set

**Checkpoint:** "Lynis gave a hardening index of [N]/100. Here are the [N] warnings that need attention."

### Phase 4: Remediation

Fix issues in priority order with verification.

**Priority framework:**

| Priority | Criteria | Examples |
|----------|----------|---------|
| **P0 — Fix now** | Actively exploitable, exposed to network | Default credentials on exposed service, SSH with password auth from internet |
| **P1 — Fix today** | Vulnerable but requires additional conditions | Outdated service with known CVE, missing firewall rules |
| **P2 — Fix this week** | Hardening improvement, defense in depth | Missing audit logging, unnecessary services running |
| **P3 — Fix when convenient** | Best practice, low risk | Non-standard SSH port, banner removal |

**For each fix:**
- Document the current state (before)
- Apply the change
- Verify the fix works (test the service still functions)
- Verify the vulnerability is resolved (re-scan/re-check)
- Document the new state (after)

**Common remediations:**

```bash
# Disable unnecessary services
sudo systemctl disable --now avahi-daemon
sudo systemctl disable --now cups

# SSH hardening
sudo sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Firewall — default deny
sudo firewall-cmd --set-default-zone=drop
sudo firewall-cmd --zone=drop --add-service=ssh --permanent
sudo firewall-cmd --reload

# Auto-updates (Fedora)
sudo dnf install dnf-automatic
sudo systemctl enable --now dnf-automatic-install.timer
```

### Phase 5: Report

```markdown
## Infrastructure Security Report

**Scope:** [network range / host / system]
**Date:** [date]
**Authorization:** [confirmed by user]

### Network Summary
- Hosts discovered: [N]
- Open services: [N]
- Unexpected services: [N]

### Findings by Priority
#### P0 — Fix Now
[findings with remediation steps]

#### P1 — Fix Today
[...]

### Host Hardening
- Lynis score: [before] → [after remediation]
- CIS areas checked: [list]

### Remediation Applied
[what was fixed, with before/after]

### Remaining Recommendations
[what still needs attention]

### Out of Scope
[Application security → route to app-security]
```

## Bias Guards

| Trap | Reality | Do Instead |
|------|---------|------------|
| "My home network is safe" | Consumer routers have default credentials, UPnP enabled, outdated firmware. IoT devices are often unpatched | Scan it. You'll be surprised |
| "Firewall is on so I'm secure" | Firewalls don't help if services are intentionally exposed with weak configs | Check what's behind the firewall, not just that it exists |
| "It's just a dev machine" | Dev machines have SSH keys, cloud credentials, database access. They're high-value targets | Harden dev machines like production |
| "I'll update later" | Known CVEs with public exploits get automated scanning within days | Auto-updates for security patches, manual for major versions |
| "Nobody would target me" | Automated scanners don't care who you are. They scan everything | Security isn't about being a target, it's about being exposed |

## Anti-Patterns

| Anti-Pattern | What Goes Wrong | Prevention |
|--------------|----------------|------------|
| **Scan without authorization** | Legal liability, ethical violation | Hard gate: confirm authorization before any active scanning |
| **Scan and forget** | One-time audit, never repeated. Network changes, new devices added | Schedule periodic re-scans; at minimum after network changes |
| **Harden without testing** | Locked down SSH and locked yourself out | Always verify you can still access the system after changes |
| **All findings equal** | 50 findings with no priority; nothing gets fixed | Use priority framework; fix P0 before worrying about P3 |
| **Security through obscurity** | Non-standard ports, hidden services as sole defense | Obscurity is a layer, not a strategy. Fix the underlying issue |

## MCP Tools

Use `ToolSearch` to discover available security MCP tools at the start of any assessment.

**pentestMCP** (`smithery-ai/pentestmcp`) — If available, provides 20+ security testing tools including nmap scanning, subdomain enumeration, directory busting, SSL analysis, and vulnerability scanning. Especially valuable in Phases 1-2 for network discovery and service assessment.

If not available, fall back to Bash with CLI tools (nmap, lynis, testssl.sh, firewall-cmd).

## Guidelines

- **Authorization is non-negotiable.** Never scan a network you don't own or aren't explicitly authorized to test. This is a legal and ethical hard line.
- **Discovery before assessment.** You can't secure what you don't know exists. Map the network before diving into specific hosts.
- **Fix and verify.** Every remediation must be tested — both that the vulnerability is gone AND that the service still works. Locking yourself out of SSH is not a security improvement.
- **Automate recurring checks.** A one-time audit is better than nothing, but scheduled scans catch drift. New devices, new services, configuration changes — the network evolves.
- **Layer defenses.** No single control is sufficient. Firewall + service hardening + monitoring + updates. Each layer catches what the others miss.
