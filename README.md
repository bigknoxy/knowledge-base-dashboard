# kbd — Knowledge Base Dashboard

[![CI](https://github.com/bigknoxy/knowledge-base-dashboard/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/bigknoxy/knowledge-base-dashboard/actions)

> For developers who treat their git history as data, not archaeology.

You've run hundreds of experiments. Some worked. You can't find them.

You've optimized `bundle_size` three times this quarter. Each time the same way.

You live in the terminal — but understanding your own repos means opening a browser.

**kbd** mines your git history and experiment logs into a living terminal dashboard. No browser. No spreadsheets. Just answers.

---

## Why We Built This

### The Problem (specific pain)

- **Invisible work**: "What did I actually ship this week?" requires archaeological dives through `git log` and GitHub. Git history is a write-only log in your head.
- **Buried experiments**: Autoresearch logs sit in reflog. Nobody tracks which optimizations actually worked. You optimize the same bottleneck twice and forget.
- **Context-switching tax**: Understanding your own repos means leaving the terminal, opening GitHub/Jira/Spreadsheet, losing the keyboard-driven flow state that makes you productive.

### The Solution

A single-command dashboard that:
- Scans all your git repos in seconds
- Parses experiment logs and surfaces win rates, patterns, and regressions
- Runs entirely in the terminal (no browser, no GUI dependency)
- Lives on XDG-compliant paths (`~/.config/kbd/`, `~/.local/share/kbd/`) so it doesn't clutter your home directory

---

## Proof It Works

### Tests (28 tests, 100% pass rate)

```
$ python -m pytest tests/ -q
............................                                             [100%]
28 passed, 16 warnings in 0.92s
```

### Linting (zero violations)

```
$ ruff check .
All checks passed!
```

### Type Safety (mypy strict mode)

```
$ mypy --strict core models export cli ui
Success: no issues found in 26 source files
```

### Coverage (40% baseline gate)

```
$ python -m pytest tests/unit -q --cov=core --cov=models --cov=export --cov=. --cov-fail-under=40
...
Required test coverage of 40% reached. Total coverage: 41.98%
25 passed, 9 warnings in 0.53s
```

### Installer (one-liner, idempotent)

```
$ curl -fsSL https://raw.githubusercontent.com/bigknoxy/knowledge-base-dashboard/main/install.sh | sh
✓ Python 3.12 found
✓ uv found
Installing knowledge-base-dashboard...
✓ Installation complete!
```

(On systems with Python 3.12+. Install script exits cleanly if requirements aren't met.)

---

## Quickstart

### 1. Install (30 seconds)

```bash
curl -fsSL https://raw.githubusercontent.com/bigknoxy/knowledge-base-dashboard/main/install.sh | sh
source ~/.bashrc  # or ~/.zshrc if using zsh
```

**What it does:** Downloads and installs `kbd` using `uv` into `~/.local/bin`. Adds `~/.local/bin` to your PATH if needed.

**Why:** Zero setup friction. No cloning repos, no venvs to activate, no PATH archaeology.

---

### 2. Initialize your config

```bash
kbd init
```

**Output:**
```
✓ Created config: /Users/joshua/.config/kbd/config.toml
✓ Data dir: /Users/joshua/.local/share/kbd
✓ Initialized!
```

**What it does:** Creates XDG-compliant directories (`~/.config/kbd/` and `~/.local/share/kbd/`). Writes a default config.

**Why:** Your database lives in a predictable place, not wherever you happened to type `kbd`. XDG compliance means tools can discover your config automatically.

---

### 3. Scan your repos

```bash
kbd scan ~/projects
```

**What it does:** Walks every git repo under `~/projects` (up to depth 5), extracts:
- Language breakdown (by file extension)
- Stack detection (React, Next.js, etc. from `package.json`, `pyproject.toml`, etc.)
- Git history (commits, branches, last activity, authors)
- Autoresearch experiment logs (if present)

**Why:** Builds your personal knowledge base — all repos indexed in seconds. You don't have to think about which repo is which anymore.

**Expect:**
```
Scanning 1 path(s)...
  Scanning /Users/joshua/projects...
  Found X repos

Saving X repos to database...

Scan complete!
  Repos: X
  Experiments: Y
```

---

### 4. Check your data

```bash
kbd health
```

**What it does:** Prints database stats — total repos, experiments, patterns detected, pending insights.

**Why:** Confirm your scan captured what you expected before opening the dashboard.

**Expect:**
```
Knowledge Base Dashboard — Health Check
  Database: /Users/joshua/.local/share/kbd/kbd.db (X.XX MB)
  Repos: N
  Experiments: M
  Patterns detected: K
  Pending insights: J
```

---

### 5. Launch the dashboard

```bash
kbd dashboard
```

**What it does:** Opens the interactive Textual TUI with 5 tabs:
- **Overview**: Repo count, language breakdown, recent activity
- **Repos**: Sortable table of all scanned repos (click to drill down)
- **Experiments**: Run-by-run results from autoresearch sessions
- **Patterns**: Recurring strategies you use (e.g., "when optimizing bundle_size, always try code-splitting first")
- **Timeline**: Activity heatmap by commit author and month

**Why:** Browse your entire engineering history without leaving the terminal. Full keyboard navigation.

**Controls:**
- `q` — quit
- `r` — refresh
- `Tab` / `Shift+Tab` — next/previous tab
- Arrow keys — navigate within tab

---

### 6. Export a report (optional)

```bash
kbd export --output report.html
```

**What it does:** Generates a standalone HTML report with all repos, experiments, and patterns.

**Why:** Share with your team or archive a snapshot for later review.

**Expect:**
```
Report written to: /Users/joshua/report.html
```

Open `report.html` in any browser — zero dependencies, fully self-contained.

---

## Features

- **Repo Scanner** — Detects languages, frameworks, and activity across all your git repos
- **Experiment Analytics** — Parses `autoresearch.jsonl` logs into metrics, win rates, and trends
- **Pattern Detection** — Finds recurring optimization strategies you apply (and their success rate)
- **Insight Engine** — Suggests alternatives when you're stuck in loops ("you've optimized this 3 times the same way")
- **TUI Dashboard** — Interactive Textual UI with 5 tabs, keyboard navigation, zero GUI dependency
- **HTML Export** — Shareable static report, works anywhere
- **XDG-Compliant Storage** — Database and config follow XDG Base Directory spec, not scattered across your home dir

---

## Configuration

Edit `~/.config/kbd/config.toml` to customize scan paths, database location, and UI theme:

```toml
[scan]
paths = ["~/projects", "~/work"]
exclude = ["**/.venv/**", "**/node_modules/**", "**/.git/**"]
max_depth = 5

[database]
path = ""  # Defaults to ~/.local/share/kbd/kbd.db if empty

[ui]
theme = "dark"
overview_repo_limit = 10
```

---

## Autoresearch Format

Experiment logs are JSONL files named `autoresearch.jsonl`. See `docs/autoresearch_format.md` for the schema.

---

## Development

```bash
git clone https://github.com/bigknoxy/knowledge-base-dashboard
cd knowledge-base-dashboard

# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Lint and type-check
ruff check .
mypy --strict core models export cli ui
```

All tests must pass and linting must be clean before pushing.

---

## Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/bigknoxy/knowledge-base-dashboard/main/uninstall.sh | sh
```

Removes the `kbd` binary and offers to clean up your data (`~/.local/share/kbd/`, `~/.config/kbd/`).
