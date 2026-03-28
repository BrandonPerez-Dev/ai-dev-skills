# Scrollable Presentation Template

Complete HTML/CSS template for browser-rendered scrollable presentations. Supports dark and light themes via CSS variables.

## Full HTML Template

```html
<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title><!-- PRESENTATION TITLE --></title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css" id="hljs-theme">
  <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
  <style>
    /* ===== THEME VARIABLES ===== */
    :root[data-theme="dark"] {
      --bg-primary: #0F1117;
      --bg-secondary: #1A1D27;
      --bg-code: #161822;
      --bg-callout: #1E2233;
      --border-subtle: #2A2D3A;
      --border-accent: #6366F1;
      --text-primary: #E2E8F0;
      --text-secondary: #94A3B8;
      --text-muted: #64748B;
      --text-accent: #818CF8;
      --text-heading: #F8FAFC;
      --code-bg: #1E1E2E;
      --code-border: #313244;
      --callout-border: #6366F1;
      --comparison-bg-left: #1A1D27;
      --comparison-bg-right: #1D2233;
      --nav-bg: rgba(15, 17, 23, 0.9);
      --shadow: 0 2px 12px rgba(0,0,0,0.3);
    }

    :root[data-theme="light"] {
      --bg-primary: #FFFFFF;
      --bg-secondary: #F8FAFC;
      --bg-code: #F1F5F9;
      --bg-callout: #EEF2FF;
      --border-subtle: #E2E8F0;
      --border-accent: #6366F1;
      --text-primary: #1E293B;
      --text-secondary: #475569;
      --text-muted: #94A3B8;
      --text-accent: #4F46E5;
      --text-heading: #0F172A;
      --code-bg: #F8FAFC;
      --code-border: #E2E8F0;
      --callout-border: #6366F1;
      --comparison-bg-left: #F8FAFC;
      --comparison-bg-right: #EEF2FF;
      --nav-bg: rgba(255, 255, 255, 0.9);
      --shadow: 0 2px 12px rgba(0,0,0,0.08);
    }

    /* ===== RESET & BASE ===== */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.7;
      -webkit-font-smoothing: antialiased;
    }

    /* ===== NAVIGATION ===== */
    nav {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 100;
      background: var(--nav-bg);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-subtle);
      padding: 12px 32px;
      display: flex;
      align-items: center;
      gap: 24px;
    }
    nav .title {
      font-size: 14px;
      font-weight: 700;
      color: var(--text-heading);
      white-space: nowrap;
    }
    nav .sections {
      display: flex;
      gap: 8px;
      overflow-x: auto;
    }
    nav a {
      font-size: 12px;
      font-weight: 500;
      color: var(--text-muted);
      text-decoration: none;
      padding: 4px 10px;
      border-radius: 6px;
      white-space: nowrap;
      transition: all 0.2s;
    }
    nav a:hover { color: var(--text-primary); background: var(--bg-secondary); }

    /* ===== CONTENT CONTAINER ===== */
    .content {
      max-width: 820px;
      margin: 0 auto;
      padding: 80px 32px 120px;
    }

    /* ===== SECTION SPACING ===== */
    .section { padding: 60px 0; }
    .section + .section { border-top: 1px solid var(--border-subtle); }

    /* ===== HERO SECTION ===== */
    .hero {
      padding: 100px 0 80px;
      text-align: left;
    }
    .hero h1 {
      font-size: 48px;
      font-weight: 900;
      color: var(--text-heading);
      line-height: 1.1;
      letter-spacing: -0.03em;
      margin-bottom: 16px;
    }
    .hero .subtitle {
      font-size: 20px;
      color: var(--text-secondary);
      line-height: 1.5;
      max-width: 600px;
    }
    .hero .meta {
      margin-top: 24px;
      font-size: 13px;
      color: var(--text-muted);
    }

    /* ===== NARRATIVE SECTION ===== */
    .narrative h2 {
      font-size: 32px;
      font-weight: 800;
      color: var(--text-heading);
      line-height: 1.2;
      letter-spacing: -0.02em;
      margin-bottom: 20px;
    }
    .narrative h3 {
      font-size: 22px;
      font-weight: 700;
      color: var(--text-heading);
      margin-bottom: 12px;
      margin-top: 32px;
    }
    .narrative p {
      font-size: 16px;
      color: var(--text-secondary);
      margin-bottom: 16px;
      max-width: 680px;
    }
    .narrative ul, .narrative ol {
      margin: 12px 0 16px 24px;
      color: var(--text-secondary);
      font-size: 16px;
    }
    .narrative li { margin-bottom: 8px; }
    .narrative strong { color: var(--text-primary); font-weight: 600; }

    /* ===== DIAGRAM SECTION ===== */
    .diagram {
      text-align: center;
    }
    .diagram img {
      max-width: 100%;
      border-radius: 12px;
      border: 1px solid var(--border-subtle);
      box-shadow: var(--shadow);
    }
    .diagram .caption {
      margin-top: 12px;
      font-size: 13px;
      color: var(--text-muted);
      font-style: italic;
    }

    /* ===== CODE SECTION ===== */
    .code-section h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-accent);
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .code-section .file-path {
      font-size: 12px;
      font-family: 'JetBrains Mono', monospace;
      color: var(--text-muted);
      margin-bottom: 8px;
    }
    .code-section pre {
      background: var(--code-bg);
      border: 1px solid var(--code-border);
      border-radius: 10px;
      padding: 20px 24px;
      overflow-x: auto;
      box-shadow: var(--shadow);
    }
    .code-section pre code {
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      line-height: 1.6;
      tab-size: 2;
    }
    .code-section .code-note {
      margin-top: 12px;
      font-size: 14px;
      color: var(--text-muted);
    }

    /* ===== COMPARISON SECTION ===== */
    .comparison {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }
    .comparison .side {
      background: var(--bg-secondary);
      border-radius: 12px;
      padding: 28px;
      border: 1px solid var(--border-subtle);
    }
    .comparison .side:nth-child(2) {
      background: var(--comparison-bg-right);
    }
    .comparison .side h3 {
      font-size: 18px;
      font-weight: 700;
      color: var(--text-heading);
      margin-bottom: 14px;
    }
    .comparison .side p,
    .comparison .side li {
      font-size: 15px;
      color: var(--text-secondary);
    }
    .comparison .side ul { margin: 8px 0 0 20px; }
    .comparison .side li { margin-bottom: 6px; }

    /* ===== CALLOUT SECTION ===== */
    .callout {
      background: var(--bg-callout);
      border-left: 4px solid var(--callout-border);
      border-radius: 0 12px 12px 0;
      padding: 28px 32px;
    }
    .callout p {
      font-size: 18px;
      font-weight: 500;
      color: var(--text-primary);
      line-height: 1.6;
    }
    .callout .attribution {
      margin-top: 12px;
      font-size: 14px;
      color: var(--text-muted);
    }

    /* ===== FOLDER TREE ===== */
    .folder-tree {
      background: var(--code-bg);
      border: 1px solid var(--code-border);
      border-radius: 10px;
      padding: 24px 28px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      line-height: 1.8;
      color: var(--text-secondary);
      box-shadow: var(--shadow);
    }
    .folder-tree .folder { color: var(--text-accent); font-weight: 600; }
    .folder-tree .file { color: var(--text-secondary); }
    .folder-tree .comment { color: var(--text-muted); font-style: italic; }

    /* ===== RESPONSIVE ===== */
    @media (max-width: 768px) {
      .hero h1 { font-size: 36px; }
      .narrative h2 { font-size: 26px; }
      .comparison { grid-template-columns: 1fr; }
      .content { padding: 60px 20px 80px; }
    }
  </style>
</head>
<body>

  <!-- NAV: Section links for quick jumping -->
  <nav>
    <span class="title"><!-- SHORT TITLE --></span>
    <div class="sections">
      <!-- <a href="#section-1">Section Name</a> -->
    </div>
  </nav>

  <div class="content">

    <!-- HERO -->
    <div id="section-0" class="section hero">
      <h1><!-- Title --></h1>
      <p class="subtitle"><!-- One-line context --></p>
      <p class="meta"><!-- Author · Date · Audience --></p>
    </div>

    <!-- NARRATIVE SECTION -->
    <!--
    <div id="section-N" class="section narrative">
      <h2>Section Headline</h2>
      <p>Paragraph text. Keep to 2-3 sentences. Let it breathe.</p>
      <p>Second paragraph if needed. Rarely need more than two.</p>
    </div>
    -->

    <!-- DIAGRAM SECTION -->
    <!--
    <div id="section-N" class="section diagram">
      <img src="diagram-screenshot.png" alt="Description">
      <p class="caption">Caption explaining what to notice in the diagram</p>
    </div>
    -->

    <!-- CODE SECTION -->
    <!--
    <div id="section-N" class="section code-section">
      <h3>What This Shows</h3>
      <p class="file-path">path/to/file.ts:42-58</p>
      <pre><code class="language-typescript">
// Paste real code here. 15 lines max.
// Highlight the interesting part.
      </code></pre>
      <p class="code-note">Brief note on what makes this interesting.</p>
    </div>
    -->

    <!-- COMPARISON SECTION -->
    <!--
    <div id="section-N" class="section">
      <div class="comparison">
        <div class="side">
          <h3>Option A</h3>
          <p>Description or bullet points</p>
        </div>
        <div class="side">
          <h3>Option B</h3>
          <p>Description or bullet points</p>
        </div>
      </div>
    </div>
    -->

    <!-- CALLOUT SECTION -->
    <!--
    <div id="section-N" class="section">
      <div class="callout">
        <p>"The key insight or quote that you want the audience to remember."</p>
        <p class="attribution">— Source or context</p>
      </div>
    </div>
    -->

    <!-- FOLDER TREE (useful for showing project/skill structure) -->
    <!--
    <div id="section-N" class="section">
      <div class="folder-tree">
        <span class="folder">skills/</span><br>
        ├── <span class="folder">research/</span> <span class="comment">← investigates before acting</span><br>
        │   └── <span class="file">SKILL.md</span><br>
        ├── <span class="folder">design/</span> <span class="comment">← orchestrates planning</span><br>
        │   └── <span class="file">SKILL.md</span><br>
        └── <span class="folder">build/</span> <span class="comment">← implements the plan</span><br>
            └── <span class="file">SKILL.md</span><br>
      </div>
    </div>
    -->

  </div>

  <script>
    // Initialize syntax highlighting
    hljs.highlightAll();

    // Theme toggle (optional — press T to switch)
    document.addEventListener('keydown', (e) => {
      if (e.key === 't' || e.key === 'T') {
        const html = document.documentElement;
        const current = html.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        // Swap highlight.js theme
        const link = document.getElementById('hljs-theme');
        link.href = next === 'dark'
          ? 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css'
          : 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css';
        hljs.highlightAll();
      }
    });
  </script>
</body>
</html>
```

