# Profile Editing Improvements - October 24, 2025

## New Features

### 1. TUI Option 5: Edit Individual Fields ✅
**Location**: `src/tracker/cli/tui/app.py`

**Added new menu option in Profile section**:
```
1. Update Nickname
2. Update Tone & Preferences
3. Update Emotional Baseline
4. Full Profile Setup
5. Edit Individual Fields  ← NEW!
0. Back
```

**Features**:
- Shows current value before each field
- Press Enter to keep current value
- Edit only what you want to change
- Immediate feedback on updates
- No need to re-enter everything

**Fields you can edit**:
- Nickname
- Preferred tone (casual/professional/encouraging/stoic)
- Context depth (basic/personal/deep)
- Average energy level (1-10)
- Average stress level (1-10)

**Example Flow**:
```
Edit Profile Fields
Press Enter to keep current value, or type new value

Basic Information
Current: John
Nickname: [Enter to keep, or type new name]
✓ Updated!

Current: casual
Preferred Tone: 1=casual, 2=professional, 3=encouraging, 4=stoic
Choose (or Enter to skip): 3
✓ Updated!

Current: personal
Context Depth: 1=basic, 2=personal, 3=deep
Choose (or Enter to skip): [Enter]
(kept as personal)

Emotional Baseline
Current: 7/10
Average energy level (1-10, or Enter to skip): 8
✓ Updated!

Current: 6/10
Average stress level (1-10, or Enter to skip): [Enter]
(kept as 6)

✅ Profile updated!
```

### 2. Improved Profile Setup Wizard ✅
**Location**: `src/tracker/cli/commands/profile.py`

**Problem**: Typo in last question = redo entire section

**Solution**: Added confirmation after each question

**New Flow**:
```
Step 1: Basic Information
Press Enter to accept, or type 'back' to go to previous question

What should I call you?: John Doe
You entered: John Doe
Is this correct? [Y/n]: y

Preferred tone for feedback:
  1. Casual & friendly
  2. Professional & direct
  3. Encouraging & supportive
  4. Stoic & analytical
Choose [1/2/3/4] (1): 2
You chose: professional
Is this correct? [Y/n]: n

[Asks again...]
Choose [1/2/3/4] (1): 3
You chose: encouraging
Is this correct? [Y/n]: y

✓ Basic info saved!

Step 2: Emotional Baseline
You can correct any mistakes before saving

On average, what's your energy level? (1-10) [5]: 7
You entered: 7/10
Is this correct? [Y/n]: y

On average, what's your stress level? (1-10) [5]: 6
You entered: 6/10
Is this correct? [Y/n]: y

What are your main stress triggers? (comma-separated): work deadlines, bills
Triggers: work deadlines, bills
Is this correct? [Y/n]: n

[Asks again...]
What are your main stress triggers? (comma-separated): work deadlines, unexpected bills, traffic
Triggers: work deadlines, unexpected bills, traffic
Is this correct? [Y/n]: y

✓ Emotional baseline saved!
```

**Benefits**:
- Fix typos immediately
- No need to restart sections
- See what you entered before confirming
- More confidence in data entry

### 3. Enhanced Profile Update Command ✅
**Location**: `src/tracker/cli/commands/profile.py`

**Before**:
```bash
tracker profile update
# Choose section
# Re-enter ALL fields in that section
```

**After**:
```bash
tracker profile update
# Choose section
# See current values
# Update only what you want
```

**Example**:
```
Update Profile
Press Enter to keep current value

What would you like to update?
  1. Basic info (nickname, tone, context depth)
  2. Emotional baseline (energy, stress, triggers)
  3. Work information
  4. Financial information
  5. Goals
  6. Lifestyle

Choose section [1/2/3/4/5/6]: 1

Basic Information
Current nickname: John
New nickname (or Enter to keep): John Doe

Current tone: casual
1=casual, 2=professional, 3=encouraging, 4=stoic
New tone (or Enter to keep): 3

Current context: basic
1=basic, 2=personal, 3=deep
New context depth (or Enter to keep): [Enter]

✓ Profile updated!
```

