# 🧠 Knowledge Base Dashboard

> Your coding patterns, visualized. An interactive TUI that mines your git history and experiment logs into a living analytics engine.

## Quick Start

### One-liner Install

```bash
curl -fsSL https://raw.githubusercontent.com/bigknoxy/knowledge-base-dashboard/main/install.sh | sh
```

Then reload your shell:
```bash
source ~/.bashrc  # or ~/.zshrc if using zsh
```

### From Source

```bash
# Install
cd ~/projects/knowledge-base-dashboard
uv venv && source .venv/bin/activate
uv pip install -e .

# Scan your projects
kbd scan ~/projects

# Launch dashboard
kbd dashboard

# Check health
kbd health

# Export HTML report
kbd export --output report.html
```

### Uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/bigknoxy/knowledge-base-dashboard/main/uninstall.sh | sh
```

## Features

- **Repo Scanner** — Detects languages, frameworks, and activity across all your git repos
- **Experiment Analytics** — Parses `autoresearch.jsonl` logs into metrics and win rates
- **Pattern Detection** — Finds recurring optimization strategies you apply
- **Insight Engine** — Suggests alternatives when you're stuck in loops
- **TUI Dashboard** — Interactive Textual UI with 5 tabs: Overview, Repos, Experiments, Patterns, Timeline
- **HTML Export** — Shareable static report

## Development

```bash
uv pip install -e ".[dev]"
python -m pytest tests/ -v
ruff check .
```

## Configuration

Edit `config.toml` to set scan paths, database location, and theme.

## Autoresearch Format

Experiment logs are JSONL files named `autoresearch.jsonl`. See `docs/autoresearch_format.md` for the schema.
