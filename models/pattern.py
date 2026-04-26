from datetime import datetime

from pydantic import BaseModel


class PatternModel(BaseModel):
    id: int | None = None
    trigger: str
    action: str
    frequency: int = 1
    confidence: float = 0.0
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    repo_examples: list[str] = []
