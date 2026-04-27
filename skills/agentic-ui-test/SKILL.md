---
name: agentic-ui-test
description: >-
  Drive a real browser via Playwright/Chrome DevTools MCP to test or debug a
  running UI app, capturing evidence at every layer — network, app state,
  framework callbacks, render output — not just the DOM. Use when verifying
  a feature in a stateful SPA that is hard to assert from DOM alone, when a
  user reports "the UI is broken but I can't see why" (blank screen, missing
  data, silent freeze), or when bisecting which layer of a frontend pipeline
  drops/mangles data. Produces a runtime evidence report and (when
  diagnosing) a single focused regression test, after stripping the
  bisection-only scaffolding.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - mcp__playwright__browser_navigate
  - mcp__playwright__browser_snapshot
  - mcp__playwright__browser_evaluate
  - mcp__playwright__browser_console_messages
  - mcp__playwright__browser_network_requests
  - mcp__playwright__browser_take_screenshot
  - mcp__playwright__browser_click
  - mcp__playwright__browser_type
  - mcp__playwright__browser_press_key
  - mcp__playwright__browser_wait_for
  - mcp__playwright__browser_close
  - mcp__chrome-devtools__navigate_page
  - mcp__chrome-devtools__take_snapshot
  - mcp__chrome-devtools__evaluate_script
  - mcp__chrome-devtools__list_console_messages
  - mcp__chrome-devtools__list_network_requests
---

# Agentic UI Test

Capture evidence at every layer; let bisection find the breaking point. Don't assume which layer is broken.

The DOM is the surface. A modern UI is a pipeline — network → decoder → state store → framework callback → renderer → DOM. Testing or debugging it from the DOM alone hides where the divergence actually happens. This skill drives a real browser, exposes the app's runtime internals, and captures bytes/state at each boundary so you can prove (not guess) what is actually going wrong or right.

<HARD-GATE>
Do NOT propose a fix or pass/fail verdict based on "this looks plausible." Capture evidence at the layer in question first. "The DA1 reply isn't being processed" is a hypothesis; the captured byte stream proving the daemon never sent the reply is evidence. The user has been burned before by patches built on plausible-but-wrong hypotheses — don't repeat it.
</HARD-GATE>

## When to Use

| Situation | Use this skill? | Why |
|-----------|-----------------|-----|
| Verify a new feature works in the running app | Yes | DOM assertions miss state-layer regressions; runtime hooks let you assert state too |
| User says "the UI shows nothing / wrong data, I don't know why" | Yes — this is the highest-value case | Blank/silent failures are exactly what bisection diagnoses |
| Pure unit test of a pure function | No | Use a normal test runner, not a browser |
| Verify a backend API contract | No | Use an integration test against the API directly |
| Visual regression / pixel diff | Adjacent — pair with a screenshot tool | This skill captures runtime data, not screenshots-as-truth |
| Performance investigation | Adjacent — use Chrome DevTools `performance_*` tools instead | Different methodology |

## The Method

### Phase 1: Define the Pipeline and the Question

Write down (mentally or in a scratch comment) the data flow from input to render. Examples:

- *Daemon WS → protobuf decode → transport callback → Zustand store → React render → xterm.write → DOM canvas*
- *REST fetch → JSON parse → React Query cache → component render → DOM*
- *User input → form state → debounced API call → response → cache invalidate → re-render*

Then state precisely what you are testing or what is broken. Vague: "claude doesn't render." Precise: "I type `claude<enter>` and the terminal shows the prompt + my input, but no further bytes appear in the buffer." The precision comes from **which layer the symptom is observed at** (DOM, store, network, etc.).

### Phase 2: Add Dev-Only Runtime Hooks (if not already present)

A skill-driven test needs introspection points the production app doesn't ship. The pattern:

```ts
// e.g. in the WebSocket transport bootstrap
if (import.meta.env.DEV) {
  ;(globalThis as any).__appTransport = transport
  ;(globalThis as any).__appDebug = { rxBytes: 0, rxFrames: 0 }
}
```

```ts
// e.g. in the React component that owns a domain instance
if (import.meta.env.DEV) {
  ;(globalThis as any).__appTerm = term  // or store, or query client, etc.
}
```

