# Daily Tracker - User Guide

**Version:** 1.0.0  
**Last Updated:** October 24, 2025

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interactive TUI Mode](#interactive-tui-mode)
3. [Daily Workflow](#daily-workflow)
4. [Command Reference](#command-reference)
5. [AI Feedback](#ai-feedback)
6. [Chat System](#chat-system)
7. [Profile System](#profile-system)
8. [Philosophy Engine](#philosophy-engine)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

Daily Tracker requires Python 3.12+ and uses `uv` for fast dependency management.

#### Prerequisites

```bash
# Install Python 3.12+ (if not already installed)
# On Ubuntu/Debian:
sudo apt update && sudo apt install python3.12 python3.12-venv

# On macOS (via Homebrew):
brew install python@3.12

# Install uv (10-100x faster than pip/poetry)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Install Daily Tracker

```bash
# Clone the repository
git clone https://github.com/EanHD/tracker.git
cd tracker

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Initialize the database
python scripts/init_db.py
```

### Security Configuration

Before using the API server or MCP server, you need to set secure secrets in your `.env` file.

#### Generate Secure Secrets

```bash
# Generate a secure JWT secret (for API authentication)
openssl rand -hex 32

# Generate a secure encryption key (for database encryption)
openssl rand -hex 32
```

Copy these values and update your `.env` file:

```bash
# Example .env configuration
JWT_SECRET=your-generated-jwt-secret-here
ENCRYPTION_KEY=your-generated-encryption-key-here
```

**Important Security Notes:**

- 🔒 **Never commit `.env` to git** - It's already in `.gitignore`
- 🔑 **Use different secrets for each environment** (dev, production)
- ⚠️ **Never change ENCRYPTION_KEY after encrypting data** - Will corrupt your database!
- 🔄 **Rotate JWT_SECRET periodically** (every 90 days) for better security
- 📝 **Store production secrets securely** - Use environment variables or secret managers

### Initial Setup

#### 1. Configure AI Provider

Daily Tracker supports multiple AI providers for feedback generation. Choose one by editing your `.env` file:

**Option A: Edit .env file directly** (Recommended)

```bash
# Edit /home/eanhd/projects/tracker/.env

# For OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-...
# OPENAI_MODEL=gpt-4  # Optional, defaults to gpt-4

# For Anthropic
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...
# ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # Optional

# For OpenRouter (access to multiple models)
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
# OPENROUTER_MODEL=anthropic/claude-3.5-sonnet  # Optional

# For local models (via Ollama)
AI_PROVIDER=local
LOCAL_API_URL=http://localhost:11434/v1
LOCAL_MODEL=llama3.2
```

**Option B: Interactive setup wizard**

```bash
tracker config setup
```

Note: The setup wizard has limited provider options. For full control, edit `.env` directly.

#### 2. Run Onboarding

The onboarding wizard helps you set up your tracking preferences:

```bash
tracker onboard
```

This interactive process will:
- Guide you through AI provider selection
- Create your first entry
- Explain core features
- Show you the ropes

#### 3. Create Your First Entry

```bash
tracker new
```

You'll be prompted for:
- **Date** (defaults to today)
- **Financial data**: Income, bills, food spending
- **Work data**: Hours worked, stress level (1-10)
- **Wellbeing**: Exercise, sleep, social time
- **Notes**: Priority task, daily reflection

After submitting, the AI will generate personalized feedback based on your entry!

---

## Interactive TUI Mode

Daily Tracker now features a full interactive TUI (Text User Interface) for easier navigation:

```bash
# Launch interactive mode
tracker tui
```

The TUI provides:
- **Main Menu**: Easy navigation to all features
- **New Entry**: Guided form for creating entries
- **View Entries**: Browse recent entries (last 30 days)
- **Search**: Find entries by date, keywords, or filters
- **Chats**: Access AI chat conversations
- **Statistics**: View your tracking analytics
- **Achievements**: Check progress and streaks
- **Configuration**: Manage settings
- **Profile**: View and update your user profile

**Mobile/Narrow Terminal Support**: The TUI automatically adapts to narrow terminals (useful for mobile terminal emulators like Termius).

---

## Daily Workflow

### Morning Routine

Start your day by reviewing yesterday's entry and planning today:

```bash
# Show yesterday's entry with AI feedback
tracker show yesterday

# Check your current streak
tracker achievements
```

### Evening Routine

End your day by logging your activities:

```bash
# Quick entry with command-line flags (fast!)
tracker new \
  --income 150.00 \
  --bills 50.00 \
  --food 25.00 \
  --hours 8 \
  --stress 4 \
  --exercise 1 \
  --sleep 7 \
  --social 2 \
  --priority "Completed project milestone" \
  --notes "Good productive day, feeling energized"

# Or use interactive mode (guided prompts)
tracker new
```

### Weekly Review

Every week, review your progress:

```bash
# View last 7 days
tracker list --limit 7

# Check statistics
tracker stats --days 7

# Search for specific themes
tracker search "productive"
tracker search "stress"

# View your achievements
tracker achievements
```

### Monthly Patterns

At the end of each month:

```bash
# Export your data for analysis
tracker export --format csv --output ~/Documents/tracker_data.csv

# View monthly statistics
tracker stats --days 30

# Check financial trends
tracker list --limit 30 | grep "Net:"
```

---

## Command Reference

### Core Commands

#### `tracker new` - Create New Entry

Create a new daily entry with optional AI feedback.

**Interactive Mode:**

```bash
tracker new
# Follow the prompts to enter your data
# After entering all fields, you'll see a preview with options to:
# [1] Save - Confirm and save the entry
# [2] Edit - Fix any mistakes before saving
# [3] Cancel - Abort without saving
```

**Review & Edit Feature:**

After completing all prompts, you can review and edit any field before saving:

```text
📋 Entry Preview
━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Financial
  Cash on hand: $500.00
  Bank balance: $1500.00
...

What would you like to do?
[1] 💾 Save this entry
[2] ✏️  Edit a field      ← Fix mistakes!
[3] ❌ Cancel

Choose [1/2/3] (1): 2

Which field would you like to edit?
[1] 📅 Date: 2025-10-21
[2] 💵 Cash on hand: $500.00
[3] 🏦 Bank balance: $1500.00
...
[13] 📝 Notes: not set

Field to edit: 3
New bank balance: $2500    ← Corrected!
✓ Updated 🏦 Bank balance
```

**Error Recovery:**

Invalid input no longer crashes the form - you'll be prompted to try again:

```text
Cash on hand: $abc
❌ Invalid input: Please enter a valid number
⚠️  Please try again (or press Ctrl+C to cancel)
Cash on hand: $500   ← Retry!

Stress level (1-10): 99
❌ Invalid input: Value must be between 1 and 10
⚠️  Please enter a number between 1 and 10
Stress level (1-10): 7   ← Fixed!
```

**Quick Mode (with flags):**

```bash
tracker new \
  --date 2025-10-21 \
  --income 200.00 \
  --bills 75.00 \
  --food 30.00 \
  --hours 8 \
  --stress 5 \
  --exercise 1 \
  --sleep 7 \
  --social 3 \
  --priority "Important task" \
  --notes "Daily reflection" \
  --no-feedback  # Skip AI feedback generation
```

**Options:**
- `--date DATE` - Entry date (default: today)
- `--income DECIMAL` - Income for the day
- `--bills DECIMAL` - Bills paid
- `--food DECIMAL` - Food spending
- `--hours INTEGER` - Hours worked (0-24)
- `--stress INTEGER` - Stress level (1-10)
- `--exercise INTEGER` - Exercise hours
- `--sleep INTEGER` - Sleep hours
- `--social INTEGER` - Social interaction hours
- `--priority TEXT` - Priority task
- `--notes TEXT` - Daily notes
- `--no-feedback` - Skip AI feedback generation

#### `tracker edit` - Edit Existing Entry

Modify a previously created entry.

**Interactive Mode:**
```bash
tracker edit 2025-10-21
# Prompts show current values as defaults
```

**Quick Mode:**
```bash
tracker edit yesterday --stress 6 --notes "Updated reflection"
```

**Options:**
- All the same options as `tracker new`
- `--regenerate-feedback` - Generate new AI feedback after editing

#### `tracker show` - Display Single Entry

View detailed information about a specific entry.

```bash
tracker show                  # Show today's entry
tracker show yesterday        # Show yesterday
tracker show 2025-10-21      # Show specific date
tracker show --no-feedback    # Hide AI feedback
```

#### `tracker list` - Browse Entries

List multiple entries in chronological order.

```bash
tracker list                  # Last 7 days
tracker list --limit 30       # Last 30 days
tracker list --limit 100      # Last 100 days
```

#### `tracker search` - Full-Text Search

Search entries by keywords with highlighting.

```bash
tracker search "productive"
tracker search "meeting"
tracker search "stress" --limit 50
```

#### `tracker retry` - Retry AI Feedback Generation

Regenerate AI feedback for an entry when initial generation fails.

```bash
tracker retry                  # Retry today's entry
tracker retry yesterday        # Retry yesterday
tracker retry 2025-10-23      # Retry specific date
tracker retry -1              # Retry 1 day ago
```

**When to use:**
- Initial feedback generation failed
- Want fresh feedback with updated configuration
- AI service was temporarily unavailable

**Tips on failure:**
1. Check your AI configuration: `tracker config show`
2. Verify API key is valid
3. Ensure AI service is running (for local providers)
4. Try again after a moment
```

**Features:**
- Case-insensitive search
- Searches notes and priority fields
- Highlighted matches in results
- Color-coded stress levels

#### `tracker stats` - View Statistics

Display aggregated statistics and trends.

```bash
tracker stats                 # Last 7 days
tracker stats --days 30       # Last 30 days
tracker stats --days 365      # Full year
```

**Metrics Include:**
- Total entries
- Average stress level (with trend)
- Total income vs. spending
- Average work hours
- Average sleep, exercise, social time
- Current streak and longest streak

#### `tracker export` - Export Data

Export your data to CSV or JSON format.

```bash
# Export as JSON (default)
tracker export

# Export as CSV
tracker export --format csv

# Custom output path
tracker export --output ~/backup/tracker_data.json

# Date range filtering
tracker export \
  --format csv \
  --start-date 2025-01-01 \
  --end-date 2025-12-31 \
  --output yearly_data.csv

# Compact JSON (no pretty-print)
tracker export --format json --compact
```

**Formats:**
- **JSON**: Structured format with nested objects (great for programming)
- **CSV**: Flat format with all fields (great for Excel/Google Sheets)

#### `tracker achievements` - View Gamification

Display your achievements, streaks, and progress.

```bash
tracker achievements
```

**Available Achievements:**
- 🎯 **Getting Started** - Create your first entry
- 🔥 **Week Warrior** - Maintain a 7-day streak
- ⭐ **Monthly Master** - Maintain a 30-day streak
- 💯 **Century Club** - Maintain a 100-day streak
- 📈 **Halfway There** - Create 50 total entries
- 🏆 **Centennial** - Create 100 total entries
- 👑 **Year of Tracking** - Create 365 total entries
- 🧘 **Zen Master** - Keep stress ≤3 for a full week
- 💰 **In the Black** - Stay net positive for 30 days

### Configuration

#### `tracker config` - Manage Settings

View and modify configuration settings.

```bash
# View current configuration
tracker config show

# Interactive configuration setup
tracker config setup

# Or edit .env file directly for full control
# Edit: /home/your-user/projects/tracker/.env
```

**Key Settings (in .env file):**
- `AI_PROVIDER` - AI service: openai, anthropic, openrouter, local
- `OPENAI_API_KEY`, `OPENAI_MODEL` - OpenAI configuration
- `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` - Anthropic configuration
- `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` - OpenRouter configuration
- `LOCAL_API_URL`, `LOCAL_MODEL` - Local model configuration

### API Server

#### `tracker server` - Run API Server

Start the FastAPI server for programmatic access.

```bash
# Development mode (with auto-reload)
tracker server

# Production mode
tracker server --host 0.0.0.0 --port 5703

# Custom configuration
tracker server --host 127.0.0.1 --port 5000 --no-reload
```

**Options:**
- `--host HOST` - Bind address (default: 127.0.0.1)
- `--port PORT` - Port number (default: 8000)
- `--reload` / `--no-reload` - Auto-reload on code changes

Access the API at `http://localhost:5703/api/v1/`  
Interactive docs at `http://localhost:5703/docs`

### MCP Integration

#### `tracker mcp` - Model Context Protocol Server

Run the MCP server for integration with AI assistants (Claude Desktop, etc.).

```bash
# Standard output mode (for stdio transport)
tracker mcp

# Development mode with logging
tracker mcp --log-file /tmp/tracker_mcp.log
```

Configure in `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "daily-tracker": {
      "command": "/home/you/projects/tracker/.venv/bin/tracker",
      "args": ["mcp"]
    }
  }
}
```

---

## Advanced Features

### Regenerating AI Feedback

If you want fresh AI insights on an existing entry:

```bash
# Edit and regenerate feedback
tracker edit 2025-10-21 --regenerate-feedback

# Or manually request new feedback via API
curl -X POST http://localhost:5703/api/v1/feedback/2025-10-21/regenerate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Batch Operations via API

The REST API enables bulk operations:

```python
import requests

# Authenticate
response = requests.post("http://localhost:5703/api/v1/auth/login", json={
    "username": "your_username",
    "password": "your_password"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Create multiple entries
for date, data in entries_dict.items():
    requests.post(
        "http://localhost:5703/api/v1/entries/",
        json=data,
        headers=headers
    )

# Export all data
response = requests.get(
    "http://localhost:5703/api/v1/export/json",
    headers=headers
)
with open("backup.json", "wb") as f:
    f.write(response.content)
```

### Data Migration

Export from old system, import to Daily Tracker:

```bash
# Export from Daily Tracker
tracker export --format json --output backup.json

# Import script (customize for your source)
python scripts/import_data.py backup.json
```

### Custom AI Prompts

Modify the AI feedback prompt by editing:
```
src/tracker/services/ai_client.py
```

Look for the `generate_feedback()` method and customize the system prompt to match your preferences.

---

## Troubleshooting

### Common Issues

#### "Database is locked" Error

**Symptom:** `sqlite3.OperationalError: database is locked`

**Solution:**
```bash
# Close all tracker processes
pkill -f tracker

# If that doesn't work, restart the database connection
rm ~/.config/tracker/tracker.db-wal
rm ~/.config/tracker/tracker.db-shm
```

#### AI Feedback Not Generating

**Symptom:** Entries created but no feedback shown

**Possible Causes:**
1. **Invalid API key** - Check your configuration:
   ```bash
   tracker config show
   ```

2. **API quota exceeded** - Check your provider's dashboard

3. **Network issues** - Test connectivity:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

**Solution:**
```bash
# Verify configuration
tracker config get ai_provider
tracker config get openai_api_key  # Or anthropic_api_key, etc.

# Try regenerating feedback
tracker edit today --regenerate-feedback
```

#### "Command not found: tracker"

**Symptom:** Shell can't find the `tracker` command

**Solution:**
```bash
# Activate virtual environment
cd /path/to/tracker
source .venv/bin/activate

# Or install globally
uv pip install -e .

# Or use full path
.venv/bin/tracker new
```

#### Import Errors

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Solution:**
```bash
# Reinstall dependencies
cd /path/to/tracker
source .venv/bin/activate
uv pip install -e .

# Or force reinstall
uv pip install --force-reinstall -e .
```

#### Permission Denied on Database

**Symptom:** Can't read/write to `~/.config/tracker/tracker.db`

**Solution:**
```bash
# Check permissions
ls -la ~/.config/tracker/

# Fix permissions
chmod 644 ~/.config/tracker/tracker.db
chmod 755 ~/.config/tracker/
```

### Performance Issues

#### Slow API Responses

If the API is slow:

1. **Check database size:**
   ```bash
   du -h ~/.config/tracker/tracker.db
   ```

2. **Rebuild indexes:**
   ```bash
   sqlite3 ~/.config/tracker/tracker.db "REINDEX;"
   ```

3. **Vacuum database:**
   ```bash
   sqlite3 ~/.config/tracker/tracker.db "VACUUM;"
   ```

#### High Memory Usage

If tracker uses excessive memory:

1. **Limit query results:**
   ```bash
   tracker list --limit 10  # Instead of large limits
   ```

2. **Use date filters:**
   ```bash
   tracker export --start-date 2025-01-01  # Instead of all data
   ```

---

## FAQ

### General Questions

**Q: Is my data secure?**  
A: Yes! Data is stored locally in `~/.config/tracker/tracker.db`. Passwords are hashed with bcrypt. The API uses JWT tokens. Your data never leaves your machine except when making AI API calls (only entry data, not credentials).

**Q: Can I use this without AI?**  
A: Absolutely! Use `--no-feedback` flag or skip AI configuration entirely:
```bash
tracker new --no-feedback
```

**Q: How much does AI feedback cost?**  
A: Costs vary by provider:
- OpenAI GPT-4: ~$0.01-0.03 per entry
- Anthropic Claude: ~$0.01-0.02 per entry
- OpenRouter: Varies by model
- Local models: Free!

**Q: Can multiple users use the same installation?**  
A: Yes, but you'll need to manage authentication. Each user gets their own account via the API. The CLI uses the first user by default.

**Q: How do I backup my data?**  
A: Regular exports are recommended:
```bash
# Automated backup script
tracker export --output ~/Backups/tracker_$(date +%Y%m%d).json
```

### Technical Questions

**Q: What database is used?**  
A: SQLite for simplicity and portability. No server required!

**Q: Can I migrate to PostgreSQL?**  
A: Yes! The codebase uses SQLAlchemy, so changing the connection string in `config.py` will work. Just update:
```python
SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/tracker"
```

**Q: How do I access the API programmatically?**  
A: See the [API Documentation](API_DOCS.md) for full details. Quick example:
```python
import requests
# See "Batch Operations via API" section above
```

**Q: Can I self-host this?**  
A: Yes! See the [Deployment Guide](DEPLOYMENT.md) for production setup instructions.

**Q: Is there a mobile app?**  
A: Not yet, but the API is mobile-friendly. You could build a mobile frontend using React Native or Flutter that consumes the REST API.

**Q: Can I customize the AI feedback prompt?**  
A: Yes! Edit `src/tracker/services/ai_client.py` and modify the system prompt in `generate_feedback()`.

**Q: How do I contribute?**  
A: Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## Getting Help

- **Documentation**: Check `docs/` folder
- **API Docs**: Run `tracker server` and visit `http://localhost:5703/docs`
- **Issues**: Report bugs on GitHub
- **Discussions**: Join the community on GitHub Discussions

---

**Happy Tracking!** 🎯📊✨
