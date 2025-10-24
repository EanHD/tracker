"""Philosophy Engine - Knowledge base of financial and life principles"""

from typing import Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass


class PhilosophyCategory(Enum):
    """Categories of philosophical principles"""
    FINANCIAL_DISCIPLINE = "financial_discipline"
    WEALTH_MINDSET = "wealth_mindset"
    HABIT_BUILDING = "habit_building"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    BALANCE_HEALTH = "balance_health"
    BEHAVIORAL_ECONOMICS = "behavioral_economics"
    MINDSET_GROWTH = "mindset_growth"


class LifePhase(Enum):
    """User's current financial/life phase"""
    DEBT_PAYOFF = "debt_payoff"
    STABILITY = "stability"
    GROWTH = "growth"
    LEGACY = "legacy"


class Tone(Enum):
    """Communication tone options"""
    ENCOURAGING = "encouraging"
    HONEST = "honest"
    ANALYTICAL = "analytical"
    FRIENDLY = "friendly"
    FIRM = "firm"
    COMPASSIONATE = "compassionate"
    MOTIVATIONAL = "motivational"


@dataclass
class Principle:
    """A single philosophical principle or framework"""
    id: str
    title: str
    description: str
    category: PhilosophyCategory
    trigger_conditions: List[str]  # When this principle is relevant
    preferred_tone: Tone
    relevant_phases: List[LifePhase]
    actionable_advice: str
    quote: Optional[str] = None
    metaphor: Optional[str] = None
    follow_up_habits: Optional[List[str]] = None
    source: Optional[str] = None  # e.g., "Dave Ramsey", "Robert Kiyosaki"


