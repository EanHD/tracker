"""
Gamification Service - Achievements, badges, and motivational elements

Provides streak tracking, achievement unlocking, and progress milestones.
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from tracker.services.history_service import HistoryService


@dataclass
class Achievement:
    """Represents an unlocked achievement"""
    id: str
    name: str
    description: str
    icon: str
    unlocked_at: Optional[date] = None
    progress: float = 0.0  # 0.0 to 1.0


class GamificationService:
    """Service for gamification features"""
    
    # Define available achievements
    ACHIEVEMENTS = {
        "first_entry": {
            "name": "Getting Started",
            "description": "Created your first entry",
            "icon": "🎯",
            "threshold": 1
        },
        "week_streak": {
            "name": "Week Warrior",
            "description": "Logged entries for 7 consecutive days",
            "icon": "🔥",
            "threshold": 7
        },
        "month_streak": {
            "name": "Monthly Master",
            "description": "Logged entries for 30 consecutive days",
            "icon": "⭐",
            "threshold": 30
        },
        "hundred_day": {
            "name": "Century Club",
            "description": "Logged entries for 100 consecutive days",
            "icon": "💯",
            "threshold": 100
        },
        "total_50": {
            "name": "Halfway There",
            "description": "Created 50 total entries",
            "icon": "📈",
            "threshold": 50
        },
        "total_100": {
            "name": "Centennial",
            "description": "Created 100 total entries",
            "icon": "🏆",
            "threshold": 100
        },
        "total_365": {
            "name": "Year of Tracking",
            "description": "Created 365 total entries",
            "icon": "👑",
            "threshold": 365
        },
        "low_stress_week": {
            "name": "Zen Master",
            "description": "Maintained stress level ≤3 for a week",
            "icon": "🧘",
            "threshold": 7
        },
        "financial_positive": {
            "name": "In the Black",
            "description": "30 days with positive income-expense balance",
            "icon": "💰",
            "threshold": 30
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.history_service = HistoryService(db)
    
    def get_achievements(self, user_id: int) -> List[Achievement]:
        """
        Get all achievements with unlock status
        
        Args:
            user_id: User ID
            
        Returns:
            List of Achievement objects
        """
        achievements = []
        
        # Get user stats
        entries = self.history_service.list_entries(user_id, limit=10000)
        total_entries = len(entries)
        
        streak_info = self.history_service.get_streak_info(user_id)
        current_streak = streak_info.get("current_streak", 0)
        longest_streak = streak_info.get("longest_streak", 0)
        
        # Check each achievement
        for achievement_id, achievement_data in self.ACHIEVEMENTS.items():
            unlocked = False
            progress = 0.0
            
            if achievement_id == "first_entry":
                unlocked = total_entries >= 1
                progress = min(1.0, total_entries / 1.0)
            
            elif achievement_id == "week_streak":
                unlocked = longest_streak >= 7
                progress = min(1.0, current_streak / 7.0)
            
            elif achievement_id == "month_streak":
                unlocked = longest_streak >= 30
                progress = min(1.0, current_streak / 30.0)
            
            elif achievement_id == "hundred_day":
                unlocked = longest_streak >= 100
                progress = min(1.0, current_streak / 100.0)
            
            elif achievement_id == "total_50":
                unlocked = total_entries >= 50
                progress = min(1.0, total_entries / 50.0)
            
            elif achievement_id == "total_100":
                unlocked = total_entries >= 100
                progress = min(1.0, total_entries / 100.0)
            
            elif achievement_id == "total_365":
                unlocked = total_entries >= 365
                progress = min(1.0, total_entries / 365.0)
            
            elif achievement_id == "low_stress_week":
                # Check last 7 entries for low stress
                recent = entries[:7] if len(entries) >= 7 else entries
                low_stress_count = sum(1 for e in recent if e.stress_level <= 3)
                unlocked = low_stress_count >= 7
                progress = min(1.0, low_stress_count / 7.0)
            
            elif achievement_id == "financial_positive":
                # Count days with positive balance (simplified)
                positive_days = sum(
                    1 for e in entries 
                    if (e.income_today or 0) > (e.bills_due_today or 0)
                )
                unlocked = positive_days >= 30
                progress = min(1.0, positive_days / 30.0)
            
            achievements.append(Achievement(
                id=achievement_id,
                name=achievement_data["name"],
                description=achievement_data["description"],
                icon=achievement_data["icon"],
                unlocked_at=date.today() if unlocked else None,
                progress=progress
            ))
        
        return achievements
    
    def get_streak_message(self, streak: int) -> str:
        """
        Get motivational message based on streak
        
        Args:
            streak: Current streak count
            
        Returns:
            Motivational message
        """
        if streak == 0:
            return "Start your streak today!"
        elif streak == 1:
            return "Great start! Keep it going!"
        elif streak < 7:
            return f"{streak} days strong! 🔥"
        elif streak == 7:
            return f"🎉 One week streak! Amazing!"
        elif streak < 30:
            return f"{streak} day streak! You're on fire! 🔥"
        elif streak == 30:
            return f"🌟 30 days! You're a tracking superstar!"
        elif streak < 100:
            return f"{streak} days! Incredible dedication! 💪"
        elif streak == 100:
            return f"💯 100 DAY STREAK! Legendary!"
        else:
            return f"👑 {streak} day streak! Absolutely legendary!"
    
    def get_next_milestone(self, user_id: int) -> Optional[dict]:
        """
        Get the next achievement milestone to unlock
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with milestone info or None
        """
        achievements = self.get_achievements(user_id)
        
        # Find next unearned achievement with highest progress
        locked = [a for a in achievements if a.unlocked_at is None]
        if not locked:
            return None
        
        # Sort by progress (descending)
        locked.sort(key=lambda a: a.progress, reverse=True)
        next_achievement = locked[0]
        
        return {
            "name": next_achievement.name,
            "description": next_achievement.description,
            "icon": next_achievement.icon,
            "progress": next_achievement.progress,
            "progress_percent": int(next_achievement.progress * 100)
        }
    
    def get_summary(self, user_id: int) -> dict:
        """
        Get gamification summary for display
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with streak, achievements, next milestone
        """
        streak_info = self.history_service.get_streak_info(user_id)
        achievements = self.get_achievements(user_id)
        
        unlocked_count = sum(1 for a in achievements if a.unlocked_at is not None)
        total_count = len(achievements)
        
        return {
            "streak": {
                "current": streak_info.get("current_streak", 0),
                "longest": streak_info.get("longest_streak", 0),
                "message": self.get_streak_message(streak_info.get("current_streak", 0))
            },
            "achievements": {
                "unlocked": unlocked_count,
                "total": total_count,
                "percent": int((unlocked_count / total_count) * 100) if total_count > 0 else 0
            },
            "next_milestone": self.get_next_milestone(user_id),
            "total_entries": streak_info.get("total_entries", 0)
        }
