---
name: rust-quality
description: Rust code quality rules for AI build context. Prevents the most common AI-generated Rust mistakes — ownership band-aids, unwrap abuse, async deadlocks, non-idiomatic APIs. Injected into build subagents when plan specifies Rust verticals.
type: reference
---

# Rust Quality

Code quality rules for AI-generated Rust. These are the mistakes AI makes most often, ranked by production impact.

## Edition & Toolchain

Target **Rust 2024 edition** (1.85+). Key 2024 changes to follow:
- Explicit `unsafe {}` blocks required inside `unsafe fn`
- `extern` blocks require `unsafe`
- Async closures stable: `async || { ... }` with `AsyncFn` traits
- `LazyLock`/`OnceLock` in stdlib — never use `lazy_static` or `once_cell`
- `Future`/`IntoFuture` in prelude

## Critical: Ownership & Borrowing

<HARD-GATE>
Never use `.clone()`, lifetime annotations, or `Arc<Mutex<T>>` as a first response to a borrow checker error. Restructure ownership first.
</HARD-GATE>

When the borrow checker complains:
1. **Ask:** Is the data borrowed, moved, or shared? What is the correct ownership model?
2. **Restructure** the code to match that model
3. **Only then** consider `.clone()` (with a comment justifying the cost) or `Arc` (for genuine shared ownership)

**Prefer in this order:**
1. Pass by reference (`&T`, `&mut T`)
2. Move ownership (pass by value when caller is done with it)
3. `Clone` with explicit acknowledgment of cost
4. `Rc`/`Arc` for genuine shared ownership

## Critical: Error Handling

| Context | Use | Never |
|---|---|---|
| Library crates | `thiserror 2` | `anyhow`, `Box<dyn Error>`, `String` errors |
| Application/binary | `anyhow 1` | `thiserror` for internal errors |
| All code | `?` propagation | `.unwrap()` in non-test code |

```rust
// Library: typed, matchable errors
#[derive(Debug, thiserror::Error)]
pub enum ParseError {
    #[error("invalid header: {0}")]
    InvalidHeader(String),
    #[error("io error")]
    Io(#[from] std::io::Error),
}

// Application: ergonomic with context
fn run() -> anyhow::Result<()> {
    let data = read_file("config.json")
        .context("failed to read config")?;
    Ok(())
}
```

**Rules:**
- `.unwrap()` only in tests or after a condition that guarantees `Some`/`Ok`
- `.expect("reason")` only for programmer invariants — the message explains WHY it can't fail
- Always use `.context()` / `.with_context()` in application code — bare `?` loses call-site info
- Implement `From` conversions via `#[from]` in thiserror — avoid manual `map_err`

## Critical: Async Correctness

<HARD-GATE>
Never hold a `std::sync::Mutex` guard across an `.await` point. Use `tokio::sync::Mutex` in async contexts, or scope the lock before the await.
</HARD-GATE>

```rust
// WRONG — deadlock risk
let guard = mutex.lock().unwrap();
do_something(&guard).await;  // guard held across await

// RIGHT — scope the lock
let value = {
    let guard = mutex.lock().unwrap();
    guard.clone()
};
do_something(&value).await;

// RIGHT — use tokio::sync::Mutex
let guard = mutex.lock().await;
do_something(&guard).await;
```

**Async rules:**
- `tokio::task::spawn_blocking` for CPU-bound or blocking I/O work — never block the async runtime
- `tokio::join!` / `try_join!` for independent concurrent operations — not sequential `.await` chains
- `tokio::select!` for racing — design for cancellation safety
- `#[tokio::test]` for async tests — `#[test]` won't drive the runtime
- Prefer single-threaded runtime (`flavor = "current_thread"`) unless parallelism is needed — avoids `Send + Sync` constraints
- Use channels (`mpsc`, `oneshot`, `broadcast`) before shared mutable state

## API Signatures

Accept the most general type that satisfies your needs:

| Instead of | Write | Why |
|---|---|---|
| `&String` | `&str` | Accepts both `String` and `&str` |
| `&Vec<T>` | `&[T]` | Accepts arrays, slices, vectors |
| `String` param | `impl Into<String>` | Caller decides allocation |
| `Box<dyn Trait>` (static dispatch) | `impl Trait` | Zero-cost monomorphization |

