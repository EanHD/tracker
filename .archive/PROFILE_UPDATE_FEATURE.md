# Profile Management Feature - TUI Integration

## Summary
Successfully fixed and enhanced the TUI Profile menu (option 9) with interactive profile management capabilities.

## Issues Fixed

### 1. Profile Command Not Found Error
**Problem**: TUI was calling `profile show` which doesn't exist
- Wrong import path: `tracker.cli.commands.profile` 
- Wrong command: `show` instead of `view`

**Solution**: Updated `src/tracker/cli/tui/app.py`:
- Fixed import: `from tracker.cli.profile import profile as profile_cmd`
- Fixed command: `['view']` instead of `['show']`

### 2. Limited Profile Management
**Problem**: TUI only displayed profile info, couldn't update it

**Solution**: Created interactive profile management menu with options to:
- Update nickname
- Update tone & preferences
- Update emotional baseline
- Run full profile setup wizard

## Features Implemented

### Profile Menu Options

1. **Update Nickname** - Quick nickname change
2. **Update Tone & Preferences** - Change AI feedback style and context depth
   - Tone options: Casual, Professional, Encouraging, Stoic
   - Context depth: Basic, Personal, Deep
3. **Update Emotional Baseline** - Set average energy and stress levels (1-10)
4. **Full Profile Setup** - Launch comprehensive setup wizard
0. **Back** - Return to main menu

### Profile Display
Shows current profile information:
- Nickname
- Preferred Tone
- Context Depth
- Total Entries
- Current Streak
- Baseline Energy
- Baseline Stress

## User Profile Fields

### Basic Info
- `nickname` - Display name (default: username)
- `preferred_tone` - AI feedback style (casual/professional/encouraging/stoic)
- `context_depth` - How much context to share (basic/personal/deep)

### Emotional Context
- `baseline_energy` - Average energy level (1-10)
- `baseline_stress` - Average stress level (1-10)
- `stress_triggers` - List of stress triggers
- `calming_activities` - List of calming activities

### Advanced Fields (via Full Setup)
- Work information (encrypted)
- Financial information (encrypted)
- Goals (encrypted)
- Lifestyle preferences (encrypted)

## Testing Results

✅ Profile menu loads correctly  
✅ Displays current profile information  
✅ Nickname updates successfully  
✅ Tone & preferences update successfully  
✅ Changes persist to database  
✅ All updates are encrypted where appropriate  

## Usage

```bash
# Launch TUI
tracker tui

# Select option 9 (Profile)
# Choose update option:
#   1 - Quick nickname update
#   2 - Tone and context preferences
#   3 - Emotional baseline
#   4 - Complete setup wizard
```

## CLI Alternative

Users can also manage profiles via CLI:
```bash
tracker profile view      # View current profile
tracker profile setup     # Initial setup wizard
tracker profile update    # Update specific sections
tracker profile checkin   # Monthly check-in
```

## Notes

- "TestUser" was a placeholder - actual profile uses real user data
- All sensitive information (financial, work, goals) is encrypted
- Profile updates are immediate and persistent
- Context depth affects AI feedback richness
