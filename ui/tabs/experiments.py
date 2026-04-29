from pathlib import Path

from textual.widgets import Static

from core.db import db_conn


class ExperimentsTab(Static):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__("")
        self.db_path = db_path

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        db = Path(self.db_path)
        if not db.exists():
            self.update("No database. Run: kbd scan")
            return
        with db_conn(db) as conn:
            exps = conn.execute(
                "SELECT session_name, metric_name, total_runs, kept_runs, best_metric "
                "FROM experiments ORDER BY completed_at DESC LIMIT 20"
            ).fetchall()
        if not exps:
            self.update("No experiments found yet.")
            return
        lines = ["[bold]Recent Experiments[/bold]\n"]
        for e in exps:
            lines.append(
                f"  {e['session_name']:<30} {e['metric_name']:<20} "
                f"kept={e['kept_runs']}/{e['total_runs']} best={e['best_metric']}"
            )
        self.update("\n".join(lines))