**Naming conventions:**
- No `get_` prefix on getters: `fn name(&self) -> &str`
- Conversions: `as_*` (free/borrowed), `to_*` (expensive/owned), `into_*` (consumes self)
- Builder pattern for structs with 3+ optional fields
- Newtype for type safety: `struct UserId(u64)`

**Visibility:** Default to `pub(crate)`. Only `pub` what's part of the public API. Use `pub use` re-exports in `lib.rs` to flatten the API surface.

## Project Structure

```
my-project/
├── Cargo.toml
├── src/
│   ├── main.rs       # thin — parse args, call lib, handle errors
│   ├── lib.rs        # all testable logic, pub use re-exports
│   ├── error.rs      # thiserror error types
│   └── modules/      # pub(crate) internals
└── tests/            # integration tests (pub API only)
```

- All logic in `lib.rs` (testable without binary)
- `main.rs` is a thin entry point
- Prefer `module_name.rs` over `module_name/mod.rs`
- For workspaces: use `[workspace.dependencies]` inheritance — never duplicate version pins

## Testing

```rust
// Unit tests — co-located with code
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parses_valid_input() { ... }

    #[tokio::test]
    async fn fetches_data() { ... }

    #[test]
    #[should_panic(expected = "invalid")]
    fn rejects_bad_input() { ... }
}
```

- Integration tests in `tests/` — can only access `pub` API
- `cargo-nextest` as test runner (faster, parallel, better output)
- `proptest` for property-based testing on invariant-heavy logic
- `insta` for snapshot testing (run `cargo insta review` after changes)
- `rstest` for parameterized/fixture tests

## Iterators Over Index Loops

```rust
// WRONG
for i in 0..vec.len() { process(vec[i]); }
// RIGHT
for item in &vec { process(item); }

// WRONG — intermediate collect
let filtered: Vec<_> = items.iter().filter(p).collect();
let mapped: Vec<_> = filtered.iter().map(t).collect();
// RIGHT — chain iterators
let result: Vec<_> = items.iter().filter(p).map(t).collect();

// WRONG — contains_key then insert
if !map.contains_key(&key) { map.insert(key, value); }
// RIGHT — entry API
map.entry(key).or_insert(value);
```

## Clippy

Enable in `lib.rs` / `main.rs`:
```rust
#![warn(clippy::all, clippy::pedantic)]
#![allow(clippy::module_name_repetitions)]
```

For library crates, also deny:
```rust
#![deny(clippy::unwrap_used, clippy::expect_used)]
```

CI command: `cargo clippy --all-targets --all-features -- -D warnings`

## Crate Choices (2026)

| Need | Use | Not |
|---|---|---|
| CLI | `clap v4+` (derive) | manual arg parsing |
| HTTP server | `axum 0.7+` | |
| HTTP client | `reqwest` (`rustls-tls`) | |
| Serialization | `serde` + `serde_json` | |
| Async | `tokio 1.x` | |
| Error (lib) | `thiserror 2` | `anyhow` |
| Error (app) | `anyhow 1` | `thiserror` |
| Logging | `tracing` + `tracing-subscriber` | `log` crate |
| Lazy init | `std::sync::LazyLock` | `lazy_static`, `once_cell` |
| Fast hash | `rustc-hash` (`FxHashMap`) | default `HashMap` on hot paths |

## Performance Defaults

- `&[u8]` and `&str` in function signatures — not `Vec<u8>` and `String`
- `Cow<'a, T>` for maybe-owned data (allocate only when needed)
- `FxHashMap` for internal hot-path maps
- Profile before optimizing: `cargo flamegraph`, `criterion`

## Unsafe

- Avoid unless genuinely needed (FFI, SIMD, specific memory patterns)
- Every `unsafe` block gets a `// SAFETY:` comment explaining the invariant
- Don't write convoluted safe workarounds when a small, well-documented `unsafe` is cleaner
- Use `#[repr(C)]` for FFI structs
