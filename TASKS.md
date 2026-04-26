# Knowledge Base Dashboard — Atomic Task List

> Every task is self-contained. Read the task fully, execute each step exactly,
> run the verification command, and only proceed when it passes.
> Small models: do NOT skip verifications. If one fails, fix it before moving on.

Reference docs (read these first):
- `PLAN.md` — architecture and goals
- `IMPLEMENTATION.md` — schemas, APIs, test strategy, CI

---

## TASK-001: Initialize uv project and pyproject.toml

**Depends on:** nothing
**Files created:** `pyproject.toml`, `.python-version`, `.gitignore`

### Steps

```bash
cd ~/projects/knowledge-base-dashboard
uv init --name knowledge-base-dashboard --python 3.12
```

Replace the generated `pyproject.toml` with this exact content:

```toml
[project]
name = "knowledge-base-dashboard"
version = "0.1.0"
description = "Interactive TUI dashboard for git history and experiment analytics"
requires-python = ">=3.12"
dependencies = [
    "textual>=0.55.0",
    "gitpython>=3.1.40",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.2.0",
    "plotly>=5.20.0",
    "structlog>=24.1.0",
    "typer>=0.12.0",
    "rich>=13.7.0",
    "tomli>=2.0.1",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.1.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=5.0.0",
    "ruff>=0.4.0",
    "mypy>=1.9.0",
]

[project.scripts]
kbd = "cmd.kbd:app"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP"]

[tool.mypy]
python_version = "3.12"
strict = false
ignore_missing_imports = true
```

Create `.python-version`:
```
3.12
```

Create `.gitignore`:
```
.venv/
__pycache__/
*.pyc
*.db
*.prof
.coverage
dist/
*.egg-info/
.mypy_cache/
.ruff_cache/
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
python -c "import textual, gitpython, pydantic, structlog, typer; print('OK')"
```
**Done when:** prints `OK` with no errors.

---

## TASK-002: Create full directory skeleton

**Depends on:** TASK-001
**Files created:** all package directories + `__init__.py` files

### Steps

```bash
cd ~/projects/knowledge-base-dashboard
mkdir -p cmd core models ui/tabs ui/components export tests/unit tests/integration tests/fixtures/synthetic_repo tests/fixtures/mixed_stack_repo tests/fixtures/empty_repo .github/workflows
touch cmd/__init__.py
touch core/__init__.py
touch models/__init__.py
touch ui/__init__.py ui/tabs/__init__.py ui/components/__init__.py
touch export/__init__.py
touch tests/__init__.py tests/unit/__init__.py tests/integration/__init__.py
```

Create `tests/conftest.py`:
```python
import pytest
from pathlib import Path

FIXTURES_DIR = Path(__file__).parent / "fixtures"
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
python -c "
from pathlib import Path
required = [
    'cmd/__init__.py', 'core/__init__.py', 'models/__init__.py',
    'ui/__init__.py', 'ui/tabs/__init__.py', 'ui/components/__init__.py',
    'export/__init__.py', 'tests/conftest.py',
    'tests/fixtures/synthetic_repo', 'tests/fixtures/empty_repo',
]
for p in required:
    assert Path(p).exists(), f'Missing: {p}'
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-003: Create config.toml with documented defaults

**Depends on:** TASK-002
**Files created:** `config.toml`

### Steps

Create `config.toml`:
```toml
[scan]
# Directories to scan for git repositories (glob patterns supported)
paths = ["~/projects"]
# Patterns to exclude entirely from scanning
exclude = ["**/.venv/**", "**/node_modules/**", "**/.git/**"]
# Maximum depth to recurse when searching for .git directories
max_depth = 5

[database]
# SQLite database file path (relative to project or absolute)
path = "kbd.db"

[autoresearch]
# Filename to search for experiment logs
filename = "autoresearch.jsonl"

[ui]
# TUI color theme: "dark" or "light"
theme = "dark"
# Number of repos to show on overview panel
overview_repo_limit = 10

[export]
# Default output directory for HTML exports
output_dir = "exports"
```

Create `core/config.py`:
```python
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
import tomllib


class ScanConfig(BaseSettings):
    paths: list[str] = Field(default=["~/projects"])
    exclude: list[str] = Field(default=["**/.venv/**", "**/node_modules/**"])
    max_depth: int = 5


class DBConfig(BaseSettings):
    path: str = "kbd.db"


class UIConfig(BaseSettings):
    theme: str = "dark"
    overview_repo_limit: int = 10


class AppConfig(BaseSettings):
    scan: ScanConfig = Field(default_factory=ScanConfig)
    database: DBConfig = Field(default_factory=DBConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    @classmethod
    def from_toml(cls, path: Path = Path("config.toml")) -> "AppConfig":
        if not path.exists():
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.model_fields})
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "from core.config import AppConfig; c = AppConfig.from_toml(); print(c.scan.paths)"
```
**Done when:** prints `['~/projects']` with no errors.

---

## TASK-004: Define autoresearch.jsonl format and create fixture

**Depends on:** TASK-002
**Files created:** `tests/fixtures/sample_autoresearch.jsonl`, `tests/fixtures/large_jsonl.jsonl`, `docs/autoresearch_format.md`

### Steps

Create `docs/` directory:
```bash
mkdir -p ~/projects/knowledge-base-dashboard/docs
```

Create `docs/autoresearch_format.md`:
```markdown
# Autoresearch JSONL Format

Each line is a JSON object representing one experiment run.

## Required Fields
- `session`: string — experiment session name (e.g. "bundle_size_opt")
- `metric`: string — metric being optimized (e.g. "bundle_size_kb")
- `unit`: string — unit of metric (e.g. "KB", "ms", "requests/s")
- `direction`: "lower" | "higher" — whether lower or higher is better
- `run`: integer — sequential run number within the session
- `value`: float — measured metric value for this run
- `status`: "keep" | "discard" | "crash" | "checks_failed"
- `description`: string — short description of what was tried
- `timestamp`: ISO-8601 datetime string

## Optional Fields
- `commit`: string — git commit SHA if applicable
- `extra_metrics`: object — additional measured metrics
- `duration_ms`: integer — how long the run took
```

Create `tests/fixtures/sample_autoresearch.jsonl` (10 lines, 2 sessions):
```json
{"session":"bundle_size_opt","metric":"bundle_size_kb","unit":"KB","direction":"lower","run":1,"value":892.3,"status":"keep","description":"baseline measurement","timestamp":"2024-01-10T09:00:00Z"}
{"session":"bundle_size_opt","metric":"bundle_size_kb","unit":"KB","direction":"lower","run":2,"value":845.1,"status":"keep","description":"removed lodash, use native","timestamp":"2024-01-10T09:30:00Z"}
{"session":"bundle_size_opt","metric":"bundle_size_kb","unit":"KB","direction":"lower","run":3,"value":843.7,"status":"keep","description":"tree-shaking enabled","timestamp":"2024-01-10T10:00:00Z"}
{"session":"bundle_size_opt","metric":"bundle_size_kb","unit":"KB","direction":"lower","run":4,"value":899.1,"status":"discard","description":"css-in-js experiment failed","timestamp":"2024-01-10T10:30:00Z"}
{"session":"bundle_size_opt","metric":"bundle_size_kb","unit":"KB","direction":"lower","run":5,"value":820.5,"status":"keep","description":"dynamic imports for routes","timestamp":"2024-01-10T11:00:00Z"}
{"session":"api_latency_opt","metric":"p95_latency_ms","unit":"ms","direction":"lower","run":1,"value":245.0,"status":"keep","description":"baseline p95 latency","timestamp":"2024-01-15T09:00:00Z"}
{"session":"api_latency_opt","metric":"p95_latency_ms","unit":"ms","direction":"lower","run":2,"value":198.0,"status":"keep","description":"added redis cache layer","timestamp":"2024-01-15T09:45:00Z"}
{"session":"api_latency_opt","metric":"p95_latency_ms","unit":"ms","direction":"lower","run":3,"value":0.0,"status":"crash","description":"connection pool exhausted","timestamp":"2024-01-15T10:30:00Z"}
{"session":"api_latency_opt","metric":"p95_latency_ms","unit":"ms","direction":"lower","run":4,"value":185.0,"status":"keep","description":"tuned pool size to 20","timestamp":"2024-01-15T11:00:00Z"}
{"session":"api_latency_opt","metric":"p95_latency_ms","unit":"ms","direction":"lower","run":5,"value":172.0,"status":"keep","description":"query index added","timestamp":"2024-01-15T11:30:00Z"}
```

Generate `tests/fixtures/large_jsonl.jsonl` (1000 lines for stress tests):
```python
# Run this script once to generate the fixture:
# python tests/fixtures/generate_large_jsonl.py
```

Create `tests/fixtures/generate_large_jsonl.py`:
```python
import json
import random
from pathlib import Path

