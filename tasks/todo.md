# Tasks — Current Work Session (2026-04-28)

## Session Status: IN PROGRESS

## Completed This Session

- [x] **TASK-INSTALL-FIX**: Lower Python requirement from 3.12 to 3.10
  - pyproject.toml updated
  - install.sh updated
  - AGENTS.md, PLAN.md updated
  - CI workflow updated (Python 3.10, 3.11)

- [x] **TASK-UNINSTALL-FIX**: Fix uninstall script issues
  - Added /usr/local/bin/kbd removal
  - Added --break-system-packages flag
  - Verified uninstall works completely

- [x] **TASK-E2E-TEST**: End-to-end test of all commands
  - kbd init ✅
  - kbd scan ✅ (scanned tests/fixtures)
  - kbd health ✅
  - kbd export ✅ (generated HTML report)
  - Unit tests: 25/25 passed
  - Warnings: 3 deprecation warnings (datetime.utcnow())

## Pending Tasks

- [ ] **TASK-DEPRECATION**: Fix datetime.utcnow() deprecation warnings
  - core/git_scanner.py:139
  - core/pattern_engine.py:33-34
  - Use datetime.now(datetime.UTC) instead

- [ ] **TASK-DASHBOARD**: Test the Textual dashboard TUI
  - Haven't tested kbd dashboard command yet
  - Need to verify it launches properly

- [ ] **TASK-VERSION**: Add --version flag to CLI
  - kbd --version returns error
  - Add proper version support via pyproject.toml

## Notes

- All changes committed and pushed to main branch
- Commit history:
  - 56d8f0d: Fix uninstall to use --break-system-packages flag
  - 947d64c: Fix uninstall script to remove /usr/local/bin/kbd binary
  - 242a8fb: Lower Python requirement from 3.12 to 3.10

## Verification Commands

```bash
# Install test
bash -c 'curl -fsSL https://raw.githubusercontent.com/bigknoxy/knowledge-base-dashboard/main/install.sh | sh'

# Uninstall test
bash -c 'curl -fsSL https://raw.githubusercontent.com/bigknoxy/knowledge-base-dashboard/main/uninstall.sh | sh'

# Unit tests
cd /root/code/knowledge-base-dashboard && source .venv/bin/activate && python -m pytest tests/unit/ -v

# Lint check
ruff check .
```