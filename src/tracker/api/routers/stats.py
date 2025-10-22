"""Statistics API endpoints"""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from tracker.api.dependencies import get_current_user, get_db
from tracker.core.models import User
from tracker.services.history_service import HistoryService

router = APIRouter(prefix="/api/v1/stats", tags=["statistics"])


@router.get("/summary")
def get_summary(
    days: int = Query(30, description="Number of days to analyze"),
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregate statistics for a time period
    
    Returns financial and wellbeing metrics including:
    - Total and average income
    - Total and average bills
    - Spending breakdown
    - Work hours
    - Stress levels
    - Net income
    """
    history_service = HistoryService(db)
    
    # Determine date range
    if not start_date and not end_date:
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)
    elif not start_date:
        start_date = end_date - timedelta(days=days - 1)
    elif not end_date:
        end_date = date.today()
    
    statistics = history_service.get_statistics(
        current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return statistics


@router.get("/trends")
def get_trends(
    metric: str = Query("stress_level", description="Metric to track (stress_level, income_today, hours_worked)"),
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trend data for a specific metric over time
    
    Returns time series data for visualization
    """
    history_service = HistoryService(db)
    
    trend_data = history_service.get_trends(
        current_user.id,
        days=days,
        metric=metric
    )
    
    return {
        "metric": metric,
        "days": days,
        "data": trend_data
    }


@router.get("/streak")
def get_streak(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get logging streak information
    
    Returns:
    - Current streak (consecutive days)
    - Longest streak ever
    - Last entry date
    - Total entries
    """
    history_service = HistoryService(db)
    
    streak_info = history_service.get_streak_info(current_user.id)
    
    return streak_info