random.seed(42)
out = Path(__file__).parent / "large_jsonl.jsonl"
lines = []
for i in range(1000):
    session = f"session_{i // 100}"
    lines.append(json.dumps({
        "session": session,
        "metric": "perf_score",
        "unit": "points",
        "direction": "higher",
        "run": i % 100 + 1,
        "value": round(random.uniform(50, 100), 2),
        "status": random.choice(["keep", "keep", "keep", "discard", "crash"]),
        "description": f"run {i} experiment",
        "timestamp": f"2024-0{(i % 9)+1}-10T09:00:00Z",
    }))
out.write_text("\n".join(lines))
print(f"Generated {len(lines)} lines")
```

```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python tests/fixtures/generate_large_jsonl.py
```

Create `tests/fixtures/synthetic_repo/.gitignore`:
```
*.pyc
```

Create a real git repo in `tests/fixtures/synthetic_repo/`:
```bash
cd ~/projects/knowledge-base-dashboard/tests/fixtures/synthetic_repo
git init
git config user.email "test@test.com"
git config user.name "Test User"
echo '{"name":"synthetic-app","version":"1.0.0","dependencies":{"react":"^18.0.0"}}' > package.json
echo "# Synthetic App" > README.md
mkdir -p src
echo "console.log('hello');" > src/index.js
git add .
git commit -m "feat: initial commit"
echo "console.log('world');" >> src/index.js
git add .
git commit -m "feat: add world log"
```

Create empty repo fixture:
```bash
cd ~/projects/knowledge-base-dashboard/tests/fixtures/empty_repo
git init
git config user.email "test@test.com"
git config user.name "Test User"
```

Create mixed stack repo:
```bash
mkdir -p ~/projects/knowledge-base-dashboard/tests/fixtures/mixed_stack_repo
cd ~/projects/knowledge-base-dashboard/tests/fixtures/mixed_stack_repo
git init
git config user.email "test@test.com"
git config user.name "Test User"
echo '{"name":"mixed","dependencies":{"react":"18"}}' > package.json
cat > pyproject.toml << 'EOF'
[project]
name = "mixed"
dependencies = ["fastapi"]
EOF
echo "# Mixed" > README.md
git add .
git commit -m "initial"
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
python -c "
from pathlib import Path
lines = Path('tests/fixtures/sample_autoresearch.jsonl').read_text().strip().splitlines()
assert len(lines) == 10, f'expected 10 lines, got {len(lines)}'
large = Path('tests/fixtures/large_jsonl.jsonl').read_text().strip().splitlines()
assert len(large) == 1000
import subprocess
result = subprocess.run(['git','log','--oneline'], capture_output=True, cwd='tests/fixtures/synthetic_repo')
assert result.returncode == 0
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-005: Implement SQLite database module (db.py)

**Depends on:** TASK-003
**Files created:** `core/db.py`

### Steps

Create `core/db.py` with this exact content:

```python
import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
from typing import Any


DB_PATH = Path("kbd.db")


def get_connection(path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def db_conn(path: Path = DB_PATH):
    conn = get_connection(path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables(path: Path = DB_PATH) -> None:
    with db_conn(path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS repos (
                id              TEXT PRIMARY KEY,
                path            TEXT UNIQUE NOT NULL,
                name            TEXT NOT NULL,
                description     TEXT,
                url             TEXT,
                created_at      DATETIME,
                last_active     DATETIME,
                total_commits   INTEGER DEFAULT 0,
                branch_count    INTEGER DEFAULT 1,
                primary_lang    TEXT,
                stack_json      TEXT,
                status          TEXT DEFAULT 'active',
                scanned_at      DATETIME
            );

            CREATE TABLE IF NOT EXISTS experiments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_id         TEXT REFERENCES repos(id),
                jsonl_path      TEXT NOT NULL,
                session_name    TEXT,
                metric_name     TEXT,
                metric_unit     TEXT,
                direction       TEXT,
                total_runs      INTEGER DEFAULT 0,
                kept_runs       INTEGER DEFAULT 0,
                discarded_runs  INTEGER DEFAULT 0,
                crashed_runs    INTEGER DEFAULT 0,
                best_metric     REAL,
                noise_floor     REAL,
                started_at      DATETIME,
                completed_at    DATETIME
            );

            CREATE TABLE IF NOT EXISTS experiment_runs (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id   INTEGER REFERENCES experiments(id),
                commit          TEXT,
                metric          REAL,
                status          TEXT,
                description     TEXT,
                extra_metrics   TEXT,
                duration_ms     INTEGER,
                run_order       INTEGER,
                created_at      DATETIME
            );

            CREATE TABLE IF NOT EXISTS patterns (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                trigger         TEXT NOT NULL,
                action          TEXT NOT NULL,
                frequency       INTEGER DEFAULT 1,
                confidence      REAL DEFAULT 0.0,
                first_seen      DATETIME,
                last_seen       DATETIME
            );

            CREATE TABLE IF NOT EXISTS insights (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id      INTEGER REFERENCES patterns(id),
                suggestion      TEXT NOT NULL,
                urgency         TEXT DEFAULT 'low',
                resolved        INTEGER DEFAULT 0,
                created_at      DATETIME
            );

            CREATE INDEX IF NOT EXISTS idx_repos_last_active ON repos(last_active);
            CREATE INDEX IF NOT EXISTS idx_repos_primary_lang ON repos(primary_lang);
            CREATE INDEX IF NOT EXISTS idx_experiments_repo ON experiments(repo_id);
            CREATE INDEX IF NOT EXISTS idx_runs_experiment ON experiment_runs(experiment_id);
            CREATE INDEX IF NOT EXISTS idx_runs_status ON experiment_runs(status);
        """)


# --- Repos CRUD ---

def upsert_repo(conn: sqlite3.Connection, repo: dict[str, Any]) -> None:
    conn.execute("""
        INSERT INTO repos (id, path, name, description, url, created_at, last_active,
            total_commits, branch_count, primary_lang, stack_json, status, scanned_at)
        VALUES (:id,:path,:name,:description,:url,:created_at,:last_active,
            :total_commits,:branch_count,:primary_lang,:stack_json,:status,:scanned_at)
        ON CONFLICT(id) DO UPDATE SET
            last_active=excluded.last_active,
            total_commits=excluded.total_commits,
            primary_lang=excluded.primary_lang,
            stack_json=excluded.stack_json,
            status=excluded.status,
            scanned_at=excluded.scanned_at
    """, repo)


def get_all_repos(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM repos ORDER BY last_active DESC").fetchall()


def get_repo(conn: sqlite3.Connection, repo_id: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM repos WHERE id=?", (repo_id,)).fetchone()


# --- Experiments CRUD ---

def insert_experiment(conn: sqlite3.Connection, exp: dict[str, Any]) -> int:
    cur = conn.execute("""
        INSERT INTO experiments (repo_id, jsonl_path, session_name, metric_name, metric_unit,
            direction, total_runs, kept_runs, discarded_runs, crashed_runs,
            best_metric, noise_floor, started_at, completed_at)
        VALUES (:repo_id,:jsonl_path,:session_name,:metric_name,:metric_unit,
            :direction,:total_runs,:kept_runs,:discarded_runs,:crashed_runs,
            :best_metric,:noise_floor,:started_at,:completed_at)
    """, exp)
    return cur.lastrowid


def insert_run(conn: sqlite3.Connection, run: dict[str, Any]) -> None:
    conn.execute("""
        INSERT INTO experiment_runs (experiment_id, commit, metric, status, description,
            extra_metrics, duration_ms, run_order, created_at)
        VALUES (:experiment_id,:commit,:metric,:status,:description,
            :extra_metrics,:duration_ms,:run_order,:created_at)
    """, run)


# --- Patterns CRUD ---

def upsert_pattern(conn: sqlite3.Connection, trigger: str, action: str,
                   confidence: float) -> int:
    existing = conn.execute(
        "SELECT id, frequency FROM patterns WHERE trigger=? AND action=?",
        (trigger, action)
    ).fetchone()
    now = datetime.utcnow().isoformat()
    if existing:
        conn.execute(
            "UPDATE patterns SET frequency=frequency+1, confidence=?, last_seen=? WHERE id=?",
            (confidence, now, existing["id"])
        )
        return existing["id"]
    cur = conn.execute(
        "INSERT INTO patterns (trigger, action, confidence, first_seen, last_seen) VALUES (?,?,?,?,?)",
        (trigger, action, confidence, now, now)
    )
    return cur.lastrowid


def get_all_patterns(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM patterns ORDER BY frequency DESC").fetchall()


def insert_insight(conn: sqlite3.Connection, pattern_id: int,
                   suggestion: str, urgency: str = "low") -> None:
    conn.execute(
        "INSERT INTO insights (pattern_id, suggestion, urgency, created_at) VALUES (?,?,?,?)",
        (pattern_id, suggestion, urgency, datetime.utcnow().isoformat())
    )


def get_pending_insights(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM insights WHERE resolved=0 ORDER BY urgency DESC, created_at DESC"
    ).fetchall()
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "
from core.db import create_tables, db_conn, upsert_repo, get_all_repos
import tempfile, os
from pathlib import Path
with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    db = Path(f.name)
create_tables(db)
with db_conn(db) as conn:
    upsert_repo(conn, {
        'id': 'test1', 'path': '/tmp/test', 'name': 'test', 'description': None,
        'url': None, 'created_at': None, 'last_active': '2024-01-01',
        'total_commits': 5, 'branch_count': 1, 'primary_lang': 'Python',
        'stack_json': '[]', 'status': 'active', 'scanned_at': '2024-01-01'
    })
with db_conn(db) as conn:
    repos = get_all_repos(conn)
    assert len(repos) == 1
    assert repos[0]['name'] == 'test'
os.unlink(db)
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-006: Implement Pydantic data models

**Depends on:** TASK-002
**Files created:** `models/repo.py`, `models/experiment.py`, `models/pattern.py`, `models/insight.py`

### Steps

Create `models/repo.py`:
```python
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from pathlib import Path


