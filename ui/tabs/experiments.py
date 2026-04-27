from pathlib import Path

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static

from core.db import db_conn


class ExperimentsTab(Widget):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Static("", id="exp-content")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            self.query_one("#exp-content").update("No database. Run: kbd scan")  # type: ignore[attr-defined]
            return
        with db_conn(db) as conn:
            exps = conn.execute(
                "SELECT session_name, metric_name, total_runs, kept_runs, best_metric "
                "FROM experiments ORDER BY completed_at DESC LIMIT 20"
            ).fetchall()
        if not exps:
            self.query_one("#exp-content").update("No experiments found yet.")  # type: ignore[attr-defined]
            return
        lines = ["[bold]Recent Experiments[/bold]\n"]
        for e in exps:
            lines.append(
                f"  {e['session_name']:<30} {e['metric_name']:<20} "
                f"kept={e['kept_runs']}/{e['total_runs']} best={e['best_metric']}"
            )
        self.query_one("#exp-content").update("\n".join(lines))  # type: ignore[attr-defined]
