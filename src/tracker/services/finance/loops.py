"""Cash flow loop analytics

Pure functions for analyzing cash flow events, loops, and weekly patterns.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from tracker.core.models import CashFlowEvent
from tracker.services.cashflow_config import CashFlowConfig, LoopConfig


def get_week_window(
    any_date: date, 
    week_start: str = "FRI", 
    payday_is_thursday: bool = True
) -> tuple[date, date]:
    """Get the week window (start_date, end_date) containing any_date
    
    Args:
        any_date: Any date within the week
        week_start: Day of week to start (e.g., "FRI", "MON")
        payday_is_thursday: If True, uses Thu-night payroll cadence (Fri→Thu)
    
    Returns:
        Tuple of (start_date, end_date) inclusive
    
    Examples:
        >>> get_week_window(date(2025, 10, 20), "FRI", True)
        (date(2025, 10, 17), date(2025, 10, 23))  # Fri→Thu
    """
    # Map day names to weekday numbers (0=Monday, 6=Sunday)
    day_map = {
        "MON": 0, "TUE": 1, "WED": 2, "THU": 3,
        "FRI": 4, "SAT": 5, "SUN": 6
    }
    
    start_weekday = day_map.get(week_start.upper(), 4)  # Default to Friday
    
    # Find the most recent week_start day
    current_weekday = any_date.weekday()
    days_since_start = (current_weekday - start_weekday) % 7
    
    start_date = any_date - timedelta(days=days_since_start)
    end_date = start_date + timedelta(days=6)  # 7-day window
    
    return start_date, end_date


def get_events_in_range(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
    event_types: Optional[list[str]] = None,
    providers: Optional[list[str]] = None,
) -> list[CashFlowEvent]:
    """Get cash flow events within date range with optional filters
    
    Args:
        db: Database session
        user_id: User ID
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        event_types: Optional list of event types to filter
        providers: Optional list of providers to filter
    
    Returns:
        List of CashFlowEvent objects
    """
    query = db.query(CashFlowEvent).filter(
        CashFlowEvent.user_id == user_id,
        CashFlowEvent.event_date >= start_date,
        CashFlowEvent.event_date <= end_date,
    )
    
    if event_types:
        query = query.filter(CashFlowEvent.event_type.in_(event_types))
    
    if providers:
        query = query.filter(CashFlowEvent.provider.in_(providers))
    
    return query.order_by(CashFlowEvent.event_date).all()


def sum_events(
    events: list[CashFlowEvent],
    event_types: Optional[list[str]] = None,
    providers: Optional[list[str]] = None,
) -> int:
    """Sum event amounts (in cents) with optional filters
    
    Args:
        events: List of CashFlowEvent objects
        event_types: Optional list of event types to include
        providers: Optional list of providers to include
    
    Returns:
        Total amount in cents (positive = outflow, negative = inflow)
    """
    total = 0
    
    for event in events:
        # Apply filters
        if event_types and event.event_type not in event_types:
            continue
        if providers and event.provider not in providers:
            continue
        
        total += event.amount_cents
    
    return total


def is_event_in_loop(event: CashFlowEvent, loop: LoopConfig) -> bool:
    """Check if an event belongs to a loop
    
    Args:
        event: CashFlowEvent to check
        loop: LoopConfig definition
    
    Returns:
        True if event matches any of the loop's includes
    """
    for include in loop.includes:
        if event.event_type == include.event_type:
            # If provider is specified in include, it must match
            if include.provider is None or event.provider == include.provider:
                return True
    
    return False


def filter_loop_events(
    events: list[CashFlowEvent],
    loop: LoopConfig,
) -> list[CashFlowEvent]:
    """Filter events that belong to a specific loop
    
    Args:
        events: List of CashFlowEvent objects
        loop: LoopConfig definition
    
    Returns:
        List of events in the loop
    """
    return [event for event in events if is_event_in_loop(event, loop)]


def summarize_loops(
    db: Session,
    user_id: int,
    config: CashFlowConfig,
    start_date: date,
    end_date: date,
) -> dict:
    """Summarize loop activity for a period
    
    Args:
        db: Database session
        user_id: User ID
        config: CashFlowConfig with loop definitions
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
    
    Returns:
        Dict with loop summaries:
        {
            "loop_name": {
                "events": [...],
                "total_cents": int,
                "inflow_cents": int,  # negative amounts
                "outflow_cents": int,  # positive amounts
                "used": bool,
            }
        }
    """
    # Get all events in range
    events = get_events_in_range(db, user_id, start_date, end_date)
    
    summaries = {}
    
    for loop in config.loops:
        loop_events = filter_loop_events(events, loop)
        
        inflow = sum(e.amount_cents for e in loop_events if e.amount_cents < 0)
        outflow = sum(e.amount_cents for e in loop_events if e.amount_cents > 0)
        
        summaries[loop.name] = {
            "events": loop_events,
            "total_cents": inflow + outflow,
            "inflow_cents": inflow,
            "outflow_cents": outflow,
            "used": len(loop_events) > 0,
        }
    
    return summaries


def end_of_week_cash(
    db: Session,
    user_id: int,
    config: CashFlowConfig,
    start_date: date,
    end_date: date,
    starting_balance_cents: int,
    include_loops: bool = True,
) -> int:
    """Calculate end-of-week cash with or without loops
    
    Args:
        db: Database session
        user_id: User ID
        config: CashFlowConfig with loop definitions
        start_date: Week start date
        end_date: Week end date
        starting_balance_cents: Starting balance in cents
        include_loops: If False, excludes loop inflows (shows true strain)
    
    Returns:
        End of week balance in cents
    """
    events = get_events_in_range(db, user_id, start_date, end_date)
    
    balance = starting_balance_cents
    
    # Get all loop events if we need to exclude them
    loop_inflow_events = set()
    if not include_loops:
        for loop in config.loops:
            loop_events = filter_loop_events(events, loop)
            # Only exclude inflows (negative amounts)
            for event in loop_events:
                if event.amount_cents < 0:  # Inflow
                    loop_inflow_events.add(event.id)
    
    # Sum all events
    for event in events:
        # Skip loop inflows if include_loops=False
        if not include_loops and event.id in loop_inflow_events:
            continue
        
        # Negative = inflow (add to balance), Positive = outflow (subtract from balance)
        balance -= event.amount_cents
    
    return balance


def get_loop_delta_vs_prior_week(
    db: Session,
    user_id: int,
    config: CashFlowConfig,
    loop_name: str,
    current_period: tuple[date, date],
    prior_period: tuple[date, date],
) -> dict:
    """Compare loop usage between two weeks
    
    Args:
        db: Database session
        user_id: User ID
        config: CashFlowConfig
        loop_name: Name of loop to analyze
        current_period: (start, end) for current week
        prior_period: (start, end) for prior week
    
    Returns:
        Dict with:
        {
            "current_total_cents": int,
            "prior_total_cents": int,
            "delta_cents": int,
            "direction": "increase"|"decrease"|"same",
        }
    """
    # Find the loop
    loop = next((l for l in config.loops if l.name == loop_name), None)
    if not loop:
        return {
            "current_total_cents": 0,
            "prior_total_cents": 0,
            "delta_cents": 0,
            "direction": "same",
        }
    
    # Get events for both periods
    current_events = get_events_in_range(
        db, user_id, current_period[0], current_period[1]
    )
    prior_events = get_events_in_range(
        db, user_id, prior_period[0], prior_period[1]
    )
    
    # Filter to loop events
    current_loop = filter_loop_events(current_events, loop)
    prior_loop = filter_loop_events(prior_events, loop)
    
    current_total = sum(e.amount_cents for e in current_loop)
    prior_total = sum(e.amount_cents for e in prior_loop)
    
    delta = current_total - prior_total
    
    if delta > 0:
        direction = "increase"
    elif delta < 0:
        direction = "decrease"
    else:
        direction = "same"
    
    return {
        "current_total_cents": current_total,
        "prior_total_cents": prior_total,
        "delta_cents": delta,
        "direction": direction,
    }


def calculate_weeks_without_loop(
    db: Session,
    user_id: int,
    config: CashFlowConfig,
    loop_name: str,
    end_date: date,
    max_weeks: int = 52,
) -> dict:
    """Calculate streak of weeks without using a loop
    
    Args:
        db: Database session
        user_id: User ID
        config: CashFlowConfig
        loop_name: Name of loop to analyze
        end_date: End date to count backwards from
        max_weeks: Maximum weeks to look back
    
    Returns:
        Dict with:
        {
            "current_streak": int,
            "best_streak": int,
        }
    """
    loop = next((l for l in config.loops if l.name == loop_name), None)
    if not loop:
        return {"current_streak": 0, "best_streak": 0}
    
    current_streak = 0
    best_streak = 0
    temp_streak = 0
    
    # Walk backwards week by week
    for i in range(max_weeks):
        week_end = end_date - timedelta(days=i * 7)
        week_start, week_end = get_week_window(
            week_end, 
            config.payroll.week_start, 
            config.payroll.payday_is_thursday
        )
        
        events = get_events_in_range(db, user_id, week_start, week_end)
        loop_events = filter_loop_events(events, loop)
        
        if len(loop_events) == 0:
            # No loop activity this week
            if i == current_streak:
                current_streak += 1
            temp_streak += 1
            best_streak = max(best_streak, temp_streak)
        else:
            # Loop was used this week
            temp_streak = 0
    
    return {
        "current_streak": current_streak,
        "best_streak": best_streak,
    }


def get_essentials_total(
    events: list[CashFlowEvent],
    essential_categories: set[str],
) -> int:
    """Sum spending on essential categories
    
    Args:
        events: List of CashFlowEvent objects
        essential_categories: Set of category names considered essential
    
    Returns:
        Total spending in cents (positive amount)
    """
    total = 0
    
    for event in events:
        if event.category and event.category in essential_categories:
            # Only count outflows (positive amounts)
            if event.amount_cents > 0:
                total += event.amount_cents
    
    return total


def format_cents_to_usd(cents: int) -> str:
    """Format cents to USD string
    
    Args:
        cents: Amount in cents
    
    Returns:
        Formatted string like "$1,234.56" or "-$1,234.56"
    """
    abs_cents = abs(cents)
    dollars = abs_cents // 100
    cents_part = abs_cents % 100
    
    # Format with commas
    dollars_str = f"{dollars:,}"
    
    result = f"${dollars_str}.{cents_part:02d}"
    
    if cents < 0:
        result = "-" + result
    
    return result