class RepoModel(BaseModel):
    id: str
    path: str
    name: str
    description: str | None = None
    url: str | None = None
    created_at: datetime | None = None
    last_active: datetime | None = None
    total_commits: int = 0
    branch_count: int = 1
    primary_lang: str | None = None
    stack: list[str] = Field(default_factory=list)
    status: str = "active"
    scanned_at: datetime | None = None

    @computed_field
    @property
    def is_active(self) -> bool:
        if not self.last_active:
            return False
        delta = datetime.utcnow() - self.last_active.replace(tzinfo=None)
        return delta.days < 90

    def to_db_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "path": self.path,
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "total_commits": self.total_commits,
            "branch_count": self.branch_count,
            "primary_lang": self.primary_lang,
            "stack_json": json.dumps(self.stack),
            "status": self.status,
            "scanned_at": self.scanned_at.isoformat() if self.scanned_at else None,
        }
```

Create `models/experiment.py`:
```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class ExperimentRun(BaseModel):
    run_order: int
    value: float
    status: Literal["keep", "discard", "crash", "checks_failed"]
    description: str
    commit: str | None = None
    extra_metrics: dict = Field(default_factory=dict)
    duration_ms: int | None = None
    timestamp: datetime | None = None


class ExperimentSession(BaseModel):
    session_name: str
    metric_name: str
    metric_unit: str
    direction: Literal["lower", "higher"]
    jsonl_path: str
    runs: list[ExperimentRun] = Field(default_factory=list)

    @property
    def total_runs(self) -> int:
        return len(self.runs)

    @property
    def kept_runs(self) -> int:
        return sum(1 for r in self.runs if r.status == "keep")

    @property
    def discarded_runs(self) -> int:
        return sum(1 for r in self.runs if r.status == "discard")

    @property
    def crashed_runs(self) -> int:
        return sum(1 for r in self.runs if r.status == "crash")

    @property
    def kept_values(self) -> list[float]:
        return [r.value for r in self.runs if r.status == "keep"]

    @property
    def best_metric(self) -> float | None:
        if not self.kept_values:
            return None
        return min(self.kept_values) if self.direction == "lower" else max(self.kept_values)
```

Create `models/pattern.py`:
```python
from pydantic import BaseModel
from datetime import datetime


class PatternModel(BaseModel):
    id: int | None = None
    trigger: str
    action: str
    frequency: int = 1
    confidence: float = 0.0
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    repo_examples: list[str] = []
```

Create `models/insight.py`:
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Literal


class InsightModel(BaseModel):
    id: int | None = None
    pattern_id: int
    suggestion: str
    urgency: Literal["low", "medium", "high"] = "low"
    resolved: bool = False
    created_at: datetime | None = None
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "
from models.repo import RepoModel
from models.experiment import ExperimentSession, ExperimentRun
from models.pattern import PatternModel
from models.insight import InsightModel
from datetime import datetime

r = RepoModel(id='x', path='/tmp', name='test', last_active=datetime(2025,1,1))
assert r.is_active == False

run = ExperimentRun(run_order=1, value=100.0, status='keep', description='test')
sess = ExperimentSession(
    session_name='s1', metric_name='m', metric_unit='ms',
    direction='lower', jsonl_path='/tmp/f.jsonl', runs=[run]
)
assert sess.kept_runs == 1
assert sess.best_metric == 100.0
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-007: Implement git_scanner.py

**Depends on:** TASK-004, TASK-006
**Files created:** `core/git_scanner.py`

### Steps

Create `core/git_scanner.py`:
```python
import hashlib
import subprocess
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from models.repo import RepoModel


MANIFEST_STACK_MAP = {
    "package.json": lambda d: _parse_npm_stack(d),
    "pyproject.toml": lambda d: ["Python"],
    "Cargo.toml": lambda d: ["Rust"],
    "go.mod": lambda d: ["Go"],
    "Gemfile": lambda d: ["Ruby"],
    "pom.xml": lambda d: ["Java", "Maven"],
    "build.gradle": lambda d: ["Java", "Gradle"],
}

LANG_EXT_MAP = {
    ".py": "Python", ".rs": "Rust", ".go": "Go", ".ts": "TypeScript",
    ".tsx": "TypeScript", ".js": "JavaScript", ".jsx": "JavaScript",
    ".rb": "Ruby", ".java": "Java", ".kt": "Kotlin", ".swift": "Swift",
    ".c": "C", ".cpp": "C++", ".h": "C/C++", ".cs": "C#",
    ".ex": "Elixir", ".exs": "Elixir",
}


def _repo_id(path: Path) -> str:
    return hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:16]


def _run_git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(cwd)] + args,
        capture_output=True, text=True, timeout=15
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def _parse_npm_stack(content: str) -> list[str]:
    try:
        data = json.loads(content)
        deps = list(data.get("dependencies", {}).keys()) + list(data.get("devDependencies", {}).keys())
        stack = ["JavaScript"]
        known = {
            "react": "React", "vue": "Vue", "svelte": "Svelte",
            "next": "Next.js", "nuxt": "Nuxt", "typescript": "TypeScript",
            "vite": "Vite", "webpack": "Webpack", "tailwindcss": "Tailwind CSS",
        }
        for dep in deps:
            for key, label in known.items():
                if key in dep.lower() and label not in stack:
                    stack.append(label)
        return stack
    except Exception:
        return ["JavaScript"]


def detect_languages(repo_path: Path) -> dict[str, float]:
    counts: dict[str, int] = {}
    total = 0
    for f in repo_path.rglob("*"):
        if f.is_file() and ".git" not in f.parts:
            lang = LANG_EXT_MAP.get(f.suffix.lower())
            if lang:
                counts[lang] = counts.get(lang, 0) + 1
                total += 1
    if total == 0:
        return {}
    return {lang: round(count / total * 100, 1) for lang, count in
            sorted(counts.items(), key=lambda x: -x[1])}


def detect_stack(repo_path: Path) -> list[str]:
    stack: list[str] = []
    for manifest, parser in MANIFEST_STACK_MAP.items():
        manifest_path = repo_path / manifest
        if manifest_path.exists():
            content = manifest_path.read_text(errors="replace")
            items = parser(content)
            for item in items:
                if item not in stack:
                    stack.append(item)
    return stack


