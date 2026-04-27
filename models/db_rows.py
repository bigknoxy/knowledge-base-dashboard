from typing import TypedDict


class RepoRow(TypedDict, total=False):
    id: str
    path: str
    name: str
    description: str | None
    url: str | None
    created_at: str | None
    last_active: str | None
    total_commits: int
    branch_count: int
    primary_lang: str | None
    stack_json: str
    status: str
    scanned_at: str | None


class ExperimentRow(TypedDict, total=False):
    id: int
    repo_id: str | None
    jsonl_path: str
    session_name: str | None
    metric_name: str
    metric_unit: str | None
    direction: str | None
    total_runs: int
    kept_runs: int
    discarded_runs: int
    crashed_runs: int
    best_metric: float | None
    noise_floor: float | None
    started_at: str | None
    completed_at: str


class ExperimentRunRow(TypedDict, total=False):
    id: int
    experiment_id: int
    commit: str | None
    metric: float | None
    status: str
    description: str | None
    extra_metrics: str
    duration_ms: int | None
    run_order: int
    created_at: str | None


class PatternRow(TypedDict, total=False):
    id: int
    trigger: str
    action: str
    frequency: int
    confidence: float
    first_seen: str
    last_seen: str


class InsightRow(TypedDict, total=False):
    id: int
    pattern_id: int | None
    suggestion: str
    urgency: str
    resolved: int
    created_at: str
