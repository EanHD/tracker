# Hotfix: Chat Context & Profile Setup - October 24, 2025

## Issues Fixed

### 1. Chat Context UserProfile Attribute Error ✅
**Error**: `'UserProfile' object has no attribute 'display_name'`

**Location**: `src/tracker/services/chat.py`

**Problem**: 
- Code referenced `profile.display_name` which doesn't exist
- Also referenced `profile.communication_style`, `profile.primary_goals`, `profile.coping_strategies` which don't exist
- UserProfile model uses different field names

**Fix**:
Changed to correct field names:
- `display_name` → `nickname`
- `communication_style` → `preferred_tone`
- `primary_goals` → (removed, uses encrypted goals_encrypted)
- `coping_strategies` → `calming_activities`

**Actual UserProfile Fields**:
```python
# Basic Info
nickname = Column(String(100), nullable=True)
preferred_tone = Column(String(50), nullable=True)  # casual, professional, encouraging, stoic
context_depth = Column(String(20), default="basic", nullable=False)  # basic, personal, deep

# Encrypted fields (JSON)
work_info_encrypted = Column(Text, nullable=True)
financial_info_encrypted = Column(Text, nullable=True)
goals_encrypted = Column(Text, nullable=True)
lifestyle_encrypted = Column(Text, nullable=True)

# Emotional Context
stress_triggers = Column(Text, nullable=True)  # JSON array
calming_activities = Column(Text, nullable=True)  # JSON array
baseline_energy = Column(Integer, default=5, nullable=False)
baseline_stress = Column(Float, default=5.0, nullable=False)
```

### 2. Profile Setup (Option 4) Returns Nothing ✅
**Error**: Selecting option 4 "Full Profile Setup" returned nothing

**Location**: `src/tracker/cli/tui/app.py`

**Problem**: 
- Import path was incorrect: `from tracker.cli.profile import profile`
- Should be: `from tracker.cli.commands.profile import profile`
- Missing `standalone_mode=False` in CliRunner invocation

**Fix**:
```python
# Before
from tracker.cli.profile import profile as profile_cmd
runner.invoke(profile_cmd, ['setup'], catch_exceptions=False)

# After
from tracker.cli.commands.profile import profile as profile_cmd
runner.invoke(profile_cmd, ['setup'], catch_exceptions=False, standalone_mode=False)
```

Applied fix to both:
- Line 859: Create profile when none exists (option 1 in no-profile state)
- Line 903: Full profile setup (option 4 when profile exists)

## New Chat Context Structure

### For All Chats:
```python
# User Profile
Name: {nickname}
Preferred Tone: {preferred_tone}  # casual/professional/encouraging/stoic
Context Depth: {context_depth}    # basic/personal/deep
Stress Triggers: {stress_triggers}  # JSON array
Calming Activities: {calming_activities}  # JSON array
```

### For Standalone Chats (+ Recent Activity):
```python
# Recent Activity (Last 7 Days)
Entries logged: 7
Average stress: 5.2/10
Total income: $1,400.00
Total expenses: $850.00
Net: $550.00
```

### For Entry-Linked Chats (+ Entry Details):
```python
# Today's Journal Entry: October 24, 2025

## Financial
Income Today: $200.00
Side Income: $0.00
Bills Due: $150.00
Food Spending: $25.00
Gas Spending: $40.00
Net Balance: -$15.00

## Work & Wellbeing
Hours Worked: 8
Stress Level: 7/10
Priority Task: Finish project proposal

Journal Notes:
{full notes content}
```

## Files Modified

1. `src/tracker/services/chat.py` - Fixed UserProfile field references
2. `src/tracker/cli/tui/app.py` - Fixed profile setup import path

## Testing

```bash
✓ All files compile successfully
✓ Chat context now uses correct field names
✓ Profile setup option 4 now works
```

## Impact

**Before**:
- ❌ Chat throws error on any message
- ❌ Profile setup option 4 does nothing
- ❌ Can't use chat feature at all

**After**:
- ✅ Chat works in all sections (view, search, chat menu, retry)
- ✅ Profile setup runs correctly
- ✅ Context includes actual profile data
- ✅ Personalized responses work

## Root Cause

Initial chat integration referenced field names that don't exist in the actual UserProfile model. The model was designed with:
- Simple fields: nickname, preferred_tone, context_depth, stress_triggers, calming_activities
- Encrypted fields: work_info, financial_info, goals, lifestyle (as JSON)

The chat context should focus on the simple accessible fields and decrypt encrypted fields as needed (future enhancement).