## Section Patterns — Quick Reference

### Hero
```html
<div class="section hero">
  <h1>Title</h1>
  <p class="subtitle">One line of context</p>
  <p class="meta">Author · Date</p>
</div>
```

### Narrative
```html
<div class="section narrative">
  <h2>Headline</h2>
  <p>Short paragraph. 2-3 sentences max.</p>
</div>
```

### Code
```html
<div class="section code-section">
  <h3>WHAT THIS SHOWS</h3>
  <p class="file-path">src/skills/research/SKILL.md:1-15</p>
  <pre><code class="language-yaml">---
name: research
description: >-
  Systematic investigation...
allowed-tools:
  - Read
  - WebSearch
  - Agent
---</code></pre>
  <p class="code-note">Skills define their own tool access — this is what makes them agents.</p>
</div>
```

### Comparison
```html
<div class="section">
  <div class="comparison">
    <div class="side">
      <h3>Claude Code Skills</h3>
      <ul>
        <li>Tool access defined per skill</li>
        <li>Context-naive — no state between invocations</li>
        <li>Can delegate to other skills</li>
      </ul>
    </div>
    <div class="side">
      <h3>Cursor Rules</h3>
      <ul>
        <li>Global rules, no per-rule tool scoping</li>
        <li>Always-on context</li>
        <li>No delegation model</li>
      </ul>
    </div>
  </div>
</div>
```