Rules:
- Always gate on the dev-mode flag (`import.meta.env.DEV` for Vite, `process.env.NODE_ENV !== 'production'` for Next, etc.). The exposure must NOT ship to production.
- Expose objects, not snapshots — the harness should be able to call methods, monkey-patch them, read fresh state.
- Name with a project-specific prefix (`__rct*`, `__appName*`) so they never collide with other apps the user might also be running.
- One commit per "expose this" — small, reviewable. Do not bundle with other changes.

If hooks are already present, skip this phase.

### Phase 3: Drive the Scenario in the Browser

Use the Playwright MCP tools (preferred) or Chrome DevTools MCP. Typical bootstrap:

1. `mcp__playwright__browser_navigate` to the dev URL.
2. `mcp__playwright__browser_evaluate` to install instrumentation patches *before* clicking anything that triggers the broken behavior (monkey-patch handlers, set up byte captures, etc.).
3. `mcp__playwright__browser_click` / `_type` / `_press_key` to drive the user flow.
4. `mcp__playwright__browser_wait_for` (or a `setTimeout` inside `_evaluate`) to give async work time to complete.
5. `mcp__playwright__browser_evaluate` to read captured data.

Patterns for capture:

```js
// Wrap a function on a runtime object to log every call
const orig = window.__appTerm.write.bind(window.__appTerm)
window.__appTerm.write = (data, cb) => {
  ;(window.__captures ??= []).push({ ts: performance.now(), len: data.byteLength })
  return orig(data, cb)
}
```

```js
// Capture event-emitter callbacks that fire later
window.__appTerm.onData((data) => {
  ;(window.__replies ??= []).push({ ts: performance.now(), str: data })
})
```

```js
// Walk React fiber to extract the sessionId / queryKey / etc. that components were given as props
function findProp(node, key) {
  const fk = Object.keys(node).find(k => k.startsWith('__reactFiber'))
  let f = fk && node[fk]
  while (f) { if (f.memoizedProps && key in f.memoizedProps) return f.memoizedProps[key]; f = f.return }
  return null
}
```

Capture **enough** — first chunks, last chunks, total bytes, timing, cursor position, visible text, DOM accessibility tree. You will not get to repeat the run cheaply; record more than you think you need.

### Phase 4: Bisect Until the Layer Is Found

If the test is verifying a feature and it passes — done, write the regression test (Phase 6).

If the test fails or you cannot explain the captured data, **bisect**. Compare each layer's evidence against the layer just upstream. The bisection ladder for the example pipeline above:

| Compare | Tells you |
|---------|-----------|
| Bytes captured at WS frame vs bytes the protobuf decoder emitted | Decoder dropped/mangled? |
| Decoder output vs what the transport callback received | Routing/dispatch bug? |
| Callback invocations vs store mutations | State update bug? |
| Store state vs what the renderer was called with | Selector/memoization bug? |
| Render output vs DOM | Rendering bug? |

When the comparison shows a divergence, you have found the layer. If the bug is reachable in a unit/integration test, **write a failing test at that layer** (much faster feedback than the browser). If not, keep the browser harness for the regression test.

If browser-only bisection is not converging, **build a ground-truth standalone reproduction** that bypasses the suspect layer entirely. Example: if the daemon-via-WS path is broken, run the same daemon code in a Go test directly. If the standalone passes and the integrated fails, the integration path is the bug — keep bisecting there.

### Phase 5: Diagnose, Then Fix

Only now propose a fix. Tie it to the captured evidence:

> The vt emulator's auto-reply to DA1 writes to a synchronous io.Pipe (handlers.go:695). Nothing reads that pipe in our session manager, so the next Write blocks forever. Evidence: pty.Manager test passes; pty + emulator.Write test hangs after exactly the byte count where the DA1 query first appears. Fix: drain the pipe in a goroutine and write back to the PTY.

Implement the fix. Re-run the same browser scenario to confirm.

### Phase 6: Lock the Regression and Strip the Scaffolding

- Keep ONE focused regression test that fails without the fix and passes with it. Where possible, push it down the test pyramid (a Go/integration test is better than a browser test for CI cost).
- Delete the bisection-only tests and probes. Their job was to find the layer; they are not load-bearing for the fix.
- Keep the dev-only runtime hooks — they are useful for the next investigation. Do not commit any production-mode exposure.
- Update memory or project notes if the bug surfaces a class of issue future sessions should be aware of.

## Tooling Cheatsheet

### Playwright MCP — primary

