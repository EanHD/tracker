# Quickstart Guide: Daily Logging App

**Version**: 1.0.0  
**Updated**: 2025-10-21

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer (recommended)
- API key for OpenAI, Anthropic, OpenRouter, or local AI server (for AI feedback features)

## Installation

### Option 1: Using uv (Recommended - 10-100x faster)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone <repository-url>
cd tracker

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Initialize database
tracker init

# Run onboarding wizard
tracker onboard
```

### Option 2: Using uvx (No virtual environment needed)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone <repository-url>
cd tracker

# Run commands directly with uvx
uvx --from . tracker init
uvx --from . tracker onboard
uvx --from . tracker new
```

### Option 3: Using pip (Traditional)

```bash
# Clone repository
git clone <repository-url>
cd tracker

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Initialize database
tracker init
```

### 2. Configuration

```bash
# Run configuration wizard
tracker config setup

# Or manually set configuration
tracker config set AI_PROVIDER anthropic
tracker config set ANTHROPIC_API_KEY your-api-key-here

# Generate API token for external access
tracker config generate-token
```

Configuration file location: `~/.config/tracker/config.yaml`

### 3. Database Initialization

```bash
# Initialize database schema
tracker db init

# Optionally load demo data
tracker db seed --demo
```

## Quick Start: CLI Usage

### Create Your First Entry

```bash
# Interactive mode (recommended for first use)
tracker new

# You'll be prompted for each field:
# Date: 2025-10-21
# Cash on hand: 142.35
# Bank balance: -53.21
# ...

# Quick mode (fewer prompts)
tracker new --quick

# Non-interactive mode (all flags)
tracker new \
  --date 2025-10-21 \
  --cash 142.35 \
  --bank -53.21 \
  --income 420 \
  --bills 275 \
  --debt 18600 \
  --hours 8 \
  --side 80 \
  --food 22.17 \
  --gas 38.55 \
  --stress 6 \
  --priority "clear card debt" \
  --notes "Paid Snap-On min. late. Worked overtime."
```

### View Your Entries

```bash
# View recent entries (last 30 days)
tracker view

# View specific date
tracker show 2025-10-21

# View date range
tracker view --from 2025-10-01 --to 2025-10-21

# View with AI feedback
tracker show 2025-10-21 --with-feedback
```

### Edit an Entry

```bash
# Interactive edit
tracker edit 2025-10-21

# Update specific fields
tracker edit 2025-10-21 --stress 5 --notes "Updated: feeling better"
```

### Trends and Statistics

```bash
# View weekly summary
tracker trends --last-week

# View monthly summary
tracker trends --last-month

# Custom date range
tracker trends --from 2025-10-01 --to 2025-10-21

# Export data
tracker export --format csv --output entries.csv
```

### Search

```bash
# Search notes
tracker search "overtime"

# Search with date filter
tracker search "bills" --from 2025-10-01
```

## Quick Start: API Server

### Start the Server

```bash
# Development mode (with auto-reload)
tracker api serve --dev

# Production mode
tracker api serve --host 0.0.0.0 --port 8000

# Background mode
tracker api serve --daemon
```

Server will be available at `http://localhost:8000`

### Generate API Token

```bash
# Generate token with default scopes
tracker config generate-token

# Generate token with specific scopes
tracker config generate-token --scopes entries:read,entries:write,feedback:generate

# Output:
# Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# Expires: 2026-01-19T18:45:00Z
# Scopes: entries:read, entries:write, feedback:generate
```

### API Examples

#### Create Entry (cURL)

```bash
curl -X POST http://localhost:8000/api/v1/entries \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-10-21",
    "cash_on_hand": 142.35,
    "bank_balance": -53.21,
    "income_today": 420.00,
    "bills_due_today": 275.00,
    "debts_total": 18600.00,
    "hours_worked": 8.0,
    "side_income": 80.00,
    "food_spent": 22.17,
    "gas_spent": 38.55,
    "stress_level": 6,
    "priority": "clear card debt",
    "notes": "Paid Snap-On min. late. Worked overtime."
  }'
```

#### Get Entry (cURL)

```bash
curl http://localhost:8000/api/v1/entries/2025-10-21 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Python Client Example

```python
import requests

TOKEN = "your-token-here"
BASE_URL = "http://localhost:8000/api/v1"

headers = {"Authorization": f"Bearer {TOKEN}"}

# Create entry
entry_data = {
    "date": "2025-10-21",
    "cash_on_hand": 142.35,
    "bank_balance": -53.21,
    "income_today": 420.00,
    "bills_due_today": 275.00,
    "debts_total": 18600.00,
    "hours_worked": 8.0,
    "side_income": 80.00,
    "food_spent": 22.17,
    "gas_spent": 38.55,
    "stress_level": 6,
    "priority": "clear card debt",
    "notes": "Worked overtime today."
}

response = requests.post(
    f"{BASE_URL}/entries",
    json=entry_data,
    headers=headers
)
print(response.json())

