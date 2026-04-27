import json
from datetime import datetime
from pathlib import Path
from typing import Any

from models.experiment import ExperimentRun, ExperimentSession


def parse_jsonl(path: Path) -> list[ExperimentSession]:
    """Parse an autoresearch.jsonl file into ExperimentSession objects."""
    sessions: dict[str, dict[str, Any]] = {}

    with open(path, encoding="utf-8") as f:
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
