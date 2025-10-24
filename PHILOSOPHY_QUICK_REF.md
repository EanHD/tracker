# Philosophy Engine - Quick Reference

## What Is It?

A wisdom system that makes Tracker's AI speak like a trusted financial mentor by combining:
- Dave Ramsey's financial discipline
- Robert Kiyosaki's wealth mindset
- Behavioral economics insights
- Emotional intelligence principles
- Life balance wisdom

## Quick Stats

- **19 Core Principles** across 7 categories
- **4 Life Phases** (Debt Payoff → Stability → Growth → Legacy)
- **7 Communication Tones** (Encouraging, Honest, Analytical, Friendly, Firm, Compassionate, Motivational)
- **Auto-detects** user's phase and emotional state
- **Context-aware** principle selection

## How It Works (3 Steps)

### 1. Detect Context
```
User's Phase: Debt Payoff
Behaviors: high_stress, has_debt, overspending
Stress: 8/10
```

### 2. Select Principles
```
Best Matches:
  - Debt Snowball Method
  - Rest Well, Decide Well
  - Notice Emotions Before They Act
```

### 3. Generate Feedback
```
Tone: Compassionate (high stress override)
Includes: Actionable advice, metaphors, empathy
```

## Core Principles (Quick List)

### Financial Discipline (Dave Ramsey)
| Principle | When Used | Key Advice |
|-----------|-----------|------------|
| Live Below Means | High spending, lifestyle creep | Find one category to reduce 10% |
| Every Dollar Job | No budget, aimless spending | Assign every dollar before month starts |
| Emergency Fund | No safety net, anxiety | Start with $1,000. $50/week = 20 weeks |
| Debt Snowball | Multiple debts, overwhelm | Attack smallest debt first. Momentum > math |
| Delay Gratification | Impulse spending | Wait 24 hours. Most urges pass |

### Wealth Mindset (Robert Kiyosaki)
| Principle | When Used | Key Advice |
|-----------|-----------|------------|
| Assets vs Liabilities | Growth phase, investing | Does it put money in or take it out? |
| Pay Yourself First | Low savings, paycheck day | 10% auto-transfer before you see it |
| Multiple Incomes | Job insecurity, growth | Test one side project this month |
| Financial Education | Confusion, new user | One book per quarter, one podcast/week |

### Habit & Mindset
| Principle | When Used | Key Advice |
|-----------|-----------|------------|
| Progress Not Perfection | Perfectionism, guilt | Better than last month is enough |
| Automate Decisions | Inconsistent, overwhelm | Automate top 3 money moves |
| Celebrate Wins | Milestones, progress | Write it down. Tell someone. |
| Gratitude Changes Spending | Scarcity mindset | List 3 things you're grateful for daily |
| Forgive Mistakes | Financial slip-up | Learn, adjust, move forward |

### Emotional Intelligence
| Principle | When Used | Key Advice |
|-----------|-----------|------------|
| Notice Before React | Stress spending | Ask: "What am I really feeling?" |
| Rest Well Decide Well | Burnout, low energy | Don't make money decisions when exhausted |
| Align with Values | Life transition | Does spending reflect your top 3 values? |

### Behavioral Economics
| Principle | When Used | Key Advice |
|-----------|-----------|------------|
| Momentum Over Math | Debt payoff, paralysis | Smallest debt first. Wins build confidence. |
| Simplify Goals | Too many targets | Pick #1 goal for this quarter |

## Life Phases

| Phase | Trigger | Focus | Tone | Key Principles |
|-------|---------|-------|------|----------------|
| **Debt Payoff** | Debt > 3x income | Discipline, wins, resilience | Encouraging, Firm | Snowball, Emergency Fund, Delay Gratification |
| **Stability** | Building foundation | Habits, planning, consistency | Friendly, Analytical | Every Dollar Job, Automate, Budget |
| **Growth** | No debt + goals | Wealth building, income streams | Analytical, Visionary | Assets, Multiple Incomes, Pay Self First |
| **Legacy** | Wealth established | Giving, teaching, impact | Wise, Reflective | Generosity, Mentorship, Purpose |

## Communication Tones

| Tone | When | Example |
|------|------|---------|
| **Encouraging** | Progress, good streak | "12 days straight—you're crushing it!" |
| **Honest** | Lifestyle creep | "That pattern isn't sustainable. Let's adjust." |
| **Analytical** | Data-driven, growth | "At this rate, $5k by May." |
| **Friendly** | Default, casual | "Hey! You're doing great today." |
| **Firm** | Needs accountability | "Every dollar needs a job. Let's assign them." |
| **Compassionate** | Stress 8+, energy <3 | "You're not lazy, you're tired. Rest first." |
| **Motivational** | Streaks, milestones | "60% to goal—keep this momentum!" |

## Integration with User Profile

