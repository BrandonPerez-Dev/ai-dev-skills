# Compose Multiplatform Desktop UI Testing: What Are Your Options?

## Answer

There is no Playwright-equivalent external CLI tool for Compose Multiplatform desktop — a tool that drives a running app from the outside via a protocol, cross-platform, with a stable API. The closest thing to that today is **compose-driver** (experimental, v0.5.0, 2025–2026), which runs the UI in-process via a local HTTP server. The practical primary option for real test automation is the **JetBrains-official in-process testing API** (`compose.desktop.uiTestJUnit4`) invoked via `./gradlew desktopTest`. External-process automation via platform accessibility APIs is theoretically possible on Windows and macOS but has no verified working solution specific to Compose desktop, and has no path at all on Linux.

---

## Key Findings

### 1. Official JetBrains testing API — the only mature, supported option

The official testing API lives inside the Compose Multiplatform SDK. For desktop it uses JUnit4 under the hood.

**Setup:**
```kotlin
// shared/build.gradle.kts
val desktopTest by getting {
    dependencies {
        implementation(compose.desktop.uiTestJUnit4)
        implementation(compose.desktop.currentOs)
    }
}
```

**Run from CLI:**
```bash
./gradlew desktopTest
```

**API:**
```kotlin
@get:Rule val rule = createComposeRule()

@Test fun myTest() {
    rule.setContent { MyComposable() }
    rule.onNodeWithTag("btn").performClick()
    rule.onNodeWithTag("result").assertTextEquals("Done")
}
```

The common `runComposeUiTest` function (no JUnit TestRule) also works for desktop as of CMP 1.6.0 (Feb 2024, experimental). CMP 1.11 (late 2025/2026) promoted this to non-experimental for non-Android targets and switched to `StandardTestDispatcher`, meaning coroutines no longer run eagerly — `waitUntil()` / `waitForIdle()` required for async composables.

**Headless / CI:** Desktop tests do require a display context. On Linux CI (GitHub Actions, etc.) you need `xvfb-run ./gradlew desktopTest`. Mac/Windows CI runners work without extra steps. Desktop is confirmed to be the fastest feedback loop — no emulator needed, warm build under 30 seconds.

**Status:** Stable enough for production use. The common-test path was experimental through 1.10, graduated in 1.11.