def scan_repo(path: Path) -> RepoModel | None:
    git_dir = path / ".git"
    if not git_dir.exists():
        return None

    try:
        repo_id = _repo_id(path)
        name = path.name

        first_commit_str = _run_git(["log", "--reverse", "--format=%cI", "--max-count=1"], path)
        last_commit_str = _run_git(["log", "--format=%cI", "--max-count=1"], path)
        total_str = _run_git(["rev-list", "--count", "HEAD"], path)
        branch_str = _run_git(["branch", "--list"], path)

        first_commit = datetime.fromisoformat(first_commit_str) if first_commit_str else None
        last_commit = datetime.fromisoformat(last_commit_str) if last_commit_str else None
        total_commits = int(total_str) if total_str.isdigit() else 0
        branch_count = len([b for b in branch_str.splitlines() if b.strip()])

        langs = detect_languages(path)
        primary_lang = list(langs.keys())[0] if langs else None
        stack = detect_stack(path)

        remote = _run_git(["remote", "get-url", "origin"], path) or None

        readme_path = next((path / f for f in ["README.md", "readme.md", "README.txt"]
                            if (path / f).exists()), None)
        description = None
        if readme_path:
            lines = readme_path.read_text(errors="replace").splitlines()
            for line in lines:
                stripped = line.strip().lstrip("#").strip()
                if stripped and not stripped.startswith("!"):
                    description = stripped[:200]
                    break

        return RepoModel(
            id=repo_id,
            path=str(path.resolve()),
            name=name,
            description=description,
            url=remote,
            created_at=first_commit,
            last_active=last_commit,
            total_commits=total_commits,
            branch_count=max(branch_count, 1),
            primary_lang=primary_lang,
            stack=stack,
            status="active",
            scanned_at=datetime.utcnow(),
        )
    except Exception as e:
        return None


def scan_directory(root: Path, max_depth: int = 5) -> list[RepoModel]:
    repos: list[RepoModel] = []
    root = root.expanduser().resolve()
    if not root.exists():
        return repos

    def _walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        if (current / ".git").exists():
            repo = scan_repo(current)
            if repo:
                repos.append(repo)
            return
        try:
            for child in sorted(current.iterdir()):
                if child.is_dir() and not child.name.startswith("."):
                    _walk(child, depth + 1)
        except PermissionError:
            pass

    _walk(root, 0)
    return repos
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "
from core.git_scanner import scan_repo, scan_directory
from pathlib import Path

# Test single repo scan
repo = scan_repo(Path('tests/fixtures/synthetic_repo'))
assert repo is not None, 'scan_repo returned None'
assert repo.name == 'synthetic_repo'
assert repo.total_commits >= 2
assert 'JavaScript' in repo.stack or repo.primary_lang is not None

# Test directory scan
repos = scan_directory(Path('tests/fixtures'))
assert len(repos) >= 1
print(f'Found {len(repos)} repos. OK')
"
```
**Done when:** prints `Found N repos. OK`.

---

## TASK-008: Write unit tests for git_scanner

**Depends on:** TASK-007
**Files created:** `tests/unit/test_git_scanner.py`

### Steps

Create `tests/unit/test_git_scanner.py`:
```python
import pytest
from pathlib import Path
from tests.conftest import FIXTURES_DIR
from core.git_scanner import scan_repo, scan_directory, detect_languages, detect_stack


def test_scan_repo_returns_model():
    repo = scan_repo(FIXTURES_DIR / "synthetic_repo")
    assert repo is not None
    assert repo.name == "synthetic_repo"
    assert repo.total_commits >= 2
    assert repo.id is not None
    assert len(repo.id) == 16


def test_scan_repo_empty_returns_model():
    repo = scan_repo(FIXTURES_DIR / "empty_repo")
    # Empty repo (no commits) may return None or model with 0 commits
    # Either is acceptable — just must not raise
    assert repo is None or repo.total_commits == 0


def test_scan_repo_non_git_returns_none(tmp_path):
    repo = scan_repo(tmp_path)
    assert repo is None


def test_scan_repo_id_is_stable():
    r1 = scan_repo(FIXTURES_DIR / "synthetic_repo")
    r2 = scan_repo(FIXTURES_DIR / "synthetic_repo")
    assert r1 is not None and r2 is not None
    assert r1.id == r2.id


def test_detect_languages_synthetic_repo():
    langs = detect_languages(FIXTURES_DIR / "synthetic_repo")
    assert "JavaScript" in langs
    assert all(0 < v <= 100 for v in langs.values())


def test_detect_stack_npm():
    stack = detect_stack(FIXTURES_DIR / "synthetic_repo")
    assert "JavaScript" in stack or "React" in stack


def test_detect_stack_mixed():
    stack = detect_stack(FIXTURES_DIR / "mixed_stack_repo")
    assert len(stack) >= 2  # both Python and JavaScript detected


def test_scan_directory_finds_repos():
    repos = scan_directory(FIXTURES_DIR)
    names = [r.name for r in repos]
    assert "synthetic_repo" in names


def test_scan_directory_nonexistent_returns_empty():
    repos = scan_directory(Path("/nonexistent/path/that/does/not/exist"))
    assert repos == []
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -m pytest tests/unit/test_git_scanner.py -v
```
**Done when:** all tests pass (PASSED), no FAILED or ERROR.

---

## TASK-009: Implement experiment_parser.py

**Depends on:** TASK-004, TASK-006
**Files created:** `core/experiment_parser.py`

### Steps

Create `core/experiment_parser.py`:
```python
import json
import math
from pathlib import Path
from datetime import datetime

from models.experiment import ExperimentSession, ExperimentRun


def parse_jsonl(path: Path) -> list[ExperimentSession]:
    """Parse an autoresearch.jsonl file into ExperimentSession objects."""
    sessions: dict[str, dict] = {}
    
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue

            session_name = record.get("session", "unknown")
            if session_name not in sessions:
                sessions[session_name] = {
                    "session_name": session_name,
                    "metric_name": record.get("metric", "value"),
                    "metric_unit": record.get("unit", ""),
                    "direction": record.get("direction", "lower"),
                    "jsonl_path": str(path),
                    "runs": [],
                }

            ts = record.get("timestamp")
            try:
                parsed_ts = datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None
            except (ValueError, AttributeError):
                parsed_ts = None

            run = ExperimentRun(
                run_order=record.get("run", line_num),
                value=float(record.get("value", 0)),
                status=record.get("status", "keep"),
                description=record.get("description", ""),
                commit=record.get("commit"),
                extra_metrics=record.get("extra_metrics", {}),
                duration_ms=record.get("duration_ms"),
                timestamp=parsed_ts,
            )
            sessions[session_name]["runs"].append(run)

    return [ExperimentSession(**data) for data in sessions.values()]


def find_all_jsonl(root: Path, filename: str = "autoresearch.jsonl") -> list[Path]:
    """Recursively find all autoresearch.jsonl files under root."""
    root = root.expanduser().resolve()
    if not root.exists():
        return []
    return sorted(root.rglob(filename))


