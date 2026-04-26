from core.db import create_tables, db_conn, upsert_repo
from core.git_scanner import scan_directory
from export.html_report import generate_html_report
from tests.conftest import FIXTURES_DIR


def test_export_html_creates_valid_file(tmp_path):
    db = tmp_path / "test.db"
    out = tmp_path / "report.html"
    create_tables(db)

    repos = scan_directory(FIXTURES_DIR)
    with db_conn(db) as conn:
        for repo in repos:
            upsert_repo(conn, repo.to_db_dict())

    generate_html_report(db, out)
    assert out.exists()
    content = out.read_text()
    assert "<!DOCTYPE html>" in content
    assert "synthetic_repo" in content
    assert len(content) > 1000
