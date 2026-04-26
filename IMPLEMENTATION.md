# Knowledge Base Dashboard — Implementation Details

> Append to PLAN.md. Covers the operational specifics: schemas, APIs, tests, CI, error handling.

---

## 1. Database Schema (`db.py`)

```sql
-- Repositories
CREATE TABLE repos (
    id              TEXT PRIMARY KEY,       -- filepath hash (sha256 of path)
    path            TEXT UNIQUE NOT NULL,
    name            TEXT NOT NULL,
    description     TEXT,                  -- from README or git branch desc
    url             TEXT,                  -- remote origin URL
    created_at      DATETIME,             -- first commit
    last_active     DATETIME,             -- last commit
    total_commits   INTEGER DEFAULT 0,
    branch_count    INTEGER DEFAULT 1,
    primary_lang    TEXT,
    stack_json      TEXT,                 -- JSON array of detected tech
    status          TEXT DEFAULT 'active', -- active, archived, abandoned
    scanned_at      DATETIME
);

-- Experiments (parsed from autoresearch.jsonl)
CREATE TABLE experiments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_id         TEXT REFERENCES repos(id),
    jsonl_path      TEXT NOT NULL,
    session_name    TEXT,
    metric_name     TEXT,
    metric_unit     TEXT,
    direction       TEXT,              -- 'lower' or 'higher'
    total_runs      INTEGER DEFAULT 0,
    kept_runs       INTEGER DEFAULT 0,
    discarded_runs  INTEGER DEFAULT 0,
    crashed_runs    INTEGER DEFAULT 0,
    best_metric     REAL,
    noise_floor     REAL,
    started_at      DATETIME,
    completed_at    DATETIME
);

-- Individual runs
CREATE TABLE experiment_runs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id   INTEGER REFERENCES experiments(id),
    commit          TEXT,
    metric          REAL,
    status          TEXT,             -- keep, discard, crash, checks_failed
    description     TEXT,
    extra_metrics   TEXT,            -- JSON object
    duration_ms     INTEGER,
    run_order       INTEGER,
    created_at      DATETIME
);

-- Detected patterns
CREATE TABLE patterns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger         TEXT NOT NULL,    -- e.g., "optimizing bundle_size"
    action          TEXT NOT NULL,    -- e.g., "tried tree_shaking first"
    frequency       INTEGER DEFAULT 1,
    confidence      REAL DEFAULT 0.0, -- 0.0 - 1.0
    first_seen      DATETIME,
    last_seen       DATETIME
);

-- Generated insights/suggestions
CREATE TABLE insights (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id      INTEGER REFERENCES patterns(id),
    suggestion      TEXT NOT NULL,
    urgency         TEXT DEFAULT 'low', -- low, medium, high
    resolved        BOOLEAN DEFAULT 0,
    created_at      DATETIME
);
```

### Indexes
```sql
CREATE INDEX idx_repos_last_active ON repos(last_active);
CREATE INDEX idx_repos_primary_lang ON repos(primary_lang);
CREATE INDEX idx_experiments_repo ON experiments(repo_id);
CREATE INDEX idx_runs_experiment ON experiment_runs(experiment_id);
CREATE INDEX idx_runs_status ON experiment_runs(status);
```

---

## 2. API Contracts

### Git Scanner Interface
```python
@dataclass
class RepoMetadata:
    path: Path
    name: str
    description: str
    primary_language: str
    stack: list[str]
    first_commit: datetime
    last_commit: datetime
    total_commits: int
    branches: int
    remote_url: str | None

class GitScanner:
    async def scan_directory(self, root: Path) -> list[RepoMetadata]: ...
    async def scan_repo(self, path: Path) -> RepoMetadata: ...
    async def detect_languages(self, path: Path) -> dict[str, float]: ...
    async def detect_stack(self, path: Path) -> list[str]: ...
    async def commit_stats(self, path: Path) -> CommitStats: ...

@dataclass
class CommitStats:
    total: int
    authors: list[Author]
    frequency_per_month: float
    avg_msg_length: float
    conventional_commits_pct: float
```

