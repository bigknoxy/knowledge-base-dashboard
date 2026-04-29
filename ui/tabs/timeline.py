from pathlib import Path

from textual.widgets import Static

from core.db import db_conn


class TimelineTab(Static):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__("")
        self.db_path = db_path

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            self.update("No database found.")
            return
        with db_conn(db) as conn:
            rows = conn.execute("""
                SELECT strftime('%Y-%m', last_active) as month,
                       primary_lang, COUNT(*) as count
                FROM repos
                WHERE last_active IS NOT NULL
                GROUP BY month, primary_lang
                ORDER BY month DESC
                LIMIT 30
            """).fetchall()
        if not rows:
            self.update("No timeline data yet.")
            return
        lines = ["[bold]Activity Timeline (by month)[/bold]\n"]
        current_month = None
        for row in rows:
            if row["month"] != current_month:
                current_month = row["month"]
                lines.append(f"\n  [bold]{current_month}[/bold]")
            lines.append(f"    {row['primary_lang'] or 'Unknown':<15} {row['count']} repos")
        self.update("\n".join(lines))