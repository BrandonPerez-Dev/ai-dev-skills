
---
name: boilerplate-cicd
description: Project scaffolding and CI/CD — golden path templates for TypeScript/Node.js projects. Covers directory structure, tooling (Biome, TypeScript, Vitest), GitHub Actions, security scanning, pre-commit hooks, and monorepo setup. Use when starting a new project or standardizing an existing one.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebSearch
  - WebFetch
  - Task
---

# Boilerplate & CI/CD

Golden path templates for TypeScript/Node.js projects. Scaffolding, tooling, CI/CD pipelines, security scanning, and developer experience.

## When to Use

- Starting a new TypeScript/Node.js project
- Adding CI/CD to an existing project
- Standardizing tooling (linter, formatter, testing)
- Setting up monorepo structure
- Adding security scanning to a pipeline
- Setting up pre-commit hooks

## Core Principle: Golden Paths

A golden path is an opinionated, pre-built template that makes the right thing the easy thing. It encodes team conventions into scaffolding so every new project starts with consistent structure, tooling, and pipelines.

**Not mandatory.** Teams can diverge — but the golden path should be good enough that they rarely need to.

## Project Structure

### Single Package

```
project/
├── src/
│   ├── index.ts              # Entry point
│   ├── routes/               # API routes (thin — validate and delegate)
│   ├── services/             # Business logic
│   ├── adapters/             # External integrations
│   └── types/                # Shared type definitions
├── tests/
│   ├── integration/          # Integration tests (real deps)
│   └── unit/                 # Unit tests (isolated)
├── .github/
│   └── workflows/
│       ├── ci.yml            # Lint, typecheck, test on PR
│       └── security.yml      # SAST, dependency scanning
├── biome.json                # Linter + formatter config
├── tsconfig.json             # TypeScript config
├── package.json
├── .gitignore
├── .nvmrc                    # Pin Node version
└── README.md
```

### Monorepo

```
monorepo/
├── packages/
│   ├── shared/               # Shared types, schemas, utilities
│   │   ├── src/
│   │   ├── package.json
│   │   └── tsconfig.json
│   ├── api/                  # Backend service
│   │   ├── src/
│   │   ├── tests/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── web/                  # Frontend app
│       ├── src/
│       ├── tests/
│       ├── package.json
│       └── tsconfig.json
├── .github/workflows/
├── biome.json                # Root-level — applies to all packages
├── tsconfig.base.json        # Shared TS config — packages extend this
├── pnpm-workspace.yaml       # Workspace definition
├── package.json              # Root scripts, dev deps
└── turbo.json                # Turborepo pipeline config
```

**Package manager:** pnpm. Content-addressable store, strict dependency trees, Corepack support for version pinning.

**Build orchestrator:** Turborepo. Remote caching, dependency-aware task execution, only rebuilds what changed.

## TypeScript Configuration

### tsconfig.json (single package)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noUncheckedIndexedAccess": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

### tsconfig.base.json (monorepo root)

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noUncheckedIndexedAccess": true,
    "composite": true,
    "incremental": true
  }
}
```

Each package extends the base:
```json
{
  "extends": "../../tsconfig.base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"],
  "references": [
    { "path": "../shared" }
  ]
}
```

### Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module system | `NodeNext` (ESM) | Modern standard, tree-shakeable, `"type": "module"` in package.json |
| Target | `ES2022` | Matches Node 18+ (top-level await, private fields) |
| `strict: true` | Always | Catches bugs. Non-negotiable |
| `noUncheckedIndexedAccess` | On | Forces null checks on array/object access |
| `exactOptionalPropertyTypes` | On | Distinguishes `undefined` from missing |
| `composite` + `incremental` | Monorepo only | Enables project references, faster rebuilds |

## Biome (Linter + Formatter)

Biome replaces ESLint + Prettier. Single binary, 10-25x faster, one config file.

### biome.json

```json
{
  "$schema": "https://biomejs.dev/schemas/2.0/schema.json",
  "vcs": {
    "clientKind": "git",
    "enabled": true,
    "useIgnoreFile": true
  },
  "organizeImports": {
    "enabled": true
  },
  "linter": {
    "enabled": true,
    "rules": {
      "recommended": true,
      "correctness": {
        "noUnusedImports": "error",
        "noUnusedVariables": "warn",
        "useExhaustiveDependencies": "warn"
      },
      "suspicious": {
        "noExplicitAny": "warn"
      },
      "style": {
        "noNonNullAssertion": "warn",
        "useConst": "error"
      }
    }
  },
  "formatter": {
    "enabled": true,
    "indentStyle": "space",
    "indentWidth": 2,
    "lineWidth": 100,
    "lineEnding": "lf"
  },
  "javascript": {
    "formatter": {
      "quoteStyle": "single",
      "semicolons": "always",
      "trailingCommas": "all"
    }
  },
  "json": {
    "formatter": {
      "indentStyle": "space",
      "indentWidth": 2
    }
  }
}
```

### VS Code Integration

`.vscode/settings.json`:
```json
{
  "editor.defaultFormatter": "biomejs.biome",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "quickfix.biome": "explicit",
    "source.organizeImports.biome": "explicit"
  }
}
```

### When to Use ESLint Instead

- Project already has extensive ESLint config and plugins
- Need rules Biome doesn't support yet (some framework-specific rules)
- Team prefers ESLint ecosystem

**For new projects, default to Biome.**

## Testing

### Vitest (recommended)

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:integration": "vitest run --config vitest.integration.config.ts",
    "test:coverage": "vitest run --coverage"
  }
}
```

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/unit/**/*.test.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      exclude: ['tests/', 'dist/', 'node_modules/'],
    },
  },
});
```

### vitest.integration.config.ts

```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    include: ['tests/integration/**/*.test.ts'],
    testTimeout: 30000,
    hookTimeout: 30000,
  },
});
```

## Pre-Commit Hooks

### Setup (Husky + lint-staged)

```bash
npm install -D husky lint-staged
npx husky init
```

`.husky/pre-commit`:
```bash
lint-staged
```

`package.json`:
```json
{
  "lint-staged": {
    "*": ["biome check --write --no-errors-on-unmatched --files-ignore-unknown=true"],
    "*.ts": ["vitest related --run"]
  }
}
```

This runs Biome on all staged files and related unit tests on changed TypeScript files.

## GitHub Actions CI

### ci.yml (Pull Request Checks)

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4

      - uses: actions/setup-node@v4
        with:
          node-version-file: '.nvmrc'
          cache: 'pnpm'

      - run: pnpm install --frozen-lockfile

      - name: Lint & Format
        run: pnpm biome ci .

      - name: Type Check
        run: pnpm tsc --noEmit

      - name: Unit Tests
        run: pnpm test

      - name: Integration Tests
        run: pnpm test:integration
```