class PhilosophyEngine:
    """
    Core philosophy engine that stores and retrieves relevant principles
    based on user context, emotional state, and financial phase
    """
    
    def __init__(self):
        self.principles: Dict[str, Principle] = {}
        self._load_core_principles()
    
    def _load_core_principles(self):
        """Load all core philosophical principles"""
        
        # Dave Ramsey Principles - Financial Discipline
        self.add_principle(Principle(
            id="ramsey_live_below_means",
            title="Live Below Your Means",
            description="Your lifestyle should never exceed your income. The gap between earning and spending is where freedom grows.",
            category=PhilosophyCategory.FINANCIAL_DISCIPLINE,
            trigger_conditions=["high_spending", "lifestyle_creep", "income_increase"],
            preferred_tone=Tone.HONEST,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY],
            actionable_advice="Review your last month's spending. Find one category where you can reduce by 10% without pain. That's your breathing room.",
            quote="We buy things we don't need with money we don't have to impress people we don't like. — Dave Ramsey",
            source="Dave Ramsey"
        ))
        
        self.add_principle(Principle(
            id="ramsey_every_dollar_job",
            title="Every Dollar Has a Job",
            description="Zero-based budgeting means giving every dollar a purpose before the month begins. No money sits idle without intention.",
            category=PhilosophyCategory.FINANCIAL_DISCIPLINE,
            trigger_conditions=["no_budget", "aimless_spending", "month_start"],
            preferred_tone=Tone.FIRM,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="Before next month starts, assign every dollar you expect to earn. Bills first, then savings, then spending. What's left over gets a job too—even if that job is 'fun money.'",
            follow_up_habits=["weekly_budget_review", "monthly_budget_planning"],
            source="Dave Ramsey"
        ))
        
        self.add_principle(Principle(
            id="ramsey_emergency_fund",
            title="Emergency Fund First",
            description="Before investing, before extra debt payments, build a $1,000 starter emergency fund. Then work toward 3-6 months of expenses.",
            category=PhilosophyCategory.FINANCIAL_DISCIPLINE,
            trigger_conditions=["no_emergency_fund", "unexpected_expense", "anxiety_about_money"],
            preferred_tone=Tone.ENCOURAGING,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY],
            actionable_advice="Start with $1,000. Put $50 aside each week. In 20 weeks, you'll have a safety net. That's peace you can measure.",
            metaphor="An emergency fund is like a life jacket—you hope you never need it, but you sleep better knowing it's there.",
            source="Dave Ramsey"
        ))
        
        self.add_principle(Principle(
            id="ramsey_debt_snowball",
            title="Debt Snowball Method",
            description="Pay off debts smallest to largest, regardless of interest rate. Momentum beats math when building confidence.",
            category=PhilosophyCategory.BEHAVIORAL_ECONOMICS,
            trigger_conditions=["multiple_debts", "debt_overwhelm", "low_motivation"],
            preferred_tone=Tone.MOTIVATIONAL,
            relevant_phases=[LifePhase.DEBT_PAYOFF],
            actionable_advice="List your debts smallest to largest. Attack the smallest with everything extra you have while paying minimums on the rest. When it's gone, celebrate—then roll that payment to the next debt.",
            quote="Personal finance is 80% behavior and 20% head knowledge. — Dave Ramsey",
            metaphor="Like a snowball rolling downhill, each paid-off debt makes the next one easier and faster.",
            source="Dave Ramsey"
        ))
        
        self.add_principle(Principle(
            id="ramsey_delay_gratification",
            title="Delay Gratification",
            description="Temporary sacrifice creates permanent peace. What you give up today, you gain back tenfold tomorrow.",
            category=PhilosophyCategory.HABIT_BUILDING,
            trigger_conditions=["impulse_spending", "wants_vs_needs", "temptation"],
            preferred_tone=Tone.COMPASSIONATE,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY],
            actionable_advice="When you want something, wait 24 hours. If you still want it and it fits your budget, buy it. Most of the time, the urge passes.",
            metaphor="A seed planted today becomes a tree tomorrow. You can't eat the seed and grow the tree.",
            source="Dave Ramsey"
        ))
        
        # Robert Kiyosaki Principles - Wealth Mindset
        self.add_principle(Principle(
            id="kiyosaki_assets_vs_liabilities",
            title="Assets vs. Liabilities",
            description="Assets put money in your pocket. Liabilities take money out. Build assets, minimize liabilities.",
            category=PhilosophyCategory.WEALTH_MINDSET,
            trigger_conditions=["confused_about_wealth", "growth_phase", "investment_thinking"],
            preferred_tone=Tone.ANALYTICAL,
            relevant_phases=[LifePhase.STABILITY, LifePhase.GROWTH, LifePhase.LEGACY],
            actionable_advice="Look at your big purchases. Ask: Does this generate income or cost me money every month? Cars, subscriptions, and unused stuff are liabilities. Savings, skills, and side income are assets.",
            quote="The rich buy assets. The poor only have expenses. The middle class buys liabilities they think are assets. — Robert Kiyosaki",
            source="Robert Kiyosaki"
        ))
        
        self.add_principle(Principle(
            id="kiyosaki_pay_yourself_first",
            title="Pay Yourself First",
            description="Before bills, before fun, before anything—save and invest. Treat your future like your most important creditor.",
            category=PhilosophyCategory.WEALTH_MINDSET,
            trigger_conditions=["low_savings_rate", "month_start", "paycheck_received"],
            preferred_tone=Tone.FIRM,
            relevant_phases=[LifePhase.STABILITY, LifePhase.GROWTH, LifePhase.LEGACY],
            actionable_advice="Set up automatic transfers on payday. 10% minimum goes to savings or investment before you see it. Live on what's left.",
            follow_up_habits=["automate_savings", "increase_savings_rate_quarterly"],
            source="Robert Kiyosaki"
        ))
        
        self.add_principle(Principle(
            id="kiyosaki_multiple_income_streams",
            title="Multiple Income Streams",
            description="Don't rely solely on wages. Build side income, passive income, and skills that pay. Diversification = security.",
            category=PhilosophyCategory.WEALTH_MINDSET,
            trigger_conditions=["single_income_source", "job_insecurity", "growth_mindset"],
            preferred_tone=Tone.ENCOURAGING,
            relevant_phases=[LifePhase.STABILITY, LifePhase.GROWTH, LifePhase.LEGACY],
            actionable_advice="Identify one skill you have that others would pay for. Spend 5 hours this month building a small side project. Test the waters.",
            metaphor="A table with one leg falls easily. Four legs make it stable. Income streams work the same way.",
            source="Robert Kiyosaki"
        ))
        
        self.add_principle(Principle(
            id="kiyosaki_financial_education",
            title="Invest in Financial Education",
            description="The best investment is in yourself. Learn how money works, how to grow it, and how to protect it.",
            category=PhilosophyCategory.WEALTH_MINDSET,
            trigger_conditions=["confusion_about_money", "new_user", "growth_phase"],
            preferred_tone=Tone.FRIENDLY,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="Read one finance book this quarter. Listen to one money podcast per week. Knowledge compounds like interest.",
            follow_up_habits=["weekly_financial_learning", "quarterly_book_reading"],
            source="Robert Kiyosaki"
        ))
        
        # Habit & Mindset Principles
        self.add_principle(Principle(
            id="habit_progress_not_perfection",
            title="Progress, Not Perfection",
            description="Small consistent actions beat perfect plans that never start. 1% better every day compounds into transformation.",
            category=PhilosophyCategory.HABIT_BUILDING,
            trigger_conditions=["perfectionism", "giving_up", "missed_goal", "self_criticism"],
            preferred_tone=Tone.COMPASSIONATE,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="You don't need a perfect month. You need a better-than-last-month month. What's one small win you can lock in this week?",
            quote="You don't have to be great to start, but you have to start to be great. — Zig Ziglar",
            metaphor="A plane off course 1% of the time still reaches its destination. Perfection isn't the goal—direction is."
        ))
        
        self.add_principle(Principle(
            id="habit_automate_decisions",
            title="Automate to Eliminate Willpower",
            description="Default systems beat daily decisions. Automate savings, bills, and investments so discipline doesn't depend on how you feel.",
            category=PhilosophyCategory.BEHAVIORAL_ECONOMICS,
            trigger_conditions=["decision_fatigue", "inconsistent_savings", "setup_phase"],
            preferred_tone=Tone.ANALYTICAL,
            relevant_phases=[LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="Identify your 3 most important money moves (save, pay bills, invest). Automate them. Remove the choice.",
            follow_up_habits=["automate_savings", "automate_bill_payments"]
        ))
        
        self.add_principle(Principle(
            id="habit_celebrate_small_wins",
            title="Celebrate Small Wins",
            description="Momentum builds on recognition. Track wins, no matter how small. What you celebrate, you repeat.",
            category=PhilosophyCategory.HABIT_BUILDING,
            trigger_conditions=["low_motivation", "progress_made", "milestone_reached"],
            preferred_tone=Tone.MOTIVATIONAL,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="When you hit a savings goal, paid off a debt, or stuck to your budget—pause and acknowledge it. Write it down. Tell someone.",
            metaphor="Every mountain is climbed one step at a time. Celebrate the steps, not just the summit."
        ))
        
        # Emotional Intelligence Principles
        self.add_principle(Principle(
            id="emotional_notice_before_react",
            title="Notice Emotions Before They Act",
            description="Emotions drive money decisions. Pause between feeling and spending. Awareness creates choice.",
            category=PhilosophyCategory.EMOTIONAL_INTELLIGENCE,
            trigger_conditions=["stress_spending", "emotional_purchase", "high_stress"],
            preferred_tone=Tone.COMPASSIONATE,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="Next time you feel the urge to buy something, ask: 'What am I really feeling right now?' Often, the answer isn't about the thing—it's about the emotion.",
            quote="Between stimulus and response there is a space. In that space is our power to choose. — Viktor Frankl"
        ))
        
        self.add_principle(Principle(
            id="emotional_gratitude_changes_spending",
            title="Gratitude Changes Spending",
            description="What you appreciate grows. Gratitude shifts focus from what's missing to what's present, reducing impulse spending.",
            category=PhilosophyCategory.EMOTIONAL_INTELLIGENCE,
            trigger_conditions=["feeling_scarcity", "comparison_trap", "dissatisfaction"],
            preferred_tone=Tone.FRIENDLY,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="Each day, write down 3 things you already have that you're grateful for. Watch how it changes what you think you need.",
            follow_up_habits=["daily_gratitude_practice"]
        ))
        
        self.add_principle(Principle(
            id="emotional_forgive_mistakes",
            title="Forgive Financial Mistakes",
            description="Guilt wastes energy. Mistakes teach. Acknowledge, learn, adjust, move forward. You're not your worst decision.",
            category=PhilosophyCategory.EMOTIONAL_INTELLIGENCE,
            trigger_conditions=["guilt", "overspending", "financial_mistake", "self_blame"],
            preferred_tone=Tone.COMPASSIONATE,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY],
            actionable_advice="Write down what happened, what you learned, and what you'll do differently. Then close that chapter. Forward is the only direction.",
            metaphor="A GPS doesn't judge you for missing a turn—it just recalculates. Be your own GPS."
        ))
        
        # Balance & Health Principles
        self.add_principle(Principle(
            id="balance_rest_well_decide_well",
            title="Rest Well, Decide Well",
            description="Burnout leads to bad money decisions. Physical, emotional, and financial health are interconnected.",
            category=PhilosophyCategory.BALANCE_HEALTH,
            trigger_conditions=["high_stress", "low_energy", "burnout", "poor_sleep"],
            preferred_tone=Tone.COMPASSIONATE,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="If you're exhausted, don't make financial decisions today. Rest first. Clarity comes with energy.",
            metaphor="You can't pour from an empty cup. Fill yourself first."
        ))
        
        self.add_principle(Principle(
            id="balance_align_with_values",
            title="Align Finances with Values",
            description="Money is a tool for building the life you want. Spend on what matters, cut what doesn't. Intentionality creates peace.",
            category=PhilosophyCategory.BALANCE_HEALTH,
            trigger_conditions=["value_misalignment", "existential_question", "life_transition"],
            preferred_tone=Tone.FRIENDLY,
            relevant_phases=[LifePhase.STABILITY, LifePhase.GROWTH, LifePhase.LEGACY],
            actionable_advice="List your top 3 life values (e.g., family, freedom, health). Review your spending. Does it reflect those values?",
            follow_up_habits=["quarterly_values_review"]
        ))
        
        # Behavioral Economics Principles
        self.add_principle(Principle(
            id="behavioral_momentum_over_math",
            title="Momentum Over Math",
            description="Humans respond to progress more than logic. The debt snowball works because wins build confidence.",
            category=PhilosophyCategory.BEHAVIORAL_ECONOMICS,
            trigger_conditions=["debt_payoff", "low_motivation", "analysis_paralysis"],
            preferred_tone=Tone.MOTIVATIONAL,
            relevant_phases=[LifePhase.DEBT_PAYOFF],
            actionable_advice="Don't overthink the math. Pick the smallest debt and crush it. The psychological win fuels the next one.",
            source="Dave Ramsey (behavioral insight)"
        ))
        
        self.add_principle(Principle(
            id="behavioral_simplify_goals",
            title="Simplify to Sustain",
            description="Too many goals lead to paralysis. Focus on 1-3 meaningful targets. Clarity directs action.",
            category=PhilosophyCategory.BEHAVIORAL_ECONOMICS,
            trigger_conditions=["too_many_goals", "overwhelm", "goal_setting"],
            preferred_tone=Tone.ANALYTICAL,
            relevant_phases=[LifePhase.DEBT_PAYOFF, LifePhase.STABILITY, LifePhase.GROWTH],
            actionable_advice="Choose your #1 financial goal for this quarter. What's the single most important thing? Do that first.",
            follow_up_habits=["quarterly_goal_review"]
        ))
    
    def add_principle(self, principle: Principle):
        """Add a principle to the engine"""
        self.principles[principle.id] = principle
    
    def get_relevant_principles(
        self,
        user_context: Dict,
        limit: int = 3
    ) -> List[Principle]:
        """
        Get principles relevant to user's current context
        
        Args:
            user_context: Dict with keys like:
                - phase: LifePhase
                - stress_level: int
                - recent_behavior: List[str] (e.g., ["overspending", "high_stress"])
                - goals: List[str]
            limit: Maximum number of principles to return
        
        Returns:
            List of most relevant principles
        """
        phase = user_context.get("phase", LifePhase.STABILITY)
        behaviors = user_context.get("recent_behavior", [])
        stress = user_context.get("stress_level", 5)
        
        scored_principles = []
        
        for principle in self.principles.values():
            score = 0
            
            # Phase match
            if phase in principle.relevant_phases:
                score += 10
            
            # Trigger condition match
            for behavior in behaviors:
                if behavior in principle.trigger_conditions:
                    score += 5
            
            # Stress-based tone matching
            if stress >= 7 and principle.preferred_tone == Tone.COMPASSIONATE:
                score += 3
            elif stress <= 3 and principle.preferred_tone in [Tone.MOTIVATIONAL, Tone.ENCOURAGING]:
                score += 3
            
            if score > 0:
                scored_principles.append((score, principle))
        
        # Sort by score and return top N
        scored_principles.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in scored_principles[:limit]]
    
    def get_principle_by_id(self, principle_id: str) -> Optional[Principle]:
        """Get a specific principle by ID"""
        return self.principles.get(principle_id)
    
    def get_principles_by_category(self, category: PhilosophyCategory) -> List[Principle]:
        """Get all principles in a category"""
        return [p for p in self.principles.values() if p.category == category]
    
    def get_principle_summary(self, principle: Principle, include_quote: bool = True) -> str:
        """Generate a human-readable summary of a principle"""
        summary = f"**{principle.title}**\n{principle.description}\n\n"
        
        if principle.actionable_advice:
            summary += f"→ {principle.actionable_advice}\n\n"
        
        if include_quote and principle.quote:
            summary += f"_{principle.quote}_\n\n"
        
        if principle.metaphor:
            summary += f"💭 {principle.metaphor}\n"
        
        return summary
