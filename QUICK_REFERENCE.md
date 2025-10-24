# Tracker Quick Reference Card

## 🚀 Launch Commands

```bash
tracker tui        # Interactive TUI (menu-driven)
tracker new        # CLI: Create new entry (prompts)
tracker server     # Start REST API server
```

## 📋 TUI Navigation

### Main Menu Hotkeys
```
n - New Entry          v - View Entries
s - Search            t - Statistics
a - Achievements      c - Configuration
e - Export Data       p - Profile
q - Quit
```

### Universal Keys
```
↑↓←→  - Navigate          Tab       - Next field
Esc   - Back/Cancel       Ctrl+S    - Save
Ctrl+F - Search          r         - Refresh
Ctrl+C - Quit app
```

## 💻 CLI Commands

### Create & Edit
```bash
tracker new --income 150 --bills 50
tracker edit today --mood 8
tracker edit 2024-01-15 --stress 5
```

### View & Search
```bash
tracker show today
tracker show yesterday
tracker list --days 7
tracker search "exercise"
```

### Analytics
```bash
tracker stats
tracker stats --plot
tracker achievements
```

### Export
```bash
tracker export --format csv
tracker export --format json --output data.json
```

### Configuration
```bash
tracker config show
tracker config set ai_provider openai
tracker onboard  # Interactive setup
```

### Server
```bash
tracker server --port 5703
tracker mcp     # Start MCP server
```

### Chat
```bash
tracker chat new          # Start a standalone conversation
tracker chat new --entry-id 42  # Attach chat to Entry #42
tracker chat list         # Show conversations
tracker chat open 5       # Resume chat ID 5
```

## 🎯 Common Workflows

### Daily Entry (TUI)
```bash
tracker tui
# Press 'n' for new entry
# Fill form with Tab
# Ctrl+S to save
```

### Quick Update (CLI)
```bash
tracker edit today --food 12.50 --transport 5
```

### Weekly Review (TUI)
```bash
tracker tui
# Press 't' for stats
# Press 'v' to view entries
# Press 'a' for achievements
```

### Data Export (CLI)
```bash
tracker export --format csv --output weekly.csv --days 7
```

### Custom Frontend (Server)
```bash
# Terminal 1
tracker server --port 5703

# Terminal 2
cd my-frontend && npm run dev
```

## 🔧 Mode Selection Guide

| Task | Use Mode |
|------|----------|
| Daily detailed entry | TUI |
| Quick expense update | CLI |
| Browse past entries | TUI |
| Automate reports | CLI |
| Learn features | TUI |
| Build app | Server |
| SSH session | CLI |
| View statistics | TUI or CLI |

## 🏆 Entry Fields

### Financial
- Income, Bills, Food, Entertainment
- Shopping, Health, Transport
- Education, Gifts, Other

### Wellbeing
- Work Hours (0-24)
- Stress Level (1-10)
- Mood Level (1-10)
- Sleep Hours (0-24)
- Exercise Minutes
- Social Minutes

### Optional
- Date (defaults to today)
- Notes (free text)

## 📊 API Endpoints (Server Mode)

```
GET    /api/v1/entries           # List entries
POST   /api/v1/entries           # Create entry
GET    /api/v1/entries/{id}      # Get entry
PUT    /api/v1/entries/{id}      # Update entry
DELETE /api/v1/entries/{id}      # Delete entry
GET    /api/v1/stats              # Get statistics
GET    /api/v1/achievements       # Get achievements

Docs: http://localhost:5703/docs
```

## 🐛 Troubleshooting

### TUI won't start
```bash
uv pip install textual
```

### Database error
```bash
tracker init
```

### Missing AI key
```bash
tracker onboard
# or
export OPENAI_API_KEY=sk-...
```

### Server won't start
```bash
# Check if port is in use
lsof -i :5703

# Use different port
tracker server --port 8080
```

## 📚 Documentation Links

- Full TUI Guide: `docs/TUI_MODE.md`
- Mode Comparison: `docs/USAGE_MODES.md`
- API Docs: `docs/API.md`
- README: `README.md`

## 💡 Tips

1. **Start with TUI** if you're new
2. **Use CLI for scripts** and automation
3. **Run server** for custom frontends
4. **Combine modes** for best experience
5. **Use hotkeys** for speed in TUI
6. **Create aliases** for common CLI commands

## 🎨 Example Aliases

Add to `~/.bashrc` or `~/.zshrc`:

```bash
alias tt='tracker tui'
alias tn='tracker new'
alias ts='tracker show today'
alias tst='tracker stats'
alias tl='tracker list'
```

## 🔐 Environment Variables

```bash
AI_PROVIDER=openai           # or anthropic, openrouter, local
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...
DATABASE_PATH=~/.tracker/tracker.db
API_PORT=5703
DEBUG=0                      # Set to 1 for debug mode
```

## 📦 Installation

```bash
# Clone repo
git clone https://github.com/EanHD/tracker.git
cd tracker

# Install with uv
uv venv && source .venv/bin/activate
uv pip install -e .

# Initialize
tracker init
tracker onboard

# Start using
tracker tui
```

## 🐳 Docker

```bash
# Quick start
docker-compose up -d

# Access API
curl http://localhost:5703/api/v1/health

# View logs
docker-compose logs -f
```

---

**Version:** 0.1.0  
**Last Updated:** 2024-10-22  
**License:** MIT