### security.yml (Security Scanning)

```yaml
name: Security

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am

jobs:
  codeql:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - uses: github/codeql-action/init@v3
        with:
          languages: javascript-typescript

      - uses: github/codeql-action/analyze@v3

  dependency-review:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - uses: actions/dependency-review-action@v4

  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

### Security Tools

| Tool | What It Scans | When |
|------|--------------|------|
| **CodeQL** | Source code (SAST) — SQL injection, XSS, command injection | Every PR + weekly |
| **Dependency Review** | New dependencies for known vulnerabilities | PRs only |
| **TruffleHog** | Git history for leaked secrets, API keys, credentials | Every PR |
| **Dependabot** | Outdated dependencies with security patches | Automated PRs |

### dependabot.yml

```yaml
version: 2
updates:
  - package-ecosystem: npm
    directory: /
    schedule:
      interval: weekly
    open-pull-requests-limit: 10
    groups:
      dev-dependencies:
        dependency-type: development
      production-dependencies:
        dependency-type: production
```

## package.json Scripts

Standard scripts every project should have:

```json
{
  "scripts": {
    "build": "tsc",
    "dev": "tsx watch src/index.ts",
    "start": "node dist/index.js",
    "lint": "biome check .",
    "lint:fix": "biome check --write .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:integration": "vitest run --config vitest.integration.config.ts",
    "test:coverage": "vitest run --coverage",
    "check": "biome check . && tsc --noEmit && vitest run"
  }
}
```

The `check` script runs everything — use it before committing.

## .gitignore

```
node_modules/
dist/
*.tsbuildinfo
.env
.env.*
!.env.example
coverage/
.turbo/
.DS_Store
```

## .nvmrc

```
22
```

Pin the Node.js LTS version. Corepack handles the package manager version:
```bash
corepack enable
corepack use pnpm@latest
```

## Monorepo-Specific

### pnpm-workspace.yaml

```yaml
packages:
  - 'packages/*'
```

### turbo.json

```json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**"]
    },
    "test": {
      "dependsOn": ["build"]
    },
    "lint": {},
    "typecheck": {
      "dependsOn": ["^build"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    }
  }
}
```

### Monorepo CI Workflow

Add to the CI job:

```yaml
      - name: Build
        run: pnpm turbo build

      - name: Lint
        run: pnpm turbo lint

      - name: Type Check
        run: pnpm turbo typecheck

      - name: Test
        run: pnpm turbo test
```

Turborepo only runs tasks for packages that changed (plus their dependents).

## Scaffolding Process

When starting a new project:

1. **Choose template** — single package or monorepo
2. **Initialize** — `pnpm init`, install TypeScript, Biome, Vitest
3. **Configure** — tsconfig.json, biome.json, vitest.config.ts
4. **Set up CI** — copy workflow templates, configure secrets
5. **Set up hooks** — Husky + lint-staged for pre-commit
6. **Add security** — CodeQL, dependency review, TruffleHog, Dependabot
7. **Verify** — run `pnpm check` to confirm everything works
8. **Commit** — initial commit with all scaffolding

## Guidelines

- **Biome over ESLint+Prettier for new projects.** Faster, simpler, one config file. Migrate incrementally for existing projects.
- **Pin versions.** Node in `.nvmrc`, pnpm via Corepack, dependencies in lockfile. "Works on my machine" is not a feature.
- **`strict: true` always.** TypeScript without strict mode is TypeScript without a safety net.
- **Security scanning from day one.** Adding it later means vulnerabilities in the backlog. Start with CodeQL + Dependabot at minimum.
- **One `check` script.** A single command that runs lint, typecheck, and tests. Use it in CI and pre-commit.
- **Match existing conventions.** If the team uses ESLint, don't force Biome. Golden paths are recommendations, not mandates.
