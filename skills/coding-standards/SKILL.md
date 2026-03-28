---
name: coding-standards
description: >-
  Universal coding rubric — the quality bar for all code written or reviewed.
  Referenced by build, code-review, simplify, tdd, and any skill that writes or
  evaluates code. Not invoked directly by users.
user-invocable: false
---

# Coding Standards

Code should be concise, elegant, and tell a story through its names. If you need a comment to explain what code does, rename things until you don't.

## The Bar

Four rules, in priority order (Kent Beck). When they conflict, earlier rules win:

1. **Passes the tests.** Working software beats beautiful software.
2. **Reveals intention.** A reader should understand what code does and why — from the names, types, and structure alone.
3. **No accidental duplication.** Eliminate redundancy only when the duplicated pieces genuinely represent the same concept. Three similar lines are fine if they do different things.
4. **Fewest elements.** Every function, type, and module must earn its existence. Delete anything that doesn't pull its weight.

## Philosophy

**Complexity is the enemy** (Ousterhout). Every design decision either adds or removes complexity. Prefer designs that hide complexity behind simple interfaces — deep modules with small surfaces, not shallow modules that scatter logic across many tiny pieces.

**Simple ≠ easy** (Hickey). Simple means "one thing, untangled." Easy means "familiar to me right now." Don't confuse them. A familiar pattern that entangles concerns is worse than an unfamiliar one that keeps them separate.

**Duplication is far cheaper than the wrong abstraction** (Metz/Abramov). When in doubt, leave code duplicated. Abstract only when you see the real pattern — after the third use, not the second. Premature abstraction creates coupling that's harder to undo than copy-paste.

**Strategic over tactical** (Ousterhout). Tactical programming solves today's task. Strategic programming invests in good structure. But "strategic" doesn't mean gold-plating — it means thinking one step ahead, not ten.

## Naming

Names tell the story. Spend time here — it pays off everywhere else.

- **Functions**: verb phrases describing what happens. `parseInvoice`, `retryWithBackoff`, `validateEmailAddress`
- **Booleans**: questions that read as English. `isActive`, `hasPermission`, `shouldRetry`
- **Variables with units**: `elapsedMs`, `maxRetries`, `timeoutSeconds` — never bare `elapsed`, `max`, `timeout`
- **Collections**: plural nouns. `users`, `pendingTasks`, `failedAttempts`
- **Transforms**: `toJson`, `fromRecord`, `asReadonly` — preposition reveals direction

| Context | Convention | Example |
|---------|-----------|---------|
| Components | PascalCase | `UserProfile.tsx` |
| Functions, hooks | camelCase | `useAuth`, `formatDate` |
| Types, interfaces | PascalCase | `interface InvoiceLineItem` |
| Constants | SCREAMING_SNAKE | `MAX_RETRIES`, `DEFAULT_TIMEOUT_MS` |
| Files (non-component) | kebab-case | `parse-invoice.ts` |

## Functions

- **Do one thing, name it precisely.** If you need "and" in the name, split it.
- **Earn your abstraction.** A function must simplify its call site. If the reader has to jump to the definition to understand what happens, the abstraction failed — the function is too shallow.
- **Parameters tell a story.** 0-2 parameters is ideal. 3+ means the function is doing too much, or the parameters should be an options object.
- **Depth over breadth.** A 30-line function that reads top-to-bottom is better than five 6-line functions that scatter the logic. Optimize for reading, not for line count.

## Modules and Files

- **Deep modules** (Ousterhout): simple interface, complex implementation hidden. The best module is one you can use without reading the source.
- **Co-locate related code.** Tests next to source. Types next to implementation. Don't scatter related things into `types/`, `utils/`, `helpers/` directories by category — group by feature.
- **One public interface.** Barrel exports from `index.ts` define the module boundary. Internal files are implementation details.

## Types (TypeScript)

- **Strict mode always.** `"strict": true` in every tsconfig.
- **`interface` for object shapes**, `type` for unions and intersections. Interfaces are extendable and give better error messages.
- **Never `any`.** Use `unknown` and narrow. If you reach for `any`, the types are telling you the design is wrong.
- **Explicit return types** on exported functions. Internal functions can rely on inference.
- **Zod at boundaries.** Validate external input (API responses, user input, env vars) at the system edge. Trust internal types after validation.

## Error Handling

- **`Result<T>` for expected failures.** API errors, validation failures, missing records — these are normal control flow, not exceptions. Return `{ success: true, data }` or `{ success: false, error }`.
- **Throw only for programmer errors.** Null pointer, assertion failure, impossible state — bugs that should crash loudly.
- **`fail()` and `succeed()` helpers.** Consistent construction. Never manually build result objects.
- **Errors carry context.** `Failed to parse invoice ${invoiceId}: ${reason}` — not `Parse error` or `Something went wrong`.

## Comments

- **Comments explain WHY, never WHAT.** If the comment restates the code, delete it and rename instead.
- **Acceptable comments**: business rule justifications, regulatory references, non-obvious performance decisions, links to external docs explaining a workaround.
- **No commented-out code.** That's what git is for.
- **No section dividers** (`// ---- Helpers ----`). If you need dividers, extract a module.

## Testing

- **Write tests. Not too many. Mostly integration.** (Dodds) Integration tests provide the highest confidence-to-cost ratio.
- **Test behavior, not implementation.** Tests that break when you refactor internals are worse than no tests.
- **Edge cases over happy paths.** The happy path usually works. Test the boundaries.
- **Eval-driven for AI.** When output is non-deterministic, define expected behavior as test cases with assertions + LLM-as-judge for subjective quality.

## Git

- **Conventional commits**: `type(scope): description` — `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- **Atomic commits.** One logical change per commit. If you need "and" in the message, split it.
- **Feature branches.** Never commit directly to main.

## AI Anti-Patterns

Guard against these — they're the failure modes of AI-generated code:

| Anti-Pattern | What It Looks Like | Instead |
|---|---|---|
| **Premature abstraction** | `createHandler(config)` wrapping a single handler | Write the handler directly. Abstract after the third use. |
| **Defensive generation** | Unused imports, empty catch blocks, dead parameters | Delete anything not needed. YAGNI. |
| **Over-configuration** | Config objects for values that never change | Hardcode it. Extract to config when it actually varies. |
| **Shallow modules** | 10 tiny functions that each do one trivial thing | Combine into fewer, deeper functions. Optimize for reading. |
| **Cargo cult** | Copying a pattern without understanding why it exists | Ask: does the context that motivated this pattern apply here? |
| **Sycophantic refactoring** | "Improving" code that works fine, adding docstrings everywhere | Only change what was asked for. Working code has value. |
| **Type theater** | Complex generics that add safety theater but no real safety | Simpler types that actually prevent bugs. |