| Tool | Use for |
|------|---------|
| `browser_navigate` | First step every session |
| `browser_snapshot` | Accessibility tree — better than DOM for finding refs |
| `browser_evaluate` | Run JS in the page; the workhorse for instrumentation + capture |
| `browser_click`, `_type`, `_press_key` | Drive the user flow |
| `browser_wait_for` | Wait for text or a fixed time; never poll in a tight loop |
| `browser_console_messages` | Pull console errors/warnings the page emits |
| `browser_network_requests` | Inspect XHR/fetch/WS upgrade traffic |
| `browser_take_screenshot` | Last resort — the user often cannot view inline images. Save to disk and describe. |
| `browser_close` | End of session |

### Chrome DevTools MCP — when you need raw DevTools

Use when you need: real-time WebSocket frames (CDP `Network.webSocketFrameReceived`), CPU/memory profiling, DOM mutation traces, lighthouse audits. Otherwise prefer Playwright — its API is tighter and the snapshot is more useful than full DOM dumps.

### Avoid

- Pure puppeteer/raw CDP unless an MCP wrapper is missing what you need.
- Headed browser windows when an agent is driving — slower, no visibility benefit since the model can't see the screen.

## Output Format

### When verifying a feature

```
## Verdict
[PASS / FAIL — one sentence]

## Scenario
[What was clicked/typed in plain English]

## Evidence
- Network: [N requests, status codes, key bodies]
- Store: [relevant state values after the action]
- Render: [N elements matched, key text content]
- Console: [errors/warnings or "clean"]

## Regression test
[Path to test file added/updated]
```

### When diagnosing a bug

```
## Symptom
[What the user sees]

## Root cause
[Specific layer + specific call/line, tied to evidence]

## Evidence ladder
| Layer | Expected | Observed | Status |
|-------|----------|----------|--------|
| Network | ... | ... | OK / DIFF |
| Decoder | ... | ... | OK / DIFF |
| Store | ... | ... | OK / DIFF |
| Render | ... | ... | OK / DIFF |

## Fix
[File:line, one sentence on what changes]

## Regression test
[Path; level (unit/integration/browser) and why that level]

## Cleanup
[Bisection-only files/tests deleted]
```

## Anti-Patterns

| Anti-Pattern | What it looks like | Do instead |
|--------------|--------------------|-----------|
| **DOM-only assertion** | `expect(page.getByText('foo')).toBeVisible()` for a stateful app | Capture state too — `expect(window.__store.getState().items).toHaveLength(3)` |
| **Plausible-cause patching** | "It looks like xterm.js doesn't reply to DA1, let me write a fix" | Capture the byte stream and prove which side dropped it before fixing |
| **Snapshot-as-truth** | Comparing screenshots / accessibility trees and calling "looks right" a pass | Snapshots are coarse; assert specific runtime values too |
| **Polling in a tight loop** | `while (!found) { eval(...) }` with no delay | Use `browser_wait_for` or a `setTimeout` inside one `evaluate` call |
| **Production-flag exposure** | `window.__appTerm = term` with no env gate | `if (import.meta.env.DEV)` — the exposure must not ship |
| **Bisection cruft in main** | Committing 8 diagnostic tests after finding the bug | Strip them — keep one focused regression test |
| **Pasting screenshots to the user** | Tool returns a PNG, you describe it as "see attached" | Many environments cannot render inline images. Describe in text or save to a path. |
| **Trusting your instrumentation order** | Hooking `onData` AFTER the event you wanted to capture has fired | Install hooks BEFORE the trigger; if you cannot, restart the session |

## Guidelines

- **Evidence over plausibility.** A fix justified by "this looks like it would cause that" is a guess. Capture the boundary in question; if the bug is upstream of the captured boundary, move the boundary upstream.
- **Push tests down the pyramid.** A passing browser test is good. A passing Go/integration test is better — faster, cheaper, more reliable. After a browser bisection finds the layer, write the regression test at the lowest practical level.
- **One commit per dev-hook exposure.** Reviewable, revertable, never bundled with feature changes.
- **Strip the scaffolding.** The bisection tests served their purpose when they pointed at the layer. They are not regression tests. Delete them; keep the one assertion that proves the fix is in.
- **Do not paste images.** Describe what you saw or save the screenshot to a path the user can open. Many CLI environments do not render inline images from tool results.
- **Memory check.** If you bisected a class of bug worth remembering (e.g. "this UI library auto-replies on a synchronous pipe"), save it as a project memory so the next session does not redo the work.

Follow the communication-protocol skill for all user-facing output and interaction.
