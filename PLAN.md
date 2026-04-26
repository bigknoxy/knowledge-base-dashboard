# 🧠 Knowledge Base Dashboard — Plan

> **Your coding patterns, visualized.** An interactive terminal dashboard that mines your git history and Autoresearch experiments into a living "what I know" analytics engine.

---

## 🎯 Project Goal

Build a tool that scans all local git repositories and Autoresearch experiment logs to produce:
- An **interactive TUI dashboard** (using a library like `blessed` or `Textual`)
- **Architecture pattern maps** — which frameworks, languages, and design patterns you use most
- **Experiment analytics** — which optimizations actually moved the needle vs noise
- **Auto-suggestions** — "When X, you try Y first. Have you tried Z?"
- **Skill evolution timeline** — how your focus areas shift over months

This becomes your personal "second brain" for engineering decisions.

---

## 📦 Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Runtime | Python 3.12+ | Rich ecosystem for data science + TUI |
| TUI Framework | **Textual** (Python) | Modern reactive terminal UI, built-in widgets, theming |
| Git Analysis | `gitpython` + raw `git log` plumbing | Parse commits, diffs, author stats, timelines |
| Data Model | `pydantic` models + `sqlite3` | Schema-validated records, fast queries |
| Experiment Parsing | Custom parser for `autoresearch.jsonl` | Extract pass/fail, metrics, improvements, trends |
| Viz (web export) | **Plotly** or **Echarts** via HTML | Shareable static charts from terminal data |
| Config | `pydantic-settings` (TOML) | User-customizable scan paths, ignored repos, time ranges |

---

## 🏗 Architecture

```
knowledge-base-dashboard/
├── cmd/
│   ├── kbd.py              # Main entry point + CLI (typer/click)
│   └── kbd-tui             # TUI launcher script
├── core/
│   ├── git_scanner.py      # Walks git repos, extracts metadata
│   ├── experiment_parser.py # Parses autoresearch.jsonl files
│   ├── pattern_engine.py   # Detects recurring patterns (X → Y)
│   ├── insight_engine.py   # Generates suggestions from patterns
│   └── db.py               # SQLite schema + CRUD operations
├── ui/
│   ├── dashboard.py        # Main TUI dashboard with tabs
│   ├── tabs/
│   │   ├── overview.py     # Summary stats, quick facts
│   │   ├── repos.py        # Repo browser with tech detection
│   │   ├── experiments.py  # Experiment timelines, win rates
│   │   ├── patterns.py     # Discovered patterns & suggestions
│   │   └── timeline.py     # Skill evolution over time
│   └── components/
│       ├── metric_chart.py  # Reusable chart widget
│       ├── repo_card.py     # Repo info display
│       └── suggestion_list.py # Auto-suggestion feed
├── models/
│   ├── repo.py             # Repo metadata (name, stack, activity)
│   ├── experiment.py       # Experiment run, metric, pass/fail
│   ├── pattern.py          # Detected pattern (trigger → action)
│   └── insight.py          # Generated suggestion
├── export/
│   └── html_report.py      # Generate shareable HTML dashboard
├── config.toml             # Scan paths, exclusions, themes
└── pyproject.toml
```

---

## 🔍 Key Features by Phase

### Phase 1: Foundation (Week 1-2)
- [ ] SQLite schema for repos, experiments, patterns
- [ ] Git scanner: walk `~/projects/`, detect repos, extract:
  - Languages (via file extensions in tree)
  - Package manifests (`package.json`, `pyproject.toml`, etc.)
  - Commit frequency, last active, branch count
- [ ] Autoresearch parser: read all `autoresearch.jsonl`, extract:
  - Experiment name, metric name, runs array with pass/fail
  - Best improvement, noise floor, keep/discard/crash ratio
- [ ] Basic TUI shell with tab navigation

### Phase 2: Analytics (Week 3-4)
- [ ] Skill distribution chart: "Python 45%, TypeScript 30%, Rust 15%..."
- [ ] Experiment heatmap: metric values over time, color-coded by status
- [ ] Win-rate calculator: % of experiments that produced real improvements
- [ ] "Most optimized" ranking: which metrics you've chased most
- [ ] Noise detection: experiments where improvement < noise floor

### Phase 3: Intelligence (Week 5-6)
- [ ] Pattern engine: detect recurring sequences
  - Example: "When optimizing bundle_size → always try tree-shaking first"
  - Example: "You use Textual for every TUI project"
- [ ] Suggestion engine: cross-reference patterns with alternatives
  - "You always try chunking + memoization. Have you considered Web Workers?"
- [ ] Timeline view: skill evolution with labeled eras
  - "2024 Q1: Performance focus" → "2024 Q3: DX focus"

### Phase 4: Polish & Export (Week 7-8)
- [ ] Theme support (dark/light/custom)
- [ ] HTML export for shareable reports
- [ ] Markdown export for README-style summaries
- [ ] Plugin system for custom metrics/sources

---

## 📊 Dashboard Wireframe (TUI)

```
┌────────────────────────────────────────────────────────┐
│  🧠 Knowledge Base Dashboard                           │
├──────────┬─────────────────────────────────────────────┤
│  OVERVIEW│                                            │
│  REPOS   │  📊 Tech Stack                             │
│  EXPERIM │  ████████ Python  45%                      │
│  PATTERN │  ████████ TS       30%                     │
│  TIMELINE│  ████ Rust     12%                         │
│          │  ██ Go          8%                         │
│          │                                            │
│  ──────  │  📈 Recent Activity                        │
│  ⚙️      │  - 14 commits in last 7 days               │
│          │  - 3 experiment sessions                   │
└──────────┴─────────────────────────────────────────────┘
```

---

## 🧪 Success Metrics

| Metric | Target |
|--------|--------|
| Repos scanned in < 5s | 50+ repos |
| TUI renders in < 2s | Cold start |
| Patterns detected | 10+ non-trivial patterns |
| Suggestions generated | 5+ per session |
| HTML export size | < 500KB |

---

## 🚀 Quick Start Commands

```bash
# Install
cd ~/projects/knowledge-base-dashboard
uv venv && source .venv/bin/activate
uv pip install textual gitpython pydantic plotly

# Scan and launch
python cmd/kbd.py scan ~/projects/
python cmd/kbd.py dashboard

# Export report
python cmd/kbd.py export --html --output report.html
```

---

## 💡 Unique Insights to Uncover

1. **"Optimization ROI"** — Which experiment categories produce the biggest gains per hour invested?
2. **"Pattern fatigue"** — Are you stuck in the same optimization loop? (e.g., reducing bundle size for 3 months with diminishing returns)
3. **"Stack drift"** — Are you slowly migrating away from certain technologies?
4. **"Deep work sessions"** — When do your most productive experiment runs happen? (day of week, time of day)
5. **"The forgotten repo"** — Repos you started with enthusiasm but abandoned (high initial commits, zero recent activity)
