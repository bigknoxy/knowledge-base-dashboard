# AGENTS.md — Knowledge Base Dashboard

> Instructions for all AI coding agents working on this project.
> Read this file **before** reading any other file.

---

## Project at a Glance

| Item | Value |
|------|-------|
| Language | Python 3.10+ |
| Package manager | `uv` |
| Test runner | `pytest` |
| Linter | `ruff` |
| TUI framework | Textual |
| Database | SQLite via `sqlite3` stdlib |

---

## Golden Rule

**Never mark a task complete unless its verification command exits 0.**
If verification fails: fix the issue, re-run, then proceed. Do not skip.

---

## Workflow Protocol

1. Read `TASKS.md` — it is the single source of truth for what to build and in what order.
2. Execute tasks **sequentially** (TASK-001 → TASK-002 → … → TASK-020).
3. For each task:
   a. Read the full task before starting any work.
   b. Execute every step in the exact order given.
   c. Run the `### Verification` command.
   d. If it passes → move to the next task.
   e. If it fails → debug, fix, re-run verification. Do NOT move on.
4. After every 5 tasks, run the full test suite:
   ```bash
   cd ~/projects/knowledge-base-dashboard && source .venv/bin/activate
   python -m pytest tests/ -q --tb=short
   ```
5. After every fix, record the learning in `LEARNINGS.md`.

---

## Environment Setup (run once before first task)

```bash
cd ~/projects/knowledge-base-dashboard
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

---

## Task Tracking Rules

- Before starting a task: write `## In Progress: TASK-NNN` at the top of `LEARNINGS.md`.
- After completing a task: update to `## Completed: TASK-NNN` and remove the in-progress line.
- If a task fails partway: write what step failed and what you tried.

---

## Code Standards

### Python Style
- `ruff` must pass with zero warnings: `ruff check .`
- Line length: 100 characters
- All public functions must have type annotations
- No bare `except:` — always catch specific exceptions
- Use `pathlib.Path` everywhere, never `os.path`

### Testing Standards
- Every new module must have a corresponding test file in `tests/unit/`
- Tests must not touch real `~/projects/` data — use `tests/fixtures/` only
- Use `pytest` — no `unittest.TestCase`
- Test filenames: `test_<module_name>.py`
- Each test function must have a docstring explaining what it tests

### Database Rules
- Never write raw SQL outside `core/db.py`
- All DB operations go through `db_conn()` context manager
- Use parameterized queries only — no string formatting in SQL

### File Structure
- Do not create files outside the defined structure in `PLAN.md`
- All new Python files must have an `__init__.py` in their package directory

---

## Common Mistakes — Read Before Coding

These are patterns that cause failures. Avoid them.

1. **Forgetting to activate the venv**: All `python` commands require `source .venv/bin/activate` first.
2. **Absolute paths in tests**: Use `FIXTURES_DIR` from `tests/conftest.py`, never hardcode `/Users/Joshua.Knox/`.
3. **Missing `__init__.py`**: Every new package directory needs one. Check with `ls <dir>/__init__.py`.
4. **SQLite thread safety**: Always use the `db_conn()` context manager; never pass connections across threads.
5. **Pydantic v2 changes**: Use `model_dump()` not `.dict()`. Use `model_validate()` not `parse_obj()`.
6. **Textual async**: Textual widget methods that update UI must be called from the main thread. Use `call_from_thread()` for background updates.
7. **git subprocess encoding**: Always pass `text=True, errors='replace'` to subprocess calls on git output.
8. **Empty git repos**: `scan_repo()` must handle repos with zero commits — check for empty `HEAD` output.

---

## Learnings System

When you discover a bug, unexpected behavior, or a better approach, append it to `LEARNINGS.md`:

```markdown
## Learning NNN — <date>
**Task:** TASK-NNN
**Problem:** What went wrong
**Root cause:** Why it happened
**Fix:** What you did to fix it
**Prevention:** What to do differently next time
```

---

## Verification Quick Reference

```bash
# Activate environment
source .venv/bin/activate

# Run all unit tests
python -m pytest tests/unit/ -v

# Run all integration tests
python -m pytest tests/integration/ -v

# Run all tests
python -m pytest tests/ -v --tb=short

# Lint
ruff check .

# Type check (optional but encouraged)
mypy core/ models/ --ignore-missing-imports

# Smoke test the CLI
python cmd/kbd.py --help
python cmd/kbd.py health --db /tmp/test.db || true
```

---

## When You're Stuck

1. Re-read the task description from `TASKS.md` carefully.
2. Re-read `IMPLEMENTATION.md` for the module you're implementing.
3. Check `LEARNINGS.md` for similar past problems.
4. Run the failing verification command with verbose output: add `-v` or `-s` to pytest.
5. Add a `print()` statement and run the module directly: `python -c "from core.x import y; y()"`.
6. Do NOT change the project structure to avoid the problem — fix the actual issue.

---

## Definition of Done

The project is complete when:
- [ ] All 20 tasks in `TASKS.md` are verified (exit 0)
- [ ] `python -m pytest tests/ -v` shows 0 failed, 0 errors
- [ ] `ruff check .` shows 0 issues
- [ ] `python cmd/kbd.py scan tests/fixtures --db /tmp/smoke.db` completes without error
- [ ] `python cmd/kbd.py export --output /tmp/report.html --db /tmp/smoke.db` creates a valid HTML file
- [ ] `LEARNINGS.md` has been populated with any non-trivial discoveries
