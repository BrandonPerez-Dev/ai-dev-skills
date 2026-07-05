# Web App / API README Patterns

Patterns for HTTP servers, REST/GraphQL APIs, frontend applications, SaaS projects, and full-stack applications.

## What Makes Web App READMEs Different

Web apps have two distinct audiences: **users** who want to deploy/use the app, and **developers** who want to contribute. The README must serve both without conflating them. Additionally, web apps are visual — screenshots are essential, not optional.

## Key Patterns

### Screenshot as the Hook

Web apps MUST have a screenshot in the first screenful. Unlike CLIs where the output is text, a web app's value is communicated visually:

```markdown
# My App

A self-hosted dashboard for monitoring your infrastructure.

![Dashboard showing server metrics and alerts](docs/images/screenshot.png)
```

- Show the primary view, not the login page
- Use realistic data, not empty states
- If dark/light themes exist, show both via `<picture>` tag
- Keep screenshots current — date them in the filename if needed (`screenshot-2024-03.png`)

### Live Demo Link

If a demo instance exists, link it prominently:

```markdown
## Try It

**[Live demo →](https://demo.example.com)** (credentials: demo/demo)
```

This is the fastest path to evaluation — faster than any install command.

### Deployment-First Quick Start

For self-hosted web apps, the Quick Start should get the app running, not set up a dev environment:

```markdown
## Quick Start

\```bash
docker compose up -d
\```

Open [http://localhost:3000](http://localhost:3000). Default login: `admin` / `changeme`.
```

Separate deployment from development:

```markdown
## Development

\```bash
git clone https://github.com/org/myapp
cd myapp
npm install
npm run dev
\```

Open [http://localhost:3000](http://localhost:3000) for the dev server with hot reload.
```

### API Documentation

For projects that expose an API:

```markdown
## API

Base URL: `http://localhost:3000/api/v1`

### Authentication

\```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:3000/api/v1/users
\```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users` | List all users |
| POST | `/api/v1/users` | Create a user |
| GET | `/api/v1/users/:id` | Get user by ID |

[Full API documentation →](https://docs.example.com/api) or see `/api/docs` (Swagger UI).
```

Show 3-5 key endpoints inline. Link to Swagger/OpenAPI for the full reference.

### Tech Stack

Web apps benefit from listing the tech stack — it helps contributors ramp up and helps users assess operational complexity:

```markdown
## Tech Stack

- **Frontend**: React, TypeScript, Tailwind CSS
- **Backend**: Node.js, Express, PostgreSQL
- **Infrastructure**: Docker, nginx, Redis (optional, for caching)
```

### Environment Variables

Web apps typically have many env vars. Show the essential ones in README, link to a `.env.example` for the full list:

```markdown
## Configuration

Copy the example environment file:
\```bash
cp .env.example .env
\```

Key variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `SECRET_KEY` | Yes | — | Session encryption key |
| `PORT` | No | `3000` | HTTP port |

See [`.env.example`](.env.example) for all configuration options.
```

### Database Setup

If the app needs a database, document the setup explicitly:

```markdown
## Database Setup

\```bash
# Create the database
createdb myapp

# Run migrations
npm run db:migrate

# Seed with sample data (optional)
npm run db:seed
\```
```

## Section Order (Web App-Specific)

```
1. Logo + Badges (CI, license, demo link badge)
2. Title + one-liner
3. Screenshot (primary view with realistic data)
4. Live Demo link (if available)
5. Quick Start (docker compose or equivalent — get it running)
6. Features (with screenshots for key features)
7. Tech Stack
8. Installation / Deployment
9. Configuration (key env vars, link to .env.example)
10. Database Setup (if applicable)
11. API Documentation (key endpoints, link to full docs)
12. Development Setup (separate from deployment)
13. Architecture (brief, for contributors)
14. Contributing
15. License
```

## Web App-Specific Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| No screenshot | The primary view screenshot is mandatory for web apps |
| Dev setup as the Quick Start | Quick Start = deployment. Dev setup is a separate section for contributors |
| Login page as the screenshot | Show the main functionality, not the auth gate |
| Full API docs in README | Top endpoints inline, full docs in Swagger/dedicated page |
| Missing `.env.example` | Create one and reference it — don't document 30 env vars in README |
| Empty state screenshot | Use realistic sample data that shows the app's value |
| Database setup undocumented | Explicit migration/seed commands — don't assume the reader knows your ORM |
