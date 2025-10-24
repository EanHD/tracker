# User Profile & Context System

## Overview

The User Profile & Context System transforms Tracker from a simple logger into a truly personalized companion. By giving the AI richer context about you—your work, finances, goals, and emotional patterns—it can provide feedback that feels genuinely human and useful.

## Philosophy

> "The more Tracker knows about you, the smarter and more personalized its guidance becomes."

This isn't about collecting data—it's about building a living context that evolves with you. Think of it as your personal character sheet that the AI reads before giving feedback.

## Privacy Levels

You control how much context you share:

### Basic Mode (Default)
- **What's tracked**: Spending, stress, and basic patterns
- **Who it's for**: Privacy-conscious users who want minimal data sharing
- **AI benefits**: Generic but still empathetic feedback

### Personal Mode
- **What's tracked**: Work info, bills, debts, and goals
- **Who it's for**: Users who want smarter financial insights
- **AI benefits**: 
  - Reminders aligned with pay schedule
  - Bill timing awareness
  - Progress tracking toward goals
  - Work-life balance insights

### Deep Context Mode
- **What's tracked**: Everything in Personal + AI-detected patterns
- **Who it's for**: Users who want the richest, most personalized experience
- **AI benefits**:
  - Pattern recognition ("You mention work burnout often")
  - Predictive insights
  - Emotional trend analysis
  - Micro-goal suggestions

All sensitive data is **encrypted at rest** using field-level encryption.

## Getting Started

### Initial Setup

Run the interactive setup wizard:

```bash
tracker profile setup
```

This walks you through:
1. **Basic Info**: Nickname, preferred tone, privacy level
2. **Emotional Baseline**: Energy/stress levels, triggers, calming activities
3. **Work Setup** (optional): Job, pay schedule, commute
4. **Financial Info** (optional): Income, bills, debts
5. **Goals** (optional): Short-term and long-term aspirations

### Quick Commands

```bash
# View your current profile
tracker profile view

# Update specific sections
tracker profile update

# Monthly check-in (keeps data fresh)
tracker profile checkin
```

## What Gets Stored

### Basic Information
```json
{
  "nickname": "What the AI calls you",
  "preferred_tone": "casual | professional | encouraging | stoic",
  "context_depth": "basic | personal | deep"
}
```

### Work Information (Encrypted)
```json
{
  "job_title": "Your role",
  "employment_type": "hourly | salary",
  "pay_schedule": "weekly | biweekly | monthly",
  "typical_hours_per_week": 40,
  "commute_minutes": 30,
  "side_gigs": [
    {"name": "Weekend gig", "typical_income": 200}
  ]
}
```

### Financial Information (Encrypted)
```json
{
  "monthly_income": 4200,
  "income_sources": [
    {"source": "Main job", "amount": 3800},
    {"source": "Side gig", "amount": 400}
  ],
  "recurring_bills": [
    {"name": "Rent", "amount": 1200, "due_day": 1},
    {"name": "Car", "amount": 350, "due_day": 15}
  ],
  "debts": [
    {
      "name": "Chase Card",
      "balance": 2400,
      "min_payment": 75,
      "interest_rate": 18.99
    }
  ]
}
```

### Goals (Encrypted)
```json
{
  "short_term": [
    {
      "goal": "Save $5k emergency fund",
      "target_date": "2025-06-01",
      "target_amount": 5000
    }
  ],
  "long_term": [
    {
      "goal": "Buy hybrid car",
      "target_date": "2026-12-01",
      "target_amount": 15000
    }
  ]
}
```

### Lifestyle (Encrypted)
```json
{
  "gym_membership": true,
  "gym_cost": 40,
  "avg_gas_per_week": 50,
  "meals_out_per_week": 3,
  "avg_meal_cost": 15,
  "other_subscriptions": [
    {"name": "Netflix", "cost": 15}
  ]
}
```

