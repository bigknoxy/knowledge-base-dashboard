from pathlib import Path

from textual.widgets import Static

from core.db import db_conn, get_all_repos, get_pending_insights


class OverviewTab(Static):
    def __init__(self, db_path: str = "kbd.db"):
        super().__init__("Loading...")
        self.db_path = db_path

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        try:
            db = Path(self.db_path)
            if not db.exists():
                self.update("No database found. Run: kbd scan")
                return
            with db_conn(db) as conn:
                repos = get_all_repos(conn)
                insights = get_pending_insights(conn)
            langs: dict[str, int] = {}
            for r in repos:
                if r["primary_lang"]:
                    langs[r["primary_lang"]] = langs.get(r["primary_lang"], 0) + 1
            lang_lines = "\n".join(
                f"  {lang:<15} {count:>3} repos"
                for lang, count in sorted(langs.items(), key=lambda x: -x[1])[:8]
            )
            active = sum(1 for r in repos if r["status"] == "active")
            text = (
                f"[bold]Knowledge Base Dashboard[/bold]\n\n"
                f"Total repos: {len(repos)}  |  Active: {active}\n"
                f"Pending insights: {len(insights)}\n\n"
                f"[bold]Top Languages:[/bold]\n{lang_lines}"
            )
            self.update(text)
        except Exception as e:
            self.update(f"Error: {e}")