### Experiment Parser Interface
```python
class ExperimentParser:
    async def parse_jsonl(self, path: Path) -> ExperimentSession: ...
    async def find_all_jsonl(self, root: Path) -> list[Path]: ...
    def calculate_noise_floor(self, runs: list[Run]) -> float: ...
    def calculate_confidence(self, improvement: float, noise: float) -> float: ...

@dataclass
class ExperimentSession:
    name: str
    metric_name: str
    metric_unit: str
    direction: str
    runs: list[ExperimentRun]
    improved: bool
    noise_floor: float
    best_improvement: float
```

### Pattern Engine Interface
```python
class PatternEngine:
    async def detect_patterns(self, sessions: list[ExperimentSession]) -> list[Pattern]: ...
    async def suggest_alternatives(self, pattern: Pattern) -> list[Suggestion]: ...
    async def update_confidence(self, pattern_id: int, matched: bool): ...

@dataclass
class Pattern:
    trigger: str
    action: str
    frequency: int
    confidence: float
    repo_examples: list[str]

@dataclass
class Suggestion:
    pattern_id: int
    suggestion: str
    urgency: Urgency
    rationale: str
```

---

## 3. Textual TUI Component Hierarchy

```
Screen (MainDashboard)
├── Header (fixed)
│   ├── Logo + Title
│   ├── Status indicators (DB size, last scan, # repos)
│   └── Action buttons (rescan, export, settings)
├── Sidebar (dockable, resizable)
│   └── TabList
│       ├── OverviewTab
│       ├── ReposTab
│       ├── ExperimentsTab
│       ├── PatternsTab
│       └── TimelineTab
├── ContentArea (main panel, switches on tab)
│   ├── OverviewPanel
│   │   ├── TechStackChart (bar chart widget)
│   │   ├── ActivitySummary (stat cards)
│   │   ├── RecentRepos (list with preview)
│   │   └── InsightFeed (auto-suggestion cards)
│   ├── ReposPanel
│   │   ├── SearchBar (filter by name, lang, status)
│   │   ├── FilterBar (language, activity, stars)
│   │   └── RepoGrid (cards sorted by config)
│   ├── ExperimentsPanel
│   │   ├── ExperimentList (accordion per session)
│   │   ├── MetricTimeline (sparkline per metric)
│   │   ├── WinRateBar (pass/fail/crash breakdown)
│   │   └── BestRunHighlight (callout)
│   ├── PatternsPanel
│   │   ├── PatternList (with frequency + confidence)
│   │   └── SuggestionQueue (actionable items)
│   └── TimelinePanel
│       ├── EraViewer (labeled time blocks)
│       ├── SkillMigration (sankey diagram)
│       └── CommitHeatmap (GitHub-style grid)
└── Footer (fixed)
    ├── Progress indicator (during scan)
    ├── Quick actions
    └── Help / about
```

---

## 4. Testing Strategy

### Unit Tests (py.test)
```
tests/unit/
├── test_git_scanner.py         # Mock repos, verify metadata extraction
├── test_experiment_parser.py   # Synthetic jsonl → verify parsing
├── test_pattern_engine.py      # Inject patterns → verify detection
├── test_db.py                  # Schema migrations, CRUD operations
├── test_calculators.py         # Noise floor, confidence, win rate math
└── test_models.py             # Pydantic validation, edge cases
```

### Integration Tests
```
tests/integration/
├── test_full_scan.py           # Scan real repo subset → verify DB
├── test_experiment_ingest.py   # Ingest jsonl → full pipeline → DB → query
├── test_pattern_detection.py   # Full chain: experiment → pattern → suggestion
├── test_export_html.py         # Generate HTML → verify valid + links work
└── test_tui_startup.py         # Launch TUI → verify widgets render → close
```

### Test Data
```
tests/fixtures/
├── synthetic_repo/             # Tiny repo with known structure
├── sample_autoresearch.jsonl   # Pre-made experiment data
├── mixed_stack_repo/          # Project with multiple manifests
├── empty_repo/                # Edge case: no commits, no files
└── large_jsonl.jsonl          # Stress test: 1000+ runs
```

### Coverage Target
| Module | Target |
|--------|--------|
| `core/` | 90%+ |
| `models/` | 95%+ |
| `ui/` | 50% (hard to test, smoke tests only) |
| `export/` | 80%+ |

---

