# CLI Tool README Patterns

Patterns derived from ripgrep, bat, fd, fzf, zoxide, starship, nushell, age, and nsjail.

## What Makes CLI READMEs Different

CLI tools compete directly with existing Unix tools. The reader already has `grep`, `cat`, `find`, `cd`. The README must answer "why switch?" within the first scroll.

## Key Patterns

### Adversarial Value Prop

Name the predecessor. Every great CLI README opens by positioning against what the reader already uses:

- "a line-oriented search tool... while respecting your gitignore" (ripgrep vs grep)
- "a cat(1) clone with syntax highlighting and Git integration" (bat vs cat)
- "a simple, fast and user-friendly alternative to find" (fd vs find)
- "a smarter cd command, inspired by z and autojump" (zoxide vs cd/z)

The one-sentence pitch should follow this pattern: **"[Name] is a [category] that [key differentiator], designed to replace [predecessor]."**

### Visual Demo Above the Fold

Every top CLI README has a terminal screenshot or animated recording in the first screenful. This is non-negotiable for CLI tools — the output IS the interface.

**Preference order:**
1. **asciinema** recording (text-based, searchable, lightweight, doesn't go stale as fast)
2. **Static screenshot** of terminal output (permanent, fast-loading)
3. **GIF** of terminal session (heavier, can go stale, but shows workflow)

The demo should show the tool's most impressive output, not its most basic. bat's README shows syntax highlighting + git diff markers + line numbers in one screenshot. ripgrep's shows colored matches with context lines.

### Benchmark Table

If performance is a selling point, prove it with real numbers:

```markdown
| Command | Time |
|---------|------|
| `find ~ -iregex '.*[0-9]\.jpg$'` | 19.9s |
| `fd -u '[0-9]\.jpg$' ~` | 855ms |
```

Always specify: hardware, corpus size, methodology. Link to a blog post or benchmark script for full reproducibility. Never say "blazingly fast" without numbers.

### Feature Comparison Matrix

For tools with direct competitors, a comparison table prevents the reader from needing to research alternatives:

```markdown
| Feature | ripgrep | ag | ack | grep |
|---------|---------|-----|-----|------|
| Unicode support | Yes | Yes | Yes | Partial |
| Compressed search | Yes | No | No | Yes |
| Gitignore respect | Yes | Yes | Yes | No |
```

### "Why NOT to Use This" Section

ripgrep is the only major CLI that does this, and it's consistently cited as a high-trust signal. List genuine limitations:

- Not POSIX-compliant (won't work in scripts expecting grep behavior)
- Missing features that alternatives have
- Edge cases where alternatives are faster

This section communicates: "the maintainer knows this tool's boundaries and respects your time."

### Exhaustive Platform Installation Matrix

CLI tools must document every distribution method. Order by popularity, fastest path first:

```markdown
## Installation

### Package Managers

| Platform | Command |
|----------|---------|
| macOS (Homebrew) | `brew install toolname` |
| macOS (MacPorts) | `sudo port install toolname` |
| Ubuntu/Debian | `sudo apt install toolname` |
| Fedora | `sudo dnf install toolname` |
| Arch Linux | `pacman -S toolname` |
| Windows (scoop) | `scoop install toolname` |
| Windows (choco) | `choco install toolname` |
| Windows (winget) | `winget install toolname` |

### From Source

<details>
<summary>Building from source</summary>

Requires Rust 1.70+:
\```bash
cargo install toolname
\```

Or clone and build:
\```bash
git clone https://github.com/org/toolname
cd toolname
cargo build --release
\```

</details>
```

Use `<details>` blocks for less common paths to keep the section scannable.

### Shell Integration as a First-Class Step

For tools that modify shell behavior (fzf, zoxide, starship), shell integration is a numbered step in installation, not buried in configuration:

```markdown
## Installation

1. Install the binary (see table above)
2. Add to your shell config:

   **bash** (`~/.bashrc`):
   \```bash
   eval "$(toolname init bash)"
   \```

   **zsh** (`~/.zshrc`):
   \```bash
   eval "$(toolname init zsh)"
   \```

   **fish** (`~/.config/fish/config.fish`):
   \```fish
   toolname init fish | source
   \```

3. Restart your shell
```

### Third-Party Integrations Table

For CLI tools that compose with other tools, document the ecosystem:

```markdown
## Integration with Other Tools

| Tool | How |
|------|-----|
| fzf | `export FZF_DEFAULT_COMMAND='fd --type f'` |
| vim | `:set grepprg=rg\ --vimgrep` |
| VS Code | Extension: [vscode-toolname](link) |
```

### Translations / i18n

If the README has translations, list them with links near the top. This signals global adoption (social proof) and accessibility.

## Section Order (CLI-Specific)

```
1. Logo + Badges (CI, crates.io/npm version, license)
2. Title + adversarial one-liner ("a faster X that replaces Y")
3. Terminal demo (asciinema or screenshot)
4. Quick Start (brew install + one invocation showing output)
5. Features / Why use this? (bullet list, benchmarks if applicable)
6. Why NOT to use this? (honest limitations)
7. Installation (platform matrix with <details> blocks)
8. Usage (3-5 common invocations with expected output)
9. Configuration (flags + config file, minimum viable)
10. Integration with other tools
11. Translations (if applicable)
12. Contributing
13. License
```

## CLI-Specific Anti-Patterns

| Anti-Pattern | Fix |
|--------------|-----|
| Flag documentation as the Usage section | Show real invocations with real output first; link to `--help` for the full flag list |
| "Fast" without benchmarks | Numbers or don't mention speed |
| Only `cargo install` / only from source | List every package manager the tool is in |
| Shell integration buried in a wiki | It's part of installation, not configuration |
| Demo GIF showing a different version's output | Re-record or use asciinema (easier to update) |
