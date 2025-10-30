"""Financial forecasting engine

Predicts daily balances, upcoming bills, and provides budget estimates.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from tracker.core.models import CashFlowEvent, DailyEntry, User
from tracker.services.cashflow_config import CashFlowConfig, RecurringWeeklyRule


def get_latest_balance(db: Session, user_id: int) -> tuple[Optional[Decimal], Optional[Decimal]]:
    """Get the most recent bank balance and cash on hand
    
    Returns:
        Tuple of (bank_balance, cash_on_hand) or (None, None)
    """
    latest_entry = (
        db.query(DailyEntry)
        .filter_by(user_id=user_id)
        .order_by(DailyEntry.date.desc())
        .first()
    )
    
    if latest_entry:
        return latest_entry.bank_balance, latest_entry.cash_on_hand
    
    return None, None


def get_next_payday(config: CashFlowConfig, from_date: date) -> date:
    """Get the next payday from a given date
    
    Args:
        config: Cash flow configuration
        from_date: Start date
    
    Returns:
        Next payday date
    """
    # Map day names to weekday numbers
    day_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    target_weekday = day_map.get(config.payroll.payday.lower(), 3)  # Default Thursday
    
    # Calculate days until next payday
    current_weekday = from_date.weekday()
    days_ahead = (target_weekday - current_weekday) % 7
    
    if days_ahead == 0:
        # If today is payday, return today
        return from_date
    
    return from_date + timedelta(days=days_ahead)


def calculate_gas_fills(start_date: date, end_date: date, config: CashFlowConfig) -> list[tuple[date, float]]:
    """Calculate gas fill dates and costs
    
    Args:
        start_date: Start of period
        end_date: End of period
        config: Configuration with gas fill frequency
    
    Returns:
        List of (date, cost) tuples
    """
    fills = []
    current_date = start_date

    while current_date <= end_date:
        fills.append((current_date, config.essentials.gas.fill_cost_usd))
        current_date += timedelta(days=config.essentials.gas.fill_frequency_days)
    
    return fills


def forecast_week(
    db: Session,
    user_id: int,
    config: CashFlowConfig,
    start_date: date,
    starting_bank_balance: Optional[Decimal] = None,
    starting_cash: Optional[Decimal] = None,
) -> dict:
    """Generate a weekly forecast with daily breakdown
    
    Args:
        db: Database session
        user_id: User ID
        config: Cash flow configuration
        start_date: Week start date (typically Friday)
        starting_bank_balance: Starting bank balance (or fetch from latest entry)
        starting_cash: Starting cash on hand (or fetch from latest entry)
    
    Returns:
        Dict with daily forecasts and summary
    """
    # Get starting balances if not provided
    if starting_bank_balance is None or starting_cash is None:
        bank, cash = get_latest_balance(db, user_id)
        starting_bank_balance = bank or Decimal("0.00")
        starting_cash = cash or Decimal("0.00")
    
    # Initialize daily tracking
    end_date = start_date + timedelta(days=6)  # 7-day week
    daily_forecast = []
    
    current_bank = starting_bank_balance
    current_cash = starting_cash
    
    # Get actual recorded events
    recorded_events = (
        db.query(CashFlowEvent)
        .filter(
            CashFlowEvent.user_id == user_id,
            CashFlowEvent.event_date >= start_date,
            CashFlowEvent.event_date <= end_date,
        )
        .all()
    )
    
    # Organize events by date
    events_by_date = {}
    for event in recorded_events:
        event_date = event.event_date
        if event_date not in events_by_date:
            events_by_date[event_date] = []
        events_by_date[event_date].append(event)
    
    # Calculate gas fills
    gas_fills = calculate_gas_fills(start_date, end_date, config)
    gas_by_date = {d: cost for d, cost in gas_fills}
    
    # Get next payday in this week
    next_payday = get_next_payday(config, start_date)
    
    # Process each day
    current_date = start_date
    while current_date <= end_date:
        day_events = []
        day_total = Decimal("0.00")
        
        # Check for payday
        if current_date == next_payday:
            payday_amount = Decimal(str(config.payroll.net_pay_usd))
            day_events.append({
                "type": "income",
                "description": "Paycheck",
                "amount": -payday_amount,  # Negative = inflow
                "balance_after": current_bank + payday_amount,
            })
            current_bank += payday_amount
            day_total -= payday_amount
        
        # Process weekly recurring items
        day_name = current_date.strftime("%A")
        
        # Apply weekly recurring bills
        for item_name, item_amount in config.recurring_weekly.__dict__.items():
            # Check if this item should apply today
            apply = False

            if item_name == "EarnIn" and day_name == "Thursday":
                # EarnIn repayment on Thursday
                apply = True
            elif item_name == "SnapOn" and config.recurring_weekly_rules.get(item_name, RecurringWeeklyRule()).reserved_then_clears:
                # Thursday: Reserve funds (move to Acorns)
                if day_name == "Thursday":
                    day_events.append({
                        "type": "transfer",
                        "description": f"{item_name} Reserved (→ Acorns)",
                        "amount": Decimal(str(item_amount)),
                        "balance_after": current_bank - Decimal(str(item_amount)),
                        "note": "Reserved, clears Friday"
                    })
                    current_bank -= Decimal(str(item_amount))
                    day_total += Decimal(str(item_amount))
                    continue  # Skip normal processing
                # Friday: Actual autopull (but don't double-count)
                elif day_name == "Friday":
                    day_events.append({
                        "type": "bill",
                        "description": f"{item_name} Cleared",
                        "amount": Decimal("0.00"),  # Already counted on Thursday
                        "balance_after": current_bank,
                        "note": "Already reserved Thu"
                    })
                    continue  # Don't affect balance
            elif item_name == "ChaseTransfer" and day_name == "Thursday":
                apply = True

            if apply:
                bill_amount = Decimal(str(item_amount))
                day_events.append({
                    "type": "bill",
                    "description": item_name,
                    "amount": bill_amount,
                    "balance_after": current_bank - bill_amount,
                })
                current_bank -= bill_amount
                day_total += bill_amount
        
        # Apply gas fills
        if current_date in gas_by_date:
            gas_cost = Decimal(str(gas_by_date[current_date]))
            day_events.append({
                "type": "essential",
                "description": "Gas Fill",
                "amount": gas_cost,
                "balance_after": current_bank - gas_cost,
            })
            current_bank -= gas_cost
            day_total += gas_cost
        
        # Apply food budget (split evenly across week)
        daily_food = Decimal(str(config.essentials.food_weekly_usd)) / 7
        day_events.append({
            "type": "essential",
            "description": "Food (daily avg)",
            "amount": daily_food,
            "balance_after": current_bank - daily_food,
        })
        current_bank -= daily_food
        day_total += daily_food
        
        # Check for recorded actual events
        if current_date in events_by_date:
            for event in events_by_date[current_date]:
                event_amount = Decimal(event.amount_cents) / 100
                day_events.append({
                    "type": "recorded",
                    "description": f"{event.event_type}: {event.category or event.provider or 'misc'}",
                    "amount": event_amount,
                    "balance_after": current_bank - event_amount,
                    "note": event.memo or ""
                })
                current_bank -= event_amount
                day_total += event_amount
        
        # Store daily forecast
        daily_forecast.append({
            "date": current_date,
            "day_name": day_name,
            "events": day_events,
            "day_total": day_total,
            "end_balance_bank": current_bank,
            "end_balance_cash": current_cash,  # Cash tracking TBD
        })
        
        current_date += timedelta(days=1)
    
    # Calculate summary
    week_total_income = Decimal(str(config.payroll.net_pay_usd))
    week_total_expenses = sum(day["day_total"] for day in daily_forecast)
    
    return {
        "period": {"start": start_date, "end": end_date},
        "starting_balances": {
            "bank": starting_bank_balance,
            "cash": starting_cash,
        },
        "ending_balances": {
            "bank": current_bank,
            "cash": current_cash,
        },
        "daily_forecast": daily_forecast,
        "summary": {
            "total_income": week_total_income,
            "total_expenses": week_total_expenses,
            "net_change": week_total_income - week_total_expenses,
        },
    }


def tomorrow_budget(
    db: Session,
    user_id: int,
    config: CashFlowConfig,
) -> dict:
    """Calculate tomorrow's budget estimate
    
    Args:
        db: Database session
        user_id: User ID
        config: Cash flow configuration
    
    Returns:
        Dict with tomorrow's budget breakdown
    """
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_name = tomorrow.strftime("%A")
    
    # Get current balance
    bank, cash = get_latest_balance(db, user_id)
    bank = bank or Decimal("0.00")
    cash = cash or Decimal("0.00")
    
    # Calculate expected events tomorrow
    expected_events = []
    total_expected = Decimal("0.00")
    
    # Check for payday
    next_payday = get_next_payday(config, date.today())
    if next_payday == tomorrow:
        payday_amount = Decimal(str(config.payroll.net_pay_usd))
        expected_events.append({
            "type": "income",
            "description": "Paycheck",
            "amount": -payday_amount,
        })
        total_expected -= payday_amount
    
    # Check for recurring bills tomorrow
    for item_name, item_amount in config.recurring_weekly.__dict__.items():
        applies = False

        if item_name == "EarnIn" and tomorrow_name == "Thursday":
            applies = True
        elif item_name == "SnapOn":
            if tomorrow_name == "Thursday":
                expected_events.append({
                    "type": "transfer",
                    "description": f"{item_name} Reserve → Acorns",
                    "amount": Decimal(str(item_amount)),
                })
                total_expected += Decimal(str(item_amount))
                continue
            elif tomorrow_name == "Friday":
                expected_events.append({
                    "type": "note",
                    "description": f"{item_name} clears (already reserved)",
                    "amount": Decimal("0.00"),
                })
                continue
        elif item_name == "ChaseTransfer" and tomorrow_name == "Thursday":
            applies = True

        if applies:
            expected_events.append({
                "type": "bill",
                "description": item_name,
                "amount": Decimal(str(item_amount)),
            })
            total_expected += Decimal(str(item_amount))
    
    # Check for gas fill tomorrow
    last_fill_date = date.today() - timedelta(days=config.essentials.gas.fill_frequency_days)
    gas_fills = calculate_gas_fills(last_fill_date, tomorrow, config)
    if any(d == tomorrow for d, _ in gas_fills):
        expected_events.append({
            "type": "essential",
            "description": "Gas Fill",
            "amount": Decimal(str(config.essentials.gas.fill_cost_usd)),
        })
        total_expected += Decimal(str(config.essentials.gas.fill_cost_usd))
    
    # Daily food average
    daily_food = Decimal(str(config.essentials.food_weekly_usd)) / 7
    expected_events.append({
        "type": "essential",
        "description": "Food (est.)",
        "amount": daily_food,
    })
    total_expected += daily_food
    
    # Calculate projected end balance
    projected_bank = bank - total_expected
    
    return {
        "date": tomorrow,
        "day_name": tomorrow_name,
        "current_balances": {
            "bank": bank,
            "cash": cash,
        },
        "expected_events": expected_events,
        "total_expected_outflow": total_expected,
        "projected_end_balance": projected_bank,
        "available_for_discretionary": max(Decimal("0.00"), projected_bank - Decimal("50.00")),  # Keep $50 buffer
    }
