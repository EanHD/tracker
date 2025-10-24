# Philosophy Engine - Tracker's AI Mentor System

## Overview

The **Philosophy Engine** transforms Tracker from a simple feedback generator into a wise, empathetic financial and life mentor. It combines timeless financial wisdom (Dave Ramsey, Robert Kiyosaki) with life philosophies (habits, mindset, balance) to provide context-aware, principle-driven guidance.

## Core Philosophy

> "Tracker's AI should empower, never guilt. Teach, never preach. Support, never judge. Motivate through truth and empathy."

The Philosophy Engine makes the AI capable of:
- Speaking like a wise mentor who's experienced both struggle and success
- Blending empathy with accountability
- Providing context-aware advice based on user's phase and emotional state
- Adapting tone dynamically (encouraging, honest, compassionate, etc.)
- Offering actionable wisdom, not generic platitudes

## Architecture

```
┌──────────────────────────────────────────────────┐
│  Philosophy Engine                                │
│  - 19+ core principles                            │
│  - 7 categories                                   │
│  - 4 life phases                                  │
│  - 7 communication tones                          │
└───────────────┬──────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────┐
│  Philosophy Context Service                       │
│  - Detects user's life phase                      │
│  - Analyzes recent behaviors                      │
│  - Selects relevant principles                    │
│  - Determines best tone                           │
└───────────────┬──────────────────────────────────┘
                │
┌───────────────▼──────────────────────────────────┐
│  Feedback Service                                 │
│  - Loads philosophy context                       │
│  - Enriches AI prompts                            │
│  - Generates wisdom-based feedback                │
└──────────────────────────────────────────────────┘
```

## Philosophy Categories

### 1. Financial Discipline (Dave Ramsey)
Principles focused on living below means, budgeting, emergency funds, and debt elimination.

**Core Principles:**
- Live Below Your Means
- Every Dollar Has a Job
- Emergency Fund First
- Debt Snowball Method
- Delay Gratification

**When Applied:** Debt payoff phase, high spending, lifestyle creep

### 2. Wealth Mindset (Robert Kiyosaki)
Principles focused on assets vs liabilities, multiple income streams, and financial education.

**Core Principles:**
- Assets vs. Liabilities
- Pay Yourself First
- Multiple Income Streams
- Invest in Financial Education

**When Applied:** Stability/growth phase, investment thinking, wealth building

### 3. Habit Building
Principles focused on consistency, automation, and small wins.

**Core Principles:**
- Progress, Not Perfection
- Automate to Eliminate Willpower
- Celebrate Small Wins

**When Applied:** New users, inconsistent behavior, motivation needed

### 4. Emotional Intelligence
Principles focused on self-awareness, gratitude, and emotional regulation.

**Core Principles:**
- Notice Emotions Before They Act
- Gratitude Changes Spending
- Forgive Financial Mistakes

**When Applied:** Stress spending, guilt, comparison trap

### 5. Balance & Health
Principles focused on holistic wellbeing and value alignment.

**Core Principles:**
- Rest Well, Decide Well
- Align Finances with Values

**When Applied:** Burnout, value misalignment, high stress

### 6. Behavioral Economics
Principles based on how humans actually make decisions.

**Core Principles:**
- Momentum Over Math
- Simplify to Sustain

**When Applied:** Debt payoff, overwhelm, goal setting

### 7. Mindset & Growth
Principles focused on continuous improvement and learning.

*Space for future expansion: Stoicism, Minimalism, FIRE movement, etc.*

## Life Phases

The system automatically detects which phase a user is in:

### 1. Debt Payoff Phase
**Trigger:** Significant debt (>3x monthly income)  
**Focus:** Discipline, momentum, small wins, emotional resilience  
**Tone:** Encouraging, firm, motivational  
**Principles:** Ramsey-heavy (snowball, delay gratification, emergency fund)

### 2. Stability Phase
**Trigger:** No significant debt, building emergency fund  
**Focus:** Consistent habits, long-term planning, foundation building  
**Tone:** Friendly, analytical, balanced  
**Principles:** Mix of Ramsey discipline + Kiyosaki education

### 3. Growth Phase
**Trigger:** No debt + long-term goals + emergency fund  
**Focus:** Wealth building, multiple income, strategic thinking  
**Tone:** Analytical, encouraging, visionary  
**Principles:** Kiyosaki-heavy (assets, income streams, investing)

### 4. Legacy Phase
**Trigger:** Wealth established, focus on giving/teaching  
**Focus:** Generosity, teaching, leaving impact  
**Tone:** Wise, reflective, generous  
**Principles:** Giving, mentoring, purpose

## Communication Tones

The AI adapts its voice based on user state:

| Tone | When Used | Example |
|------|-----------|---------|
| **Encouraging** | Good streak, progress made | "12 days straight—you're crushing it!" |
| **Honest** | Lifestyle creep, overspending | "That spending pattern isn't sustainable. Let's adjust." |
| **Analytical** | Growth phase, data-driven users | "At this save rate, you'll hit $5k by May." |
| **Friendly** | Default, casual preference | "Hey! You're doing great today." |
| **Firm** | Needs accountability, budgeting | "Every dollar needs a job. Let's assign them." |
| **Compassionate** | High stress (8+), low energy (<3) | "You're not lazy, you're tired. Rest first." |
| **Motivational** | Strong streaks, milestones | "60% to your goal—keep this momentum!" |

## How It Works

### 1. Context Detection

When generating feedback, the system:

1. **Determines Life Phase**
   ```python
   phase = determine_life_phase(user_id)
   # Checks: debt level, emergency fund, goals
   # Result: DEBT_PAYOFF, STABILITY, GROWTH, or LEGACY
   ```

2. **Detects Recent Behaviors**
   ```python
   behaviors = detect_recent_behaviors(user_id, current_entry)
   # Analyzes: stress patterns, spending, streak, consistency
   # Returns: ["high_stress", "overspending", "strong_streak", ...]
   ```

3. **Determines Best Tone**
   ```python
   tone = determine_preferred_tone(user_id, stress, energy)
   # Considers: user preference, stress level, energy, streak
   # Returns: COMPASSIONATE if struggling, MOTIVATIONAL if succeeding
   ```

### 2. Principle Selection

```python
user_context = {
    "phase": LifePhase.DEBT_PAYOFF,
    "recent_behavior": ["high_stress", "has_debt", "overspending"],
    "stress_level": 8,
    "energy_level": 3
}

principles = philosophy_engine.get_relevant_principles(user_context, limit=2)
```

**Scoring Algorithm:**
- Phase match: +10 points
- Trigger condition match: +5 points each
- Tone alignment with stress/energy: +3 points

**Result:** Top 2-3 most relevant principles for current situation

### 3. Prompt Enhancement

The philosophy context is injected into the AI prompt:

```
# Guiding Philosophy

User is in the **Debt Payoff Phase** - Focus on discipline, momentum, 
small wins, and emotional resilience.

**Tone**: Use a gentle, understanding tone that validates struggles.

## Relevant Principles to Reference:

### Debt Snowball Method
Pay off debts smallest to largest, regardless of interest rate. Momentum 
beats math when building confidence.

**Actionable**: List your debts smallest to largest. Attack the smallest 
with everything extra you have while paying minimums on the rest.

_Personal finance is 80% behavior and 20% head knowledge. — Dave Ramsey_

### Rest Well, Decide Well
Burnout leads to bad money decisions. Physical, emotional, and financial 
health are interconnected.

**Actionable**: If you're exhausted, don't make financial decisions today. 
Rest first. Clarity comes with energy.

**Recent patterns**: high_stress, overspending, has_debt

## Communication Guidelines:
- Speak like a wise mentor who's been through struggle and success
- Blend empathy with accountability
- Use metaphors and real-world examples naturally
- Avoid generic platitudes—be specific and practical
- Reference principles conversationally, not academically
```

### 4. AI Generation

The AI uses this philosophical context to generate feedback that:
- References relevant principles naturally
- Speaks in the appropriate tone
- Provides actionable advice aligned with the philosophy
- Uses quotes or metaphors when helpful
- Shows awareness of user's journey and progress

## Example Feedback Evolution

### Without Philosophy Engine
```
You logged your entry today. Your stress is at 8/10. Try to reduce 
spending and manage stress better.
```

### With Philosophy Engine (Debt Payoff, High Stress)
```
Hey, I see you today. Stress at 8/10, spending up—that's real and hard. 
You're not failing, you're human.

Here's what I know: you can't make great money decisions when you're 
running on empty. Rest comes before budgeting. Clarity comes with energy.

When you're ready, let's look at that smallest debt again. You're closer 
than you think—$200 more and it's gone. That psychological win will fuel 
the next one. Momentum beats math every time.

One day, one step. You've got this. 💪
```

## Principles Library

### Financial Discipline Principles

#### Live Below Your Means
- **Category:** Financial Discipline
- **Phase:** Debt Payoff, Stability
- **Trigger:** High spending, lifestyle creep, income increase
- **Tone:** Honest
- **Advice:** Review spending, find one category to reduce by 10%
- **Quote:** "We buy things we don't need with money we don't have to impress people we don't like."

