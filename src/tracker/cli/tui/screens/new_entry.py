"""New entry screen"""

from datetime import date
from decimal import Decimal, InvalidOperation

from textual.app import ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Input, Label, Static
from textual.binding import Binding

from tracker.core.database import SessionLocal
from tracker.core.schemas import EntryCreate
from tracker.services.entry_service import EntryService


class NewEntryScreen(Screen):
    """Screen for creating a new entry"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save Entry"),
    ]
    
    def __init__(self):
        super().__init__()
        self.form_data = {}
    
    def compose(self) -> ComposeResult:
        """Compose the new entry form"""
        yield Header()
        yield Container(
            Static("[bold cyan]📝 New Entry[/bold cyan]\n[dim]Fill in the fields below[/dim]", id="form_title"),
            Vertical(
                Label("Date (YYYY-MM-DD, leave empty for today):"),
                Input(placeholder="2024-01-15", id="date_input"),
                
                Label("💰 Income (e.g., 150.00):"),
                Input(placeholder="0.00", id="income_input"),
                
                Label("💸 Bills (e.g., 50.00):"),
                Input(placeholder="0.00", id="bills_input"),
                
                Label("🍕 Food (e.g., 25.00):"),
                Input(placeholder="0.00", id="food_input"),
                
                Label("🎮 Entertainment (e.g., 15.00):"),
                Input(placeholder="0.00", id="entertainment_input"),
                
                Label("🛍️ Shopping (e.g., 30.00):"),
                Input(placeholder="0.00", id="shopping_input"),
                
                Label("💊 Health (e.g., 10.00):"),
                Input(placeholder="0.00", id="health_input"),
                
                Label("🚗 Transport (e.g., 20.00):"),
                Input(placeholder="0.00", id="transport_input"),
                
                Label("📚 Education (e.g., 40.00):"),
                Input(placeholder="0.00", id="education_input"),
                
                Label("🎁 Gifts (e.g., 25.00):"),
                Input(placeholder="0.00", id="gifts_input"),
                
                Label("📊 Other Expenses (e.g., 10.00):"),
                Input(placeholder="0.00", id="other_input"),
                
                Label("⏰ Work Hours (0-24):"),
                Input(placeholder="8", id="work_hours_input"),
                
                Label("😰 Stress Level (1-10):"),
                Input(placeholder="5", id="stress_input"),
                
                Label("😊 Mood Level (1-10):"),
                Input(placeholder="7", id="mood_input"),
                
                Label("😴 Sleep Hours (0-24):"),
                Input(placeholder="8", id="sleep_input"),
                
                Label("🏃 Exercise Minutes:"),
                Input(placeholder="30", id="exercise_input"),
                
                Label("👥 Social Time Minutes:"),
                Input(placeholder="60", id="social_input"),
                
                Label("📝 Notes (optional):"),
                Input(placeholder="How was your day?", id="notes_input"),
                
                Horizontal(
                    Button("💾 Save Entry (Ctrl+S)", id="save_btn", variant="primary"),
                    Button("❌ Cancel (Esc)", id="cancel_btn", variant="error"),
                    id="button_row"
                ),
                id="form_fields"
            ),
            id="form_container"
        )
        yield Footer()
    
    def action_cancel(self) -> None:
        """Cancel and return to main menu"""
        self.app.pop_screen()
    
    def action_save(self) -> None:
        """Save the entry"""
        self.on_button_pressed(Button.Pressed(self.query_one("#save_btn", Button)))
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "cancel_btn":
            self.action_cancel()
        elif event.button.id == "save_btn":
            self._save_entry()
    
    def _get_decimal(self, input_id: str) -> Decimal:
        """Get decimal value from input"""
        try:
            value = self.query_one(f"#{input_id}", Input).value.strip()
            return Decimal(value) if value else Decimal("0")
        except InvalidOperation:
            return Decimal("0")
    
    def _get_int(self, input_id: str, default: int = 0) -> int:
        """Get integer value from input"""
        try:
            value = self.query_one(f"#{input_id}", Input).value.strip()
            return int(value) if value else default
        except ValueError:
            return default
    
    def _save_entry(self) -> None:
        """Save the entry to database"""
        try:
            # Get date
            date_str = self.query_one("#date_input", Input).value.strip()
            entry_date = date.fromisoformat(date_str) if date_str else date.today()
            
            # Get all financial data
            income = self._get_decimal("income_input")
            bills = self._get_decimal("bills_input")
            food = self._get_decimal("food_input")
            entertainment = self._get_decimal("entertainment_input")
            shopping = self._get_decimal("shopping_input")
            health = self._get_decimal("health_input")
            transport = self._get_decimal("transport_input")
            education = self._get_decimal("education_input")
            gifts = self._get_decimal("gifts_input")
            other = self._get_decimal("other_input")
            
            # Get metrics
            work_hours = self._get_int("work_hours_input")
            stress_level = self._get_int("stress_input", 5)
            mood_level = self._get_int("mood_input", 7)
            sleep_hours = self._get_int("sleep_input", 8)
            exercise_minutes = self._get_int("exercise_input")
            social_minutes = self._get_int("social_input")
            
            # Get notes
            notes = self.query_one("#notes_input", Input).value.strip()
            
            # Create entry
            entry_data = EntryCreate(
                date=entry_date,
                income=income,
                bills=bills,
                food=food,
                entertainment=entertainment,
                shopping=shopping,
                health=health,
                transport=transport,
                education=education,
                gifts=gifts,
                other_expenses=other,
                work_hours=work_hours,
                stress_level=stress_level,
                mood_level=mood_level,
                sleep_hours=sleep_hours,
                exercise_minutes=exercise_minutes,
                social_minutes=social_minutes,
                notes=notes if notes else None
            )
            
            # Save to database
            with SessionLocal() as db:
                service = EntryService(db)
                entry = service.create_entry(entry_data, user_id=1)
            
            self.notify(f"✅ Entry saved for {entry_date}", severity="information")
            self.app.pop_screen()
            
        except Exception as e:
            self.notify(f"❌ Error saving entry: {str(e)}", severity="error")