### Emotional Context
```json
{
  "stress_triggers": ["tight deadlines", "unexpected expenses"],
  "calming_activities": ["gym", "gaming", "walks"],
  "baseline_energy": 6,
  "baseline_stress": 5.5
}
```

### AI-Detected Patterns (Deep Mode Only)
The AI automatically notices and records:
- Recurring themes in your notes
- Financial patterns (e.g., "stress spikes mid-month")
- Work-life balance trends
- Celebration moments
- Progress toward goals

## How AI Uses Your Profile

### Tone Adaptation
- **Casual**: "Hey! You crushed that overtime shift 💪"
- **Professional**: "Excellent work managing the additional hours this week."
- **Encouraging**: "I'm so proud of you for pushing through today!"
- **Stoic**: "You logged 9 hours. Debt decreased by $50. Progress continues."

### Context-Aware Insights

**Without Profile:**
> "You spent $45 on food today. Try to be mindful of spending."

**With Profile (Personal Mode):**
> "You spent $45 on food today, Sarah. With rent due in 3 days and your biweekly paycheck tomorrow, you're actually well-positioned. Your $5k emergency fund goal is 60% there—keep this momentum!"

**With Profile (Deep Mode):**
> "You spent $45 on food today, Sarah. I notice you tend to spend more on food when stress is high (like that 8/10 today). Last time this happened, a gym session helped reset your mindset. You mentioned the gym is your go-to calming activity—maybe hit it tomorrow before work?"

### Schedule Awareness
The AI can:
- Remind you paycheck is tomorrow
- Warn about bills due same week as rent
- Suggest spreading payments
- Track debt payoff timelines

### Goal Progress Tracking
```
"You're 3 weeks into your 4-week streak—that's tied with your longest ever! 
At your current save rate of $400/month, you'll hit that $5k emergency fund 
by May 2025. Just 3 months to go!"
```

## Monthly Check-Ins

Tracker prompts for a monthly check-in to keep your profile current:

```bash
tracker profile checkin
```

It asks:
- Have bills or debts changed?
- Is work situation the same?
- Do you want to update goals?

This ensures the AI's context stays accurate without being intrusive.

## Implementation Details

### Architecture

```
┌─────────────────────────────────────────┐
│  CLI Commands (profile.py)              │
│  - setup, view, update, checkin          │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  ProfileService (profile_service.py)     │
│  - get_or_create_profile()               │
│  - update_*_info()                       │
│  - get_ai_context()                      │
│  - update_entry_stats()                  │
└─────────────┬───────────────────────────┘
              │
┌─────────────▼───────────────────────────┐
│  UserProfile Model (models.py)           │
│  - Encrypted fields for sensitive data   │
│  - Privacy-aware getters/setters         │
│  - Streak tracking                       │
└──────────────────────────────────────────┘
```

### Database Schema

```sql
CREATE TABLE user_profiles (
  id INTEGER PRIMARY KEY,
  user_id INTEGER UNIQUE NOT NULL,
  
  -- Basic
  nickname VARCHAR(100),
  preferred_tone VARCHAR(50),
  context_depth VARCHAR(20) DEFAULT 'basic',
  
  -- Encrypted JSON fields
  work_info_encrypted TEXT,
  financial_info_encrypted TEXT,
  goals_encrypted TEXT,
  lifestyle_encrypted TEXT,
  detected_patterns_encrypted TEXT,
  
  -- Emotional context
  stress_triggers TEXT,  -- JSON array
  calming_activities TEXT,  -- JSON array
  baseline_energy INTEGER DEFAULT 5,
  baseline_stress FLOAT DEFAULT 5.0,
  
  -- Stats
  total_entries INTEGER DEFAULT 0,
  entry_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  last_entry_date DATE,
  last_monthly_checkin DATE,
  
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

### Services Integration

**FeedbackService** now:
1. Loads profile context via `ProfileService.get_ai_context()`
2. Updates entry stats automatically
3. Passes context to AI client

**AIClient** now:
1. Accepts `profile_context` parameter
2. Builds richer prompts with user info
3. Adapts tone based on preferences

## Example Workflow

### 1. User Sets Up Profile
```bash
$ tracker profile setup
Welcome to Tracker Profile Setup!
...
What should I call you? Sarah
Preferred tone: 3 (encouraging)
Context depth: 2 (personal)
...
✓ Profile setup complete!
```

### 2. User Creates Entry
```bash
$ tracker new
# Creates entry as usual
```

### 3. Behind the Scenes
```python
# When generating feedback:
profile_context = profile_service.get_ai_context(user_id=1)
# Returns: {
#   "nickname": "Sarah",
#   "preferred_tone": "encouraging",
#   "entry_streak": 12,
#   "stress_triggers": ["bills", "deadlines"],
#   "goals": {...},
#   ...
# }

