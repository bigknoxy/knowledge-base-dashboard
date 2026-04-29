# Tasks/Lessons — Mistake Recovery Log

> Append to this file whenever you make a correction, hit a wall, or discover a pattern.
> Read this at session start and before major refactors.

## Format

```
## Lesson NNN — YYYY-MM-DD
**Failure:** What went wrong
**Detection:** How you noticed / what signal
**Prevention:** Rule for next time
```

---

## Pre-populated Lessons (from past sessions)

### Lesson 001 — 2026-04-28
**Failure:** Install script checked Python 3.12 but project didn't actually need it
**Detection:** User reported install failing with Python 3.11.2, and uv enforced pyproject.toml requirement
**Prevention:** Always verify declared dependencies match actual requirements. Check if any Python 3.12+ specific syntax is used before locking minimum version.

### Lesson 002 — 2026-04-28
**Failure:** Untested install/uninstall scripts left orphaned binaries
**Detection:** kbd command still worked after "uninstall" because binary was at /usr/local/bin/kbd not ~/.local/bin/kbd
**Prevention:** Track actual install locations, not just expected ones. Always verify uninstall removes all traces.

### Lesson 003 — 2026-04-28
**Failure:** GitHub raw URL caching caused stale script testing
**Detection:** Uninstall said "No kbd binary found" but binary was still there (cache hit)
**Prevention:** Use direct raw.githubusercontent.com URLs or specific commit hashes when testing. Verify with fresh shell processes.

### Lesson 004 — 2026-04-26
**Failure:** datetime.utcnow() deprecation warnings in tests
**Detection:** pytest output showed warnings in git_scanner.py and pattern_engine.py
**Prevention:** Use datetime.now(datetime.UTC) instead of datetime.utcnow() for Python 3.12+ compatibility.

### Lesson 005 — 2026-04-26
**Failure:** SQLite "commit" column name required quoting
**Detection:** CREATE TABLE failed on "commit" (reserved keyword)
**Prevention:** Always quote reserved words in SQL, or rename columns to non-reserved names.

---

## Blank Lessons (template)

```
### Lesson NNN — YYYY-MM-DD
**Failure:** 
**Detection:** 
**Prevention:** 
```

---

## Active Sessions

| Session Date | Key Work | Status |
|-------------|---------|--------|
| 2026-04-28 | Python 3.12→3.10, Install/Uninstall fixes | IN PROGRESS |

---

## Next Session Pickup

See `tasks/todo.md` for current tasks and verification commands.