**Emotional Baseline Updates**:
```
Choose section [1/2/3/4/5/6]: 2

Emotional Baseline
Current energy: 7/10
New average energy (1-10, or Enter to keep): [Enter]

Current stress: 6/10
New average stress (1-10, or Enter to keep): 5

Edit stress triggers? (comma-separated)
Stress triggers (or Enter to keep current): [Enter]

Edit calming activities? (comma-separated)
Calming activities (or Enter to keep current): meditation, exercise, music

✓ Profile updated!
```

## Implementation Details

### Files Modified:
1. `src/tracker/cli/tui/app.py`
   - Added `_edit_profile_fields()` function
   - Added menu option 5
   - Updated choices array

2. `src/tracker/cli/commands/profile.py`
   - Enhanced `setup()` with confirmation loops
   - Rewrote `update()` with current value display
   - Added field-by-field editing

### New Function:
```python
def _edit_profile_fields(console, service, user_id: int):
    """Edit individual profile fields one at a time"""
    # Shows current values
    # Press Enter to keep, or type new value
    # Immediate updates with feedback
```

## User Experience Improvements

### Before:
```
❌ Setup wizard:
   - Typo on question 5? → Start over from question 1
   - No way to see what you entered
   - No confirmation before saving

❌ Profile update:
   - Want to change nickname? → Re-enter tone, context too
   - Want to update stress? → Re-enter energy, triggers too
   - No field-level granularity
```

### After:
```
✅ Setup wizard:
   - Typo anywhere? → Fix it immediately
   - See your entry before confirming
   - Confirm each question
   - No need to restart

✅ Profile update:
   - Change only what you want
   - See current values
   - Press Enter to keep
   - Fine-grained control
```

## Access Points

### 1. TUI Path:
```
tracker tui
→ 9. Profile
→ 5. Edit Individual Fields
```

### 2. CLI Path:
```bash
# Setup wizard (with confirmations)
tracker profile setup

# Update specific sections
tracker profile update
```

### 3. Quick Update:
```bash
# From TUI
tracker tui → Profile → 5. Edit Individual Fields

# From CLI
tracker profile update → Choose section → Edit fields
```

## Benefits

### 1. Less Friction
- Edit one field without touching others
- Fix typos without restarting
- See what you have before changing

### 2. More Control
- Granular field-level editing
- Clear indication of current values
- Choice to keep or update

### 3. Better UX
- Confirmation prompts in wizard
- Instructions always visible
- No lost progress

### 4. Time Savings
- Update nickname: ~5 seconds (not 30 seconds)
- Fix typo: Immediate (not restart section)
- Change one value: One prompt (not all prompts)

## Testing

```bash
✓ All files compile successfully
✓ No syntax errors
```

### Manual Test Scenarios:

**Scenario 1: Fix Typo in Setup**
1. Run `tracker profile setup`
2. Enter nickname correctly
3. Enter tone incorrectly
4. Answer "n" to "Is this correct?"
5. Re-enter tone correctly
6. Complete setup

**Scenario 2: Update Only Nickname**
1. Run `tracker tui` → Profile → 5
2. Type new nickname
3. Press Enter for all other fields
4. Verify only nickname changed

**Scenario 3: Update Only Stress Level**
1. Run `tracker profile update`
2. Choose "2. Emotional baseline"
3. Press Enter for energy
4. Enter new stress level
5. Press Enter for triggers/activities
6. Verify only stress changed

## Token Usage

This session total: ~106K tokens (~11% of budget)
Remaining: ~894K tokens (89%)

## Future Enhancements

Potential improvements:
- [ ] Work/Financial/Goals field-by-field editing (currently requires re-entry)
- [ ] Bulk edit mode (edit multiple fields in one session)
- [ ] Import/export profile settings
- [ ] Profile templates for quick setup
- [ ] Undo last profile change
