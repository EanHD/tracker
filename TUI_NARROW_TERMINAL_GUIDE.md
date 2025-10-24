# TUI Narrow Terminal Guide

## Quick Reference

The Tracker TUI now automatically adapts to your terminal width!

### Terminal Width Modes

**Wide Mode (≥80 columns)**: Full detail view with all columns
**Narrow Mode (<80 columns)**: Compact view optimized for small screens

### What Changes in Narrow Mode?

#### View Entries
- **Before**: #, Date, Income, Expenses, Balance, Stress, Priority
- **After**: #, Date, Net, Stress, Priority (combined income/expenses into net balance)

#### Search Results
- Same as View Entries - compact layout

#### Entry Details
- Shorter labels (e.g., "Financial" instead of "Financial Summary")
- No decorative divider lines
- Tighter spacing

#### Chat List
- **Before**: #, ID, Title, Type, Messages, Last Updated
- **After**: #, Title, Msgs, Updated (shorter date format)
- Titles truncate at 25 characters

#### Profile
- **Before**: "Preferred Tone", "Context Depth", etc.
- **After**: "Tone", "Context", etc. (shorter labels)
- More compact panel title

### Testing Your Terminal Width

```bash
# Check your current terminal width
tput cols

# Test with specific width (60 columns)
COLUMNS=60 tracker tui

# Test very narrow (50 columns)
COLUMNS=50 tracker tui

# Test wide (120 columns)
COLUMNS=120 tracker tui
```

### Perfect For

✅ SSH sessions on phones  
✅ Split terminal windows  
✅ Tmux/Screen panes  
✅ Small laptop screens  
✅ Remote access via phone apps (Termux, etc.)  

### What Stays the Same

- All functionality still works
- No data is hidden (just more compact)
- All menu options available
- Icons still display (if supported)
- Main menu unchanged

### Recommended Minimum Width

**Absolute minimum**: 50 columns  
**Comfortable**: 60+ columns  
**Optimal**: 80+ columns  

### Tips

1. **Text wrapping is enabled** - long priority names will wrap to next line
2. **Titles truncate gracefully** - you'll see "..." if text is cut off
3. **Resize anytime** - changes take effect on next screen refresh
4. **No configuration needed** - detection is automatic

### Before & After Examples

#### View Entries (120 cols vs 60 cols)

**Wide (120 cols)**:
```
 #    Date              Income    Expenses     Balance   Stress   Priority                  
 1    2025-10-22         $0.00     $215.00    $-215.00    5/10    Staying awake             
```

**Narrow (60 cols)**:
```
 #    Date              Net  Stress   Priority             
 1    2025-10-22   $-215.00   5/10    Staying awake        
```

#### Profile (120 cols vs 60 cols)

**Wide**:
```
╭──────────────────────────────────╮
│ 👤 User Profile                  │
│ Manage your personal information │
╰──────────────────────────────────╯

  Preferred Tone    encouraging  
  Context Depth     personal     
```

**Narrow**:
```
╭────────────╮
│ 👤 Profile │
╰────────────╯

  Tone        encouraging  
  Context     personal     
```

### Troubleshooting

**Issue**: Text looks squished or wraps awkwardly  
**Solution**: Increase terminal width to 60+ columns

**Issue**: Some columns are cut off  
**Solution**: Terminal might be below 50 columns - try increasing width

**Issue**: Want to force wide mode  
**Solution**: Resize terminal to 80+ columns and restart screen

### No Breaking Changes!

- Existing workflows unchanged
- Wide terminals get full experience
- Backward compatible
- All tests passing
