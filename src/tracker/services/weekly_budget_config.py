"""Weekly Budget Configuration for tracking income and expenses."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class TransactionType(Enum):
    """Types of financial transactions."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Frequency(Enum):
    """Frequency of recurring transactions."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    DAILY = "daily"
    EVERY_N_DAYS = "every_n_days"


@dataclass
class RecurringTransaction:
    """Represents a recurring financial transaction."""
    name: str
    amount: float
    type: TransactionType
    frequency: Frequency
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    interval_days: Optional[int] = None  # For EVERY_N_DAYS frequency
    notes: Optional[str] = None
    clear_delay_days: Optional[int] = None  # Days until funds clear


class WeeklyBudgetConfig:
    """Configuration for weekly budget tracking."""
    
    def __init__(self):
        """Initialize the weekly budget configuration."""
        self.transactions = self._setup_transactions()
    
    def _setup_transactions(self) -> List[RecurringTransaction]:
        """Set up all recurring transactions based on user's budget."""
        return [
            # Weekly Income
            RecurringTransaction(
                name="EarnIn",
                amount=600.00,
                type=TransactionType.INCOME,
                frequency=Frequency.WEEKLY,
                day_of_week=0,  # Monday (assuming weekly start)
                notes="Weekly paycheck from EarnIn"
            ),
            RecurringTransaction(
                name="Snap-On",
                amount=400.00,
                type=TransactionType.INCOME,
                frequency=Frequency.WEEKLY,
                day_of_week=3,  # Thursday (reserves)
                clear_delay_days=1,  # Clears Friday
                notes="Weekly Snap-On payment - reserves Thursday, clears Friday"
            ),
            RecurringTransaction(
                name="Chase Transfer",
                amount=180.00,
                type=TransactionType.TRANSFER,
                frequency=Frequency.WEEKLY,
                notes="Weekly transfer from Chase"
            ),
            
            # Essential Expenses
            RecurringTransaction(
                name="Gas",
                amount=55.00,
                type=TransactionType.EXPENSE,
                frequency=Frequency.EVERY_N_DAYS,
                interval_days=2,
                notes="Gas every 2 days (Tue-Sat)"
            ),
            RecurringTransaction(
                name="Food",
                amount=125.00,
                type=TransactionType.EXPENSE,
                frequency=Frequency.WEEKLY,
                notes="Weekly food budget"
            ),
            RecurringTransaction(
                name="Pets",
                amount=60.00,
                type=TransactionType.EXPENSE,
                frequency=Frequency.WEEKLY,
                notes="Weekly pet expenses"
            ),
        ]
    
    def get_weekly_income(self) -> float:
        """Calculate total weekly income."""
        return sum(
            t.amount for t in self.transactions 
            if t.type in [TransactionType.INCOME, TransactionType.TRANSFER]
        )
    
    def get_weekly_expenses(self) -> float:
        """Calculate total weekly expenses."""
        weekly_expenses = 0
        for t in self.transactions:
            if t.type == TransactionType.EXPENSE:
                if t.frequency == Frequency.WEEKLY:
                    weekly_expenses += t.amount
                elif t.frequency == Frequency.EVERY_N_DAYS and t.interval_days:
                    # Calculate weekly equivalent for gas (5 days a week)
                    days_per_week = 5  # Tue-Sat
                    weekly_expenses += (t.amount * days_per_week) / t.interval_days
        return weekly_expenses
    
    def get_weekly_balance(self) -> float:
        """Calculate weekly balance (income - expenses)."""
        return self.get_weekly_income() - self.get_weekly_expenses()
    
    def get_daily_gas_days(self) -> List[str]:
        """Get the days when gas is needed."""
        return ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    def generate_weekly_schedule(self) -> Dict[str, List[Dict]]:
        """Generate a weekly schedule of transactions."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        schedule = {day: [] for day in days}
        
        for transaction in self.transactions:
            if transaction.frequency == Frequency.WEEKLY and transaction.day_of_week is not None:
                day_name = days[transaction.day_of_week]
                schedule[day_name].append({
                    "name": transaction.name,
                    "amount": transaction.amount,
                    "type": transaction.type.value,
                    "notes": transaction.notes,
                    "clears": days[(transaction.day_of_week + (transaction.clear_delay_days or 0)) % 7] 
                             if transaction.clear_delay_days else "Same day"
                })
            elif transaction.name == "Gas":
                # Add gas to specific days
                for day in self.get_daily_gas_days():
                    if day in ["Tuesday", "Thursday", "Saturday"]:  # Every other day pattern
                        schedule[day].append({
                            "name": transaction.name,
                            "amount": transaction.amount,
                            "type": transaction.type.value,
                            "notes": transaction.notes
                        })
        
        # Add weekly expenses without specific days
        for transaction in self.transactions:
            if transaction.frequency == Frequency.WEEKLY and transaction.day_of_week is None:
                if transaction.type == TransactionType.EXPENSE:
                    # Distribute weekly expenses across the week or assign to Monday
                    schedule["Monday"].append({
                        "name": f"{transaction.name} (Weekly)",
                        "amount": transaction.amount,
                        "type": transaction.type.value,
                        "notes": transaction.notes
                    })
                elif transaction.type == TransactionType.TRANSFER:
                    # Add transfers to Monday by default
                    schedule["Monday"].append({
                        "name": transaction.name,
                        "amount": transaction.amount,
                        "type": transaction.type.value,
                        "notes": transaction.notes
                    })
        
        return schedule
    
    def get_summary(self) -> Dict:
        """Get a summary of the weekly budget."""
        return {
            "weekly_income": {
                "earnin": 600.00,
                "snap_on": 400.00,
                "chase_transfer": 180.00,
                "total": self.get_weekly_income()
            },
            "weekly_expenses": {
                "gas": 137.50,  # $55 every 2 days for 5 days
                "food": 125.00,
                "pets": 60.00,
                "total": self.get_weekly_expenses()
            },
            "weekly_balance": self.get_weekly_balance(),
            "daily_average_balance": self.get_weekly_balance() / 7,
            "schedule": self.generate_weekly_schedule()
        }


def display_budget_summary():
    """Display a formatted budget summary."""
    config = WeeklyBudgetConfig()
    summary = config.get_summary()
    
    print("\n" + "="*50)
    print("WEEKLY BUDGET SUMMARY")
    print("="*50)
    
    print("\n📈 WEEKLY INCOME:")
    print(f"  • EarnIn: ${summary['weekly_income']['earnin']:,.2f}")
    print(f"  • Snap-On: ${summary['weekly_income']['snap_on']:,.2f} (reserves Thu → clears Fri)")
    print(f"  • Chase Transfer: ${summary['weekly_income']['chase_transfer']:,.2f}")
    print(f"  • TOTAL: ${summary['weekly_income']['total']:,.2f}")
    
    print("\n📉 WEEKLY EXPENSES:")
    print(f"  • Gas: ${summary['weekly_expenses']['gas']:,.2f} ($55 every 2 days, Tue-Sat)")
    print(f"  • Food: ${summary['weekly_expenses']['food']:,.2f}")
    print(f"  • Pets: ${summary['weekly_expenses']['pets']:,.2f}")
    print(f"  • TOTAL: ${summary['weekly_expenses']['total']:,.2f}")
    
    print("\n💰 BALANCE:")
    print(f"  • Weekly Balance: ${summary['weekly_balance']:,.2f}")
    print(f"  • Daily Average: ${summary['daily_average_balance']:,.2f}")
    
    print("\n📅 WEEKLY SCHEDULE:")
    for day, transactions in summary['schedule'].items():
        if transactions:
            print(f"\n  {day}:")
            for t in transactions:
                symbol = "+" if t['type'] in ['income', 'transfer'] else "-"
                print(f"    {symbol} {t['name']}: ${t['amount']:,.2f}")
                if 'clears' in t and t['clears'] != "Same day":
                    print(f"      (clears {t['clears']})")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    display_budget_summary()
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class TransactionType(Enum):
    """Types of financial transactions."""
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class Frequency(Enum):
    """Frequency of recurring transactions."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    DAILY = "daily"
    EVERY_N_DAYS = "every_n_days"