def calculate_noise_floor(values: list[float]) -> float:
    """
    Estimate the noise floor as 1.5 * median absolute deviation.
    Returns 0.0 for fewer than 3 values.
    """
    if len(values) < 3:
        return 0.0
    sorted_vals = sorted(values)
    median = sorted_vals[len(sorted_vals) // 2]
    mad = sorted([abs(v - median) for v in values])[len(values) // 2]
    return round(1.5 * mad, 4)


def calculate_confidence(improvement: float, noise: float) -> float:
    """
    Confidence = improvement / noise, clamped to [0.0, 1.0].
    If noise is 0, return 1.0 when improvement > 0, else 0.0.
    """
    if noise == 0:
        return 1.0 if improvement > 0 else 0.0
    raw = improvement / noise
    return round(max(0.0, min(1.0, raw / 3.0)), 4)
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "
from core.experiment_parser import parse_jsonl, calculate_noise_floor, calculate_confidence
from pathlib import Path

sessions = parse_jsonl(Path('tests/fixtures/sample_autoresearch.jsonl'))
assert len(sessions) == 2, f'expected 2 sessions, got {len(sessions)}'

bundle = next(s for s in sessions if s.session_name == 'bundle_size_opt')
assert bundle.total_runs == 5
assert bundle.kept_runs == 4
assert bundle.crashed_runs == 0
assert bundle.discarded_runs == 1
assert bundle.best_metric == 820.5

noise = calculate_noise_floor([100.0, 102.0, 98.0, 101.0, 99.0])
assert noise > 0, 'noise floor should be positive'

conf = calculate_confidence(10.0, 5.0)
assert 0.0 <= conf <= 1.0

print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-010: Write unit tests for experiment_parser

**Depends on:** TASK-009
**Files created:** `tests/unit/test_experiment_parser.py`

### Steps

Create `tests/unit/test_experiment_parser.py`:
```python
import pytest
from pathlib import Path
from tests.conftest import FIXTURES_DIR
from core.experiment_parser import (
    parse_jsonl, find_all_jsonl, calculate_noise_floor, calculate_confidence
)


def test_parse_sample_returns_two_sessions():
    sessions = parse_jsonl(FIXTURES_DIR / "sample_autoresearch.jsonl")
    assert len(sessions) == 2


def test_parse_bundle_session_stats():
    sessions = parse_jsonl(FIXTURES_DIR / "sample_autoresearch.jsonl")
    bundle = next(s for s in sessions if s.session_name == "bundle_size_opt")
    assert bundle.total_runs == 5
    assert bundle.kept_runs == 4
    assert bundle.discarded_runs == 1
    assert bundle.crashed_runs == 0
    assert bundle.metric_name == "bundle_size_kb"
    assert bundle.direction == "lower"


def test_best_metric_is_minimum_kept():
    sessions = parse_jsonl(FIXTURES_DIR / "sample_autoresearch.jsonl")
    bundle = next(s for s in sessions if s.session_name == "bundle_size_opt")
    assert bundle.best_metric == 820.5


def test_parse_large_jsonl():
    sessions = parse_jsonl(FIXTURES_DIR / "large_jsonl.jsonl")
    assert len(sessions) == 10  # 1000 runs / 100 per session


def test_parse_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_jsonl(Path("/nonexistent/file.jsonl"))


def test_noise_floor_with_stable_values():
    noise = calculate_noise_floor([100.0, 100.1, 99.9, 100.2, 99.8])
    assert noise < 1.0


def test_noise_floor_with_volatile_values():
    noise = calculate_noise_floor([50.0, 100.0, 75.0, 120.0, 30.0])
    assert noise > 5.0


def test_noise_floor_too_few_values():
    assert calculate_noise_floor([1.0, 2.0]) == 0.0


def test_confidence_no_noise():
    assert calculate_confidence(5.0, 0.0) == 1.0


def test_confidence_clamped():
    assert 0.0 <= calculate_confidence(100.0, 1.0) <= 1.0
    assert 0.0 <= calculate_confidence(0.0, 10.0) <= 1.0


def test_find_all_jsonl(tmp_path):
    (tmp_path / "a.jsonl").write_text("")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "autoresearch.jsonl").write_text("")
    results = find_all_jsonl(tmp_path, "autoresearch.jsonl")
    assert len(results) == 1
    assert results[0].name == "autoresearch.jsonl"
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -m pytest tests/unit/test_experiment_parser.py -v
```
**Done when:** all tests pass.

---

## TASK-011: Implement pattern_engine.py and insight_engine.py

**Depends on:** TASK-009
**Files created:** `core/pattern_engine.py`, `core/insight_engine.py`

### Steps

Create `core/pattern_engine.py`:
```python
from collections import Counter
from models.experiment import ExperimentSession
from models.pattern import PatternModel
from datetime import datetime


def detect_patterns(sessions: list[ExperimentSession]) -> list[PatternModel]:
    """
    Detect recurring patterns: when optimizing METRIC, always try ACTION first.
    Simple approach: find (metric_name, first_kept_description) pairs that appear
    across multiple sessions.
    """
    patterns: list[PatternModel] = []
    
    # Pattern 1: "when optimizing X, first action is Y"
    first_actions: Counter[tuple[str, str]] = Counter()
    for session in sessions:
        kept = [r for r in session.runs if r.status == "keep"]
        if kept:
            trigger = f"optimizing {session.metric_name}"
            action = kept[0].description[:60] if kept[0].description else "unknown"
            first_actions[(trigger, action)] += 1

    for (trigger, action), freq in first_actions.items():
        if freq >= 2:
            confidence = min(1.0, freq / 5.0)
            patterns.append(PatternModel(
                trigger=trigger,
                action=action,
                frequency=freq,
                confidence=confidence,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
            ))

    # Pattern 2: "always discards runs when description contains X"
    discard_desc_counter: Counter[str] = Counter()
    for session in sessions:
        for run in session.runs:
            if run.status == "discard" and run.description:
                key = run.description[:40]
                discard_desc_counter[key] += 1

    for desc, count in discard_desc_counter.items():
        if count >= 2:
            patterns.append(PatternModel(
                trigger="attempting optimization",
                action=f"discarded: {desc}",
                frequency=count,
                confidence=min(1.0, count / 4.0),
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
            ))

    return patterns
```

Create `core/insight_engine.py`:
```python
from models.pattern import PatternModel
from models.insight import InsightModel


SUGGESTION_TEMPLATES = {
    "optimizing bundle_size": "Have you tried code splitting with dynamic imports() for route-based chunking?",
    "optimizing p95_latency": "Consider connection pooling and query caching if you haven't tried them yet.",
    "optimizing memory": "Profile heap allocations with py-spy or valgrind to find the real bottleneck.",
}


def generate_insights(patterns: list[PatternModel]) -> list[InsightModel]:
    insights: list[InsightModel] = []
    for pattern in patterns:
        if pattern.id is None:
            continue
        
        # Look for matching template
        suggestion = None
        for keyword, template in SUGGESTION_TEMPLATES.items():
            if keyword in pattern.trigger.lower():
                suggestion = template
                break
        
        if not suggestion:
            suggestion = (
                f"You frequently try '{pattern.action}' when {pattern.trigger}. "
                f"Consider exploring an alternative approach to see if you can break through the plateau."
            )
        
        urgency = "high" if pattern.frequency >= 5 else "medium" if pattern.frequency >= 3 else "low"
        
        insights.append(InsightModel(
            pattern_id=pattern.id,
            suggestion=suggestion,
            urgency=urgency,
        ))
    
    return insights
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "
from core.experiment_parser import parse_jsonl
from core.pattern_engine import detect_patterns
from core.insight_engine import generate_insights
from pathlib import Path

sessions = parse_jsonl(Path('tests/fixtures/sample_autoresearch.jsonl'))
# Add duplicate sessions to trigger pattern detection
sessions_doubled = sessions + sessions
patterns = detect_patterns(sessions_doubled)
print(f'Patterns: {len(patterns)}')

# Manually assign IDs for insight test
for i, p in enumerate(patterns):
    p.id = i + 1
insights = generate_insights(patterns)
print(f'Insights: {len(insights)}')
assert all(i.urgency in ['low','medium','high'] for i in insights)
print('OK')
"
```
**Done when:** prints patterns count, insights count, and `OK`.

---

## TASK-012: Write unit tests for pattern and insight engines

**Depends on:** TASK-011
**Files created:** `tests/unit/test_pattern_engine.py`

### Steps

Create `tests/unit/test_pattern_engine.py`:
```python
import pytest
from datetime import datetime
from models.experiment import ExperimentSession, ExperimentRun
from models.pattern import PatternModel
from core.pattern_engine import detect_patterns
from core.insight_engine import generate_insights


def make_session(name: str, metric: str, runs_data: list[tuple]) -> ExperimentSession:
    """Helper: make session from list of (value, status, description) tuples."""
    runs = [
        ExperimentRun(run_order=i+1, value=v, status=s, description=d)
        for i, (v, s, d) in enumerate(runs_data)
    ]
    return ExperimentSession(
        session_name=name, metric_name=metric, metric_unit="ms",
        direction="lower", jsonl_path="/tmp/test.jsonl", runs=runs
    )


def test_detect_patterns_requires_min_2_occurrences():
    sess = make_session("s1", "latency", [(100, "keep", "baseline")])
    patterns = detect_patterns([sess])
    # Only 1 session → no patterns (frequency < 2)
    assert all(p.frequency >= 2 for p in patterns)


def test_detect_patterns_finds_repeated_first_action():
    sessions = [
        make_session(f"s{i}", "latency", [
            (100, "keep", "try redis cache"),
            (90, "keep", "tune index"),
        ])
        for i in range(3)
    ]
    patterns = detect_patterns(sessions)
    assert len(patterns) >= 1
    triggers = [p.trigger for p in patterns]
    assert any("latency" in t for t in triggers)


def test_pattern_confidence_range():
    sessions = [
        make_session(f"s{i}", "perf", [(100, "keep", "baseline")])
        for i in range(5)
    ]
    patterns = detect_patterns(sessions)
    for p in patterns:
        assert 0.0 <= p.confidence <= 1.0


def test_generate_insights_produces_one_per_pattern():
    patterns = [
        PatternModel(id=1, trigger="optimizing bundle_size", action="remove lodash",
                     frequency=3, confidence=0.6),
        PatternModel(id=2, trigger="optimizing memory", action="reduce allocations",
                     frequency=2, confidence=0.4),
    ]
    insights = generate_insights(patterns)
    assert len(insights) == 2
    assert all(i.urgency in ["low", "medium", "high"] for i in insights)


def test_generate_insights_skips_pattern_without_id():
    pattern = PatternModel(trigger="optimizing x", action="try y", frequency=3, confidence=0.5)
    insights = generate_insights([pattern])
    assert len(insights) == 0
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -m pytest tests/unit/test_pattern_engine.py -v
```
**Done when:** all tests pass.

---

## TASK-013: Implement the Textual TUI dashboard shell

**Depends on:** TASK-006, TASK-007
**Files created:** `ui/dashboard.py`, `ui/tabs/overview.py`, `ui/tabs/repos.py`, `ui/tabs/experiments.py`, `ui/tabs/patterns.py`, `ui/tabs/timeline.py`

### Steps

Create `ui/dashboard.py`:
```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent, TabPane
from textual.binding import Binding

from ui.tabs.overview import OverviewTab
from ui.tabs.repos import ReposTab
from ui.tabs.experiments import ExperimentsTab
from ui.tabs.patterns import PatternsTab
from ui.tabs.timeline import TimelineTab


class KBDApp(App):
    """Knowledge Base Dashboard — main TUI application."""

    CSS = """
    Screen {
        background: $surface;
    }
    TabbedContent {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Overview", id="overview"):
                yield OverviewTab(db_path=self.db_path)
            with TabPane("Repos", id="repos"):
                yield ReposTab(db_path=self.db_path)
            with TabPane("Experiments", id="experiments"):
                yield ExperimentsTab(db_path=self.db_path)
            with TabPane("Patterns", id="patterns"):
                yield PatternsTab(db_path=self.db_path)
            with TabPane("Timeline", id="timeline"):
                yield TimelineTab(db_path=self.db_path)
        yield Footer()

    def action_refresh(self) -> None:
        self.notify("Refreshing data…")
        for tab in self.query("*"):
            if hasattr(tab, "refresh_data"):
                tab.refresh_data()
```

Create `ui/tabs/overview.py`:
```python
from textual.widget import Widget
from textual.widgets import Static, Label
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal
from pathlib import Path
from core.db import db_conn, get_all_repos, get_pending_insights


class OverviewTab(Widget):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Static("Loading...", id="overview-content")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        try:
            from pathlib import Path as P
            db = P(self.db_path)
            if not db.exists():
                self.query_one("#overview-content").update("No database found. Run: kbd scan")
                return
            with db_conn(db) as conn:
                repos = get_all_repos(conn)
                insights = get_pending_insights(conn)
            langs: dict[str, int] = {}
            for r in repos:
                import json
                if r["primary_lang"]:
                    langs[r["primary_lang"]] = langs.get(r["primary_lang"], 0) + 1
            lang_lines = "\n".join(
                f"  {lang:<15} {count:>3} repos"
                for lang, count in sorted(langs.items(), key=lambda x: -x[1])[:8]
            )
            active = sum(1 for r in repos if r["status"] == "active")
            text = (
                f"[bold]Knowledge Base Dashboard[/bold]\n\n"
                f"Total repos: {len(repos)}  |  Active: {active}\n"
                f"Pending insights: {len(insights)}\n\n"
                f"[bold]Top Languages:[/bold]\n{lang_lines}"
            )
            self.query_one("#overview-content").update(text)
        except Exception as e:
            self.query_one("#overview-content").update(f"Error: {e}")
```

Create `ui/tabs/repos.py`:
```python
from textual.widget import Widget
from textual.widgets import Static, DataTable
from textual.app import ComposeResult
from pathlib import Path
from core.db import db_conn, get_all_repos


class ReposTab(Widget):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield DataTable(id="repos-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("Name", "Language", "Commits", "Last Active", "Status")
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            return
        table = self.query_one(DataTable)
        table.clear()
        with db_conn(db) as conn:
            repos = get_all_repos(conn)
        for r in repos[:50]:
            last = str(r["last_active"] or "")[:10]
            table.add_row(r["name"], r["primary_lang"] or "?",
                          str(r["total_commits"]), last, r["status"])
```

Create `ui/tabs/experiments.py`:
```python
from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from pathlib import Path
from core.db import db_conn


class ExperimentsTab(Widget):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Static("", id="exp-content")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            self.query_one("#exp-content").update("No database. Run: kbd scan")
            return
        with db_conn(db) as conn:
            exps = conn.execute(
                "SELECT session_name, metric_name, total_runs, kept_runs, best_metric "
                "FROM experiments ORDER BY completed_at DESC LIMIT 20"
            ).fetchall()
        if not exps:
            self.query_one("#exp-content").update("No experiments found yet.")
            return
        lines = ["[bold]Recent Experiments[/bold]\n"]
        for e in exps:
            lines.append(
                f"  {e['session_name']:<30} {e['metric_name']:<20} "
                f"kept={e['kept_runs']}/{e['total_runs']} best={e['best_metric']}"
            )
        self.query_one("#exp-content").update("\n".join(lines))
```

Create `ui/tabs/patterns.py`:
```python
from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from pathlib import Path
from core.db import db_conn, get_all_patterns, get_pending_insights


class PatternsTab(Widget):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Static("", id="patterns-content")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            self.query_one("#patterns-content").update("No database found.")
            return
        with db_conn(db) as conn:
            patterns = get_all_patterns(conn)
            insights = get_pending_insights(conn)
        lines = [f"[bold]Detected Patterns ({len(patterns)})[/bold]\n"]
        for p in patterns[:10]:
            lines.append(f"  [{p['confidence']:.2f}] {p['trigger']} → {p['action']}")
        if insights:
            lines.append(f"\n[bold]Pending Suggestions ({len(insights)})[/bold]\n")
            for i in insights[:5]:
                lines.append(f"  [{i['urgency'].upper()}] {i['suggestion'][:80]}")
        self.query_one("#patterns-content").update("\n".join(lines))
```

Create `ui/tabs/timeline.py`:
```python
from textual.widget import Widget
from textual.widgets import Static
from textual.app import ComposeResult
from pathlib import Path
from core.db import db_conn


class TimelineTab(Widget):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Static("", id="timeline-content")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            self.query_one("#timeline-content").update("No database found.")
            return
        with db_conn(db) as conn:
            rows = conn.execute("""
                SELECT strftime('%Y-%m', last_active) as month,
                       primary_lang, COUNT(*) as count
                FROM repos
                WHERE last_active IS NOT NULL
                GROUP BY month, primary_lang
                ORDER BY month DESC
                LIMIT 30
            """).fetchall()
        if not rows:
            self.query_one("#timeline-content").update("No timeline data yet.")
            return
        lines = ["[bold]Activity Timeline (by month)[/bold]\n"]
        current_month = None
        for row in rows:
            if row["month"] != current_month:
                current_month = row["month"]
                lines.append(f"\n  [bold]{current_month}[/bold]")
            lines.append(f"    {row['primary_lang'] or 'Unknown':<15} {row['count']} repos")
        self.query_one("#timeline-content").update("\n".join(lines))
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "
from ui.dashboard import KBDApp
from ui.tabs.overview import OverviewTab
from ui.tabs.repos import ReposTab
from ui.tabs.experiments import ExperimentsTab
from ui.tabs.patterns import PatternsTab
from ui.tabs.timeline import TimelineTab
print('All UI modules import OK')
"
```
**Done when:** prints `All UI modules import OK`.

---

## TASK-014: Implement the CLI entrypoint (cmd/kbd.py)

**Depends on:** TASK-005, TASK-009, TASK-011, TASK-013
**Files created:** `cmd/kbd.py`

### Steps

Create `cmd/kbd.py`:
```python
import typer
from pathlib import Path
from typing import Optional
import json

app = typer.Typer(name="kbd", help="Knowledge Base Dashboard — your coding patterns, visualized.")


def _get_db_path() -> Path:
    from core.config import AppConfig
    cfg = AppConfig.from_toml()
    return Path(cfg.database.path)


@app.command()
def scan(
    paths: Optional[list[str]] = typer.Argument(None, help="Directories to scan"),
    db: Optional[str] = typer.Option(None, "--db", help="Database path"),
):
    """Scan git repositories and ingest experiment logs."""
    from core.config import AppConfig
    from core.git_scanner import scan_directory
    from core.experiment_parser import find_all_jsonl, parse_jsonl
    from core.db import create_tables, db_conn, upsert_repo, insert_experiment, insert_run
    from core.pattern_engine import detect_patterns
    from core.insight_engine import generate_insights
    from core.db import upsert_pattern, insert_insight
    from rich.console import Console
    from rich.progress import track
    from datetime import datetime

    console = Console()
    cfg = AppConfig.from_toml()
    db_path = Path(db) if db else Path(cfg.database.path)
    scan_paths = paths or cfg.scan.paths

    create_tables(db_path)
    console.print(f"[bold]Scanning {len(scan_paths)} path(s)...[/bold]")

    all_repos = []
    for raw_path in scan_paths:
        p = Path(raw_path).expanduser()
        console.print(f"  Scanning {p}...")
        repos = scan_directory(p, max_depth=cfg.scan.max_depth)
        all_repos.extend(repos)
        console.print(f"  Found {len(repos)} repos")

    console.print(f"\n[green]Saving {len(all_repos)} repos to database...[/green]")
    with db_conn(db_path) as conn:
        for repo in all_repos:
            upsert_repo(conn, repo.to_db_dict())

    # Ingest experiment logs
    all_sessions = []
    for raw_path in scan_paths:
        jsonl_files = find_all_jsonl(Path(raw_path).expanduser(), cfg.autoresearch.filename
                                      if hasattr(cfg, 'autoresearch') else "autoresearch.jsonl")
        for jf in jsonl_files:
            try:
                sessions = parse_jsonl(jf)
                all_sessions.extend(sessions)
                with db_conn(db_path) as conn:
                    for sess in sessions:
                        exp_id = insert_experiment(conn, {
                            "repo_id": None,
                            "jsonl_path": sess.jsonl_path,
                            "session_name": sess.session_name,
                            "metric_name": sess.metric_name,
                            "metric_unit": sess.metric_unit,
                            "direction": sess.direction,
                            "total_runs": sess.total_runs,
                            "kept_runs": sess.kept_runs,
                            "discarded_runs": sess.discarded_runs,
                            "crashed_runs": sess.crashed_runs,
                            "best_metric": sess.best_metric,
                            "noise_floor": None,
                            "started_at": None,
                            "completed_at": datetime.utcnow().isoformat(),
                        })
                        for run in sess.runs:
                            insert_run(conn, {
                                "experiment_id": exp_id,
                                "commit": run.commit,
                                "metric": run.value,
                                "status": run.status,
                                "description": run.description,
                                "extra_metrics": json.dumps(run.extra_metrics),
                                "duration_ms": run.duration_ms,
                                "run_order": run.run_order,
                                "created_at": run.timestamp.isoformat() if run.timestamp else None,
                            })
            except Exception as e:
                console.print(f"  [yellow]Warning: could not parse {jf}: {e}[/yellow]")

    # Detect patterns
    if all_sessions:
        patterns = detect_patterns(all_sessions)
        with db_conn(db_path) as conn:
            for pat in patterns:
                pat_id = upsert_pattern(conn, pat.trigger, pat.action, pat.confidence)
                pat.id = pat_id
        insights = generate_insights(patterns)
        with db_conn(db_path) as conn:
            for ins in insights:
                insert_insight(conn, ins.pattern_id, ins.suggestion, ins.urgency)

    console.print(f"\n[bold green]Scan complete![/bold green]")
    console.print(f"  Repos: {len(all_repos)}")
    console.print(f"  Experiments: {len(all_sessions)}")


@app.command()
def dashboard(
    db: Optional[str] = typer.Option(None, "--db", help="Database path"),
):
    """Launch the interactive TUI dashboard."""
    from ui.dashboard import KBDApp
    db_path = db or str(_get_db_path())
    KBDApp(db_path=db_path).run()


@app.command()
def health(
    db: Optional[str] = typer.Option(None, "--db", help="Database path"),
):
    """Show database health and stats."""
    from core.db import db_conn
    from rich.console import Console
    console = Console()
    db_path = Path(db) if db else _get_db_path()
    if not db_path.exists():
        console.print("[red]No database found. Run: kbd scan[/red]")
        raise typer.Exit(1)
    with db_conn(db_path) as conn:
        repo_count = conn.execute("SELECT COUNT(*) FROM repos").fetchone()[0]
        exp_count = conn.execute("SELECT COUNT(*) FROM experiments").fetchone()[0]
        pattern_count = conn.execute("SELECT COUNT(*) FROM patterns").fetchone()[0]
        insight_count = conn.execute("SELECT COUNT(*) FROM insights WHERE resolved=0").fetchone()[0]
    size_mb = round(db_path.stat().st_size / 1024 / 1024, 2)
    console.print(f"\n[bold]Knowledge Base Dashboard — Health Check[/bold]")
    console.print(f"  Database: {db_path} ({size_mb} MB)")
    console.print(f"  Repos: {repo_count}")
    console.print(f"  Experiments: {exp_count}")
    console.print(f"  Patterns detected: {pattern_count}")
    console.print(f"  Pending insights: {insight_count}")


@app.command()
def export(
    output: str = typer.Option("exports/report.html", "--output", "-o"),
    db: Optional[str] = typer.Option(None, "--db"),
):
    """Export dashboard data to an HTML report."""
    from export.html_report import generate_html_report
    from rich.console import Console
    console = Console()
    db_path = Path(db) if db else _get_db_path()
    out_path = Path(output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    generate_html_report(db_path, out_path)
    console.print(f"[green]Report written to: {out_path}[/green]")


if __name__ == "__main__":
    app()
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python cmd/kbd.py --help
python cmd/kbd.py health --db /tmp/nonexistent.db || true
```
**Done when:** `--help` prints usage, `health` prints "No database found" and exits 1.

---

## TASK-015: Implement HTML export module

**Depends on:** TASK-005
**Files created:** `export/html_report.py`

### Steps

Create `export/html_report.py`:
```python
from pathlib import Path
from datetime import datetime
from core.db import db_conn


def generate_html_report(db_path: Path, out_path: Path) -> None:
    with db_conn(db_path) as conn:
        repos = conn.execute(
            "SELECT name, primary_lang, total_commits, last_active, status, stack_json "
            "FROM repos ORDER BY last_active DESC"
        ).fetchall()
        experiments = conn.execute(
            "SELECT session_name, metric_name, total_runs, kept_runs, best_metric "
            "FROM experiments ORDER BY completed_at DESC"
        ).fetchall()
        patterns = conn.execute(
            "SELECT trigger, action, frequency, confidence FROM patterns ORDER BY frequency DESC"
        ).fetchall()

    repo_rows = "\n".join(
        f"<tr><td>{r['name']}</td><td>{r['primary_lang'] or ''}</td>"
        f"<td>{r['total_commits']}</td><td>{str(r['last_active'] or '')[:10]}</td>"
        f"<td>{r['status']}</td></tr>"
        for r in repos
    )

    exp_rows = "\n".join(
        f"<tr><td>{e['session_name']}</td><td>{e['metric_name']}</td>"
        f"<td>{e['kept_runs']}/{e['total_runs']}</td><td>{e['best_metric'] or ''}</td></tr>"
        for e in experiments
    )

    pattern_rows = "\n".join(
        f"<tr><td>{p['trigger']}</td><td>{p['action']}</td>"
        f"<td>{p['frequency']}</td><td>{p['confidence']:.2f}</td></tr>"
        for p in patterns
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Knowledge Base Dashboard Report</title>
<style>
  body {{ font-family: -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 2rem; }}
  h1 {{ color: #1a1a2e; }} h2 {{ color: #16213e; border-bottom: 2px solid #0f3460; }}
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 2rem; }}
  th {{ background: #0f3460; color: white; padding: 0.5rem 1rem; text-align: left; }}
  td {{ padding: 0.4rem 1rem; border-bottom: 1px solid #eee; }}
  tr:hover {{ background: #f8f9fa; }}
  .stats {{ display: flex; gap: 2rem; margin-bottom: 2rem; }}
  .stat {{ background: #f8f9fa; padding: 1rem 2rem; border-radius: 8px; }}
  .stat h3 {{ margin: 0; font-size: 2rem; color: #0f3460; }}
</style>
</head>
<body>
<h1>🧠 Knowledge Base Dashboard</h1>
<p>Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</p>
<div class="stats">
  <div class="stat"><h3>{len(repos)}</h3><p>Repositories</p></div>
  <div class="stat"><h3>{len(experiments)}</h3><p>Experiments</p></div>
  <div class="stat"><h3>{len(patterns)}</h3><p>Patterns</p></div>
</div>
<h2>Repositories</h2>
<table><thead><tr><th>Name</th><th>Language</th><th>Commits</th><th>Last Active</th><th>Status</th></tr></thead>
<tbody>{repo_rows}</tbody></table>
<h2>Experiments</h2>
<table><thead><tr><th>Session</th><th>Metric</th><th>Kept/Total</th><th>Best</th></tr></thead>
<tbody>{exp_rows}</tbody></table>
<h2>Patterns</h2>
<table><thead><tr><th>Trigger</th><th>Action</th><th>Frequency</th><th>Confidence</th></tr></thead>
<tbody>{pattern_rows}</tbody></table>
</body></html>"""

    out_path.write_text(html, encoding="utf-8")
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "
from export.html_report import generate_html_report
from core.db import create_tables
from pathlib import Path
import tempfile, os

db = Path(tempfile.mktemp(suffix='.db'))
out = Path(tempfile.mktemp(suffix='.html'))
create_tables(db)
generate_html_report(db, out)
content = out.read_text()
assert '<!DOCTYPE html>' in content
assert 'Knowledge Base Dashboard' in content
assert len(content) > 500
os.unlink(db); os.unlink(out)
print('OK')
"
```
**Done when:** prints `OK`.

---

## TASK-016: Write integration tests

**Depends on:** TASK-014, TASK-015
**Files created:** `tests/integration/test_full_scan.py`, `tests/integration/test_export.py`

### Steps

Create `tests/integration/test_full_scan.py`:
```python
import pytest
import tempfile
from pathlib import Path
from tests.conftest import FIXTURES_DIR
from core.git_scanner import scan_directory
from core.db import create_tables, db_conn, upsert_repo, get_all_repos


def test_full_scan_and_store(tmp_path):
    db = tmp_path / "test.db"
    create_tables(db)
    repos = scan_directory(FIXTURES_DIR)
    assert len(repos) >= 1

    with db_conn(db) as conn:
        for repo in repos:
            upsert_repo(conn, repo.to_db_dict())

    with db_conn(db) as conn:
        stored = get_all_repos(conn)
    assert len(stored) == len(repos)
    names = [r["name"] for r in stored]
    assert "synthetic_repo" in names


def test_scan_writes_correct_commit_count(tmp_path):
    db = tmp_path / "test.db"
    create_tables(db)
    repos = scan_directory(FIXTURES_DIR)
    synth = next(r for r in repos if r.name == "synthetic_repo")
    assert synth.total_commits >= 2
```

Create `tests/integration/test_export.py`:
```python
import pytest
from pathlib import Path
from tests.conftest import FIXTURES_DIR
from core.db import create_tables, db_conn, upsert_repo
from core.git_scanner import scan_directory
from export.html_report import generate_html_report


def test_export_html_creates_valid_file(tmp_path):
    db = tmp_path / "test.db"
    out = tmp_path / "report.html"
    create_tables(db)

    repos = scan_directory(FIXTURES_DIR)
    with db_conn(db) as conn:
        for repo in repos:
            upsert_repo(conn, repo.to_db_dict())

    generate_html_report(db, out)
    assert out.exists()
    content = out.read_text()
    assert "<!DOCTYPE html>" in content
    assert "synthetic_repo" in content
    assert len(content) > 1000
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -m pytest tests/integration/ -v
```
**Done when:** all integration tests pass.

---

## TASK-017: Create GitHub Actions CI workflow

**Depends on:** TASK-016
**Files created:** `.github/workflows/ci.yml`

### Steps

Create `.github/workflows/ci.yml`:
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
        python: ['3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - name: Install uv
        run: pip install uv
      - name: Install deps
        run: uv pip install -e ".[dev]" --system
      - name: Run unit tests
        run: python -m pytest tests/unit -v --cov=core --cov=models --cov=export --cov-report=xml
      - name: Run integration tests
        run: python -m pytest tests/integration -v

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ruff
      - run: ruff check .
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
python -c "
import yaml
with open('.github/workflows/ci.yml') as f:
    data = yaml.safe_load(f)
assert 'jobs' in data
assert 'test' in data['jobs']
print('CI YAML valid. OK')
" 2>/dev/null || python -c "
from pathlib import Path
content = Path('.github/workflows/ci.yml').read_text()
assert 'pytest' in content
assert 'ruff' in content
print('CI file exists and contains expected content. OK')
"
```
**Done when:** prints `OK`.

---

## TASK-018: Run full test suite and lint checks

**Depends on:** TASK-017
**Files modified:** any files reported by ruff as having issues

### Steps

```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate

# Run all tests
python -m pytest tests/ -v --tb=short 2>&1 | tee test_results.txt

# Run linter
ruff check . 2>&1 | tee lint_results.txt

# Show summary
echo "=== TEST RESULTS ===" && grep -E "passed|failed|error" test_results.txt | tail -5
echo "=== LINT RESULTS ===" && cat lint_results.txt
```

Fix any lint errors reported by ruff. For each error, edit the file at the indicated line and fix the issue. Common fixes:
- `F401 'x' imported but unused` → remove the import
- `E501 line too long` → ruff fixes with `ruff check --fix .`
- `I001 import order` → ruff fixes with `ruff check --fix .`

```bash
# Auto-fix what ruff can fix
ruff check --fix .

# Re-run to verify
ruff check .
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -m pytest tests/unit tests/integration -v --tb=short
ruff check .
```
**Done when:** pytest shows no FAILED or ERROR, ruff outputs nothing (no lint errors).

---

## TASK-019: Write README.md

**Depends on:** TASK-018
**Files created:** `README.md`

### Steps

Create `README.md`:
```markdown
# 🧠 Knowledge Base Dashboard

> Your coding patterns, visualized. An interactive TUI that mines your git history and experiment logs into a living analytics engine.

## Quick Start

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
```

### Verification
```bash
test -f ~/projects/knowledge-base-dashboard/README.md && echo "README exists. OK"
```
**Done when:** prints `README exists. OK`.

---

## TASK-020: End-to-end smoke test

**Depends on:** TASK-019

### Steps

```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate

# Create a temp db
rm -f /tmp/kbd_smoke.db

# Scan the fixtures directory
python cmd/kbd.py scan tests/fixtures --db /tmp/kbd_smoke.db

# Run health check
python cmd/kbd.py health --db /tmp/kbd_smoke.db

# Export HTML
python cmd/kbd.py export --output /tmp/kbd_report.html --db /tmp/kbd_smoke.db
```

### Verification
```bash
cd ~/projects/knowledge-base-dashboard
source .venv/bin/activate
python -c "
from pathlib import Path
report = Path('/tmp/kbd_report.html')
assert report.exists(), 'HTML report not generated'
content = report.read_text()
assert 'synthetic_repo' in content, 'repo not in report'
assert len(content) > 2000, 'report too small'
print('End-to-end smoke test OK')
"
```
**Done when:** prints `End-to-end smoke test OK`.

---

## Summary

| Phase | Tasks | Goal |
|-------|-------|------|
| Setup | 001-004 | Project skeleton, deps, fixtures |
| Data Layer | 005-006 | SQLite schema, Pydantic models |
| Core Engines | 007-012 | Git scanner, experiment parser, pattern + insight |
| TUI | 013 | Textual dashboard with 5 tabs |
| CLI | 014-015 | `kbd` command, HTML export |
| Integration | 016-017 | Integration tests + CI |
| Polish | 018-020 | Lint, README, E2E smoke test |