# Get entry
response = requests.get(
    f"{BASE_URL}/entries/2025-10-21",
    headers=headers
)
print(response.json())
```

### Interactive API Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.

## Quick Start: MCP Server

### Configure for Claude Desktop

1. Edit Claude Desktop config:
```bash
# macOS
open ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
nano ~/.config/Claude/claude_desktop_config.json
```

2. Add tracker MCP server:
```json
{
  "mcpServers": {
    "tracker": {
      "command": "python",
      "args": ["-m", "tracker.mcp.server"],
      "env": {
        "DATABASE_URL": "sqlite:///Users/you/.config/tracker/tracker.db"
      }
    }
  }
}
```

3. Restart Claude Desktop

4. Test in Claude:
```
You: "Log today's entry: worked 8 hours, made $400, stress is 5/10"
Claude: [uses MCP tool to create entry]
```

### Start Standalone MCP Server

```bash
# Stdio transport (for local AI agents)
tracker mcp serve

# HTTP transport (for remote AI agents)
tracker mcp serve --http --port 8001
```

## Common Workflows

### Daily Entry Routine

```bash
# Morning: Quick check of yesterday
tracker show yesterday

# Evening: Log today
tracker new

# Review AI feedback
tracker show today --with-feedback
```

### Weekly Review

```bash
# Generate weekly insights
tracker insights --last-week

# View trends
tracker trends --last-week

# Export for personal analysis
tracker export --last-week --format csv
```

### Automation with MCP

1. Set up Claude Desktop with MCP server (see above)
2. Create daily reminder in calendar
3. Tell Claude: "Log my daily entry" with data
4. Claude uses MCP to create entry and show feedback

### Backup and Sync

```bash
# Create backup
tracker backup create --encrypt

# Restore from backup
tracker backup restore backup_2025-10-21.enc

# Sync to cloud (if configured)
tracker sync push
```

## Configuration Reference

### Configuration File Structure

Location: `~/.config/tracker/config.yaml`

```yaml
# Database
database:
  url: sqlite:///~/.config/tracker/tracker.db
  encryption: true

# AI Provider
ai:
  provider: anthropic  # or 'openai'
  api_key: your-key-here
  model: claude-3-sonnet  # or 'gpt-4'
  
# API Server
api:
  host: localhost
  port: 8000
  jwt_secret: auto-generated-secret
  token_expiry_days: 90

# MCP Server
mcp:
  transport: stdio
  http_port: 8001

# CLI Preferences
cli:
  interactive_mode: true
  color_output: true
  show_feedback: true
  date_format: YYYY-MM-DD

# Features
features:
  ai_feedback: true
  auto_backup: true
  daily_reminder: false

# Backup
backup:
  auto_backup: true
  backup_dir: ~/.config/tracker/backups
  retention_days: 30
```

### Environment Variables

Can override config file values:

```bash
# Database
export DATABASE_URL=sqlite:///path/to/tracker.db

# AI Provider
export AI_PROVIDER=anthropic
export ANTHROPIC_API_KEY=your-key-here
export OPENAI_API_KEY=your-key-here

# API Server
export API_HOST=0.0.0.0
export API_PORT=8000
export JWT_SECRET=your-secret-here

# Encryption
export ENCRYPTION_KEY=your-encryption-key
```

## Troubleshooting

### CLI Issues

**Problem**: `tracker: command not found`
```bash
# Ensure installed correctly
poetry install
# Or
pip install -e .

# Check PATH
which tracker
```

**Problem**: Database errors
```bash
# Reinitialize database
tracker db reset --confirm
tracker db init
```

### API Issues

**Problem**: Port already in use
```bash
# Use different port
tracker api serve --port 8001

# Or stop existing server
tracker api stop
```

**Problem**: Authentication errors
```bash
# Regenerate token
tracker config generate-token

# Check token expiry
tracker config show-token
```

### MCP Issues

**Problem**: Claude doesn't see MCP server
1. Restart Claude Desktop
2. Check config file syntax (JSON valid?)
3. Verify database path is absolute
4. Check server logs: `~/.config/tracker/mcp.log`

**Problem**: MCP tool calls fail
```bash
# Test MCP server directly
tracker mcp test

# Check database connection
tracker db status
```

### General Issues

**Problem**: Missing dependencies
```bash
# Reinstall dependencies
poetry install
# Or
pip install -e .[all]
```

**Problem**: Permission errors
```bash
# Ensure config directory exists and is writable
mkdir -p ~/.config/tracker
chmod 755 ~/.config/tracker
```

## Next Steps

- **Read API documentation**: `docs/api.md`
- **Read MCP documentation**: `docs/mcp.md`
- **Read CLI documentation**: `docs/cli.md`
- **Join community**: [Discord/GitHub Discussions link]
- **Report issues**: [GitHub Issues link]

## Tips for Great UX

1. **Set up daily reminder**: Configure calendar event to log entries
2. **Use quick mode**: `tracker new --quick` for faster entry
3. **Review trends weekly**: `tracker trends --last-week` every Sunday
4. **Enable auto-backup**: Set `features.auto_backup: true` in config
5. **Connect AI agent**: Use MCP with Claude for conversational entry logging
6. **Customize colors**: Edit `cli.theme` in config for personal preference
7. **Keyboard shortcuts**: Learn CLI shortcuts in `docs/cli.md`
8. **Export regularly**: Monthly exports for personal analysis in spreadsheet

## Support

- Documentation: `tracker help <command>`
- Version: `tracker version`
- Health check: `tracker status`
- Logs: `~/.config/tracker/logs/`