[Source: JetBrains official docs](https://kotlinlang.org/docs/multiplatform/compose-desktop-ui-testing.html) — verified June 2026
[Source: KMP Bits write-up](https://www.kmpbits.com/posts/compose-ui-test-cmp) — June 2025

---

### 2. compose-driver — experimental HTTP-based headless driver (closest to Playwright)

**What it is:** A Gradle Settings plugin that auto-generates a `:compose-driver-desktop` subproject wrapping your composables in a test harness that exposes a local HTTP API. AI agents (or your own CLI scripts) send REST-style requests to drive the UI. Zero changes to production code.

**How to run:**
```bash
./gradlew :compose-driver-desktop:run --args="--composable=com.example.MyScreen"
# Then curl or script against http://localhost:8080
# POST /click, /textInput, GET /screenshot, /tree
```

**Key traits:**
- Truly headless on JVM — no display required, virtual clock, renders in memory
- Supports screenshot + accessibility tree snapshots
- Desktop recommended over Android/Robolectric path for multiplatform work (faster startup)
- Can record GIF if ffmpeg installed
- Designed with AI coding agents in mind, but nothing stops scripted use

**Maturity:** v0.5.0, experimental. Authored by Jordan Demeulenaere (JetBrains). Sparse docs, no stable API guarantee. Built on top of the same `ComposeUiTest` internals as option 1 — it's an HTTP facade, not a reimplementation.

**Refutation attempt:** No reported failures or known blockers on desktop use. The main limitation is it's in-process (same JVM as the composable), not a black-box driver of a running native binary. It cannot test packaging, window management, tray icons, or OS-level dialogs.

[Source: github.com/jdemeulenaere/compose-driver](https://github.com/jdemeulenaere/compose-driver) — verified June 2026
[Source: DEV.to article by author](https://dev.to/jdemeulenaere/vibe-coding-mobile-apps-with-compose-driver-3379) — 2026

---

### 3. Ultron — test abstraction layer, not a standalone CLI tool

Ultron is a Kotlin library wrapping the Compose testing API with Page Object pattern support and better stability (retry logic, Allure report integration). It simplifies writing tests, not running them from outside.

**Desktop support status:** Alpha as of mid-2025. Multiplatform support is listed as alpha in the official docs.

**CLI story:** Same as option 1 — `./gradlew desktopTest`. Ultron doesn't add a CLI; it adds ergonomic Kotlin test DSL.

**When to use:** If you're writing a lot of tests and want better Page Object patterns and retries built in, add Ultron on top of the official API. Not a replacement for a driver.

[Source: open-tool.github.io/ultron/docs/compose/multiplatform/](https://open-tool.github.io/ultron/docs/compose/multiplatform/) — verified June 2026
[Source: github.com/open-tool/ultron](https://github.com/open-tool/ultron) — verified June 2026

---

### 4. External process automation (FlaUI / WinAppDriver / Appium) — largely a dead end for Compose

This is the "real Playwright" pattern: a separate process driving the running app via OS accessibility APIs. Here is what the evidence actually says:

| Platform | Accessibility API | Compose Desktop Status |
|----------|-------------------|------------------------|
| Windows | Java Access Bridge (JAB) — NOT native UIA | Supported but JAB must be explicitly enabled; no verified FlaUI/WinAppDriver integration with Compose apps found |
| macOS | Native macOS Accessibility API | Supported; Accessibility Inspector (Xcode) works; no Playwright-style CLI driver found |
| Linux | AT-SPI | **Not supported** — JetBrains docs explicitly state no accessibility support on Linux |

The critical finding: Compose desktop on Windows goes through **Java Access Bridge**, not the native Windows UI Automation (UIA) API that FlaUI and WinAppDriver use. FlaUI/WinAppDriver target UIA — they cannot see JAB-exposed elements without a JAB-to-UIA bridge layer. No such bridge with verified Compose support was found in the literature.

WinAppDriver itself is effectively abandoned (last major release 2020). Winium is abandoned (last release 2016).

**Refutation:** Searched specifically for "Compose desktop FlaUI works", "Compose desktop Windows UI Automation accessible external tools" — found zero community reports of a working external driver for Compose desktop apps on any platform. The absence of discussion in the Kotlin/Compose community is itself negative evidence.

[Source: JetBrains accessibility docs](https://kotlinlang.org/docs/multiplatform/compose-desktop-accessibility.html) — verified June 2026
[Source: testguild.com desktop automation tools 2026](https://testguild.com/automation-tools-desktop/) — 2026

---

### 5. Screenshot testing (Roborazzi / Paparazzi / ComposablePreviewScanner) — complementary, not behavioral

These tools render composables headlessly and diff pixel output against golden images. They're not behavioral test drivers — they can't click buttons or assert state changes. Useful for visual regression, not UI automation.

ComposablePreviewScanner auto-generates screenshot tests from `@Preview` annotations across Android and Compose Multiplatform. Desktop targets work.

[Source: github.com/sergio-sastre/ComposablePreviewScanner](https://github.com/sergio-sastre/ComposablePreviewScanner) — verified June 2026

---

## Comparison Matrix

| Option | In-process / External | CLI | Headless | Desktop stable | Multiplatform | Maturity |
|--------|----------------------|-----|----------|---------------|---------------|----------|
| JetBrains testing API (`uiTestJUnit4`) | In-process | `./gradlew desktopTest` | Yes (xvfb on Linux) | Yes | Common test: 1.11+ | Stable |
| compose-driver | In-process (HTTP facade) | `./gradlew :compose-driver-desktop:run` + curl | Yes (JVM, no display) | Yes | Android + JVM | Experimental v0.5.0 |
| Ultron | In-process (wrapper) | Same as above | Same as above | Alpha | Android + CMP | Alpha |
| FlaUI / WinAppDriver | External process | Yes | No (needs real window) | Not verified for Compose | Windows only | WinAppDriver abandoned |
| Screenshot testing (Roborazzi etc.) | In-process | `./gradlew test` | Yes | Yes | Yes | Stable for Android; CMP partial |

---

## Contradictions and Surprises

- **Surprise:** compose-driver is headless on JVM — it uses the Compose testing harness's virtual rendering, so it doesn't need a display at all. This is meaningfully different from the JUnit API, which does appear to need a display context (hence xvfb on Linux CI). This makes compose-driver potentially better suited for cloud CI pipelines than the official API, despite being less mature.

- **Surprise:** Compose desktop on Windows uses Java Access Bridge, not native UIA. This is the single biggest blocker for external process automation tools, and it's buried in the accessibility docs rather than the testing docs. Almost no one writing about "how to automate Compose desktop with external tools" seems aware of it.

- **Contradiction (resolved):** Some sources describe the common test API (`runComposeUiTest`) as "experimental" while others call it production-ready. Context: it was experimental through CMP 1.10, graduated in CMP 1.11. The JUnit4 desktop-specific API (`createComposeRule`) has been stable longer.

- **Linux:** No external automation path exists. In-process testing (`./gradlew desktopTest` with xvfb) is your only option.

---

## Practical Recommendation for Your Use Case

Given you're building **Compose Pilot** — a debug/inspection agent for Compose Multiplatform — the relevant finding is:

1. **compose-driver** is architecturally very close to what you'd want to build: HTTP API, headless JVM, in-process, uses ComposeUiTest internals. Study it as a reference implementation before building your own. It targets AI agents but is general enough.

2. The **official testing API** is the foundation everything builds on. Any tool in this space wraps `ComposeUiTest` / `SemanticsNodeInteractionProvider`.

3. There is no external-process black-box driver. The only "external" angle possible today is via platform accessibility APIs, and it's unverified / not supported on Linux. If you want a Playwright-level external driver, you'd be building it.

---

## Sources

- [Testing Compose Multiplatform UI](https://kotlinlang.org/docs/multiplatform/compose-test.html) — JetBrains official, June 2026
- [Testing Compose Multiplatform UI with JUnit](https://kotlinlang.org/docs/multiplatform/compose-desktop-ui-testing.html) — JetBrains official, June 2026
- [Support for desktop accessibility features](https://kotlinlang.org/docs/multiplatform/compose-desktop-accessibility.html) — JetBrains official, June 2026
- [github.com/jdemeulenaere/compose-driver](https://github.com/jdemeulenaere/compose-driver) — verified June 2026
- [Vibe coding mobile apps with Compose Driver](https://dev.to/jdemeulenaere/vibe-coding-mobile-apps-with-compose-driver-3379) — 2026
- [Multiplatform | Ultron docs](https://open-tool.github.io/ultron/docs/compose/multiplatform/) — verified June 2026
- [github.com/open-tool/ultron](https://github.com/open-tool/ultron) — verified June 2026
- [Clean Lap: UI Testing in Compose Multiplatform | KMP Bits](https://www.kmpbits.com/posts/compose-ui-test-cmp) — 2025
- [Compose Multiplatform UI Tests (Marko Novakovic)](https://markonovakovic.medium.com/compose-multiplatform-ui-tests-d59b398bb984) — Medium, 2024
- [How to run headless unit tests for GUIs on GitHub actions](https://arbitrary-but-fixed.net/2022/01/21/headless-gui-github-actions.html) — 2022 (xvfb pattern, still current)
- [github.com/sergio-sastre/ComposablePreviewScanner](https://github.com/sergio-sastre/ComposablePreviewScanner) — verified June 2026
- [Best Desktop Automation Testing Tools 2026](https://testguild.com/automation-tools-desktop/) — 2026 (FlaUI/WinAppDriver status)

---

## Open Questions

1. Does compose-driver's HTTP facade work with the full running app window (including window chrome, system dialogs) or only with individual composable roots it wraps? The current answer appears to be "only wrapped composables" — needs verification from source code.
2. Does enabling Java Access Bridge on Windows actually allow any automation tool (UiPath, etc.) to traverse a Compose desktop app's element tree? No community confirmation found.
3. Is there any JetBrains-internal work on an AT-SPI bridge for Linux? None found publicly; would be tracked in compose-multiplatform GitHub issues.
4. compose-driver is described as targeting AI coding tools — is there an MCP server wrapper planned? Author mentioned it as future work in the DEV.to article.

## Promote to context/

**For `context/compose-pilot.md`:**
- No external black-box driver exists for Compose desktop. All viable test tooling is in-process, wrapping `ComposeUiTest` / the semantics tree.
- compose-driver (`github.com/jdemeulenaere/compose-driver`) is the closest reference architecture: Gradle plugin, HTTP API, headless JVM, zero production code changes. Built by a JetBrains employee. Study before designing Compose Pilot's agent API.
- Compose desktop on Windows uses Java Access Bridge, not native UIA. External tools that target Windows UIA (FlaUI, WinAppDriver) will not work without a bridge layer that does not yet exist.
- Linux has no accessibility support in Compose desktop at all — no AT-SPI bridge.
- Any Compose Pilot architecture must be in-process (JVM) to access the semantics tree. External process control is not currently viable.
