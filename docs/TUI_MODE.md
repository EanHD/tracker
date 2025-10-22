# Tracker TUI Mode - Interactive Terminal Interface

## Overview

The Tracker TUI (Terminal User Interface) provides a full-screen, menu-driven interface for interacting with your daily tracker. It's built with [Textual](https://textual.textualize.io/), offering a beautiful and intuitive experience directly in your terminal.

## Features

### 🎯 Three Ways to Use Tracker

1. **Traditional CLI Commands** - Quick, scriptable commands
   ```bash
   tracker new --income 150 --bills 50
   tracker show today
   tracker stats
   ```

2. **Interactive TUI** - Full-screen menu navigation
   ```bash
   tracker tui
   ```

3. **Server Mode** - REST API for frontends
   ```bash
   tracker server
   # Then build/use a web frontend
   ```

## Launching the TUI

```bash
# Start the interactive TUI
tracker tui
```

## Navigation

### Keyboard Shortcuts

- **Arrow Keys** - Navigate through menus and buttons
- **Tab** - Move focus between elements
- **Enter** - Activate selected button
- **Escape** - Go back to previous screen
- **Hotkeys** - Press the letter in parentheses for quick access

### Main Menu Hotkeys

| Key | Action |
|-----|--------|
| `n` | New Entry |
| `v` | View Entries |
| `s` | Search |
| `t` | Statistics |
| `a` | Achievements |
| `c` | Configuration |
| `e` | Export Data |
| `p` | Profile |
| `q` | Quit |

## Screens

### 📝 New Entry

