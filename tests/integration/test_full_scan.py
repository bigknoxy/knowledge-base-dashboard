from core.db import create_tables, db_conn, get_all_repos, upsert_repo
from core.git_scanner import scan_directory
from tests.conftest import FIXTURES_DIR


def test_full_scan_and_store(tmp_path):
    db = tmp_path / "test.db"
    create_tables(db)
    repos = scan_directory(FIXTURES_DIR)
    assert len(repos) >= 1

    with db_conn(db) as conn:
        for repo in repos:
            upsert_repo(conn, repo.to_db_dict())

    with db_conn(db) as conn:
        stored = get_all_repos(conn)
    assert len(stored) == len(repos)
    names = [r["name"] for r in stored]
    assert "synthetic_repo" in names


def test_scan_writes_correct_commit_count(tmp_path):
    db = tmp_path / "test.db"
    create_tables(db)
    repos = scan_directory(FIXTURES_DIR)
    synth = next(r for r in repos if r.name == "synthetic_repo")
    assert synth.total_commits >= 2
