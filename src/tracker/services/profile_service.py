"""User Profile Service for managing personalized context"""

import json
from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from tracker.core.models import User, UserProfile


class ProfileService:
    """Service for managing user profiles and context"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_profile(self, user_id: int) -> UserProfile:
        """Get existing profile or create new one"""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile
    
    def update_basic_info(
        self,
        user_id: int,
        nickname: Optional[str] = None,
        preferred_tone: Optional[str] = None,
        context_depth: Optional[str] = None
    ) -> UserProfile:
        """Update basic profile information"""
        profile = self.get_or_create_profile(user_id)
        
        if nickname is not None:
            profile.nickname = nickname
        if preferred_tone is not None:
            profile.preferred_tone = preferred_tone
        if context_depth is not None:
            profile.context_depth = context_depth
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_work_info(self, user_id: int, work_data: Dict[str, Any]) -> UserProfile:
        """
        Update work information
        
        Expected work_data structure:
        {
            "job_title": str,
            "employment_type": "hourly" | "salary",
            "pay_schedule": "weekly" | "biweekly" | "monthly",
            "typical_hours_per_week": float,
            "commute_minutes": int,
            "side_gigs": [{"name": str, "typical_income": float}]
        }
        """
        profile = self.get_or_create_profile(user_id)
        current = profile.work_info or {}
        current.update(work_data)
        profile.work_info = current
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_financial_info(self, user_id: int, financial_data: Dict[str, Any]) -> UserProfile:
        """
        Update financial information
        
        Expected financial_data structure:
        {
            "monthly_income": float,
            "income_sources": [{"source": str, "amount": float}],
            "recurring_bills": [{"name": str, "amount": float, "due_day": int}],
            "debts": [{"name": str, "balance": float, "min_payment": float, "interest_rate": float}]
        }
        """
        profile = self.get_or_create_profile(user_id)
        current = profile.financial_info or {}
        current.update(financial_data)
        profile.financial_info = current
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_goals(self, user_id: int, goals_data: Dict[str, Any]) -> UserProfile:
        """
        Update goals
        
        Expected goals_data structure:
        {
            "short_term": [{"goal": str, "target_date": str, "target_amount": float}],
            "long_term": [{"goal": str, "target_date": str, "target_amount": float}]
        }
        """
        profile = self.get_or_create_profile(user_id)
        current = profile.goals or {}
        current.update(goals_data)
        profile.goals = current
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_lifestyle(self, user_id: int, lifestyle_data: Dict[str, Any]) -> UserProfile:
        """
        Update lifestyle information
        
        Expected lifestyle_data structure:
        {
            "gym_membership": bool,
            "gym_cost": float,
            "avg_gas_per_week": float,
            "meals_out_per_week": int,
            "avg_meal_cost": float,
            "other_subscriptions": [{"name": str, "cost": float}]
        }
        """
        profile = self.get_or_create_profile(user_id)
        current = profile.lifestyle or {}
        current.update(lifestyle_data)
        profile.lifestyle = current
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_emotional_context(
        self,
        user_id: int,
        stress_triggers: Optional[list] = None,
        calming_activities: Optional[list] = None,
        baseline_energy: Optional[int] = None,
        baseline_stress: Optional[float] = None
    ) -> UserProfile:
        """Update emotional context and wellbeing information"""
        profile = self.get_or_create_profile(user_id)
        
        if stress_triggers is not None:
            profile.stress_triggers = json.dumps(stress_triggers)
        if calming_activities is not None:
            profile.calming_activities = json.dumps(calming_activities)
        if baseline_energy is not None:
            profile.baseline_energy = baseline_energy
        if baseline_stress is not None:
            profile.baseline_stress = baseline_stress
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def record_detected_pattern(self, user_id: int, pattern_type: str, pattern_data: Any) -> UserProfile:
        """
        Record AI-detected patterns
        
        This is called by the AI service when it notices patterns in user behavior
        """
        profile = self.get_or_create_profile(user_id)
        patterns = profile.detected_patterns or {}
        
        if pattern_type not in patterns:
            patterns[pattern_type] = []
        
        patterns[pattern_type].append({
            "data": pattern_data,
            "detected_at": datetime.utcnow().isoformat(),
            "frequency": 1
        })
        
        # Keep only last 10 of each pattern type
        patterns[pattern_type] = patterns[pattern_type][-10:]
        
        profile.detected_patterns = patterns
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def update_entry_stats(self, user_id: int, entry_date: date) -> UserProfile:
        """Update entry statistics (called when user makes an entry)"""
        profile = self.get_or_create_profile(user_id)
        
        profile.total_entries += 1
        
        # Calculate streak
        if profile.last_entry_date:
            days_diff = (entry_date - profile.last_entry_date).days
            if days_diff == 1:
                profile.entry_streak += 1
            elif days_diff > 1:
                profile.entry_streak = 1
        else:
            profile.entry_streak = 1
        
        if profile.entry_streak > profile.longest_streak:
            profile.longest_streak = profile.entry_streak
        
        profile.last_entry_date = entry_date
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def needs_monthly_checkin(self, user_id: int) -> bool:
        """Check if user needs a monthly check-in"""
        profile = self.get_or_create_profile(user_id)
        
        if not profile.last_monthly_checkin:
            return True
        
        # Check if it's been more than 30 days
        days_since_checkin = (date.today() - profile.last_monthly_checkin).days
        return days_since_checkin >= 30
    
    def mark_monthly_checkin_complete(self, user_id: int) -> UserProfile:
        """Mark monthly check-in as complete"""
        profile = self.get_or_create_profile(user_id)
        profile.last_monthly_checkin = date.today()
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
    
    def get_ai_context(self, user_id: int) -> Dict[str, Any]:
        """
        Generate context dictionary for AI prompts
        
        This is used by the AI service to personalize feedback
        """
        profile = self.get_or_create_profile(user_id)
        
        context = {
            "nickname": profile.nickname,
            "preferred_tone": profile.preferred_tone or "casual",
            "context_depth": profile.context_depth,
            "baseline_energy": profile.baseline_energy,
            "baseline_stress": profile.baseline_stress,
            "total_entries": profile.total_entries,
            "entry_streak": profile.entry_streak,
            "longest_streak": profile.longest_streak,
        }
        
        # Add stress triggers and calming activities if available
        if profile.stress_triggers:
            context["stress_triggers"] = json.loads(profile.stress_triggers)
        if profile.calming_activities:
            context["calming_activities"] = json.loads(profile.calming_activities)
        
        # Include deeper context based on privacy settings
        if profile.context_depth in ["personal", "deep"]:
            context["work_info"] = profile.work_info
            context["financial_info"] = profile.financial_info
            context["goals"] = profile.goals
            context["lifestyle"] = profile.lifestyle
        
        if profile.context_depth == "deep":
            context["detected_patterns"] = profile.detected_patterns
        
        return context
    
    def get_profile_summary(self, user_id: int) -> Dict[str, Any]:
        """Get human-readable profile summary"""
        profile = self.get_or_create_profile(user_id)
        
        summary = {
            "basic_info": {
                "nickname": profile.nickname or "Not set",
                "preferred_tone": profile.preferred_tone or "casual",
                "context_depth": profile.context_depth,
            },
            "stats": {
                "total_entries": profile.total_entries,
                "current_streak": profile.entry_streak,
                "longest_streak": profile.longest_streak,
                "last_entry": profile.last_entry_date.isoformat() if profile.last_entry_date else None,
            },
            "emotional_baseline": {
                "energy": profile.baseline_energy,
                "stress": profile.baseline_stress,
            }
        }
        
        # Add optional sections based on what's filled out
        if profile.work_info:
            summary["work"] = profile.work_info
        
        if profile.financial_info:
            summary["financial"] = profile.financial_info
        
        if profile.goals:
            summary["goals"] = profile.goals
        
        if profile.lifestyle:
            summary["lifestyle"] = profile.lifestyle
        
        return summary
