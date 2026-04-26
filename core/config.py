import tomllib
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class ScanConfig(BaseSettings):
    paths: list[str] = Field(default=["~/projects"])
    exclude: list[str] = Field(default=["**/.venv/**", "**/node_modules/**"])
    max_depth: int = 5


class DBConfig(BaseSettings):
    path: str = "kbd.db"


class UIConfig(BaseSettings):
    theme: str = "dark"
    overview_repo_limit: int = 10


class AppConfig(BaseSettings):
    scan: ScanConfig = Field(default_factory=ScanConfig)
    database: DBConfig = Field(default_factory=DBConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    @classmethod
    def from_toml(cls, path: Path = Path("config.toml")) -> "AppConfig":
        if not path.exists():
            return cls()
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.model_fields})