Philosophy Engine uses profile data:
- ✅ **Detects life phase** from debts, goals, income
- ✅ **Analyzes behaviors** from recent entries
- ✅ **Adapts tone** based on stress and energy
- ✅ **References goals** in actionable advice
- ✅ **Tracks progress** for encouragement

## Example Transformations

### Without Philosophy Engine
> "You spent $45 on food today. Your stress is high. Try to manage spending better."

### With Philosophy Engine (Debt + High Stress)
> "I see you today. Stress at 8/10, spending up—that's real and hard. You're not failing, you're human.
>
> Here's what I know: you can't make great money decisions when you're running on empty. Rest comes before budgeting.
>
> When you're ready, let's look at that smallest debt again. $200 more and it's gone. That win will fuel the next one. Momentum beats math every time.
>
> One day, one step. You've got this. 💪"

## Key Quotes

**Dave Ramsey:**
- "We buy things we don't need with money we don't have to impress people we don't like."
- "Personal finance is 80% behavior and 20% head knowledge."
- "Live like no one else, so later you can live like no one else."

**Robert Kiyosaki:**
- "The rich buy assets. The poor only have expenses. The middle class buys liabilities they think are assets."
- "The best investment is in yourself."

**Other Wisdom:**
- "Between stimulus and response there is a space. In that space is our power to choose." — Viktor Frankl
- "You don't have to be great to start, but you have to start to be great." — Zig Ziglar

## Metaphors Library

- Emergency Fund = Life jacket (hope you don't need it, but sleep better)
- Debt Snowball = Snowball rolling downhill (each win makes next easier)
- Delayed Gratification = Seed planted today → tree tomorrow
- Multiple Income Streams = Table with 4 legs (stable)
- Rest = Can't pour from empty cup
- Mistakes = GPS recalculating (no judgment, just adjust)
- Progress = Climbing mountain one step at a time
- Airplane 1% off course = Still reaches destination (perfection not needed)

## Using the Philosophy Engine

### As a User
The philosophy engine works automatically:
- ✅ Create entries as normal
- ✅ AI feedback includes relevant wisdom
- ✅ Tone adapts to your state
- ✅ Principles referenced conversationally

### As a Developer

```python
from tracker.services.philosophy_context_service import PhilosophyContextService

# Initialize
service = PhilosophyContextService(db)

# Get philosophy context for an entry
context = service.get_contextual_philosophy(
    user_id=1,
    current_entry=entry,
    max_principles=2
)

# Generate prompt section
philosophy_prompt = service.generate_philosophy_prompt_section(
    user_id=1,
    current_entry=entry
)

# Include in AI feedback generation
feedback = ai_client.generate_feedback(
    entry=entry,
    profile_context=profile_context,
    philosophy_context=philosophy_prompt  # ← Magic happens here
)
```

## Adding New Principles

```python
from tracker.services.philosophy_engine import Principle, PhilosophyCategory, Tone, LifePhase

engine.add_principle(Principle(
    id="my_principle",
    title="Principle Name",
    description="One clear sentence",
    category=PhilosophyCategory.HABIT_BUILDING,
    trigger_conditions=["behavior", "situation"],
    preferred_tone=Tone.ENCOURAGING,
    relevant_phases=[LifePhase.STABILITY],
    actionable_advice="Specific next step",
    quote="Optional quote",
    metaphor="Optional metaphor"
))
```

## Future Expansions

Designed to support:
- **Stoicism** (control, preparation, voluntary discomfort)
- **Minimalism** (less is more, experiences > things)
- **FIRE Movement** (extreme savings, coast FI)
- **Entrepreneurship** (systems, risk-taking, self-investment)
- **Cultural Wisdom** (Ikigai, Lagom, Hygge)

## Testing

```bash
# Test principle matching
python -c "
from tracker.services.philosophy_engine import PhilosophyEngine, LifePhase

engine = PhilosophyEngine()
principles = engine.get_relevant_principles({
    'phase': LifePhase.DEBT_PAYOFF,
    'recent_behavior': ['high_stress'],
    'stress_level': 8
}, limit=3)

for p in principles:
    print(f'{p.title}: {p.actionable_advice}')
"
```

## Files

- `src/tracker/services/philosophy_engine.py` - Core principles database
- `src/tracker/services/philosophy_context_service.py` - Context detection & selection
- `PHILOSOPHY_ENGINE.md` - Full documentation
- `PHILOSOPHY_QUICK_REF.md` - This file

## Philosophy in One Sentence

> Transform financial data into wisdom by matching timeless principles to each user's unique journey, phase, and emotional state—speaking truth with empathy, accountability with compassion.

---

**Status**: ✅ Implemented and Integrated  
**Principles**: 19 core (expandable)  
**Coverage**: All phases, tones, and behaviors  
**Integration**: Automatic in all AI feedback  
