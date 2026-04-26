import subprocess
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _init_fixture_repo(repo_path: Path) -> None:
    if repo_path.exists() and not (repo_path / ".git").exists():
        subprocess.run(
            ["git", "init"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "add", "."],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "second commit"],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )


@pytest.fixture(scope="session", autouse=True)
def _setup_fixture_repos() -> None:
    _init_fixture_repo(FIXTURES_DIR / "synthetic_repo")
    _init_fixture_repo(FIXTURES_DIR / "mixed_stack_repo")
