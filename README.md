# Daily Tracker - Personal Analytics with AI Insights

[![CI/CD](https://github.com/EanHD/tracker/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/EanHD/tracker/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/r/eanhd/daily-tracker)

A powerful daily tracking application with AI-powered insights. Track finances, work patterns, wellbeing, and receive personalized feedback from multiple AI providers. **Use it your way**: traditional CLI commands, interactive TUI menu, or REST API for custom frontends.

## ✨ Features

### Core Functionality
- 📝 **Rich CLI Interface** - Beautiful terminal UI with Rich library
- 🎨 **Interactive TUI Mode** - Full-screen menu-driven interface with Textual
- 🤖 **Multi-Provider AI** - OpenAI, Anthropic, OpenRouter, or Local models
- 👤 **User Profiles** - **NEW!** Personalize AI feedback with your context (work, goals, preferences)
- 🧠 **Philosophy Engine** - **NEW!** AI mentor system with 19 principles from Ramsey, Kiyosaki, and more
- 📊 **Comprehensive Tracking** - Finance, work hours, stress, sleep, exercise, social time
- 🔒 **Privacy-First** - Local SQLite database, encrypted sensitive data, no cloud storage
- 🔍 **Full-Text Search** - Find entries with keyword highlighting
- 📈 **Statistics & Trends** - Analyze patterns with visual charts
- 🎯 **Gamification** - 9 achievements, streak tracking, progress bars
- ✏️ **Review & Edit** - Preview entries before saving, fix mistakes without restarting
- 🛡️ **Error Recovery** - Invalid input retries instead of crashing

### Three Ways to Use Tracker
1. **CLI Commands** - Fast, scriptable `tracker new`, `tracker show`, etc.
2. **Interactive TUI** - Menu-driven full-screen interface with `tracker tui`
3. **REST API Server** - Build custom frontends with `tracker server`

### Additional Interfaces
- 🌐 **REST API** - FastAPI server with JWT authentication, OpenAPI docs
- 🔌 **MCP Server** - Model Context Protocol for AI agent integration
- 🐳 **Docker Ready** - Multi-stage builds, docker-compose orchestration
- 🔄 **CI/CD** - GitHub Actions with automated testing and deployment

### Power User Features
- ✏️ **Entry Editing** - Modify past entries with audit trail
- 📤 **Data Export** - CSV/JSON formats with date filtering
- 🏆 **Achievements** - Unlock rewards for consistent tracking
- 🔄 **Hot Reload** - Development mode with live code updates

## 🚀 Quick Start

### 📦 Installation Methods

#### Method 1: UV (Recommended - Fastest)

**Why UV?**
- ⚡ 10-100x faster than pip
- 🔒 Automatic virtual environment management
- 📦 Modern Rust-based package manager

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/EanHD/tracker.git
cd tracker
uv sync
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Initialize database
python scripts/init_db.py
```

#### Method 2: Docker (Most Isolated)

**Why Docker?**
- 🐳 Complete environment isolation
- ✅ No Python version conflicts
- 📤 Easy deployment and sharing
- 💾 Data persists in volumes

```bash
git clone https://github.com/EanHD/tracker.git
cd tracker
cp .env.example .env
# Edit .env with your API keys

docker-compose up -d

# Access the container
docker-compose exec tracker bash
tracker
```

#### Method 3: Traditional pip

**Why pip?**
- 📚 Most familiar to developers
- 🛠️ Direct control over environment

```bash
git clone https://github.com/EanHD/tracker.git
cd tracker

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .

python scripts/init_db.py
```

### 🎯 Usage Modes

| Mode | Command | Best For | Pros | Cons |
|------|---------|----------|------|------|
| **Menu App** | `tracker` | Daily use | Easy navigation, beginner-friendly | Can't script |
| **CLI Commands** | `tracker new`, `tracker show` | Power users, automation | Fast, scriptable | Must remember commands |
| **API Server** | `tracker server` | Custom frontends | Build web/mobile apps | Requires API knowledge |

### Prerequisites

```bash
# Interactive onboarding (recommended)
tracker onboard

# Or edit .env file directly
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-...
```

### Accessibility Options

- `tracker --plain` – disables color markup and emoji, adds text descriptors for screen readers.
- `tracker --no-color` / `tracker --no-emoji` – opt out of individual styling features.
- Environment variables: set `TRACKER_PLAIN_MODE=1`, `TRACKER_NO_COLOR=1`, or `TRACKER_NO_EMOJI=1` to keep preferences across runs.

Plain mode works across the interactive loop, CLI commands, and the Rich-powered preview panels, so assistive technology reads actionable text instead of ANSI control codes.

### Your First Entry

```bash
# Interactive TUI (default - just run tracker)
tracker

# Interactive CLI mode (guided prompts)
tracker new

# Quick mode (command flags)
tracker new --income 150 --bills 50 --stress 4 --hours 8

# View entry with AI feedback
tracker show today

# Check your achievements
tracker achievements
```

### Talk with Tracker

Ask follow-up questions or get coaching based on your journal history.

```bash
# Start a fresh standalone conversation
tracker chat new

# List existing conversations (standalone + entry linked)
tracker chat list

# Resume a conversation by id
tracker chat open 5
```

Inside the TUI, pick **Chats** from the main menu to browse conversations with inline context, continue discussion threads, or review transcript history without leaving the interface.

## 🎯 Usage Modes

### 1. Interactive TUI (Default - Recommended for Beginners)

Launch the full-screen menu interface (just run `tracker` with no arguments):

```bash
tracker
```

Navigate with arrow keys, use hotkeys (`n` for new entry, `v` to view, etc.), and ESC to go back. Perfect for:
- Creating detailed entries with form validation
- Browsing your entry history
- Viewing statistics and achievements
- Learning available features

[📖 Full TUI Documentation](TUI_IMPLEMENTATION.md)

### 2. CLI Commands (Power Users & Automation)

Direct commands for speed and scripting:

```bash
# Create entries
tracker new --income 500 --bills 200
tracker edit today --mood 8

# View data
tracker show yesterday
tracker list --days 7
tracker search "exercise"

# Analytics
tracker stats --plot
tracker achievements

# Export
tracker export --format csv --output data.csv
```

### 3. Server Mode (Custom Frontends)

Run the REST API server:

```bash
tracker server --port 5703

# Or with Docker
docker-compose up -d
```

Build your own frontend or integrate with other tools:
- OpenAPI docs at `http://localhost:5703/docs`
- JWT authentication
- Full CRUD operations
- Real-time AI feedback endpoints

[📖 API Documentation](docs/API.md)

## 📚 Documentation

### User Documentation
- **[User Guide](docs/USER_GUIDE.md)** - Complete usage guide with examples
- **[API Documentation](docs/API_DOCUMENTATION.md)** - REST API reference
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment with systemd, nginx, SSL
- **[Docker Guide](docs/DOCKER.md)** - Container deployment and orchestration

### Developer Documentation
- **[Architecture Overview](specs/001-daily-logging-ai/spec.md)** - System design
- **[Data Model](specs/001-daily-logging-ai/data-model.md)** - Database schema
- **[API Contracts](specs/001-daily-logging-ai/contracts/api-spec.md)** - API specifications
- **[MCP Server](specs/001-daily-logging-ai/contracts/mcp-spec.md)** - MCP integration

## 🎮 Usage Examples

### Daily Workflow

```bash
# Morning: Review yesterday
tracker show yesterday
tracker achievements

# Evening: Log today
tracker new \
  --income 150 \
  --bills 50 \
  --food 25 \
  --hours 8 \
  --stress 4 \
  --sleep 7 \
  --exercise 1

# Weekly review
tracker stats --days 7
tracker search "productive"

# Monthly export
tracker export --format csv --output monthly.csv
```

### CLI Commands

```bash
# Entry Management
tracker new              # Create entry (interactive)
tracker edit yesterday   # Edit existing entry
tracker show 2025-10-21  # View specific entry
tracker list --limit 30  # List recent entries

# User Profile (NEW!)
tracker profile setup    # Interactive profile wizard
tracker profile view     # View your profile
tracker profile update   # Update sections
tracker profile checkin  # Monthly check-in

# Analysis
tracker stats --days 7   # Statistics and trends
tracker search "stress"  # Search with highlighting
tracker achievements     # View progress & achievements

# Data Management
tracker export --format csv   # Export to CSV
tracker export --format json  # Export to JSON

# Configuration
tracker config show      # View settings
tracker config setup     # Interactive wizard
# Or edit .env file directly for full control

# Servers
tracker server          # Start REST API (port 5703)
tracker mcp            # Start MCP server (stdio)
```

## 👤 User Profile System

**NEW!** Personalize AI feedback with rich context about you.

### Privacy Levels
- **Basic** - Just spending & stress (default)
- **Personal** - Add work, bills, goals
- **Deep** - Full context with AI pattern detection

### Quick Start
```bash
# Interactive setup (2-5 minutes)
tracker profile setup

# View your profile
tracker profile view

# Monthly refresh
tracker profile checkin
```

### How It Helps
The AI uses your profile to provide:
- ✅ **Personalized tone** - Casual, professional, encouraging, or stoic
- ✅ **Context-aware insights** - "Rent due in 3 days, payday tomorrow—you're set!"
- ✅ **Goal tracking** - "60% to your $5k emergency fund. On track for May!"
- ✅ **Pattern recognition** - "Stress spikes mid-month. Gym session helped last time."
- ✅ **Schedule awareness** - Reminders aligned with your pay schedule

### Example Feedback Evolution

**Without Profile:**
> "You spent $45 on food today. Good job logging your entry!"

**With Profile (Personal Mode, 12-day streak):**
> "Hey Sarah! 12 days in a row—you're crushing it! I know tight finances have been stressing you out, but you kept it together today. Your $5k emergency fund is 60% there. At this rate, you'll hit it by May. One day at a time! 💪"

📖 **Learn more**: See [USER_PROFILE_SYSTEM.md](USER_PROFILE_SYSTEM.md) for full details.

## 🧠 Philosophy Engine - AI Mentor System

**NEW!** Tracker's AI now speaks like a wise financial and life mentor.

### What Is It?
A wisdom system combining:
- **Dave Ramsey** - Financial discipline (debt snowball, emergency fund, budgeting)
- **Robert Kiyosaki** - Wealth mindset (assets, multiple incomes, financial education)
- **Behavioral Economics** - How humans actually make decisions
- **Emotional Intelligence** - Self-awareness and regulation
- **Life Balance** - Holistic wellbeing and values alignment

### How It Works
The AI automatically:
1. **Detects your life phase** (Debt Payoff → Stability → Growth → Legacy)
2. **Analyzes your patterns** (stress, spending, streaks)
3. **Selects relevant wisdom** (1-3 principles that fit your situation)
4. **Adapts communication** (encouraging, honest, compassionate, etc.)

### Example Transformation

**Without Philosophy Engine:**
> "You spent $45 on food today. Try to manage spending better."

**With Philosophy Engine:**
> "I see you today. Stress at 8/10, spending up—that's real and hard. You're not failing, you're human.
>
> Here's what I know: you can't make great money decisions when you're running on empty. Rest comes before budgeting.
>
> When you're ready, let's look at that smallest debt. $200 more and it's gone. That win will fuel the next one. Momentum beats math every time. One step at a time. 💪"

### Core Principles (19 Total)

| Category | Examples |
|----------|----------|
| **Financial Discipline** | Live Below Means, Emergency Fund First, Debt Snowball |
| **Wealth Mindset** | Assets vs Liabilities, Pay Yourself First, Multiple Income Streams |
| **Habit Building** | Progress Not Perfection, Automate Decisions, Celebrate Wins |
| **Emotional Intelligence** | Notice Before React, Gratitude, Forgive Mistakes |
| **Balance & Health** | Rest Well Decide Well, Align with Values |
| **Behavioral Economics** | Momentum Over Math, Simplify Goals |

📖 **Learn more**: See [PHILOSOPHY_ENGINE.md](PHILOSOPHY_ENGINE.md) for full documentation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  User Interfaces                    │
├─────────────┬─────────────┬────────────────────────┤
│   CLI       │  REST API   │   MCP Server           │
│  (Click)    │  (FastAPI)  │   (stdio/sse)          │
└─────────────┴─────────────┴────────────────────────┘
               │             │             │
               └─────────────┴─────────────┘
                            │
              ┌─────────────▼─────────────┐
              │     Services Layer        │
              ├───────────────────────────┤
              │ • EntryService           │
              │ • FeedbackService        │
              │ • HistoryService         │
              │ • ExportService          │
              │ • GamificationService    │
              └─────────────┬─────────────┘
                            │
              ┌─────────────▼─────────────┐
              │    Core Components        │
              ├───────────────────────────┤
              │ • Models (SQLAlchemy)    │
              │ • Schemas (Pydantic)     │
              │ • Auth (JWT, bcrypt)     │
              │ • Database (SQLite)      │
              └───────────────────────────┘
```

### Directory Structure

```
tracker/
├── src/tracker/
│   ├── cli/              # Click commands, Rich UI (13 commands)
│   ├── api/              # FastAPI routes (5 routers, 15+ endpoints)
│   ├── mcp/              # MCP server (8 tools, 4 resources, 3 prompts)
│   ├── services/         # Business logic (7 services)
│   └── core/             # Models, schemas, database, auth
├── docs/                 # Comprehensive documentation
├── scripts/              # Utility scripts (init_db.py)
├── tests/                # Unit, integration, E2E tests
├── .github/workflows/    # CI/CD pipelines
├── Dockerfile            # Multi-stage container build
└── docker-compose.yml    # Orchestration configuration
```

## 🛠️ Development

### Setup

```bash
# Install with dev dependencies
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest --cov=tracker --cov-report=html

# Lint and format
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/tracker/
```

### Running Locally

```bash
# CLI development
tracker new  # Uses local code

# API development (with hot reload)
uvicorn tracker.api.main:app --reload --host 0.0.0.0 --port 5703

# MCP development
tracker mcp --log-file /tmp/mcp.log
```

### Docker Development

```bash
# Build image
docker build -t tracker:dev .

# Run container
docker-compose up -d

# View logs
docker-compose logs -f

# Execute commands in container
docker-compose exec tracker-api tracker stats
```

### Testing

```bash
# All tests
pytest

# Specific test
pytest tests/unit/test_entry_service.py

# With coverage
pytest --cov=tracker --cov-report=html

# Watch mode
pytest-watch
```

## 🚢 Deployment

### Quick Deploy with Docker

```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f tracker-api
```

### Manual Deployment

See [Deployment Guide](docs/DEPLOYMENT.md) for:
- Systemd service configuration
- Nginx reverse proxy setup
- SSL/TLS with Let's Encrypt
- Security hardening
- Backup and monitoring

### CI/CD

GitHub Actions automatically:
- ✅ Runs tests on every push
- ✅ Builds Docker images
- ✅ Deploys on version tags
- ✅ Creates GitHub releases

See [.github/workflows/README.md](.github/workflows/README.md) for details.

## 🎯 Roadmap

### Current (v1.0.0)
- ✅ CLI with 13 commands
- ✅ REST API with 15+ endpoints
- ✅ MCP server with 8 tools
- ✅ 9 achievements system
- ✅ Search and export
- ✅ Docker deployment
- ✅ Complete documentation

### Future
- [ ] Web UI (React/Next.js)
- [ ] Mobile app (React Native)
- [ ] Data visualization dashboard
- [ ] Multi-user support
- [ ] Cloud sync (optional)
- [ ] Webhooks and integrations
- [ ] Advanced analytics
- [ ] Template system

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Rich](https://rich.readthedocs.io/) - Beautiful terminal formatting
- [Click](https://click.palletsprojects.com/) - CLI framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM and database toolkit
- [uv](https://github.com/astral-sh/uv) - Ultra-fast Python package manager

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/EanHD/tracker/issues)
- **Discussions**: [GitHub Discussions](https://github.com/EanHD/tracker/discussions)
- **Email**: your.email@example.com

---

**Made with ❤️ for better daily tracking**
