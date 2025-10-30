"""User Profile Service for managing personalized context"""

import json
import statistics
from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import and_

from tracker.core.models import User, UserProfile, DailyEntry


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
    
    def add_milestone(self, user_id: int, event_date: date, event_type: str, description: str) -> UserProfile:
        """
        Add a life event/milestone for context
        
        Args:
            event_date: Date of the milestone
            event_type: Type of event (e.g., "job_change", "bonus", "expense", "achievement")
            description: Description of the event
        """
        profile = self.get_or_create_profile(user_id)
        
        milestones = []
        if profile.milestones:
            try:
                milestones = json.loads(profile.milestones)
            except (json.JSONDecodeError, TypeError):
                milestones = []
        
        milestones.append({
            "date": event_date.isoformat(),
            "event_type": event_type,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        })
        
        profile.milestones = json.dumps(milestones)
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

    # =================
    # NEW MEMORY LAYERS
    # =================
    
    def get_recent_entry_summary(self, user_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Summarize recent entries for AI context (SHORT-TERM MEMORY)
        
        Returns trends from the last N days to show patterns
        """
        cutoff_date = date.today() - timedelta(days=days)
        entries = (
            self.db.query(DailyEntry)
            .filter(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.date >= cutoff_date
                )
            )
            .order_by(DailyEntry.date.desc())
            .all()
        )
        
        if not entries:
            return {}
        
        stress_levels = [float(e.stress_level) for e in entries]
        incomes = [float(e.income_today) + float(e.side_income) for e in entries]
        spending = [
            float(e.bills_due_today) + float(e.food_spent) + float(e.gas_spent)
            for e in entries
        ]
        
        # Determine trends
        def get_trend(values):
            if len(values) < 2:
                return "stable"
            recent_avg = statistics.mean(values[:len(values)//2])
            older_avg = statistics.mean(values[len(values)//2:])
            diff = recent_avg - older_avg
            if diff > 0.5:
                return "increasing"
            elif diff < -0.5:
                return "decreasing"
            return "stable"
        
        return {
            "days_logged": len(entries),
            "avg_stress": round(statistics.mean(stress_levels), 1),
            "stress_trend": get_trend(stress_levels),
            "stress_range": f"{min(stress_levels):.0f}-{max(stress_levels):.0f}",
            "avg_income": round(statistics.mean(incomes), 2),
            "income_trend": get_trend(incomes),
            "avg_spending": round(statistics.mean(spending), 2),
            "spending_trend": get_trend(spending),
            "most_stressful_day": max(entries, key=lambda e: e.stress_level).date if entries else None,
            "highest_income_day": max(entries, key=lambda e: e.income_today + e.side_income).date if entries else None,
        }
    
    def get_recent_wins(self, user_id: int, days: int = 30) -> List[str]:
        """
        Identify recent achievements and wins (MEMORY OF SUCCESS)
        
        Surfaces recent milestones to celebrate and reinforce
        """
        profile = self.get_or_create_profile(user_id)
        wins = []
        
        # Check streak milestones
        if profile.entry_streak in [7, 14, 21, 30, 60, 90]:
            wins.append(f"🔥 {profile.entry_streak}-day entry streak!")
        
        # Get recent entries for financial wins
        cutoff_date = date.today() - timedelta(days=days)
        entries = (
            self.db.query(DailyEntry)
            .filter(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.date >= cutoff_date
                )
            )
            .order_by(DailyEntry.date)
            .all()
        )
        
        if entries:
            # Check for positive balance achievement
            positive_balance_dates = [
                e.date for e in entries 
                if (e.income_today + e.side_income - e.bills_due_today - e.food_spent - e.gas_spent) > 0
            ]
            if positive_balance_dates:
                wins.append(f"💰 Positive balance on {len(positive_balance_dates)} days!")
            
            # Check for consecutive days with no debt increase
            if len(entries) >= 3:
                recent_entries = entries[-3:]
                avg_balance = statistics.mean([
                    float(e.bank_balance or 0) for e in recent_entries
                ])
                oldest_balance = float(entries[0].bank_balance or 0)
                if avg_balance > oldest_balance:
                    wins.append(f"📈 Bank balance trending positive!")
            
            # Check for no overspending streak
            zero_overspend = sum(1 for e in entries if (e.bills_due_today + e.food_spent + e.gas_spent) > (e.income_today + e.side_income))
            if zero_overspend == 0 and len(entries) >= 3:
                wins.append(f"✅ {len(entries)} days of staying within means!")
        
        return wins
    
    def get_weekly_patterns(self, user_id: int, lookback_days: int = 42) -> Dict[str, Any]:
        """
        Identify day-of-week patterns (SEASONAL/CYCLICAL PATTERNS)
        
        Shows which days of week tend to be harder/better for stress, spending, etc.
        """
        cutoff_date = date.today() - timedelta(days=lookback_days)
        entries = (
            self.db.query(DailyEntry)
            .filter(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.date >= cutoff_date
                )
            )
            .all()
        )
        
        if not entries:
            return {}
        
        # Group by day of week (0=Monday, 6=Sunday)
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        by_day = {i: [] for i in range(7)}
        
        for entry in entries:
            day_num = entry.date.weekday()
            by_day[day_num].append(entry)
        
        patterns = {}
        for day_num, day_entries in by_day.items():
            if not day_entries:
                continue
            
            day_name = day_names[day_num]
            stress_levels = [float(e.stress_level) for e in day_entries]
            spending = [
                float(e.bills_due_today) + float(e.food_spent) + float(e.gas_spent)
                for e in day_entries
            ]
            
            patterns[day_name] = {
                "avg_stress": round(statistics.mean(stress_levels), 1),
                "avg_spending": round(statistics.mean(spending), 2),
                "entries_logged": len(day_entries),
            }
        
        return patterns
    
    def get_momentum_context(self, user_id: int, current_entry: DailyEntry) -> Dict[str, Any]:
        """
        Track entry-to-entry changes (MOMENTUM/TRENDS)
        
        Shows if you're improving or declining compared to recent baseline
        """
        # Get yesterday's entry
        yesterday = current_entry.date - timedelta(days=1)
        yesterday_entry = (
            self.db.query(DailyEntry)
            .filter(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.date == yesterday
                )
            )
            .first()
        )
        
        # Get 7-day baseline for comparison
        cutoff = current_entry.date - timedelta(days=7)
        recent_entries = (
            self.db.query(DailyEntry)
            .filter(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.date >= cutoff,
                    DailyEntry.date < current_entry.date
                )
            )
            .all()
        )
        
        momentum = {}
        
        if yesterday_entry:
            # Day-over-day deltas
            stress_delta = current_entry.stress_level - yesterday_entry.stress_level
            income_delta = (current_entry.income_today + current_entry.side_income) - \
                          (yesterday_entry.income_today + yesterday_entry.side_income)
            spending_delta = (current_entry.bills_due_today + current_entry.food_spent + current_entry.gas_spent) - \
                            (yesterday_entry.bills_due_today + yesterday_entry.food_spent + yesterday_entry.gas_spent)
            
            momentum["stress_vs_yesterday"] = round(stress_delta, 1)
            momentum["income_vs_yesterday"] = round(income_delta, 2)
            momentum["spending_vs_yesterday"] = round(spending_delta, 2)
        
        if recent_entries:
            # Compare to 7-day average
            avg_stress = statistics.mean([float(e.stress_level) for e in recent_entries])
            avg_income = statistics.mean([float(e.income_today) + float(e.side_income) for e in recent_entries])
            
            stress_vs_avg = current_entry.stress_level - avg_stress
            income_vs_avg = (current_entry.income_today + current_entry.side_income) - avg_income
            
            momentum["stress_vs_7day_avg"] = round(stress_vs_avg, 1)
            momentum["income_vs_7day_avg"] = round(income_vs_avg, 2)
        
        return momentum
    
    def get_milestone_context(self, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get recent life events/milestones (PERSONAL CONTEXT HISTORY)
        
        Returns user-logged milestones that provide context
        """
        profile = self.get_or_create_profile(user_id)
        
        if not profile.milestones:
            return []
        
        try:
            milestones = json.loads(profile.milestones)
        except (json.JSONDecodeError, TypeError):
            return []
        
        # Filter to recent milestones
        cutoff = date.today() - timedelta(days=days)
        recent = [
            m for m in milestones
            if datetime.fromisoformat(m.get('date', '2000-01-01')).date() >= cutoff
        ]
        
        return sorted(recent, key=lambda m: m.get('date', ''), reverse=True)
    
    def get_field_consistency(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Track which behaviors are logged consistently (HABIT FORMATION TRACKING)
        
        Shows user's tracking habits and field completion rates
        """
        cutoff_date = date.today() - timedelta(days=days)
        entries = (
            self.db.query(DailyEntry)
            .filter(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.date >= cutoff_date
                )
            )
            .all()
        )
        
        if not entries:
            return {}
        
        total = len(entries)
        
        # Track field completion rates
        consistency = {
            "total_entries": total,
            "cash_tracked": round(sum(1 for e in entries if e.cash_on_hand is not None) / total * 100, 1),
            "bank_tracked": round(sum(1 for e in entries if e.bank_balance is not None) / total * 100, 1),
            "income_tracked": round(sum(1 for e in entries if e.income_today > 0 or e.side_income > 0) / total * 100, 1),
            "spending_tracked": round(sum(1 for e in entries if e.bills_due_today > 0 or e.food_spent > 0 or e.gas_spent > 0) / total * 100, 1),
            "hours_tracked": round(sum(1 for e in entries if e.hours_worked is not None) / total * 100, 1),
            "stress_logged": round(sum(1 for e in entries if e.stress_level is not None) / total * 100, 1),
            "notes_written": round(sum(1 for e in entries if e.notes) / total * 100, 1),
        }
        
        # Determine stress trend
        stress_levels = [float(e.stress_level) for e in entries if e.stress_level is not None]
        if len(stress_levels) >= 2:
            recent_stress = statistics.mean(stress_levels[:len(stress_levels)//2])
            older_stress = statistics.mean(stress_levels[len(stress_levels)//2:])
            if recent_stress < older_stress - 0.5:
                consistency["stress_trend"] = "declining ↓"
            elif recent_stress > older_stress + 0.5:
                consistency["stress_trend"] = "increasing ↑"
            else:
                consistency["stress_trend"] = "stable →"
        
        return consistency
    
    def get_journal_sentiment(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Analyze mood trends from journal entries (SENTIMENT ANALYSIS)
        
        Simple keyword-based sentiment to show emotional patterns
        """
        cutoff_date = date.today() - timedelta(days=days)
        entries = (
            self.db.query(DailyEntry)
            .filter(
                and_(
                    DailyEntry.user_id == user_id,
                    DailyEntry.date >= cutoff_date,
                    DailyEntry.notes.isnot(None)
                )
            )
            .all()
        )
        
        if not entries:
            return {}
        
        # Simple sentiment indicators
        positive_keywords = [
            "good", "great", "awesome", "excellent", "amazing", "happy", "proud",
            "win", "success", "accomplished", "grateful", "blessed", "perfect",
            "love", "excited", "energized", "hopeful", "positive"
        ]
        negative_keywords = [
            "bad", "terrible", "awful", "horrible", "depressed", "sad", "angry",
            "frustrated", "disappointed", "failed", "exhausted", "stressed",
            "anxious", "worried", "overwhelmed", "struggling", "difficult"
        ]
        
        sentiment_scores = []
        for entry in entries:
            notes_lower = entry.notes.lower() if entry.notes else ""
            positive_count = sum(1 for kw in positive_keywords if kw in notes_lower)
            negative_count = sum(1 for kw in negative_keywords if kw in notes_lower)
            score = positive_count - negative_count
            sentiment_scores.append(score)
        
        if sentiment_scores:
            avg_sentiment = statistics.mean(sentiment_scores)
            sentiment_trend = "positive 😊" if avg_sentiment > 0 else "negative 😞" if avg_sentiment < 0 else "neutral 😐"
            
            # Trend analysis
            recent_sentiment = statistics.mean(sentiment_scores[:len(sentiment_scores)//2])
            older_sentiment = statistics.mean(sentiment_scores[len(sentiment_scores)//2:])
            
            if recent_sentiment > older_sentiment + 0.3:
                sentiment_direction = "improving ↑"
            elif recent_sentiment < older_sentiment - 0.3:
                sentiment_direction = "declining ↓"
            else:
                sentiment_direction = "stable →"
            
            return {
                "overall_sentiment": sentiment_trend,
                "sentiment_direction": sentiment_direction,
                "avg_score": round(avg_sentiment, 2),
                "entries_analyzed": len(entries),
            }
        
        return {}