#### Every Dollar Has a Job
- **Category:** Financial Discipline
- **Phase:** All phases
- **Trigger:** No budget, aimless spending, month start
- **Tone:** Firm
- **Advice:** Assign every expected dollar before month starts
- **Habits:** Weekly budget review, monthly planning

#### Emergency Fund First
- **Category:** Financial Discipline
- **Phase:** Debt Payoff, Stability
- **Trigger:** No emergency fund, unexpected expense, anxiety
- **Tone:** Encouraging
- **Advice:** Start with $1,000. Put $50 aside each week.
- **Metaphor:** "A life jacket—you hope you never need it, but you sleep better knowing it's there."

#### Debt Snowball Method
- **Category:** Behavioral Economics
- **Phase:** Debt Payoff
- **Trigger:** Multiple debts, overwhelm, low motivation
- **Tone:** Motivational
- **Advice:** List debts smallest to largest, attack smallest first
- **Metaphor:** "Like a snowball rolling downhill, each paid-off debt makes the next one easier."

#### Delay Gratification
- **Category:** Habit Building
- **Phase:** Debt Payoff, Stability
- **Trigger:** Impulse spending, wants vs needs, temptation
- **Tone:** Compassionate
- **Advice:** Wait 24 hours before buying. Most urges pass.
- **Metaphor:** "A seed planted today becomes a tree tomorrow. You can't eat the seed and grow the tree."

### Wealth Mindset Principles

#### Assets vs. Liabilities
- **Category:** Wealth Mindset
- **Phase:** Stability, Growth, Legacy
- **Trigger:** Confused about wealth, growth phase
- **Tone:** Analytical
- **Advice:** Ask for every purchase: Does this generate income or cost me money?

#### Pay Yourself First
- **Category:** Wealth Mindset
- **Phase:** Stability, Growth, Legacy
- **Trigger:** Low savings rate, month start, paycheck received
- **Tone:** Firm
- **Advice:** Set up automatic transfers. 10% minimum to savings before you see it.

#### Multiple Income Streams
- **Category:** Wealth Mindset
- **Phase:** Stability, Growth, Legacy
- **Trigger:** Single income source, job insecurity
- **Tone:** Encouraging
- **Advice:** Identify one skill others would pay for. Spend 5 hours this month testing it.
- **Metaphor:** "A table with one leg falls easily. Four legs make it stable."

#### Invest in Financial Education
- **Category:** Wealth Mindset
- **Phase:** All phases
- **Trigger:** Confusion about money, new user
- **Tone:** Friendly
- **Advice:** Read one finance book this quarter. Listen to one podcast per week.
- **Habits:** Weekly financial learning, quarterly book reading

### Emotional Intelligence Principles

#### Notice Emotions Before They Act
- **Category:** Emotional Intelligence
- **Phase:** All phases
- **Trigger:** Stress spending, emotional purchase, high stress
- **Tone:** Compassionate
- **Advice:** Ask "What am I really feeling?" before buying
- **Quote:** "Between stimulus and response there is a space. In that space is our power to choose."

#### Gratitude Changes Spending
- **Category:** Emotional Intelligence
- **Phase:** All phases
- **Trigger:** Feeling scarcity, comparison trap, dissatisfaction
- **Tone:** Friendly
- **Advice:** Write down 3 things you're grateful for each day
- **Habits:** Daily gratitude practice

#### Forgive Financial Mistakes
- **Category:** Emotional Intelligence
- **Phase:** Debt Payoff, Stability
- **Trigger:** Guilt, overspending, financial mistake
- **Tone:** Compassionate
- **Advice:** Write what happened, what you learned, what you'll do differently. Then move forward.
- **Metaphor:** "A GPS doesn't judge you for missing a turn—it just recalculates."

### Balance & Health Principles

#### Rest Well, Decide Well
- **Category:** Balance & Health
- **Phase:** All phases
- **Trigger:** High stress, low energy, burnout, poor sleep
- **Tone:** Compassionate
- **Advice:** Don't make financial decisions when exhausted. Rest first.
- **Metaphor:** "You can't pour from an empty cup."

#### Align Finances with Values
- **Category:** Balance & Health
- **Phase:** Stability, Growth, Legacy
- **Trigger:** Value misalignment, life transition
- **Tone:** Friendly
- **Advice:** List top 3 values. Review spending. Does it reflect those values?
- **Habits:** Quarterly values review

### Habit Building Principles

#### Progress, Not Perfection
- **Category:** Habit Building
- **Phase:** All phases
- **Trigger:** Perfectionism, giving up, missed goal, self-criticism
- **Tone:** Compassionate
- **Advice:** You don't need a perfect month. You need a better-than-last-month month.
- **Quote:** "You don't have to be great to start, but you have to start to be great."

