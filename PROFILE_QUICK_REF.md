# User Profile Quick Reference

## Commands

```bash
# Setup (first time)
tracker profile setup

# View current profile
tracker profile view

# Update sections
tracker profile update

# Monthly check-in
tracker profile checkin
```

## Privacy Levels

| Level | What's Shared | AI Knows |
|-------|---------------|----------|
| **basic** | Spending, stress logs | Generic feedback, basic patterns |
| **personal** | + Work, bills, goals | Schedule-aware, goal progress, financial insights |
| **deep** | + AI-detected patterns | Pattern recognition, predictive insights, emotional trends |

## Profile Sections

### Always Available
- ✅ Nickname
- ✅ Preferred tone (casual/professional/encouraging/stoic)
- ✅ Privacy level
- ✅ Emotional baseline (energy, stress)
- ✅ Stress triggers & calming activities
- ✅ Entry stats (streak, total entries)

### Personal & Deep Modes
- 💼 Work info (job, pay schedule, hours)
- 💰 Financial overview (income, bills, debts)
- 🎯 Goals (short-term, long-term)
- 🏃 Lifestyle (gym, subscriptions, spending patterns)

### Deep Mode Only
- 🧠 AI-detected patterns (recurring themes, triggers)

## Example Feedback Evolution

### Without Profile
> "You logged your entry today. Good job staying consistent!"

### With Basic Profile (3-day streak)
> "Nice work, that's 3 days in a row! Keep the momentum going."

### With Personal Profile (12-day streak, goal: $5k emergency fund)
> "Hey Sarah! 12 days straight—amazing! You're 60% to your $5k emergency fund goal. At this pace, you'll hit it by May. Your rent is due in 3 days, but with payday tomorrow, you're set. One day at a time! 💪"

### With Deep Profile (detected pattern: stress spikes mid-month)
> "Hey Sarah! 12 days straight—you're crushing it. I notice your stress tends to spike mid-month when rent and bills hit together. But look—you kept it at 6 today despite all that. Last time you felt like this, a gym session helped reset. You're doing great. 🌟"

## Data Security

✅ **Encrypted**: Work, financial, goals, lifestyle data  
✅ **Local-only**: Never leaves your database  
✅ **User-controlled**: Choose your privacy level  
✅ **Gradual opt-in**: Start basic, upgrade later  

## Quick Setup Flow

```bash
tracker profile setup

# You'll be asked:
# 1. Nickname? (optional)
# 2. Preferred tone? (1-4)
# 3. Privacy level? (1-3)
# 4. Average energy? (1-10)
# 5. Average stress? (1-10)
# 6. Stress triggers? (comma-separated)
# 7. Calming activities? (comma-separated)
# 8. Want to add work/financial info? (if personal/deep)
```

Takes ~2 minutes for basic, ~5 minutes for full setup.

## Monthly Check-Ins

Every 30 days, Tracker will prompt:
```bash
tracker profile checkin
```

Updates:
- Changed bills/debts?
- Work situation same?
- Goals still relevant?

Keeps AI context fresh without being intrusive.

## Tips

🎯 **Start small**: Begin with basic mode, upgrade as you trust it  
🔄 **Monthly refresh**: Run check-ins to keep context accurate  
💬 **Try different tones**: See what communication style you prefer  
📊 **Track streaks**: Profile auto-tracks your consistency  
🧠 **Deep mode unlocks**: Pattern detection after 30+ entries  

## Tone Examples

**Casual**: "You crushed it today! 💪"  
**Professional**: "Excellent work managing your budget today."  
**Encouraging**: "I'm so proud of you for keeping at it!"  
**Stoic**: "Entry logged. Streak: 5 days. Progress continues."

## Integration with Tracker

Profile works seamlessly:
- ✅ `tracker new` - Creates entry, updates stats automatically
- ✅ AI feedback - Uses profile context in all modes
- ✅ `tracker chat` - Chat knows your profile
- ✅ Streaks - Tracked and displayed in feedback
- ✅ Goals - Referenced in insights and encouragement

## Future Features (Coming Soon)

🔮 **AI Planning**: Simulate financial decisions  
📊 **Dashboard**: Visual profile summary  
🎯 **Goal Tracker**: Progress bars and timelines  
⏰ **Smart Reminders**: Based on your schedule  
🧠 **Pattern Insights**: "I noticed you tend to..."

---

**The more you share, the smarter Tracker becomes. Start with what you're comfortable with.** 🚀
