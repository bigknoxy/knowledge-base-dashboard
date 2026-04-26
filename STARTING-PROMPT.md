# Starting Prompt — Knowledge Base Dashboard

> Paste this entire prompt into Claude Code (or your coding tool) to begin execution.

---

## Prompt

You are implementing the **knowledge-base-dashboard** project from scratch. This is a Python 3.12 interactive TUI dashboard that mines git history and autoresearch experiment logs.

**Your working directory is:** `~/projects/knowledge-base-dashboard`

**Read these files FIRST, in this exact order, before writing any code:**
1. `AGENTS.md` — workflow rules, code standards, common mistakes, safety rules
2. `CLAUDE.md` — allowed commands, file structure, do-not list
3. `PLAN.md` — architecture, tech stack, phases
4. `IMPLEMENTATION.md` — database schema, API contracts, testing strategy, CI
5. `TASKS.md` — the atomic task list you will execute

**Your mission:** Work through `TASKS.md` from TASK-001 to TASK-020, completing each task fully before moving to the next.

**Task execution protocol (MANDATORY):**
1. Read the full task before writing any code
2. Execute every step in the exact order written
3. Run the `### Verification` command at the end of each task
4. If verification exits 0 → move to the next task
5. If verification fails → debug the issue, fix it, re-run verification, then proceed
6. NEVER skip a verification step
7. NEVER mark a task as done without a passing verification

**After completing each task:**
- Append a one-line completion note to `LEARNINGS.md`
- If you encountered a bug or non-obvious issue, write a full learning entry

**After every 5 tasks, run the full test suite:**
```bash
cd ~/projects/knowledge-base-dashboard && source .venv/bin/activate
python -m pytest tests/ -q --tb=short
```
All tests must pass before continuing.

**The project is complete when:**
- All 20 tasks verified ✓
- `python -m pytest tests/ -v` shows 0 failed
- `ruff check .` shows 0 issues
- `python cmd/kbd.py scan tests/fixtures --db /tmp/smoke.db` completes
- `python cmd/kbd.py export --output /tmp/report.html --db /tmp/smoke.db` creates a valid HTML file

Begin by reading `AGENTS.md`, then `TASKS.md`, then start TASK-001.
