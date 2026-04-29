import os
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from pydantic import Field
from pydantic_settings import BaseSettings

CONFIG_DIR = Path(os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))) / "kbd"
CONFIG_PATH = CONFIG_DIR / "config.toml"
DB_DIR = Path(os.getenv("XDG_DATA_HOME", str(Path.home() / ".local/share"))) / "kbd"


class ScanConfig(BaseSettings):
    paths: list[str] = Field(default=["~/projects"])
    exclude: list[str] = Field(default=["**/.venv/**", "**/node_modules/**"])
    max_depth: int = 5


class DBConfig(BaseSettings):
    path: str = ""

    def __init__(self, **data: Any) -> None:
        if not data.get("path"):
            data["path"] = str(DB_DIR / "kbd.db")
        super().__init__(**data)


class UIConfig(BaseSettings):
    theme: str = "dark"
    overview_repo_limit: int = 10


class AppConfig(BaseSettings):
    scan: ScanConfig = Field(default_factory=ScanConfig)
    database: DBConfig = Field(default_factory=DBConfig)
    ui: UIConfig = Field(default_factory=UIConfig)

    @classmethod
    def from_toml(cls, path: Path | None = None) -> "AppConfig":
        if path is None:
            path = CONFIG_PATH
        if not path.exists():
            return cls()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.model_fields})
