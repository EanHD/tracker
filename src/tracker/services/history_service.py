"""History service - List and filter entries"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from tracker.core.models import DailyEntry


class HistoryService:
    """Service for historical entry queries and statistics"""

    def __init__(self, db: Session):
        self.db = db

    def list_entries(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "date",
        order_desc: bool = True
    ) -> List[DailyEntry]:
        """
        List entries with filtering and pagination
        
        Args:
            user_id: User ID
            start_date: Filter entries from this date (inclusive)
            end_date: Filter entries to this date (inclusive)
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            order_by: Field to order by (date, stress_level, income_today)
            order_desc: Order descending if True, ascending if False
            
        Returns:
            List of DailyEntry objects
        """
        query = self.db.query(DailyEntry).filter(DailyEntry.user_id == user_id)
        
        # Date filters
        if start_date:
            query = query.filter(DailyEntry.date >= start_date)
        if end_date:
            query = query.filter(DailyEntry.date <= end_date)
        
        # Ordering
        order_field = getattr(DailyEntry, order_by, DailyEntry.date)
        if order_desc:
            query = query.order_by(order_field.desc())
        else:
            query = query.order_by(order_field.asc())
        
        # Pagination
        return query.offset(offset).limit(limit).all()

    def get_statistics(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Calculate statistics for entries in date range
        
        Returns dictionary with aggregated statistics
        """
        query = self.db.query(DailyEntry).filter(DailyEntry.user_id == user_id)
        
        if start_date:
            query = query.filter(DailyEntry.date >= start_date)
        if end_date:
            query = query.filter(DailyEntry.date <= end_date)
        
        entries = query.all()
        
        if not entries:
            return {
                "count": 0,
                "date_range": {"start": start_date, "end": end_date}
            }
        
        # Calculate statistics
        stats = {
            "count": len(entries),
            "date_range": {
                "start": min(e.date for e in entries),
                "end": max(e.date for e in entries)
            },
            "income": {
                "total": sum(e.income_today for e in entries),
                "average": sum(e.income_today for e in entries) / len(entries),
                "max": max(e.income_today for e in entries),
                "min": min(e.income_today for e in entries),
            },
            "bills": {
                "total": sum(e.bills_due_today for e in entries),
                "average": sum(e.bills_due_today for e in entries) / len(entries),
            },
            "spending": {
                "food_total": sum(e.food_spent for e in entries),
                "gas_total": sum(e.gas_spent for e in entries),
                "total": sum(e.food_spent + e.gas_spent for e in entries),
                "average": sum(e.food_spent + e.gas_spent for e in entries) / len(entries),
            },
            "work": {
                "total_hours": sum(e.hours_worked for e in entries),
                "average_hours": sum(e.hours_worked for e in entries) / len(entries),
                "side_income_total": sum(e.side_income for e in entries),
            },
            "wellbeing": {
                "average_stress": sum(e.stress_level for e in entries) / len(entries),
                "max_stress": max(e.stress_level for e in entries),
                "min_stress": min(e.stress_level for e in entries),
            }
        }
        
        # Net income (income - bills - spending)
        stats["net_income"] = {
            "total": stats["income"]["total"] - stats["bills"]["total"] - stats["spending"]["total"],
            "average": stats["income"]["average"] - stats["bills"]["average"] - stats["spending"]["average"],
        }
        
        return stats

    def get_trends(
        self,
        user_id: int,
        days: int = 30,
        metric: str = "stress_level"
    ) -> List[Dict]:
        """
        Get trend data for a specific metric over time
        
        Args:
            user_id: User ID
            days: Number of days to look back
            metric: Field to track (stress_level, income_today, etc.)
            
        Returns:
            List of {date, value} dictionaries
        """
        start_date = date.today() - timedelta(days=days)
        
        entries = self.list_entries(
            user_id,
            start_date=start_date,
            order_by="date",
            order_desc=False,
            limit=days
        )
        
        trend_data = []
        for entry in entries:
            value = getattr(entry, metric, None)
            if value is not None:
                trend_data.append({
                    "date": entry.date.isoformat(),
                    "value": float(value) if isinstance(value, Decimal) else value
                })
        
        return trend_data

    def search_entries(
        self,
        user_id: int,
        query: str,
        limit: int = 50
    ) -> List[DailyEntry]:
        """
        Search entries by notes or priority text
        
        Args:
            user_id: User ID
            query: Search term
            limit: Maximum results
            
        Returns:
            List of matching entries
        """
        search_term = f"%{query}%"
        
        results = self.db.query(DailyEntry).filter(
            and_(
                DailyEntry.user_id == user_id,
                (DailyEntry.notes.ilike(search_term)) |
                (DailyEntry.priority.ilike(search_term))
            )
        ).order_by(DailyEntry.date.desc()).limit(limit).all()
        
        return results

    def get_recent_entries(self, user_id: int, count: int = 7) -> List[DailyEntry]:
        """Get most recent entries"""
        return self.list_entries(
            user_id,
            limit=count,
            order_by="date",
            order_desc=True
        )

    def get_streak_info(self, user_id: int) -> Dict:
        """
        Calculate current logging streak
        
        Returns:
            Dictionary with current_streak, longest_streak, last_entry_date
        """
        entries = self.db.query(DailyEntry).filter(
            DailyEntry.user_id == user_id
        ).order_by(DailyEntry.date.desc()).all()
        
        if not entries:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "last_entry_date": None
            }
        
        # Calculate current streak
        current_streak = 0
        check_date = date.today()
        
        for entry in entries:
            if entry.date == check_date or entry.date == check_date - timedelta(days=1):
                current_streak += 1
                check_date = entry.date - timedelta(days=1)
            else:
                break
        
        # Calculate longest streak
        longest_streak = 1
        current_run = 1
        
        for i in range(len(entries) - 1):
            if (entries[i].date - entries[i+1].date).days == 1:
                current_run += 1
                longest_streak = max(longest_streak, current_run)
            else:
                current_run = 1
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_entry_date": entries[0].date if entries else None,
            "total_entries": len(entries)
        }
