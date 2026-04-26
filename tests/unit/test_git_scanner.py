from pathlib import Path

from core.git_scanner import detect_languages, detect_stack, scan_directory, scan_repo
from tests.conftest import FIXTURES_DIR


def test_scan_repo_returns_model():
    repo = scan_repo(FIXTURES_DIR / "synthetic_repo")
    assert repo is not None
    assert repo.name == "synthetic_repo"
    assert repo.total_commits >= 2
    assert repo.id is not None
    assert len(repo.id) == 16


def test_scan_repo_empty_returns_model():
    repo = scan_repo(FIXTURES_DIR / "empty_repo")
    # Empty repo (no commits) may return None or model with 0 commits
    # Either is acceptable — just must not raise
    assert repo is None or repo.total_commits == 0


def test_scan_repo_non_git_returns_none(tmp_path):
    repo = scan_repo(tmp_path)
    assert repo is None


def test_scan_repo_id_is_stable():
    r1 = scan_repo(FIXTURES_DIR / "synthetic_repo")
    r2 = scan_repo(FIXTURES_DIR / "synthetic_repo")
    assert r1 is not None and r2 is not None
    assert r1.id == r2.id


def test_detect_languages_synthetic_repo():
    langs = detect_languages(FIXTURES_DIR / "synthetic_repo")
    assert "JavaScript" in langs
    assert all(0 < v <= 100 for v in langs.values())


def test_detect_stack_npm():
    stack = detect_stack(FIXTURES_DIR / "synthetic_repo")
    assert "JavaScript" in stack or "React" in stack


def test_detect_stack_mixed():
    stack = detect_stack(FIXTURES_DIR / "mixed_stack_repo")
    assert len(stack) >= 2  # both Python and JavaScript detected


def test_scan_directory_finds_repos():
    repos = scan_directory(FIXTURES_DIR)
    names = [r.name for r in repos]
    assert "synthetic_repo" in names


def test_scan_directory_nonexistent_returns_empty():
    repos = scan_directory(Path("/nonexistent/path/that/does/not/exist"))
    assert repos == []