@dataclass
class RecurringTransaction:
    """Represents a recurring financial transaction."""
    name: str
    amount: float
    type: TransactionType
    frequency: Frequency
    day_of_week: Optional[int] = None  # 0=Monday, 6=Sunday
    interval_days: Optional[int] = None  # For EVERY_N_DAYS frequency
    notes: Optional[str] = None
    clear_delay_days: Optional[int] = None  # Days until funds clear


class WeeklyBudgetConfig:
    """Configuration for weekly budget tracking."""
    
    def __init__(self):
        """Initialize the weekly budget configuration."""
        self.transactions = self._setup_transactions()
    
    def _setup_transactions(self) -> List[RecurringTransaction]:
        """Set up all recurring transactions based on user's budget."""
        return [
            # Weekly Income
            RecurringTransaction(
                name="EarnIn",
                amount=600.00,
                type=TransactionType.INCOME,
                frequency=Frequency.WEEKLY,
                day_of_week=0,  # Monday (assuming weekly start)
                notes="Weekly paycheck from EarnIn"
            ),
            RecurringTransaction(
                name="Snap-On",
                amount=400.00,
                type=TransactionType.INCOME,
                frequency=Frequency.WEEKLY,
                day_of_week=3,  # Thursday (reserves)
                clear_delay_days=1,  # Clears Friday
                notes="Weekly Snap-On payment - reserves Thursday, clears Friday"
            ),
            RecurringTransaction(
                name="Chase Transfer",
                amount=180.00,
                type=TransactionType.TRANSFER,
                frequency=Frequency.WEEKLY,
                notes="Weekly transfer from Chase"
            ),
            
            # Essential Expenses
            RecurringTransaction(
                name="Gas",
                amount=55.00,
                type=TransactionType.EXPENSE,
                frequency=Frequency.EVERY_N_DAYS,
                interval_days=2,
                notes="Gas every 2 days (Tue-Sat)"
            ),
            RecurringTransaction(
                name="Food",
                amount=125.00,
                type=TransactionType.EXPENSE,
                frequency=Frequency.WEEKLY,
                notes="Weekly food budget"
            ),
            RecurringTransaction(
                name="Pets",
                amount=60.00,
                type=TransactionType.EXPENSE,
                frequency=Frequency.WEEKLY,
                notes="Weekly pet expenses"
            ),
        ]
    
    def get_weekly_income(self) -> float:
        """Calculate total weekly income."""
        return sum(
            t.amount for t in self.transactions 
            if t.type in [TransactionType.INCOME, TransactionType.TRANSFER]
        )
    
    def get_weekly_expenses(self) -> float:
        """Calculate total weekly expenses."""
        weekly_expenses = 0
        for t in self.transactions:
            if t.type == TransactionType.EXPENSE:
                if t.frequency == Frequency.WEEKLY:
                    weekly_expenses += t.amount
                elif t.frequency == Frequency.EVERY_N_DAYS and t.interval_days:
                    # Calculate weekly equivalent for gas (5 days a week)
                    days_per_week = 5  # Tue-Sat
                    weekly_expenses += (t.amount * days_per_week) / t.interval_days
        return weekly_expenses
    
    def get_weekly_balance(self) -> float:
        """Calculate weekly balance (income - expenses)."""
        return self.get_weekly_income() - self.get_weekly_expenses()
    
    def get_daily_gas_days(self) -> List[str]:
        """Get the days when gas is needed."""
        return ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    
    def generate_weekly_schedule(self) -> Dict[str, List[Dict]]:
        """Generate a weekly schedule of transactions."""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        schedule = {day: [] for day in days}
        
        for transaction in self.transactions:
            if transaction.frequency == Frequency.WEEKLY and transaction.day_of_week is not None:
                day_name = days[transaction.day_of_week]
                schedule[day_name].append({
                    "name": transaction.name,
                    "amount": transaction.amount,
                    "type": transaction.type.value,
                    "notes": transaction.notes,
                    "clears": days[(transaction.day_of_week + (transaction.clear_delay_days or 0)) % 7] 
                             if transaction.clear_delay_days else "Same day"
                })
            elif transaction.name == "Gas":
                # Add gas to specific days
                for day in self.get_daily_gas_days():
                    if day in ["Tuesday", "Thursday", "Saturday"]:  # Every other day pattern
                        schedule[day].append({
                            "name": transaction.name,
                            "amount": transaction.amount,
                            "type": transaction.type.value,
                            "notes": transaction.notes
                        })
        
        # Add weekly expenses without specific days
        for transaction in self.transactions:
            if transaction.frequency == Frequency.WEEKLY and transaction.day_of_week is None:
                if transaction.type == TransactionType.EXPENSE:
                    # Distribute weekly expenses across the week or assign to Monday
                    schedule["Monday"].append({
                        "name": f"{transaction.name} (Weekly)",
                        "amount": transaction.amount,
                        "type": transaction.type.value,
                        "notes": transaction.notes
                    })
                elif transaction.type == TransactionType.TRANSFER:
                    # Add transfers to Monday by default
                    schedule["Monday"].append({
                        "name": transaction.name,
                        "amount": transaction.amount,
                        "type": transaction.type.value,
                        "notes": transaction.notes
                    })
        
        return schedule
    
    def get_summary(self) -> Dict:
        """Get a summary of the weekly budget."""
        return {
            "weekly_income": {
                "earnin": 600.00,
                "snap_on": 400.00,
                "chase_transfer": 180.00,
                "total": self.get_weekly_income()
            },
            "weekly_expenses": {
                "gas": 137.50,  # $55 every 2 days for 5 days
                "food": 125.00,
                "pets": 60.00,
                "total": self.get_weekly_expenses()
            },
            "weekly_balance": self.get_weekly_balance(),
            "daily_average_balance": self.get_weekly_balance() / 7,
            "schedule": self.generate_weekly_schedule()
        }