### Callout
```html
<div class="section">
  <div class="callout">
    <p>"Skills are context-naive agents. They have no memory beyond the current conversation. But with the right tools and structure, that's enough."</p>
  </div>
</div>
```

### Folder Tree
```html
<div class="section">
  <div class="folder-tree">
    <span class="folder">.claude/skills/</span><br>
    ├── <span class="folder">orchestrator/</span> <span class="comment">← routes to the right skill</span><br>
    ├── <span class="folder">design/</span> <span class="comment">← orchestrates: research → architecture → tdd</span><br>
    ├── <span class="folder">build/</span> <span class="comment">← implements one slice at a time</span><br>
    ├── <span class="folder">ship/</span> <span class="comment">← review → commit → PR</span><br>
    ├── <span class="folder">research/</span> <span class="comment">← investigate before acting</span><br>
    └── <span class="folder">verification/</span> <span class="comment">← evidence before assertions</span><br>
  </div>
</div>
```

## Theme Toggle

Press `T` to toggle dark/light theme live. Useful during presentation if someone asks. The highlight.js theme swaps automatically.

## Serving

```bash
npx -y serve /tmp/presentation -p 8790 --no-clipboard &
```

Navigate: `mcp__chrome-devtools__navigate_page` to `http://localhost:8790/deck.html`
Screenshot: `mcp__chrome-devtools__take_screenshot`
Scroll to section: `evaluate_script` with `window.scrollTo({ top: document.querySelector('#section-3').offsetTop - 60, behavior: 'smooth' })`

## Typography Scale

| Element | Size | Weight | Font |
|---------|------|--------|------|
| Hero h1 | 48px | 900 | Inter |
| Section h2 | 32px | 800 | Inter |
| Section h3 | 22px | 700 | Inter |
| Body text | 16px | 400 | Inter |
| Code | 14px | 400 | JetBrains Mono |
| Captions/meta | 13px | 400 | Inter |
| File paths | 12px | 400 | JetBrains Mono |
| Code section label | 16px | 600 | Inter, uppercase |
