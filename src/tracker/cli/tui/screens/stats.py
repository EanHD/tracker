"""Statistics screen"""

from datetime import date, timedelta

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from tracker.core.database import SessionLocal
from tracker.services.entry_service import EntryService


class StatsScreen(Screen):
    """Screen for viewing statistics"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the statistics screen"""
        yield Header()
        yield Container(
            Static("[bold cyan]📊 Statistics[/bold cyan]\n[dim]Your tracking insights[/dim]", id="stats_title"),
            Static(id="stats_content"),
            Button("⬅️  Back to Menu (Esc)", id="back_btn"),
            id="stats_container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Load statistics when screen mounts"""
        self._load_stats()
    
    def _load_stats(self) -> None:
        """Load and display statistics"""
        try:
            with SessionLocal() as db:
                service = EntryService(db)
                
                # Get last 30 days stats
                end_date = date.today()
                start_date = end_date - timedelta(days=30)
                entries = service.list_entries(
                    user_id=1,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not entries:
                    content = "[yellow]No entries found for the last 30 days[/yellow]"
                else:
                    total_income = sum(e.income for e in entries)
                    total_expenses = sum(
                        e.bills + e.food + e.entertainment + e.shopping +
                        e.health + e.transport + e.education + e.gifts + e.other_expenses
                        for e in entries
                    )
                    net_balance = total_income - total_expenses
                    
                    avg_work = sum(e.work_hours or 0 for e in entries) / len(entries)
                    avg_mood = sum(e.mood_level or 0 for e in entries) / len([e for e in entries if e.mood_level])
                    avg_stress = sum(e.stress_level or 0 for e in entries) / len([e for e in entries if e.stress_level])
                    avg_sleep = sum(e.sleep_hours or 0 for e in entries) / len([e for e in entries if e.sleep_hours])
                    
                    content = f"""
[bold green]📅 Last 30 Days Summary[/bold green]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[bold]Financial Overview[/bold]
💰 Total Income:      ${total_income:,.2f}
💸 Total Expenses:    ${total_expenses:,.2f}
💵 Net Balance:       ${net_balance:,.2f}

[bold]Work & Wellbeing[/bold]
⏰ Avg Work Hours:    {avg_work:.1f} hrs/day
😊 Avg Mood:          {avg_mood:.1f}/10
😰 Avg Stress:        {avg_stress:.1f}/10
😴 Avg Sleep:         {avg_sleep:.1f} hrs/night

[bold]Tracking Stats[/bold]
📝 Total Entries:     {len(entries)}
📆 Days Tracked:      {len(entries)} of 30
"""
                
                stats_widget = self.query_one("#stats_content", Static)
                stats_widget.update(content)
                
        except Exception as e:
            self.notify(f"Error loading statistics: {str(e)}", severity="error")
    
    def action_cancel(self) -> None:
        """Return to main menu"""
        self.app.pop_screen()
    
    def action_refresh(self) -> None:
        """Refresh statistics"""
        self._load_stats()
        self.notify("Refreshed", severity="information")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back_btn":
            self.action_cancel()
