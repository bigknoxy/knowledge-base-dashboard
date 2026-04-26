from datetime import datetime

from pydantic import BaseModel, Field, computed_field


class RepoModel(BaseModel):
    id: str
    path: str
    name: str
    description: str | None = None
    url: str | None = None
    created_at: datetime | None = None
    last_active: datetime | None = None
    total_commits: int = 0
    branch_count: int = 1
    primary_lang: str | None = None
    stack: list[str] = Field(default_factory=list)
    status: str = "active"
    scanned_at: datetime | None = None

    @computed_field
    @property
    def is_active(self) -> bool:
        if not self.last_active:
            return False
        delta = datetime.utcnow() - self.last_active.replace(tzinfo=None)
        return delta.days < 90

    def to_db_dict(self) -> dict:
        import json
        return {
            "id": self.id,
            "path": self.path,
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "total_commits": self.total_commits,
            "branch_count": self.branch_count,
            "primary_lang": self.primary_lang,
            "stack_json": json.dumps(self.stack),
            "status": self.status,
            "scanned_at": self.scanned_at.isoformat() if self.scanned_at else None,
        }
