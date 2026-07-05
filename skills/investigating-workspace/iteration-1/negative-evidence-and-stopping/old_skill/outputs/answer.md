# CLI UI Testing for Compose Multiplatform Desktop: What Are Your Options?

## Answer

There is no Playwright equivalent for Compose Multiplatform desktop. The ecosystem has one first-party in-process testing framework (JetBrains' `compose-ui-test`) and one third-party wrapper (Ultron) that simplifies its syntax. For out-of-process black-box automation from a CLI — the Playwright model — nothing exists yet. Your prior research on Compose Pilot identified this gap accurately and the gap is still open as of June 2026.

---

## What Exists Today

### Option 1: compose-ui-test (Official, in-process only)

**What it is:** JetBrains' first-party testing library, built on top of the Jetpack Compose testing API. Tests run inside the JVM process alongside your app code.

**Desktop support:**
- JUnit-based desktop API via `compose.desktop.uiTestJUnit4` and `createComposeRule()` — stable, runs with `./gradlew desktopTest`
- Common cross-platform API via `runComposeUiTest` — experimental, runs with `./gradlew jvmTest`

**What you can do:**
- `onNodeWithTag("button").performClick()`
- `onNodeWithText("Hello").assertIsDisplayed()`
- `onNodeWithTag("text").assertTextEquals("Submit")`
- Interact with LazyLists, trigger keyboard events, wait for idle state

**What you cannot do:**
- Run against a running app from outside the process (no CLI driver)
- Test the packaged/distributed binary
- Automate from a language other than Kotlin
- Automate a running app you didn't build with test dependencies

**Invocation:**
```bash
./gradlew desktopTest        # JUnit-based desktop tests
./gradlew jvmTest            # Common runComposeUiTest tests
```

**Reference:** https://kotlinlang.org/docs/multiplatform/compose-desktop-ui-testing.html

---

### Option 2: Ultron (Third-party wrapper, in-process only)

**What it is:** Open-source library (Apache 2.0, 253 stars, last release Oct 2025 v2.6.2) that wraps `compose-ui-test` with cleaner syntax, retry logic, and Page Object pattern support.

**Desktop support:** Present but labeled Alpha state. Uses `runUltronUiTest` instead of `runComposeUiTest`.

**What it adds over raw compose-ui-test:**
- Cleaner syntax: `hasTestTag("button").click()` vs `composeTestRule.onNode(hasTestTag("button")).performClick()`
- Automatic retry on flaky operations (configurable timeout, default 5s)
- Page Objects that work without threading `SemanticsNodeInteractionProvider` through every class
- LazyList helpers for scroll-to-item and item assertions
- Allure report integration (Android-only currently)

**What it cannot do:** Everything compose-ui-test can't do. It's a wrapper, not a new architecture. Still in-process, still requires test source sets, still no CLI driver.

**Dependency:**
```kotlin
testImplementation("com.atiurin:ultron-compose:<latest_version>")
```

**Reference:** https://github.com/open-tool/ultron, https://open-tool.github.io/ultron/docs/compose/multiplatform/

---

### Option 3: AWT Robot (OS-level, coordinate-only)

**What it is:** Java's `java.awt.Robot` class, available in any JVM app, lets you inject mouse clicks and keystrokes at screen coordinates.

**Desktop support:** Works on macOS, Windows, Linux — no app instrumentation needed. Purely OS-level.

**What it can do:**
- Click at pixel coordinates: `robot.mouseMove(x, y); robot.mousePress(InputEvent.BUTTON1_DOWN_MASK)`
- Type text via key events
- Take screenshots via `robot.createScreenCapture(Rectangle)`

**What it cannot do:**
- Find elements by label, test tag, or semantic role — completely coordinate-blind
- Scroll to elements, query whether a button is enabled, assert text content
- Adapt to layout changes without hardcoding coordinates

**Verdict:** Usable as a last resort for smoke testing a fixed layout. Breaks immediately on any layout change. Not a viable Playwright replacement.

---

### Option 4: OS Accessibility APIs (Platform-specific, partial coverage)

JetBrains documents that Compose Desktop exposes accessibility information via:

| Platform | Status | Technology |
|---|---|---|
| macOS | Fully supported | NSAccessibility — inspectable via Xcode Accessibility Inspector |
| Windows | Supported | Java Access Bridge (disabled by default; requires `jabswitch.exe /enable` and `jdk.accessibility` module) |
| Linux | Not supported | No implementation exists |

**What this means:** On macOS and Windows, you could theoretically drive a Compose Desktop app from an external automation tool that speaks the OS accessibility protocol — the same way screen readers and tools like Appium drive native apps.

**Practical reality:** No tool in the Kotlin ecosystem wraps this into a clean CLI today. JetBrains themselves filed a YouTrack issue (COMPOSE-1371) in April 2024 titled "Black box testing of UI written on Compose with native widgets" and proposed two approaches: accessibility API or exposing `ComposePanel.semanticNode` for external access. That issue has been closed without a public resolution, meaning the feature either landed quietly or was deferred.

**Platform-specific accessibility tools that could theoretically work on Windows/macOS:**
- **WinAppDriver** (Windows only, uses UIA) — Microsoft's Appium-compatible driver for Windows apps; Compose Desktop's Java Access Bridge exposure might make elements visible here, but this is unverified
- **macOS Accessibility Inspector** — inspection tool, not a test driver
- **JAWS / NVDA speech viewers** — screen readers, not automation tools

---

### What Does Not Work

| Tool | Reason |
|---|---|
| Maestro | Mobile only (Android + iOS). No desktop support, no plans for it. |
| Appium | Mobile only. No desktop variant for JVM/Compose apps. |
| Playwright | Browser/web only. Not applicable. |
| Paparazzi (cashapp) | Android screenshot testing only. No desktop support. |
| UI Automator | Android only. |
| Flutter integration_test | Flutter only. Different runtime entirely. |

---

## The Gap (Confirmed)

No tool exists that:
1. Runs outside the app process (black-box, CLI-driven)
2. Has element-aware semantics (find by tag, label, role — not pixel coordinates)
3. Works on Compose Desktop
4. Supports Linux (zero accessibility support in Compose Desktop on Linux)

This is the gap your Compose Pilot research identified in March 2026. A GitHub search for "compose multiplatform desktop ui test" repositories returned a single unrelated result (an ESC/POS printer library). No community tool has emerged since.

---

## Recommendation

**For component and interaction tests (most common need):** Use `compose-ui-test` with `./gradlew desktopTest` or `jvmTest`. If you want cleaner syntax and retry semantics, add Ultron (`com.atiurin:ultron-compose`). Both run from CLI via Gradle with no additional setup.

**For end-to-end / black-box tests against a running app:** Nothing ready-to-use exists. Your Compose Pilot architecture (embedded HTTP agent in-process + CLI client over localhost) is the correct approach and remains the first mover in this space.

**For screenshot regression tests:** No desktop equivalent of Paparazzi exists. The `ImageComposeScene` API in compose-ui-test lets you render composables to a bitmap in tests, which you can diff manually, but there's no framework around it.

---

## Key Known Limitations of compose-ui-test on Desktop

From live GitHub issues (confirmed fixed or wontfix):

1. **`waitForIdle` behavior differs from Android** — desktop requires explicit `waitForIdle()` calls in more places than Android does (issue #2427, closed)
2. **Key-typed events couldn't be generated in tests** — was a bug, fixed (issue #3710, closed Sep 2024)
3. **Test API doesn't fully integrate with child scenes in `Window`/`DialogWindow`** — was a bug, fixed (issue #3587, closed Sep 2024)
4. **`IllegalArgumentException` from `performClick()` thrown randomly** — intermittent flakiness issue, closed Sep 2024
5. **ProGuard strips semantics in release builds** — confirmed; if you run tests against a release build with ProGuard, semantics tree access breaks

---

## Sources

- [Testing Compose Multiplatform UI — official docs](https://kotlinlang.org/docs/multiplatform/compose-test.html)
- [Testing Compose Multiplatform UI with JUnit (Desktop) — official docs](https://kotlinlang.org/docs/multiplatform/compose-desktop-ui-testing.html)
- [Compose Desktop Accessibility — official docs](https://kotlinlang.org/docs/multiplatform/compose-desktop-accessibility.html)
- [GitHub issue #4687: Black box testing of UI written on Compose with native widgets](https://github.com/JetBrains/compose-multiplatform/issues/4687)
- [open-tool/ultron — GitHub](https://github.com/open-tool/ultron)
- [Ultron Multiplatform docs](https://open-tool.github.io/ultron/docs/compose/multiplatform/)
- [cashapp/paparazzi — GitHub](https://github.com/cashapp/paparazzi) (Android only, confirmed)
- `/home/juiz/research/kmp-ui-automation-tool.md` — prior research, March 2026

## Contradictions and Surprises

- The JetBrains "black box testing" GitHub issue (#4687) was **closed**, but the YouTrack issue it references (COMPOSE-1371) returned empty content when fetched — suggesting it may have moved to internal tracking or been intentionally closed without a public resolution. This is worth monitoring.
- Ultron explicitly labels its multiplatform support as "Alpha" — its primary audience is Android. Desktop coverage is secondary.
- Linux has zero accessibility support from JetBrains with no roadmap mention. Any accessibility-based out-of-process tool would be macOS/Windows-only by definition.

## Open Questions

- Has COMPOSE-1371 landed any `ComposePanel.semanticNode` exposure in a recent release? JetBrains' YouTrack was inaccessible during this research.
- Does WinAppDriver actually discover Compose Desktop elements via Java Access Bridge on Windows? This is theoretically possible but unverified.
- Is there any community work on a `compose-pilot` or equivalent that launched after March 2026?
