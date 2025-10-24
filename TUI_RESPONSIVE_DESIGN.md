# TUI Responsive Design Implementation

## Summary
Made all TUI menus responsive to work smoothly in narrow terminals (as narrow as 50-60 columns). The app now automatically adapts table layouts, column widths, and text wrapping based on terminal width.

## Changes Made

### Responsive Breakpoint
- **Wide mode**: Terminal width ≥ 80 columns (full detail view)
- **Narrow mode**: Terminal width < 80 columns (compact view)

### Updated Components

#### 1. View Entries (`handle_view_entries`)
**Wide Mode (≥80 cols)**:
- Columns: #, Date, Income, Expenses, Balance, Stress, Priority
- Full financial breakdown

**Narrow Mode (<80 cols)**:
- Columns: #, Date, Net, Stress, Priority
- Shows net balance instead of separate income/expenses
- Priority text truncates with "..." if needed
- Text wrapping enabled

#### 2. Search Results (`handle_search`)
**Wide Mode**: Same as View Entries
**Narrow Mode**: Same compact layout as View Entries

#### 3. Entry Detail View (`show_entry_detail`)
**Wide Mode**:
- Full financial breakdown with divider lines
- All field labels spelled out
- Standard padding (1, 2)

**Narrow Mode**:
- Compact format without divider lines
- Shorter field labels (e.g., "Financial" instead of "Financial Summary")
- Reduced padding (1, 1)
- Icons still visible but less descriptive text

#### 4. Chat List (`handle_chat`)
**Wide Mode**:
- Columns: #, ID, Title, Type, Messages, Last Updated
- Full datetime format (YYYY-MM-DD HH:MM)

**Narrow Mode**:
- Columns: #, Title, Msgs, Updated
- Title truncates at 25 chars with "..."
- Shorter date format (MM-DD HH:MM)
- Text wrapping enabled

#### 5. Profile View (`handle_profile`)
**Wide Mode**:
- Full field names (e.g., "Preferred Tone", "Context Depth")
- Standard padding (0, 2)

**Narrow Mode**:
- Shorter field names (e.g., "Tone", "Context")
- Compact padding (0, 1)
- Fixed field column width (18 chars)
- Value column allows text wrapping

**Panel Titles**:
- Wide: "👤 User Profile\nManage your personal information"
- Narrow: "👤 Profile"

## Technical Implementation

### Detection Method
```python
is_narrow = console.width < 80
```

### Table Configuration
```python
# Narrow mode settings
table = Table(
    show_header=True,
    header_style="bold cyan",
    box=None if is_narrow else None,  # Can customize box style
)

# Flexible columns
table.add_column("Title", no_wrap=False)  # Allows wrapping
table.add_column("Field", width=18)       # Fixed width
```

### Conditional Layouts
```python
if not is_narrow:
    # Full detail view
    table.add_row(all_columns)
else:
    # Compact view
    table.add_row(essential_columns_only)
```

## Testing Results

Tested with terminal widths:
- ✅ 120 columns (wide, normal desktop)
- ✅ 80 columns (standard)
- ✅ 60 columns (narrow)
- ✅ 50 columns (very narrow)

All menus tested:
- ✅ Main menu (unchanged - already compact)
- ✅ View Entries (responsive)
- ✅ Search Entries (responsive)
- ✅ Entry Detail (responsive)
- ✅ Chats List (responsive)
- ✅ Profile Menu (responsive)

## Benefits

1. **Mobile/SSH friendly**: Works great over phone SSH sessions
2. **Split-pane compatible**: Can use alongside other terminal windows
3. **No horizontal scrolling**: Everything fits within terminal width
4. **Automatic adaptation**: No user configuration needed
5. **Preserves functionality**: All data still accessible, just more compact
6. **No breaking changes**: Wide terminals still get full experience

## Examples

### View Entries - Narrow Mode (60 cols)
```
 #    Date              Net  Stress   Priority             
 1    2025-10-22   $-215.00   5/10    Staying awake        
 2    2025-10-21    $-64.00   5/10    Building tracker app 
```

### Chat List - Narrow Mode (60 cols)
```
 #    Title                    Msgs  Updated    
 1    Testing Chat Feature        5  10-23 00:19
 2    Chat: October 21, 202...    3  10-23 00:06
```

### Profile - Narrow Mode (60 cols)
```
 Nickname            Ethan       
 Tone                encouraging 
 Context             personal    
 Entries             3           
 Streak              2 days      
```

## Code Changes Summary

**File**: `src/tracker/cli/tui/app.py`

- Added `is_narrow = console.width < 80` checks throughout
- Modified table column definitions with conditional logic
- Adjusted panel titles and padding based on width
- Shortened field labels in narrow mode
- Enabled text wrapping with `no_wrap=False` where appropriate
- Truncated long text with ellipsis in compact views

## Notes

- Main menu unchanged (already compact and fits in narrow terminals)
- Stats and Achievements menus unchanged (handled by their respective CLI commands)
- Export menu unchanged (simple selection list)
- Width detection happens dynamically, so resizing terminal takes effect on next screen
- Icons still display (fallback to text if terminal doesn't support Unicode)
