from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, TabbedContent, TabPane

from ui.tabs.experiments import ExperimentsTab
from ui.tabs.overview import OverviewTab
from ui.tabs.patterns import PatternsTab
from ui.tabs.repos import ReposTab
from ui.tabs.timeline import TimelineTab


class KBDApp(App[None]):
    """Knowledge Base Dashboard — main TUI application."""

    CSS = """
    TabbedContent {
        height: 100%;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def __init__(self, db_path: str = "kbd.db"):
        super().__init__()
        self.db_path = db_path

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Overview", id="overview"):
                yield OverviewTab(db_path=self.db_path)
            with TabPane("Repos", id="repos"):
                yield ReposTab(db_path=self.db_path)
            with TabPane("Experiments", id="experiments"):
                yield ExperimentsTab(db_path=self.db_path)
            with TabPane("Patterns", id="patterns"):
                yield PatternsTab(db_path=self.db_path)
            with TabPane("Timeline", id="timeline"):
                yield TimelineTab(db_path=self.db_path)
        yield Footer()

    def action_refresh(self) -> None:
        self.notify("Refreshing data…")
        for tab in self.query("*"):
            if hasattr(tab, "refresh_data"):
                tab.refresh_data()