Create a new daily entry with an interactive form:
- All fields with validation
- Default values (e.g., today's date)
- Keyboard shortcuts: `Ctrl+S` to save, `Esc` to cancel
- Real-time input validation

**Fields:**
- Date (defaults to today)
- Financial: Income, Bills, Food, Entertainment, Shopping, Health, Transport, Education, Gifts, Other
- Work & Wellbeing: Work Hours, Stress Level, Mood Level, Sleep Hours, Exercise Minutes, Social Minutes
- Notes (optional)

### 👁️ View Entries

Browse your recent entries in a table:
- Last 30 days of entries
- Shows: Date, Income, Expenses, Balance, Work Hours, Mood, Stress
- Press `r` to refresh
- Scrollable list

### 🔍 Search

Search through your entry notes:
- Enter keywords to search
- Results show matching entries with date, notes snippet, and mood
- Press `Ctrl+F` to execute search

### 📊 Statistics

View comprehensive statistics:
- Last 30 days summary
- Financial overview (income, expenses, balance)
- Work & wellbeing averages
- Tracking stats (entries, streak)
- Press `r` to refresh

### 🏆 Achievements

View your unlocked achievements and progress:
- Unlocked achievements with descriptions
- Locked achievements (yet to unlock)
- Current and longest streak
- Total points

### ⚙️ Configuration

View current configuration:
- AI settings (provider, model, temperature)
- Database path
- API server settings
- Security status

**Note:** To modify settings, use the CLI:
```bash
tracker config set ai_provider openai
tracker config set ai_model gpt-4
```

### 📤 Export Data

Export your entries:
- CSV format - for spreadsheets
- JSON format - for programmatic access
- Files saved to current directory with timestamp

**For advanced export options, use CLI:**
```bash
tracker export --format csv --output mydata.csv --start-date 2024-01-01
```

### 👤 Profile

View user profile information:
- Username, email
- Account creation date

## Combining Modes

### Use Cases

1. **Daily Logging with TUI**
   ```bash
   # Morning routine - use TUI for detailed entry
   tracker tui
   # (Navigate to New Entry, fill form)
   ```

2. **Quick Updates with CLI**
   ```bash
   # Quick midday update
   tracker edit today --income 50
   ```

3. **Automation with CLI**
   ```bash
   # Script for recurring tasks
   #!/bin/bash
   tracker new --bills 500 --notes "Monthly rent"
   ```

4. **Frontend Integration**
   ```bash
   # Terminal 1: Start server
   tracker server
   
   # Terminal 2: Run your custom frontend
   npm run dev
   ```

### Server + TUI Workflow

You can run both simultaneously:

```bash
# Terminal 1: Keep server running for API access
tracker server --port 5703

# Terminal 2: Use TUI for interactive work
tracker tui

# Terminal 3: Use CLI commands for quick tasks
tracker show today
```

They all share the same database, so changes in one mode are immediately available in others.

## Development Mode

For TUI development and debugging:

```bash
# Enable debug logging
export DEBUG=1
tracker tui

# Watch for code changes (requires textual dev tools)
textual run --dev tracker.cli.tui.app:TrackerTUI
```

## Advantages of Each Mode

### CLI Commands
✅ Fast for single operations  
✅ Scriptable and automatable  
✅ SSH-friendly  
✅ Low resource usage  

### TUI Mode
✅ Visual feedback  
✅ No need to remember commands  
✅ Form validation before submit  
✅ Browse and navigate easily  
✅ Great for complex entry creation  

### Server Mode
✅ Build custom frontends  
✅ Web/mobile app integration  
✅ Multi-user support  
✅ RESTful API  
✅ Integration with other tools  

## Tips

1. **Quick Entry Creation**: Use TUI for your daily detailed entries
2. **Quick Updates**: Use CLI commands for minor edits
3. **Analysis**: Use TUI stats screen or CLI with `tracker stats --plot`
4. **Automation**: Use CLI in scripts and cron jobs
5. **Custom Frontend**: Run server mode and build your own UI

## Keyboard Shortcuts Summary

| Shortcut | Action |
|----------|--------|
| `Esc` | Back/Cancel |
| `Tab` | Next field |
| `Shift+Tab` | Previous field |
| `Enter` | Activate button |
| `Ctrl+S` | Save (in forms) |
| `Ctrl+F` | Search/Filter |
| `Ctrl+C` | Quit application |
| `r` | Refresh (in list views) |

## Troubleshooting

### TUI doesn't start
```bash
# Ensure textual is installed
uv pip install textual

# Or reinstall the package
uv pip install -e .
```

### Display issues
```bash
# Try different terminal
# Recommended: kitty, alacritty, wezterm, iTerm2, Windows Terminal

# Check terminal size
echo $COLUMNS x $LINES
# TUI needs at least 80x24
```

### Styling issues
```bash
# Ensure terminal supports 256 colors
echo $TERM
# Should be: xterm-256color or similar
```

## Architecture

### File Structure
```
src/tracker/cli/
├── tui/
│   ├── __init__.py
│   ├── app.py              # Main TUI app and menu
│   └── screens/
│       ├── __init__.py
│       ├── new_entry.py    # Entry creation form
│       ├── view_entries.py # Entry list view
│       ├── search.py       # Search interface
│       ├── stats.py        # Statistics display
│       ├── achievements.py # Achievements view
│       ├── config.py       # Configuration view
│       ├── export.py       # Export interface
│       └── profile.py      # Profile view
└── commands/
    └── tui.py              # TUI command registration
```

### Technology Stack
- **Textual** - TUI framework (based on Rich)
- **Rich** - Terminal formatting (shared with CLI)
- **SQLAlchemy** - Database access (shared with server)
- **Click** - Command registration

All three modes (CLI, TUI, Server) share:
- Same database
- Same models and schemas
- Same business logic (services)
- Same configuration

## Future Enhancements

Potential improvements for the TUI:

1. **Real-time AI feedback** - Show AI insights in TUI
2. **Charts and graphs** - Visual data in terminal
3. **Entry editing** - Edit past entries within TUI
4. **Batch operations** - Select and operate on multiple entries
5. **Themes** - Customizable color schemes
6. **Shortcuts config** - User-defined keybindings
7. **Split view** - View stats while creating entries

## See Also

- [CLI Documentation](../README.md#cli-usage)
- [API Documentation](../docs/API.md)
- [Configuration Guide](../docs/CONFIGURATION.md)
- [Textual Documentation](https://textual.textualize.io/)
