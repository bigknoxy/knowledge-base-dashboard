from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class InsightModel(BaseModel):
    id: int | None = None
    pattern_id: int
    suggestion: str
    urgency: Literal["low", "medium", "high"] = "low"
    resolved: bool = False
    created_at: datetime | None = None
