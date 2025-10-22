"""Main TUI application using Textual"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding
from textual.screen import Screen


class MainMenu(Screen):
    """Main menu screen"""
    
    BINDINGS = [
        Binding("n", "new_entry", "New Entry", priority=True),
        Binding("v", "view_entries", "View Entries", priority=True),
        Binding("s", "search", "Search", priority=True),
        Binding("t", "stats", "Statistics", priority=True),
        Binding("a", "achievements", "Achievements", priority=True),
        Binding("c", "config", "Configuration", priority=True),
        Binding("e", "export", "Export Data", priority=True),
        Binding("p", "profile", "Profile", priority=True),
        Binding("q", "quit", "Quit", priority=True),
    ]

    def compose(self) -> ComposeResult:
        """Compose the main menu layout"""
        yield Header(show_clock=True)
        yield Container(
            Static(
                "[bold cyan]🎯 Daily Tracker - Interactive TUI[/bold cyan]\n\n"
                "[dim]Navigate with arrow keys or press hotkeys[/dim]",
                id="title"
            ),
            Vertical(
                Button("📝 New Entry [dim](n)[/dim]", id="new_entry", variant="primary"),
                Button("👁️  View Entries [dim](v)[/dim]", id="view_entries"),
                Button("🔍 Search [dim](s)[/dim]", id="search"),
                Button("📊 Statistics [dim](t)[/dim]", id="stats"),
                Button("🏆 Achievements [dim](a)[/dim]", id="achievements"),
                Button("⚙️  Configuration [dim](c)[/dim]", id="config"),
                Button("📤 Export Data [dim](e)[/dim]", id="export"),
                Button("👤 Profile [dim](p)[/dim]", id="profile"),
                Button("❌ Quit [dim](q)[/dim]", id="quit", variant="error"),
                id="menu_buttons"
            ),
            id="main_container"
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "new_entry":
            self.action_new_entry()
        elif button_id == "view_entries":
            self.action_view_entries()
        elif button_id == "search":
            self.action_search()
        elif button_id == "stats":
            self.action_stats()
        elif button_id == "achievements":
            self.action_achievements()
        elif button_id == "config":
            self.action_config()
        elif button_id == "export":
            self.action_export()
        elif button_id == "profile":
            self.action_profile()
        elif button_id == "quit":
            self.app.exit()

    def action_new_entry(self) -> None:
        """Navigate to new entry screen"""
        from .screens.new_entry import NewEntryScreen
        self.app.push_screen(NewEntryScreen())

    def action_view_entries(self) -> None:
        """Navigate to view entries screen"""
        from .screens.view_entries import ViewEntriesScreen
        self.app.push_screen(ViewEntriesScreen())

    def action_search(self) -> None:
        """Navigate to search screen"""
        from .screens.search import SearchScreen
        self.app.push_screen(SearchScreen())

    def action_stats(self) -> None:
        """Navigate to statistics screen"""
        from .screens.stats import StatsScreen
        self.app.push_screen(StatsScreen())

    def action_achievements(self) -> None:
        """Navigate to achievements screen"""
        from .screens.achievements import AchievementsScreen
        self.app.push_screen(AchievementsScreen())

    def action_config(self) -> None:
        """Navigate to configuration screen"""
        from .screens.config import ConfigScreen
        self.app.push_screen(ConfigScreen())

    def action_export(self) -> None:
        """Navigate to export screen"""
        from .screens.export import ExportScreen
        self.app.push_screen(ExportScreen())

    def action_profile(self) -> None:
        """Navigate to profile screen"""
        from .screens.profile import ProfileScreen
        self.app.push_screen(ProfileScreen())


class TrackerTUI(App):
    """Main Tracker TUI Application"""
    
    CSS = """
    #main_container {
        align: center middle;
        width: 80;
        height: auto;
    }
    
    #title {
        text-align: center;
        padding: 1 2;
        margin-bottom: 2;
    }
    
    #menu_buttons {
        width: 60;
        height: auto;
        align: center middle;
    }
    
    Button {
        width: 100%;
        margin: 1 2;
    }
    
    .info-panel {
        border: solid $primary;
        height: auto;
        padding: 1 2;
        margin: 1 2;
    }
    
    .form-container {
        width: 80;
        height: auto;
        align: center middle;
        padding: 2;
    }
    
    Input {
        margin: 1 2;
    }
    
    Label {
        margin: 1 2;
    }
    
    DataTable {
        margin: 1 2;
    }
    """
    
    TITLE = "Tracker TUI"
    SUB_TITLE = "Daily tracking with AI insights"
    
    def on_mount(self) -> None:
        """Initialize the application"""
        self.push_screen(MainMenu())


def run_tui():
    """Run the TUI application"""
    app = TrackerTUI()
    app.run()
