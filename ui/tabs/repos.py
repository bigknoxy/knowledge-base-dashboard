from pathlib import Path

from textual.widgets import DataTable

from core.db import db_conn, get_all_repos


class ReposTab(DataTable):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def on_mount(self) -> None:
        self.add_columns("Name", "Language", "Commits", "Last Active", "Status")
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            return
        self.clear()
        with db_conn(db) as conn:
            repos = get_all_repos(conn)
        for r in repos[:50]:
            last = str(r["last_active"] or "")[:10]
            self.add_row(r["name"], r["primary_lang"] or "?",
                         str(r["total_commits"]), last, r["status"])