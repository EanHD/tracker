# Usage Modes Comparison

## Overview

Tracker offers three distinct modes of operation, each optimized for different use cases. All modes share the same database and business logic, so you can freely switch between them or use them simultaneously.

## Quick Comparison

| Feature | CLI Commands | Interactive TUI | Server Mode |
|---------|-------------|-----------------|-------------|
| **Speed** | ⚡⚡⚡ Instant | ⚡⚡ Fast | ⚡ Depends on frontend |
| **Ease of Use** | ⭐⭐ Requires learning | ⭐⭐⭐ Intuitive | ⭐⭐⭐ Depends on UI |
| **Scriptable** | ✅ Yes | ❌ No | ✅ Yes (API) |
| **Visual Feedback** | ⭐⭐ Basic | ⭐⭐⭐ Rich | ⭐⭐⭐ Full (custom) |
| **Resource Usage** | 🟢 Low | 🟡 Medium | 🔴 Higher |
| **Best For** | Quick tasks, automation | Daily detailed entry | Web/mobile apps |

## Mode Details

### 1. CLI Commands Mode

**Launch:** Just run commands directly

```bash
tracker new --income 150 --bills 50
tracker show today
tracker stats
```

#### ✅ Advantages
- **Lightning fast** - No UI overhead, instant execution
- **Scriptable** - Perfect for automation and cron jobs
- **SSH-friendly** - Works over any connection
- **Composable** - Pipe to other Unix tools
- **Low memory** - Minimal resource usage
- **Documentation** - Easy to document and share commands

#### ❌ Disadvantages
- **Learning curve** - Need to remember command syntax
- **Less visual** - Text-only output
- **No form validation** - Errors caught after submission
- **No browsing** - Can't easily navigate through data

#### 🎯 Best Use Cases
1. **Quick updates** - Add income, edit expenses
2. **Automation** - Scripts, cron jobs, hooks
3. **SSH sessions** - Remote server access
4. **Power users** - Those who prefer keyboard-only
5. **CI/CD** - Automated testing and reporting

#### 📝 Example Workflow
```bash
# Morning routine
tracker new --date today --income 100

# Throughout the day (quick updates)
tracker edit today --food 25
tracker edit today --entertainment 15

# Evening review
tracker show today
tracker stats --days 7
```

---

### 2. Interactive TUI Mode

**Launch:** `tracker tui`

```
┌─────────────────────────────────────────┐
│   🎯 Daily Tracker - Interactive TUI    │
│                                         │
│   📝 New Entry (n)                      │
│   👁️  View Entries (v)                  │
│   🔍 Search (s)                         │
│   📊 Statistics (t)                     │
│   🏆 Achievements (a)                   │
│   ⚙️  Configuration (c)                 │
│   📤 Export Data (e)                    │
│   👤 Profile (p)                        │
│   ❌ Quit (q)                           │
└─────────────────────────────────────────┘
```

#### ✅ Advantages
- **User-friendly** - No commands to memorize
- **Visual navigation** - Arrow keys and menus
- **Form validation** - Errors caught before submission
- **Browse data** - Easy scrolling through entries
- **Discoverable** - See all available features
- **Guided input** - Prompts for each field
- **Beautiful** - Rich formatting and colors

#### ❌ Disadvantages
- **Not scriptable** - Manual interaction required
- **Medium speed** - Navigation takes time
- **Terminal size** - Needs at least 80x24
- **No piping** - Can't compose with other tools

#### 🎯 Best Use Cases
1. **Daily detailed entry** - Morning/evening logging
2. **Beginners** - Learning the system
3. **Data exploration** - Browsing past entries
4. **Visual feedback** - Seeing stats and charts
5. **Complex entries** - Multiple fields to fill

#### 📝 Example Workflow
```bash
# Start TUI
tracker tui

# Navigate with keyboard:
# - Press 'n' for new entry
# - Fill out form (Tab to move between fields)
# - Ctrl+S to save
# - Esc to return to menu
# - Press 't' to see statistics
# - Press 'a' to check achievements
# - Press 'q' to quit
```

---

### 3. Server Mode (API)

**Launch:** `tracker server`

```bash
# Start server
tracker server --port 5703

# Access in browser
open http://localhost:5703/docs
```

#### ✅ Advantages
- **Custom frontends** - Build any UI you want
- **Multi-user** - Supports authentication
- **Web/mobile ready** - RESTful API
- **Integration** - Connect with other services
- **Remote access** - Access from anywhere
- **OpenAPI docs** - Auto-generated documentation
- **Real-time** - WebSocket support (future)

#### ❌ Disadvantages
- **Higher resources** - Server must run continuously
- **Setup required** - Need to configure server
- **Network dependency** - Requires connection
- **More complex** - Additional moving parts