def display_budget_summary():
    """Display a formatted budget summary."""
    config = WeeklyBudgetConfig()
    summary = config.get_summary()
    
    print("\n" + "="*50)
    print("WEEKLY BUDGET SUMMARY")
    print("="*50)
    
    print("\n📈 WEEKLY INCOME:")
    print(f"  • EarnIn: ${summary['weekly_income']['earnin']:,.2f}")
    print(f"  • Snap-On: ${summary['weekly_income']['snap_on']:,.2f} (reserves Thu → clears Fri)")
    print(f"  • Chase Transfer: ${summary['weekly_income']['chase_transfer']:,.2f}")
    print(f"  • TOTAL: ${summary['weekly_income']['total']:,.2f}")
    
    print("\n📉 WEEKLY EXPENSES:")
    print(f"  • Gas: ${summary['weekly_expenses']['gas']:,.2f} ($55 every 2 days, Tue-Sat)")
    print(f"  • Food: ${summary['weekly_expenses']['food']:,.2f}")
    print(f"  • Pets: ${summary['weekly_expenses']['pets']:,.2f}")
    print(f"  • TOTAL: ${summary['weekly_expenses']['total']:,.2f}")
    
    print("\n💰 BALANCE:")
    print(f"  • Weekly Balance: ${summary['weekly_balance']:,.2f}")
    print(f"  • Daily Average: ${summary['daily_average_balance']:,.2f}")
    
    print("\n📅 WEEKLY SCHEDULE:")
    for day, transactions in summary['schedule'].items():
        if transactions:
            print(f"\n  {day}:")
            for t in transactions:
                symbol = "+" if t['type'] in ['income', 'transfer'] else "-"
                print(f"    {symbol} {t['name']}: ${t['amount']:,.2f}")
                if 'clears' in t and t['clears'] != "Same day":
                    print(f"      (clears {t['clears']})")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    display_budget_summary()