## 5. CI/CD Pipeline (`.github/workflows/ci.yml`)

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python: ['3.12', '3.13']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - uses: astral-sh/setup-uv@v3
      - run: uv pip install -e '.[dev]'
      - run: uv run pytest tests/unit -v --cov=src --cov-report=xml
      - run: uv run pytest tests/integration -v
      - uses: codecov/codecov-action@v4
        if: matrix.python == '3.12'

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv pip install -e '.[dev]'
      - run: uv run ruff check .
      - run: uv run mypy src/

  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: uv pip install build
      - run: uv run python -m build
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

---

## 6. Error Handling Philosophy

### Principle: **Silent degradation, loud failure**

| Scenario | Behavior |
|----------|---------|
| Repo unreadable (permissions) | Skip + log warning, continue |
| Git repo corrupt | Mark `status: 'error'`, skip scan |
| jsonl parse failure | Parse what we can, log partial failure |
| DB locked or full | Retry 3x with backoff, then crash loudly |
| Network unavailable | Offline mode (cached data only) |
| TUI resize during render | Defer render to next frame |
| Export HTML timeout | Write partial state, resume flag |
| Config missing fields | Use defaults, log "filing in defaults" |

### Error Classification
```python
class KBDError(Exception):
    """Base error for all KBD exceptions."""
    severity: Literal["info", "warn", "error", "fatal"]
    recoverable: bool = True

class ScanError(KBDError):       # Skip repo, continue
class ParseError(KBDError):      # Log, continue to next file
class ConfigError(KBDError):     # Fatal, cannot proceed
class DatabaseError(KBDError):   # Fatal after 3 retries
```

---

## 7. Performance Budgets

| Operation | Budget | Measurement |
|-----------|--------|-------------|
| Cold startup | < 800ms | `time python cmd/kbd.py dashboard` |
| Scan 100 repos | < 15s | `time python cmd/kbd.py scan --dry` |
| Parse jsonl (1000 runs) | < 200ms | unit test fixture |
| TUI initial render | < 500ms | Textual debug mode |
| DB query (top 50 repos) | < 50ms | SQL EXPLAIN ANALYZE |
| HTML export (100 repos) | < 10s | `time python cmd/kbd.py export` |

### Profiling Commands
```bash
# Profile scan
python -m cProfile -o scan.prof cmd/kbd.py scan ~/projects/
snakeviz scan.prof

# Profile TUI
python cmd/kbd.py dashboard --debug --perf-log

# DB query analysis
sqlite3 kbd.db "EXPLAIN QUERY PLAN SELECT * FROM repos ORDER BY last_active;"
```

---

## 8. Migration Plan

### V1 → V2 Schema Changes
```python
# Alembic-style migration
def upgrade_v2():
    # Add new columns
    add_column('repos', 'is_private', Boolean, default=False)
    add_column('experiments', 'direction', String, default='lower')

    # Create new table
    create_table('skill_eras', id, name, start_date, end_date, dominant_stack)

    # Recompute derived fields
    recompute_all_noise_floors()
```

### Backward Compatibility
- Old jsonl formats: detect by presence of `metric_name` field, auto-convert
- Old config TOML: `config.toml` v1 fields auto-mapped to v2
- DB version stored in `schema_versions` table, auto-upgrade on startup

---

## 9. Monitoring & Health

### Built-in Health Check
```
$ python cmd/kbd.py health

🧠 Knowledge Base Dashboard — Health Check
✅ SQLite database: 2.4 MB, 142 repos, 37 experiments
✅ Last scan: 2h ago (stale > 6h)
⚠️ 3 repos marked as error (permissions issues)
✅ Pattern engine: 12 patterns detected
✅ Suggestion queue: 5 pending
📊 DB query avg: 12ms (p50), 45ms (p95)
```

### Logging
```python
# Structured logging with JSON output for machine parsing
import structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# Levels: debug (pattern details), info (scan progress), warn (skips), error (crashes)
```

### Metrics (Internal)
| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Scan duration | Timer per scan | > 60s |
| DB size | `PRAGMA page_count` | > 100MB |
| Error rate (per scan) | ScanError count | > 20% |
| TUI FPS | Textual frame timer | < 30 |
| Suggestion accuracy | User feedback (up/down) | < 40% |
