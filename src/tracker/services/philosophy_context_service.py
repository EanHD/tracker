"""Philosophy Context Service - Selects and applies relevant philosophies based on user context"""

import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from tracker.core.models import DailyEntry, UserProfile
from tracker.services.philosophy_engine import (
    PhilosophyEngine,
    LifePhase,
    Principle,
    Tone,
    PhilosophyCategory
)
from tracker.services.profile_service import ProfileService


class PhilosophyContextService:
    """
    Service that bridges user context with philosophy engine
    to provide contextually relevant guidance
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.philosophy_engine = PhilosophyEngine()
        self.profile_service = ProfileService(db)
    
    def determine_life_phase(self, user_id: int) -> LifePhase:
        """
        Determine user's current life phase based on profile and recent entries
        """
        profile = self.profile_service.get_or_create_profile(user_id)
        financial_info = profile.financial_info or {}
        
        # Check for debt
        debts = financial_info.get("debts", [])
        total_debt = sum(d.get("balance", 0) for d in debts)
        
        # Check for emergency fund (via recent entries or goals)
        goals = profile.goals or {}
        emergency_fund_goals = [
            g for g in goals.get("short_term", []) 
            if "emergency" in g.get("goal", "").lower()
        ]
        
        # Determine phase
        if total_debt > 0 and total_debt > (financial_info.get("monthly_income", 0) * 3):
            # Significant debt = debt payoff phase
            return LifePhase.DEBT_PAYOFF
        elif not emergency_fund_goals or len(goals.get("long_term", [])) == 0:
            # No solid goals = stability phase
            return LifePhase.STABILITY
        elif total_debt == 0 and len(goals.get("long_term", [])) > 0:
            # No debt + long-term goals = growth phase
            return LifePhase.GROWTH
        else:
            # Default to stability
            return LifePhase.STABILITY
    
    def detect_recent_behaviors(
        self, 
        user_id: int, 
        current_entry: Optional[DailyEntry] = None,
        lookback_days: int = 7
    ) -> List[str]:
        """
        Analyze recent entries and current entry to detect behavioral patterns
        """
        behaviors = []
        
        # Get recent entries
        since_date = date.today() - timedelta(days=lookback_days)
        recent_entries = (
            self.db.query(DailyEntry)
            .filter(DailyEntry.user_id == user_id)
            .filter(DailyEntry.date >= since_date)
            .order_by(DailyEntry.date.desc())
            .limit(lookback_days)
            .all()
        )
        
        if not recent_entries and not current_entry:
            return ["new_user"]
        
        # Include current entry if provided
        entries_to_analyze = recent_entries.copy()
        if current_entry:
            entries_to_analyze.insert(0, current_entry)
        
        # Analyze stress patterns
        avg_stress = sum(e.stress_level for e in entries_to_analyze) / len(entries_to_analyze)
        if avg_stress >= 7:
            behaviors.append("high_stress")
        if current_entry and current_entry.stress_level >= 8:
            behaviors.append("stress_spike")
        
        # Analyze spending patterns
        total_spending = sum(
            float(e.food_spent) + float(e.gas_spent) 
            for e in entries_to_analyze
        )
        avg_daily_spending = total_spending / len(entries_to_analyze)
        
        if current_entry:
            today_spending = float(current_entry.food_spent) + float(current_entry.gas_spent)
            if today_spending > avg_daily_spending * 1.5:
                behaviors.append("overspending")
            if today_spending < avg_daily_spending * 0.5:
                behaviors.append("frugal_day")
        
        # Check for income events
        if current_entry and float(current_entry.income_today) > 0:
            behaviors.append("paycheck_received")
        
        # Check for bills due
        if current_entry and float(current_entry.bills_due_today) > 0:
            behaviors.append("bills_due")
        
        # Check for debt
        if current_entry and current_entry.debts_total and float(current_entry.debts_total) > 0:
            behaviors.append("has_debt")
        
        # Check streak
        profile = self.profile_service.get_or_create_profile(user_id)
        if profile.entry_streak >= 7:
            behaviors.append("strong_streak")
        elif profile.entry_streak == 0:
            behaviors.append("streak_broken")
        
        # Check for goal progress
        if len(entries_to_analyze) >= 3:
            behaviors.append("consistent_tracking")
        
        return behaviors
    
    def determine_preferred_tone(
        self,
        user_id: int,
        stress_level: int,
        energy_level: int
    ) -> Tone:
        """
        Determine the best tone to use based on user state
        """
        profile = self.profile_service.get_or_create_profile(user_id)
        
        # User's explicit preference takes priority
        if profile.preferred_tone:
            tone_map = {
                "casual": Tone.FRIENDLY,
                "professional": Tone.ANALYTICAL,
                "encouraging": Tone.MOTIVATIONAL,
                "stoic": Tone.HONEST
            }
            base_tone = tone_map.get(profile.preferred_tone, Tone.FRIENDLY)
        else:
            base_tone = Tone.FRIENDLY
        
        # Override with compassionate tone if user is struggling
        if stress_level >= 8 or energy_level <= 2:
            return Tone.COMPASSIONATE
        
        # Use motivational tone for good streaks
        if profile.entry_streak >= 7:
            return Tone.MOTIVATIONAL
        
        return base_tone
    
    def get_contextual_philosophy(
        self,
        user_id: int,
        current_entry: Optional[DailyEntry] = None,
        max_principles: int = 2
    ) -> Dict:
        """
        Get philosophy context for AI prompt based on user's current state
        
        Returns:
            Dict with:
                - life_phase: str
                - relevant_principles: List[Principle]
                - tone: str
                - actionable_insights: List[str]
        """
        # Determine life phase
        phase = self.determine_life_phase(user_id)
        
        # Detect recent behaviors
        behaviors = self.detect_recent_behaviors(user_id, current_entry)
        
        # Get stress and energy
        stress_level = current_entry.stress_level if current_entry else 5
        profile = self.profile_service.get_or_create_profile(user_id)
        energy_level = profile.baseline_energy
        
        # Determine tone
        tone = self.determine_preferred_tone(user_id, stress_level, energy_level)
        
        # Build context for philosophy engine
        user_context = {
            "phase": phase,
            "recent_behavior": behaviors,
            "stress_level": stress_level,
            "energy_level": energy_level,
        }
        
        # Get relevant principles
        principles = self.philosophy_engine.get_relevant_principles(
            user_context,
            limit=max_principles
        )
        
        # Generate actionable insights
        actionable_insights = [p.actionable_advice for p in principles if p.actionable_advice]
        
        return {
            "life_phase": phase.value,
            "relevant_principles": principles,
            "tone": tone.value,
            "actionable_insights": actionable_insights,
            "detected_behaviors": behaviors
        }
    
    def generate_philosophy_prompt_section(
        self,
        user_id: int,
        current_entry: Optional[DailyEntry] = None
    ) -> str:
        """
        Generate a philosophy section to inject into AI prompts
        
        This provides the AI with philosophical context and guidance principles
        """
        context = self.get_contextual_philosophy(user_id, current_entry)
        
        prompt_section = "# Guiding Philosophy\n\n"
        
        # Add life phase context
        phase_descriptions = {
            "debt_payoff": "User is in the **Debt Payoff Phase** - Focus on discipline, momentum, small wins, and emotional resilience.",
            "stability": "User is in the **Stability Phase** - Focus on building emergency funds, consistent habits, and long-term planning.",
            "growth": "User is in the **Growth Phase** - Focus on wealth building, multiple income streams, and strategic thinking.",
            "legacy": "User is in the **Legacy Phase** - Focus on giving, teaching, and leaving impact."
        }
        
        prompt_section += phase_descriptions.get(context["life_phase"], "") + "\n\n"
        
        # Add tone guidance
        tone_descriptions = {
            "friendly": "Use a warm, conversational tone like talking to a trusted friend.",
            "analytical": "Use a clear, logical tone focused on data and actionable steps.",
            "motivational": "Use an energizing, encouraging tone that celebrates progress.",
            "honest": "Use a direct, no-nonsense tone that tells it like it is.",
            "compassionate": "Use a gentle, understanding tone that validates struggles."
        }
        
        prompt_section += f"**Tone**: {tone_descriptions.get(context['tone'], '')}\n\n"
        
        # Add relevant principles
        if context["relevant_principles"]:
            prompt_section += "## Relevant Principles to Reference:\n\n"
            for principle in context["relevant_principles"]:
                prompt_section += f"### {principle.title}\n"
                prompt_section += f"{principle.description}\n\n"
                if principle.actionable_advice:
                    prompt_section += f"**Actionable**: {principle.actionable_advice}\n\n"
                if principle.quote:
                    prompt_section += f"_{principle.quote}_\n\n"
        
        # Add detected behaviors
        if context["detected_behaviors"]:
            prompt_section += f"**Recent patterns**: {', '.join(context['detected_behaviors'])}\n\n"
        
        # Add final guidance
        prompt_section += """## Communication Guidelines:
- Speak like a wise mentor who's been through struggle and success
- Blend empathy with accountability
- Use metaphors and real-world examples naturally
- Avoid generic platitudes—be specific and practical
- End with something actionable or encouraging
- Reference principles conversationally, not academically
- Show you remember their journey and progress

"""
        
        return prompt_section
    
    def get_principle_by_keyword(self, keyword: str) -> Optional[Principle]:
        """Get a specific principle by keyword match in title or description"""
        keyword_lower = keyword.lower()
        for principle in self.philosophy_engine.principles.values():
            if (keyword_lower in principle.title.lower() or 
                keyword_lower in principle.description.lower()):
                return principle
        return None
    
    def get_principles_for_phase(self, phase: LifePhase) -> List[Principle]:
        """Get all principles relevant to a specific life phase"""
        return [
            p for p in self.philosophy_engine.principles.values()
            if phase in p.relevant_phases
        ]
