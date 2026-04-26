from pathlib import Path

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static

from core.db import db_conn, get_all_patterns, get_pending_insights


class PatternsTab(Widget):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Static("", id="patterns-content")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            self.query_one("#patterns-content").update("No database found.")
            return
        with db_conn(db) as conn:
            patterns = get_all_patterns(conn)
            insights = get_pending_insights(conn)
        lines = [f"[bold]Detected Patterns ({len(patterns)})[/bold]\n"]
        for p in patterns[:10]:
            lines.append(f"  [{p['confidence']:.2f}] {p['trigger']} → {p['action']}")
        if insights:
            lines.append(f"\n[bold]Pending Suggestions ({len(insights)})[/bold]\n")
            for i in insights[:5]:
                lines.append(f"  [{i['urgency'].upper()}] {i['suggestion'][:80]}")
        self.query_one("#patterns-content").update("\n".join(lines))
