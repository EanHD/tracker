"""Character Sheet Service - Builds and maintains personalized user profiles"""

import json
from datetime import date, datetime, timedelta
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from tracker.core.models import UserProfile, DailyEntry, User
from tracker.core.character_sheet import CharacterSheet


class CharacterSheetService:
    """Service for building and updating user character sheets"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_or_create_profile(self, user_id: int) -> UserProfile:
        """Get existing profile or create new one"""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            profile = UserProfile(
                user_id=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        
        return profile
    
    def build_character_sheet(self, user_id: int) -> CharacterSheet:
        """Build character sheet from database profile"""
        profile = self.get_or_create_profile(user_id)
        
        return CharacterSheet(
            user_id=profile.user_id,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
            financial_personality=profile.financial_personality or "",
            typical_income_range=profile.typical_income_range or "",
            debt_situation=profile.debt_situation or "",
            money_stressors=json.loads(profile.money_stressors) if profile.money_stressors else [],
            money_wins=json.loads(profile.money_wins) if profile.money_wins else [],
            work_style=profile.work_style or "",
            side_hustle_status=profile.side_hustle_status or "",
            career_goals=json.loads(profile.career_goals) if profile.career_goals else [],
            work_challenges=json.loads(profile.work_challenges) if profile.work_challenges else [],
            stress_pattern=profile.stress_pattern or "",
            stress_triggers=json.loads(profile.stress_triggers) if profile.stress_triggers else [],
            coping_mechanisms=json.loads(profile.coping_mechanisms) if profile.coping_mechanisms else [],
            baseline_stress=profile.baseline_stress,
            priorities=json.loads(profile.priorities) if profile.priorities else [],
            recurring_themes=json.loads(profile.recurring_themes) if profile.recurring_themes else [],
            celebration_moments=json.loads(profile.celebration_moments) if profile.celebration_moments else [],
            ongoing_challenges=json.loads(profile.ongoing_challenges) if profile.ongoing_challenges else [],
            short_term_goals=json.loads(profile.short_term_goals) if profile.short_term_goals else [],
            long_term_aspirations=json.loads(profile.long_term_aspirations) if profile.long_term_aspirations else [],
            recent_growth=json.loads(profile.recent_growth) if profile.recent_growth else [],
            communication_style=profile.communication_style or "",
            feedback_preferences=profile.feedback_preferences or "",
            total_entries=profile.total_entries,
            entry_streak=profile.entry_streak,
            longest_streak=profile.longest_streak,
            last_entry_date=profile.last_entry_date,
        )
    
    def analyze_and_update_profile(self, user_id: int, lookback_days: int = 30) -> CharacterSheet:
        """
        Analyze recent entries and update character sheet with patterns.
        This auto-builds the profile based on actual data.
        """
        profile = self.get_or_create_profile(user_id)
        
        # Get recent entries
        cutoff_date = date.today() - timedelta(days=lookback_days)
        entries = (
            self.db.query(DailyEntry)
            .filter(DailyEntry.user_id == user_id)
            .filter(DailyEntry.date >= cutoff_date)
            .order_by(desc(DailyEntry.date))
            .all()
        )
        
        if not entries:
            return self.build_character_sheet(user_id)
        
        # Analyze financial patterns
        incomes = [float(e.income_today) for e in entries if e.income_today > 0]
        if incomes:
            avg_income = sum(incomes) / len(incomes)
            if avg_income > 500:
                profile.typical_income_range = f"${avg_income:.0f}/day (high earner)"
            elif avg_income > 200:
                profile.typical_income_range = f"${avg_income:.0f}/day (solid income)"
            elif avg_income > 50:
                profile.typical_income_range = f"${avg_income:.0f}/day (modest income)"
            else:
                profile.typical_income_range = f"${avg_income:.0f}/day (variable income)"
        
        # Analyze debt situation
        debts = [float(e.debts_total) for e in entries if e.debts_total]
        if debts:
            avg_debt = sum(debts) / len(debts)
            first_debt = debts[0]
            last_debt = debts[-1]
            
            if last_debt < first_debt - 100:
                profile.debt_situation = f"Paying down debt (${first_debt:.0f} → ${last_debt:.0f})"
            elif last_debt > first_debt + 100:
                profile.debt_situation = f"Debt growing (${first_debt:.0f} → ${last_debt:.0f})"
            elif avg_debt > 10000:
                profile.debt_situation = f"Managing significant debt (~${avg_debt:.0f})"
            elif avg_debt > 1000:
                profile.debt_situation = f"Manageable debt load (~${avg_debt:.0f})"
            else:
                profile.debt_situation = "Low/no debt"
        
        # Analyze work patterns
        side_incomes = [float(e.side_income) for e in entries if e.side_income > 0]
        hours = [float(e.hours_worked) for e in entries if e.hours_worked > 0]
        
        if side_incomes:
            total_side = sum(side_incomes)
            profile.side_hustle_status = f"Active side income (${total_side:.0f} in last {lookback_days} days)"
        elif hours:
            avg_hours = sum(hours) / len(hours)
            if avg_hours > 10:
                profile.work_style = f"High intensity work ({avg_hours:.1f} hrs/day avg)"
            elif avg_hours >= 7:
                profile.work_style = f"Standard full-time ({avg_hours:.1f} hrs/day avg)"
            elif avg_hours >= 4:
                profile.work_style = f"Part-time schedule ({avg_hours:.1f} hrs/day avg)"
            else:
                profile.work_style = f"Flexible/light schedule ({avg_hours:.1f} hrs/day avg)"
        
        # Analyze stress patterns
        stress_levels = [e.stress_level for e in entries if e.stress_level]
        if stress_levels:
            profile.baseline_stress = sum(stress_levels) / len(stress_levels)
            
            high_stress_days = len([s for s in stress_levels if s >= 7])
            low_stress_days = len([s for s in stress_levels if s <= 3])
            
            if profile.baseline_stress >= 7:
                profile.stress_pattern = "Chronically high stress - needs attention"
            elif profile.baseline_stress >= 6:
                profile.stress_pattern = "Elevated stress levels"
            elif profile.baseline_stress <= 4:
                profile.stress_pattern = "Generally calm and balanced"
            else:
                profile.stress_pattern = "Moderate, manageable stress"
            
            if high_stress_days > lookback_days * 0.3:
                profile.stress_pattern += f" ({high_stress_days} high-stress days)"
        
        # Extract priorities and themes from journal entries
        priorities = []
        journal_themes = []
        
        for entry in entries[:10]:  # Last 10 entries
            if entry.priority:
                priorities.append(entry.priority)
            if entry.notes and len(entry.notes) > 20:
                # Simple theme extraction (could use AI for better results)
                journal_themes.append(entry.notes[:100])
        
        if priorities:
            profile.priorities = json.dumps(priorities[:5])
        
        # Update meta stats
        profile.total_entries = self.db.query(func.count(DailyEntry.id)).filter(DailyEntry.user_id == user_id).scalar()
        profile.last_entry_date = entries[0].date if entries else None
        
        # Calculate streak
        profile.entry_streak = self._calculate_streak(user_id)
        if profile.entry_streak > profile.longest_streak:
            profile.longest_streak = profile.entry_streak
        
        profile.updated_at = datetime.utcnow()
        profile.profile_version += 1
        
        self.db.commit()
        self.db.refresh(profile)
        
        return self.build_character_sheet(user_id)
    
    def _calculate_streak(self, user_id: int) -> int:
        """Calculate current entry streak"""
        today = date.today()
        streak = 0
        check_date = today
        
        while True:
            entry = (
                self.db.query(DailyEntry)
                .filter(DailyEntry.user_id == user_id)
                .filter(DailyEntry.date == check_date)
                .first()
            )
            
            if entry:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                break
            
            # Limit to prevent infinite loop
            if streak > 365:
                break
        
        return streak
    
    def update_profile_field(self, user_id: int, field_name: str, value) -> CharacterSheet:
        """Manually update a specific profile field"""
        profile = self.get_or_create_profile(user_id)
        
        # Convert lists to JSON if needed
        if isinstance(value, list):
            value = json.dumps(value)
        
        setattr(profile, field_name, value)
        profile.updated_at = datetime.utcnow()
        profile.profile_version += 1
        
        self.db.commit()
        self.db.refresh(profile)
        
        return self.build_character_sheet(user_id)