# AI builds personalized prompt
feedback = ai_client.generate_feedback(
    entry=entry,
    character_sheet=char_sheet,
    profile_context=profile_context
)
```

### 4. User Gets Personalized Feedback
```
Hey Sarah! 🌟

12 days in a row—you're crushing it! I know tight finances have been 
stressing you out (especially with that rent coming up), but look at 
what you did today: minimal spending, solid work hours, and you kept 
stress at a 6 despite everything. That's resilience in action.

Your $5k emergency fund is 60% there. At this rate, you'll hit it by 
May—right when you wanted to. One day at a time, one entry at a time. 
You're doing amazing. 💪
```

## Future Expansions

### Adaptive AI Planning Mode
```bash
tracker profile simulate "pay $50 extra on car note"
```
AI simulates outcome: "Debt-free by March 2026, 3 months early!"

### Profile Summary Dashboard
Visual dashboard showing:
- Net worth trend
- Monthly cash flow
- Debt timeline
- Goal progress bars

### Goal Tracker Integration
Tie goals to emotional graph:
```
"You stayed under budget 3 weeks straight → stress down 20%"
```

### Smart Reminders
```
"Sarah, payday tomorrow! Want to pre-plan next week's gas and groceries?"
```

### Pattern Detection Insights
```
"I've noticed you log fewer entries when stress hits 8+. 
Want help making it easier to track during tough weeks?"
```

## Privacy & Security

- All sensitive fields use **AES encryption**
- Encryption keys stored securely via `encryption_service`
- Profile data never leaves your local database
- Users control context depth
- Can delete profile anytime with: `tracker profile delete`

## Migration Path

Existing users can:
1. Keep using Tracker without profile (basic mode auto-enabled)
2. Run `tracker profile setup` anytime to opt in
3. Upgrade privacy level gradually (basic → personal → deep)

## Best Practices

### For Users
- Start with **basic** or **personal** mode
- Run monthly check-ins to keep data fresh
- Be honest about stress triggers—it helps the AI help you
- Update goals as they change

### For Developers
- Always check `context_depth` before using profile data
- Encrypt any new sensitive fields
- Update AI prompts to use context naturally
- Test with all three privacy levels

## Testing

```bash
# Run with test database
TRACKER_DATABASE_PATH=test.db tracker profile setup

# View test profile
TRACKER_DATABASE_PATH=test.db tracker profile view

# Generate test entry with context
TRACKER_DATABASE_PATH=test.db tracker new
```

## Troubleshooting

**Q: Profile setup fails?**
A: Run `tracker init` first to create database.

**Q: AI not using my profile?**
A: Check context depth with `tracker profile view`. Must be "personal" or "deep" for work/financial context.

**Q: Want to reset profile?**
A: Delete and recreate:
```bash
tracker profile delete
tracker profile setup
```

**Q: Privacy concerns?**
A: All data is local and encrypted. Switch to "basic" mode or don't use profile features.

## Conclusion

The User Profile & Context System turns Tracker from a logging tool into a personalized companion that truly knows you. By sharing what you're comfortable with, you unlock AI feedback that feels human, relevant, and genuinely helpful.

Start small with basic mode, then level up as trust builds. Your future self will thank you. 🚀
