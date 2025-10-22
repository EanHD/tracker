"""Export screen"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static, Input, Label
from textual.binding import Binding


class ExportScreen(Screen):
    """Screen for exporting data"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the export screen"""
        yield Header()
        yield Container(
            Static("[bold cyan]📤 Export Data[/bold cyan]\n[dim]Export your entries to CSV or JSON[/dim]", id="export_title"),
            Vertical(
                Label("Choose export format:"),
                Button("📄 Export to CSV", id="csv_btn", variant="primary"),
                Button("📋 Export to JSON", id="json_btn", variant="primary"),
                Static("\n[dim]Files will be saved to the current directory[/dim]\n[dim]Use command line for more options:[/dim]\n[cyan]tracker export --format csv --output myfile.csv[/cyan]"),
                Button("⬅️  Back to Menu (Esc)", id="back_btn"),
                id="export_form"
            ),
            id="export_container"
        )
        yield Footer()
    
    def action_cancel(self) -> None:
        """Return to main menu"""
        self.app.pop_screen()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back_btn":
            self.action_cancel()
        elif event.button.id == "csv_btn":
            self._export_csv()
        elif event.button.id == "json_btn":
            self._export_json()
    
    def _export_csv(self) -> None:
        """Export to CSV"""
        from datetime import date
        from tracker.core.database import SessionLocal
        from tracker.services.entry_service import EntryService
        
        try:
            filename = f"tracker_export_{date.today()}.csv"
            with SessionLocal() as db:
                service = EntryService(db)
                service.export_entries(user_id=1, format="csv", output_file=filename)
            
            self.notify(f"✅ Exported to {filename}", severity="information")
        except Exception as e:
            self.notify(f"❌ Export failed: {str(e)}", severity="error")
    
    def _export_json(self) -> None:
        """Export to JSON"""
        from datetime import date
        from tracker.core.database import SessionLocal
        from tracker.services.entry_service import EntryService
        
        try:
            filename = f"tracker_export_{date.today()}.json"
            with SessionLocal() as db:
                service = EntryService(db)
                service.export_entries(user_id=1, format="json", output_file=filename)
            
            self.notify(f"✅ Exported to {filename}", severity="information")
        except Exception as e:
            self.notify(f"❌ Export failed: {str(e)}", severity="error")
