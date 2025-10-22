"""Search screen"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Label, DataTable, Static
from textual.binding import Binding

from tracker.core.database import SessionLocal
from tracker.services.entry_service import EntryService


class SearchScreen(Screen):
    """Screen for searching entries"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("ctrl+f", "search", "Search"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the search screen"""
        yield Header()
        yield Container(
            Static("[bold cyan]🔍 Search Entries[/bold cyan]\n[dim]Search by keywords in notes[/dim]", id="search_title"),
            Vertical(
                Label("Enter search term:"),
                Input(placeholder="Search...", id="search_input"),
                Button("🔍 Search (Ctrl+F)", id="search_btn", variant="primary"),
                DataTable(id="results_table"),
                Button("⬅️  Back to Menu (Esc)", id="back_btn"),
                id="search_form"
            ),
            id="search_container"
        )
        yield Footer()
    
    def action_cancel(self) -> None:
        """Return to main menu"""
        self.app.pop_screen()
    
    def action_search(self) -> None:
        """Perform search"""
        self._do_search()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back_btn":
            self.action_cancel()
        elif event.button.id == "search_btn":
            self._do_search()
    
    def _do_search(self) -> None:
        """Execute the search"""
        query = self.query_one("#search_input", Input).value.strip()
        
        if not query:
            self.notify("Please enter a search term", severity="warning")
            return
        
        table = self.query_one("#results_table", DataTable)
        table.clear(columns=True)
        
        # Add columns
        table.add_column("Date", width=12)
        table.add_column("Notes", width=50)
        table.add_column("Mood", width=8)
        
        try:
            with SessionLocal() as db:
                service = EntryService(db)
                results = service.search_entries(user_id=1, query=query)
                
                for entry in results:
                    table.add_row(
                        str(entry.date),
                        entry.notes[:47] + "..." if entry.notes and len(entry.notes) > 50 else entry.notes or "",
                        str(entry.mood_level or "-")
                    )
                
                self.notify(f"Found {len(results)} result(s)", severity="information")
                
        except Exception as e:
            self.notify(f"Error searching: {str(e)}", severity="error")
