# Daily Tracker - Personal Analytics with AI Insights

[![CI/CD](https://github.com/EanHD/tracker/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/EanHD/tracker/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://hub.docker.com/r/eanhd/daily-tracker)

A powerful CLI-first daily tracking application with AI-powered insights. Track finances, work patterns, wellbeing, and receive personalized feedback from multiple AI providers.

## ✨ Features

### Core Functionality
- 📝 **Rich CLI Interface** - Beautiful terminal UI with Rich library
- 🤖 **Multi-Provider AI** - OpenAI, Anthropic, OpenRouter, or Local models
- 📊 **Comprehensive Tracking** - Finance, work hours, stress, sleep, exercise, social time
- 🔒 **Privacy-First** - Local SQLite database, no cloud storage
- 🔍 **Full-Text Search** - Find entries with keyword highlighting
- 📈 **Statistics & Trends** - Analyze patterns with visual charts
- 🎯 **Gamification** - 9 achievements, streak tracking, progress bars

### Interfaces
- 🌐 **REST API** - FastAPI server with JWT authentication, OpenAPI docs
- 🔌 **MCP Server** - Model Context Protocol for AI agent integration
- 🐳 **Docker Ready** - Multi-stage builds, docker-compose orchestration
- � **CI/CD** - GitHub Actions with automated testing and deployment

### Power User Features
- ✏️ **Entry Editing** - Modify past entries with audit trail
- 📤 **Data Export** - CSV/JSON formats with date filtering
- 🏆 **Achievements** - Unlock rewards for consistent tracking
- 🔄 **Hot Reload** - Development mode with live code updates

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+** - Required for latest features
- **uv** - Fast Python package manager (10-100x faster than pip)

### Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone https://github.com/EanHD/tracker.git
cd tracker

# Setup environment
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .

# Initialize database
python scripts/init_db.py
```

### 🐳 Docker Quick Start

```bash
# Using Docker Compose
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d

# Test API
curl http://localhost:5703/api/v1/health
```

### Configuration

```bash
# Interactive onboarding (recommended)
tracker onboard

# Or edit .env file directly
# AI_PROVIDER=openai
# OPENAI_API_KEY=sk-...
```

### Your First Entry

```bash
# Interactive mode (guided prompts)
tracker new

# Quick mode (command flags)
tracker new --income 150 --bills 50 --stress 4 --hours 8

# View entry with AI feedback
tracker show today

# Check your achievements
tracker achievements
```

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
