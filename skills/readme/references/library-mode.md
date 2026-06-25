# Library / SDK README Patterns

Patterns derived from serde, tokio, axios, express, prisma, and other widely-used libraries across ecosystems.

## What Makes Library READMEs Different

Library READMEs serve developers who will import and call your code. The critical question isn't "should I use this?" — it's "what does the API look like and can I integrate it in 5 minutes?" Usage examples are the entire pitch.

## Key Patterns

### Usage Before Install (Art of README)

Show a working code example before installation. The reader needs to evaluate whether the API fits their mental model before committing to `npm install`:

```markdown
# my-library

A lightweight HTTP client with automatic retries and type safety.

\```typescript
import { client } from 'my-library';

const response = await client.get('/users/123');
// { id: 123, name: 'Alice', role: 'admin' }
\```

## Installation
\```bash
npm install my-library
\```
```

The code example IS the pitch. If the API is clean, the reader is sold. If it's ugly, no amount of feature bullets will save it.

### Minimal Viable Example

The first code example should be:
- **Complete** — copy-pasteable into a file and it runs
- **Minimal** — the fewest lines that show the core value
- **Realistic** — not `foo`/`bar` but a plausible use case
- **Annotated** — comments on non-obvious lines, expected output shown

### API Reference Strategy

Libraries face a unique tension: the README needs enough API documentation to be useful, but the full API reference should live in generated docs (rustdoc, JSDoc, typedoc, Sphinx).

**In the README:**
- The 3-5 most-used functions/methods with examples
- The primary types/interfaces the user will interact with
- Configuration options for initialization

**NOT in the README:**
- Every method signature (link to docs.rs, npmjs.com, readthedocs)
- Internal types or implementation details
- Deprecated API surface

```markdown
## API

### `client.get(url, options?)`

Fetch a resource with automatic retries.

\```typescript
const user = await client.get<User>('/users/123', {
  retries: 3,
  timeout: 5000,
});
\```

### `client.post(url, body, options?)`

Create a resource.

\```typescript
const created = await client.post<User>('/users', {
  name: 'Alice',
  role: 'admin',
});
\```

[Full API reference →](https://docs.example.com/api)
```

### Type Information

For typed languages, show the key types/interfaces:

```markdown
## Types

\```typescript
interface ClientOptions {
  baseUrl: string;
  retries?: number;     // Default: 3
  timeout?: number;     // Default: 10000 (ms)
  headers?: Record<string, string>;
}
\```
```

### Compatibility / Requirements

Libraries must document:
- Minimum language/runtime version (Node 18+, Rust 1.70+, Python 3.10+)
- Peer dependencies
- Platform support (browser, Node, Deno, Bun, etc.)
- Breaking change policy (semver adherence)

### Migration Guides

For libraries with major versions, link to migration guides:

```markdown
## Upgrading

- [v2 → v3 Migration Guide](docs/migration-v3.md)
- [v1 → v2 Migration Guide](docs/migration-v2.md)
```

## Section Order (Library-Specific)

```
1. Badges (CI, npm/crates.io version, downloads, types included)
2. Title + one-liner ("A [language] library for [capability]")
3. Usage example (the pitch — before installation)
4. Installation (package manager + version requirements)
5. Quick Start (slightly longer worked example)
6. API Reference (top 3-5 functions with examples, link to full docs)
7. Types / Interfaces (key types the user interacts with)
8. Configuration (initialization options)
9. Advanced Usage (patterns, recipes, edge cases)
10. Compatibility / Requirements
11. Migration Guides (if applicable)
12. Contributing
13. License
```

## Library-Specific Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Full API reference in README | Show top 3-5, link to generated docs for the rest |
| `foo`/`bar` examples | Use realistic variable names and plausible use cases |
| Installation before usage | Show the API first — let the reader evaluate before committing |
| Missing type information | Show key interfaces for typed languages |
| No minimum version documented | State runtime/language version requirements explicitly |
| README duplicated as rustdoc/JSDoc via include | Write each for its context — README for evaluation, docs for reference |
