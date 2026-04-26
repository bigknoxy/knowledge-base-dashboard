from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


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