#### Automate to Eliminate Willpower
- **Category:** Behavioral Economics
- **Phase:** Stability, Growth
- **Trigger:** Decision fatigue, inconsistent savings
- **Tone:** Analytical
- **Advice:** Automate your 3 most important money moves
- **Habits:** Automate savings, automate bills

#### Celebrate Small Wins
- **Category:** Habit Building
- **Phase:** All phases
- **Trigger:** Low motivation, progress made, milestone reached
- **Tone:** Motivational
- **Advice:** Write down wins. Tell someone. Acknowledge progress.
- **Metaphor:** "Every mountain is climbed one step at a time."

### Behavioral Economics Principles

#### Momentum Over Math
- **Category:** Behavioral Economics
- **Phase:** Debt Payoff
- **Trigger:** Debt payoff, low motivation, analysis paralysis
- **Tone:** Motivational
- **Advice:** Don't overthink the math. Pick the smallest debt and crush it.

#### Simplify to Sustain
- **Category:** Behavioral Economics
- **Phase:** All phases
- **Trigger:** Too many goals, overwhelm, goal setting
- **Tone:** Analytical
- **Advice:** Choose your #1 financial goal for this quarter. Do that first.
- **Habits:** Quarterly goal review

## Future Expansion

The Philosophy Engine is designed to grow. Future additions could include:

### Stoic Finance Principles
- Control what you can control
- Negative visualization (prepare for setbacks)
- Voluntary discomfort (practice frugality intentionally)

### Minimalism & Intentional Living
- Less is more
- Buy experiences, not things
- One in, one out rule

### FIRE Movement Principles
- Extreme savings rate
- Coast FI, Barista FI, Lean FI
- Geographic arbitrage

### Entrepreneurship Mindset
- Invest in yourself
- Take calculated risks
- Build systems, not just income

### Cultural Wisdom
- Japanese Ikigai (reason for being)
- Swedish Lagom (balance, "just right")
- Danish Hygge (comfort, contentment)

## Adding New Principles

To add a new principle:

```python
engine.add_principle(Principle(
    id="unique_id",
    title="Principle Name",
    description="What it means in one clear sentence",
    category=PhilosophyCategory.HABIT_BUILDING,
    trigger_conditions=["when_relevant", "user_behavior"],
    preferred_tone=Tone.ENCOURAGING,
    relevant_phases=[LifePhase.STABILITY, LifePhase.GROWTH],
    actionable_advice="Specific next step the user can take",
    quote="Optional inspiring quote",
    metaphor="Optional metaphor for clarity",
    follow_up_habits=["habit_to_build"],
    source="Attribution if applicable"
))
```

## Integration with User Profile

The Philosophy Engine works seamlessly with the User Profile System:

```python
# User profile provides:
- Life phase (detected from debts, goals, income)
- Preferred communication tone
- Stress triggers and patterns
- Goals and aspirations
- Recent behavior (detected from entries)

# Philosophy engine uses this to:
- Select relevant principles
- Adapt tone dynamically
- Provide contextualized advice
- Reference user's goals and progress
```

## Testing Philosophy Context

```bash
# Test the engine
python -c "
from tracker.services.philosophy_engine import PhilosophyEngine, LifePhase

engine = PhilosophyEngine()
context = {
    'phase': LifePhase.DEBT_PAYOFF,
    'recent_behavior': ['high_stress', 'has_debt'],
    'stress_level': 8
}

principles = engine.get_relevant_principles(context, limit=2)
for p in principles:
    print(f'{p.title}: {p.description}')
"
```

## Best Practices

### For AI Prompt Engineering
- Always include philosophy context in feedback prompts
- Reference 1-2 principles per feedback (not all of them)
- Use principles conversationally, not academically
- Adapt quotes and metaphors to user's situation

### For Principle Design
- Keep descriptions to 1-2 clear sentences
- Make advice specific and actionable
- Include metaphors when they clarify
- Attribute sources (Ramsey, Kiyosaki, etc.) for credibility

### For Tone Adaptation
- Override user preference when compassion is needed (high stress)
- Use motivational tone for wins and streaks
- Use firm tone when accountability is needed
- Default to friendly for neutral situations

## Philosophy in Action

When a user creates an entry with high stress and debt, the system:

1. **Detects:** Debt Payoff phase, high stress (8/10), has debt
2. **Selects:** "Debt Snowball" + "Rest Well, Decide Well"
3. **Chooses Tone:** Compassionate (stress override)
4. **Generates:** Feedback that validates struggle, encourages rest, then motivates with snowball method

The result is AI that feels like a wise friend who truly understands your journey.

---

**The Philosophy Engine is the heart of Tracker's wisdom. It transforms data into meaningful guidance, numbers into encouragement, and entries into a journey of growth.** 🚀
