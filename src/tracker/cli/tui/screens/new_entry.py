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
                
                Label("💰 Income Today (e.g., 150.00):"),
                Input(placeholder="0.00", id="income_today_input"),
                
                Label("💼 Side Income (e.g., 50.00):"),
                Input(placeholder="0.00", id="side_income_input"),
                
                Label("💸 Bills Due Today (e.g., 50.00):"),
                Input(placeholder="0.00", id="bills_input"),
                
                Label("🍕 Food Spent (e.g., 25.00):"),
                Input(placeholder="0.00", id="food_input"),
                
                Label("⛽ Gas Spent (e.g., 50.00):"),
                Input(placeholder="0.00", id="gas_input"),
                
                Label("⏰ Hours Worked (0-24):"),
                Input(placeholder="8", id="hours_worked_input"),
                
                Label("😰 Stress Level (1-10):"),
                Input(placeholder="5", id="stress_input"),
                
                Label("🏦 Cash on Hand (optional, encrypted):"),
                Input(placeholder="100.00", id="cash_input"),
                
                Label("💳 Bank Balance (optional, encrypted):"),
                Input(placeholder="1000.00", id="bank_input"),
                
                Label("💳 Total Debts (optional, encrypted):"),
                Input(placeholder="0.00", id="debts_input"),
                
                Label("⭐ Priority (optional):"),
                Input(placeholder="e.g., Fix car, Go to gym", id="priority_input"),
                
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
            
            # Get financial data using correct field names
            income_today = self._get_decimal("income_today_input")
            side_income = self._get_decimal("side_income_input")
            bills_due_today = self._get_decimal("bills_input")
            food_spent = self._get_decimal("food_input")
            gas_spent = self._get_decimal("gas_input")
            
            # Get optional encrypted fields
            cash_on_hand_str = self.query_one("#cash_input", Input).value.strip()
            cash_on_hand = Decimal(cash_on_hand_str) if cash_on_hand_str else None
            
            bank_balance_str = self.query_one("#bank_input", Input).value.strip()
            bank_balance = Decimal(bank_balance_str) if bank_balance_str else None
            
            debts_total_str = self.query_one("#debts_input", Input).value.strip()
            debts_total = Decimal(debts_total_str) if debts_total_str else None
            
            # Get metrics
            hours_worked = self._get_decimal("hours_worked_input")
            stress_level = self._get_int("stress_input", 5)
            
            # Get optional fields
            priority = self.query_one("#priority_input", Input).value.strip() or None
            notes = self.query_one("#notes_input", Input).value.strip() or None
            
            # Create entry with correct schema
            entry_data = EntryCreate(
                date=entry_date,
                income_today=income_today,
                side_income=side_income,
                bills_due_today=bills_due_today,
                food_spent=food_spent,
                gas_spent=gas_spent,
                hours_worked=hours_worked,
                stress_level=stress_level,
                cash_on_hand=cash_on_hand,
                bank_balance=bank_balance,
                debts_total=debts_total,
                priority=priority,
                notes=notes
            )
            
            # Save to database
            with SessionLocal() as db:
                service = EntryService(db)
                entry = service.create_entry(entry_data, user_id=1)
            
            self.notify(f"✅ Entry saved for {entry_date}", severity="information")
            self.app.pop_screen()
            
        except Exception as e:
            self.notify(f"❌ Error saving entry: {str(e)}", severity="error")
