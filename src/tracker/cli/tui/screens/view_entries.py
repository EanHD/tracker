"""View entries screen"""

from datetime import date, timedelta

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, DataTable, Static
from textual.binding import Binding

from tracker.core.database import SessionLocal
from tracker.services.entry_service import EntryService


class ViewEntriesScreen(Screen):
    """Screen for viewing entries"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the view entries screen"""
        yield Header()
        yield Container(
            Static("[bold cyan]👁️  View Entries[/bold cyan]\n[dim]Your recent entries[/dim]", id="view_title"),
            DataTable(id="entries_table"),
            Button("⬅️  Back to Menu (Esc)", id="back_btn"),
            id="view_container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Load entries when screen mounts"""
        self._load_entries()
    
    def _load_entries(self) -> None:
        """Load and display entries"""
        table = self.query_one("#entries_table", DataTable)
        table.clear(columns=True)
        
        # Add columns
        table.add_column("Date", width=12)
        table.add_column("Income", width=10)
        table.add_column("Expenses", width=10)
        table.add_column("Balance", width=10)
        table.add_column("Work Hrs", width=10)
        table.add_column("Mood", width=8)
        table.add_column("Stress", width=8)
        
        try:
            with SessionLocal() as db:
                service = EntryService(db)
                # Get last 30 days
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
                entries = service.list_entries(
                    user_id=1,
                    start_date=start_date,
                    end_date=end_date
                )
                
                for entry in entries:
                    total_expenses = (
                        entry.bills + entry.food + entry.entertainment +
                        entry.shopping + entry.health + entry.transport +
                        entry.education + entry.gifts + entry.other_expenses
                    )
                    balance = entry.income - total_expenses
                    
                    table.add_row(
                        str(entry.date),
                        f"${entry.income:.2f}",
                        f"${total_expenses:.2f}",
                        f"${balance:.2f}",
                        str(entry.work_hours or 0),
                        str(entry.mood_level or "-"),
                        str(entry.stress_level or "-")
                    )
                
                if not entries:
                    self.notify("No entries found", severity="information")
                    
        except Exception as e:
            self.notify(f"Error loading entries: {str(e)}", severity="error")
    
    def action_cancel(self) -> None:
        """Return to main menu"""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh the entries list"""
        self._load_entries()
        self.notify("Refreshed", severity="information")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back_btn":
            self.action_cancel()
