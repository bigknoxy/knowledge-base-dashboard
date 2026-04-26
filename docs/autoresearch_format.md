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
