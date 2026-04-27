from pathlib import Path

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static

from core.db import db_conn


class TimelineTab(Widget):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Static("", id="timeline-content")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            self.query_one("#timeline-content").update("No database found.")  # type: ignore[attr-defined]
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
            self.query_one("#timeline-content").update("No timeline data yet.")  # type: ignore[attr-defined]
            return
        lines = ["[bold]Activity Timeline (by month)[/bold]\n"]
        current_month = None
        for row in rows:
            if row["month"] != current_month:
                current_month = row["month"]
                lines.append(f"\n  [bold]{current_month}[/bold]")
            lines.append(f"    {row['primary_lang'] or 'Unknown':<15} {row['count']} repos")
        self.query_one("#timeline-content").update("\n".join(lines))  # type: ignore[attr-defined]
