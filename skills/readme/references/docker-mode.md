# Docker Image README Patterns

Patterns derived from linuxserver.io, Bitnami, and official Docker Hub image conventions.

## What Makes Docker READMEs Different

Docker images have a unique documentation surface: the reader needs to know what to mount, what to expose, and what to set — before running. The README is an operations manual, not a feature pitch.

## Key Patterns

### TL;DR First (Bitnami Pattern)

Open with the absolute minimum command before any explanation:

```markdown
## TL;DR

\```bash
docker run -d --name myapp -p 8080:8080 org/myapp:latest
\```
```

This works because Docker Hub users often already know the software — they just need the container command. Description and features come after.

### Always Pair `docker run` with `docker-compose`

Never show one without the other. Different users have different automation patterns.

**docker run:**
```bash
docker run -d \
  --name myapp \
  -e APP_PORT=8080 \                    # Port the app listens on
  -e APP_SECRET=changeme \              # Required: application secret
  -e LOG_LEVEL=info \                   #optional
  -p 8080:8080 \
  -v /path/to/data:/data \
  -v /path/to/config:/config \          #optional
  --restart unless-stopped \
  org/myapp:latest
```

**docker-compose:**
```yaml
services:
  myapp:
    image: org/myapp:latest
    container_name: myapp
    environment:
      - APP_PORT=8080
      - APP_SECRET=changeme             # Required: application secret
      - LOG_LEVEL=info                  #optional
    ports:
      - "8080:8080"
    volumes:
      - /path/to/data:/data
      - /path/to/config:/config         #optional
    restart: unless-stopped
```

Key conventions:
- Flags on **separate lines** with `\` continuation
- `#optional` inline comments on optional parameters
- Required parameters annotated with their purpose
- `--restart unless-stopped` as default restart policy

### Parameter Tables

Every port, env var, and volume gets a table entry:

```markdown
### Ports

| Port | Function |
|------|----------|
| `8080` | Application HTTP interface |
| `8443` | Application HTTPS interface (optional) |

### Environment Variables

| Variable | Required | Default | Function |
|----------|----------|---------|----------|
| `APP_SECRET` | Yes | — | Application secret key |
| `APP_PORT` | No | `8080` | Port the app listens on |
| `LOG_LEVEL` | No | `info` | Log verbosity: debug, info, warn, error |
| `TZ` | No | `UTC` | Timezone (e.g., `America/New_York`) |

### Volumes

| Path | Function |
|------|----------|
| `/data` | Persistent application data |
| `/config` | Configuration files (optional) |
```

### Supported Architectures

Docker images that support multiple architectures should list them:

```markdown
## Supported Architectures

| Architecture | Tag |
|-------------|-----|
| x86-64 | `amd64-latest` |
| arm64 | `arm64v8-latest` |
| Multi-arch | `latest` (auto-selects) |
```

### Application Setup

The section between "it's running" and "it's configured." What the user needs to do after `docker run`:

- Default credentials (if any)
- First-run wizard URL
- Where to find logs
- How to verify it's working (health check endpoint, expected log line)

### Permission Model

If the image runs as non-root or supports configurable UID/GID:

```markdown
## User / Group Identifiers

The image runs as a non-root user. Set PUID and PGID to match your host user:

| Env Var | Function |
|---------|----------|
| `PUID` | User ID (find with `id -u`) |
| `PGID` | Group ID (find with `id -g`) |

This ensures files created by the container are owned by your host user.
```

### Updating

Document how to update the image:

```markdown
## Updating

\```bash
docker pull org/myapp:latest
docker stop myapp
docker rm myapp
# Re-run the docker run command above
\```

Or with docker-compose:
\```bash
docker-compose pull
docker-compose up -d
\```
```

### Building Locally

For open-source images, include the build command:

```markdown
## Building Locally

\```bash
git clone https://github.com/org/myapp
cd myapp
docker build -t org/myapp:local .
\```
```

## Section Order (Docker-Specific)

```
1. Logo + Badges (Docker Hub pulls, image size, CI)
2. Title + one-liner
3. TL;DR (minimum viable docker run)
4. Supported Architectures
5. docker run + docker-compose (full examples with all params)
6. Parameter Tables (ports, env vars, volumes)
7. Application Setup (post-run configuration)
8. Permission Model (PUID/PGID if applicable)
9. Configuration (config file format, mounting, examples)
10. Updating
11. Building Locally
12. Contributing
13. License
```

## Docker-Specific Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Only `docker run`, no compose | Always pair them |
| All flags on one line | Separate lines with `\`, annotated |
| Undocumented env vars | Every env var in the parameter table, even optional ones |
| No default values listed | Always show defaults — the reader needs to know what changes |
| `-d` flag without explaining detached mode | Mention "runs in background" or link to Docker docs |
| Missing volume documentation | Every mount point documented with its purpose |
| No update instructions | Users will pull `:latest` and lose their config — document the safe path |
