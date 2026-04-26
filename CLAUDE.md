# Knowledge Base Dashboard — Claude Code Project Instructions

## Project Overview
Python 3.12 TUI dashboard that mines git history and autoresearch experiment logs.
Tech: Textual, gitpython, pydantic, sqlite3, typer.

## Before Starting Any Work
1. Read `AGENTS.md` — workflow rules and common mistakes.
2. Read `TASKS.md` — the atomic task list; always work in order.
3. Read `IMPLEMENTATION.md` — schemas, interfaces, testing strategy.

## Allowed Shell Commands

```bash
# Package management
uv venv
uv pip install -e ".[dev]"
uv pip install <package>

# Testing
python -m pytest tests/ -v --tb=short
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/ -q

# Linting
ruff check .
ruff check --fix .

# Git (fixtures only)
git init
git add .
git commit -m "<message>"
git config user.email "test@test.com"
git config user.name "Test User"

# CLI smoke tests
python cmd/kbd.py --help
python cmd/kbd.py scan tests/fixtures --db /tmp/test.db
python cmd/kbd.py health --db /tmp/test.db
python cmd/kbd.py export --output /tmp/report.html --db /tmp/test.db

# File inspection
python -c "<inline test>"
```

## Code Style

- **No comments** unless the WHY is non-obvious
- **No print statements** in non-CLI code — use `structlog`
- **Type annotations** on every public function
- **Pathlib** everywhere — never `os.path`
- **No bare except** — catch specific exceptions
- Line length: 100 chars (`ruff` enforces)
- Import order: stdlib → third-party → local (`ruff` enforces)

## File Structure Rules

Follow `PLAN.md` structure exactly:
```
cmd/           — CLI entrypoints only
core/          — business logic (no UI imports)
models/        — Pydantic models only (no DB imports)
ui/            — Textual TUI (no business logic)
export/        — export formatters
tests/unit/    — unit tests (mocked/fixtures)
tests/integration/ — integration tests
tests/fixtures/ — static test data (committed)
```

## Database Rules
- All SQL in `core/db.py` only
- Use `db_conn()` context manager for every DB operation
- Parameterized queries only — never f-string SQL

## Testing Rules
- Every `core/` module → corresponding `tests/unit/test_<module>.py`
- Fixtures must be in `tests/fixtures/` — never real `~/projects/`
- Tests must be deterministic (no random seeds, no time-dependent assertions)
- `pytest.ini` sets `asyncio_mode = auto` — use `async def test_*` for async tests

## Learnings Protocol

After every completed task, update `LEARNINGS.md`:
```bash
# Append a learning entry
echo "## Learning $(date +%Y-%m-%d): TASK-NNN — <what you learned>" >> LEARNINGS.md
```

After any bug fixed, record:
- What caused it
- How you detected it
- How you fixed it
- What would have prevented it

## Task Tracking

```bash
# Mark task in progress (edit LEARNINGS.md header)
# Run verification before marking complete:
python -m pytest tests/ -q
ruff check .
```

## Performance Targets (from IMPLEMENTATION.md)

| Operation | Limit |
|-----------|-------|
| Cold startup | < 800ms |
| Scan 100 repos | < 15s |
| TUI first render | < 500ms |
| DB query (top 50) | < 50ms |

## Do NOT

- Install packages not listed in `pyproject.toml` without updating it
- Create files outside the defined structure
- Write SQL outside `core/db.py`
- Use `import *`
- Hard-code paths like `/Users/Joshua.Knox`
- Skip verification steps
- Commit test database files (`*.db`)