#### 🎯 Best Use Cases
1. **Web frontend** - Build React/Vue app
2. **Mobile app** - iOS/Android integration
3. **Multi-device** - Access from anywhere
4. **Team usage** - Multiple users
5. **Integration** - Connect to other tools
6. **Automation** - API-based workflows

#### 📝 Example Workflow
```bash
# Terminal 1: Start server
tracker server --port 5703

# Terminal 2: Use API
curl -X POST http://localhost:5703/api/v1/entries \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-01-15", "income": 150}'

# Or build frontend
# - React/Vue app using fetch/axios
# - Mobile app using HTTP client
# - Desktop app with Electron
```

## Choosing the Right Mode

### Decision Tree

```
Do you want to automate or script?
├─ Yes → CLI Commands
└─ No
   └─ Do you need a custom UI?
      ├─ Yes → Server Mode + Custom Frontend
      └─ No
         └─ Prefer visual menus or quick commands?
            ├─ Visual menus → Interactive TUI
            └─ Quick commands → CLI Commands
```

### Use Case Matrix

| Use Case | Recommended Mode | Why |
|----------|-----------------|-----|
| Daily morning entry | TUI | Form validation, guided input |
| Quick expense update | CLI | Fastest for single field |
| Review last week | TUI or CLI | TUI for browsing, CLI for export |
| Automate monthly report | CLI | Scriptable with cron |
| Learn the system | TUI | Discover features visually |
| Build mobile app | Server | REST API for app |
| SSH into remote server | CLI | Works over any connection |
| Complex multi-field entry | TUI | Form with validation |
| Export for analysis | CLI | Direct to file |
| Share with team | Server | Multi-user support |

## Combining Modes

You can (and should!) use multiple modes together:

### Scenario 1: Daily User

```bash
# Morning: Detailed entry with TUI
tracker tui  # Fill complete form

# During day: Quick CLI updates
tracker edit today --food 12.50
tracker edit today --transport 5.00

# Evening: Check stats in TUI
tracker tui  # Navigate to statistics
```

### Scenario 2: Developer

```bash
# Terminal 1: Keep server running
tracker server --port 5703

# Terminal 2: Work on custom frontend
cd frontend/
npm run dev

# Terminal 3: Quick CLI testing
tracker new --income 100
tracker show today
```

### Scenario 3: Power User

```bash
# CLI for automation
echo "0 9 * * * tracker new --date today" | crontab

# TUI for detailed review
tracker tui  # Weekly stats review

# Server for mobile sync
tracker server  # Let mobile app sync
```

## Performance Comparison

### Startup Time
- **CLI**: ~0.1s (instant)
- **TUI**: ~0.3s (Textual initialization)
- **Server**: ~1-2s (FastAPI startup)

### Memory Usage
- **CLI**: ~50MB (Python + dependencies)
- **TUI**: ~80MB (Python + Textual)
- **Server**: ~120MB (Python + FastAPI + workers)

### CPU Usage
- **CLI**: Minimal (runs and exits)
- **TUI**: Low (event-driven)
- **Server**: Low-Medium (depends on traffic)

## Migration Path

### Beginner → Power User

1. **Week 1-2**: Use TUI exclusively
   - Learn all features
   - Understand data model
   - Get comfortable with interface

2. **Week 3-4**: Mix TUI + CLI
   - Use TUI for daily entries
   - Use CLI for quick updates
   - Learn CLI commands gradually

3. **Month 2+**: Mostly CLI
   - CLI for 80% of tasks
   - TUI for exploration
   - Create custom scripts

### CLI User → Server Integration

1. **Keep using CLI** for daily work
2. **Start server** in background
3. **Build custom frontend** gradually
4. **Migrate workflows** one at a time

## Tips & Tricks

### CLI Tips
```bash
# Create aliases for common tasks
alias tn='tracker new'
alias ts='tracker show today'
alias tst='tracker stats'

# Combine with other tools
tracker list --days 30 | grep "high income"
tracker export --format csv | python analyze.py
```

### TUI Tips
- Learn hotkeys to navigate faster
- Use Ctrl+S to save without mouse
- Press '?' for context help
- Use Esc to quickly back out

### Server Tips
```bash
# Run in background
tracker server --daemon

# Custom port
tracker server --port 8080

# Enable CORS for frontend
export CORS_ORIGINS="http://localhost:3000"
tracker server
```

## See Also

- [TUI Mode Documentation](TUI_MODE.md)
- [CLI Reference](../README.md#cli-usage)
- [API Documentation](API.md)
- [Configuration Guide](CONFIGURATION.md)
