"""Character Sheet - Personalized user profile for AI context"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from decimal import Decimal


@dataclass
class CharacterSheet:
    """
    A dynamic character sheet that evolves based on user's entry patterns.
    This provides rich context to the AI for more personalized feedback.
    """
    
    # Identity & Background
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    # Financial Character
    financial_personality: str = ""  # "cautious saver", "strategic investor", "paycheck-to-paycheck"
    typical_income_range: str = ""  # "$100-$500/day", "$1000-$2000/month"
    debt_situation: str = ""  # "paying down aggressively", "stable manageable debt", "growing concern"
    money_stressors: List[str] = field(default_factory=list)  # ["unexpected bills", "variable income"]
    money_wins: List[str] = field(default_factory=list)  # ["hit savings goal", "paid off credit card"]
    
    # Work Character
    work_style: str = ""  # "consistent 9-5", "hustle multiple gigs", "flexible remote"
    side_hustle_status: str = ""  # "active side income", "exploring options", "focused on main job"
    career_goals: List[str] = field(default_factory=list)  # ["promotion", "start business"]
    work_challenges: List[str] = field(default_factory=list)  # ["burnout", "looking for new role"]
    
    # Wellbeing Character
    stress_pattern: str = ""  # "usually calm", "stress spikes on bill days", "chronically stressed"
    stress_triggers: List[str] = field(default_factory=list)  # ["money", "work deadlines", "family"]
    coping_mechanisms: List[str] = field(default_factory=list)  # ["exercise", "journaling", "friends"]
    baseline_stress: float = 5.0  # Average stress level
    
    # Life Patterns
    priorities: List[str] = field(default_factory=list)  # Most common priority themes
    recurring_themes: List[str] = field(default_factory=list)  # Patterns from journal entries
    celebration_moments: List[str] = field(default_factory=list)  # Recent wins
    ongoing_challenges: List[str] = field(default_factory=list)  # Persistent struggles
    
    # Growth & Goals
    short_term_goals: List[str] = field(default_factory=list)  # Next 30 days
    long_term_aspirations: List[str] = field(default_factory=list)  # Big picture
    recent_growth: List[str] = field(default_factory=list)  # Progress made
    
    # Preferences
    communication_style: str = ""  # "direct and practical", "empathetic and supportive", "data-driven"
    feedback_preferences: str = ""  # "celebrate wins", "focus on improvement", "balanced"
    
    # Meta
    total_entries: int = 0
    entry_streak: int = 0
    longest_streak: int = 0
    last_entry_date: Optional[datetime] = None
    
    def to_ai_context(self) -> str:
        """Convert character sheet to context string for AI prompts"""
        
        context_parts = []
        
        # Financial context
        if self.financial_personality:
            context_parts.append(f"Financial style: {self.financial_personality}")
        if self.typical_income_range:
            context_parts.append(f"Typical income: {self.typical_income_range}")
        if self.debt_situation:
            context_parts.append(f"Debt status: {self.debt_situation}")
        if self.money_stressors:
            context_parts.append(f"Money concerns: {', '.join(self.money_stressors[:3])}")
        
        # Work context
        if self.work_style:
            context_parts.append(f"Work style: {self.work_style}")
        if self.career_goals:
            context_parts.append(f"Career goals: {', '.join(self.career_goals[:2])}")
        
        # Wellbeing context
        if self.stress_pattern:
            context_parts.append(f"Stress pattern: {self.stress_pattern}")
        if self.stress_triggers:
            context_parts.append(f"Stress triggers: {', '.join(self.stress_triggers[:3])}")
        
        # Goals & challenges
        if self.short_term_goals:
            context_parts.append(f"Current goals: {', '.join(self.short_term_goals[:2])}")
        if self.ongoing_challenges:
            context_parts.append(f"Ongoing challenges: {', '.join(self.ongoing_challenges[:2])}")
        if self.recent_growth:
            context_parts.append(f"Recent progress: {', '.join(self.recent_growth[:2])}")
        
        # Communication preferences
        if self.communication_style:
            context_parts.append(f"Communication preference: {self.communication_style}")
        
        # Tracking history
        context_parts.append(f"Tracking: {self.total_entries} entries, {self.entry_streak} day streak")
        
        return "\n".join(context_parts)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'financial_personality': self.financial_personality,
            'typical_income_range': self.typical_income_range,
            'debt_situation': self.debt_situation,
            'money_stressors': self.money_stressors,
            'money_wins': self.money_wins,
            'work_style': self.work_style,
            'side_hustle_status': self.side_hustle_status,
            'career_goals': self.career_goals,
            'work_challenges': self.work_challenges,
            'stress_pattern': self.stress_pattern,
            'stress_triggers': self.stress_triggers,
            'coping_mechanisms': self.coping_mechanisms,
            'baseline_stress': self.baseline_stress,
            'priorities': self.priorities,
            'recurring_themes': self.recurring_themes,
            'celebration_moments': self.celebration_moments,
            'ongoing_challenges': self.ongoing_challenges,
            'short_term_goals': self.short_term_goals,
            'long_term_aspirations': self.long_term_aspirations,
            'recent_growth': self.recent_growth,
            'communication_style': self.communication_style,
            'feedback_preferences': self.feedback_preferences,
            'total_entries': self.total_entries,
            'entry_streak': self.entry_streak,
            'longest_streak': self.longest_streak,
            'last_entry_date': self.last_entry_date.isoformat() if self.last_entry_date else None,
        }
