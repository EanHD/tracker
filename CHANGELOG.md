# Changelog

All notable changes to Daily Tracker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Web UI (React/Next.js frontend)
- Mobile app (React Native)
- Multi-user support with role-based access
- Cloud sync (optional, privacy-preserving)
- Advanced data visualizations
- Webhook integrations
- Template system for recurring entries

---

## [1.0.0] - 2025-10-21

### 🎉 Initial Release

First stable release of Daily Tracker with comprehensive features for daily tracking and AI-powered insights.

### Added

#### Core Features
- **Entry Management**
  - Create daily entries with financial, work, and wellbeing data
  - Edit existing entries with audit trail
  - Delete entries with authorization checks
  - View single entries with AI feedback
  - List entries with pagination (7, 30, 100 days)
  
- **AI Integration**
  - Multi-provider support: OpenAI, Anthropic, OpenRouter, Local models
  - Personalized feedback generation
  - Configurable AI models and parameters
  - Feedback regeneration on demand
  - Error handling and retry logic

- **Search & Discovery**
  - Full-text search across notes and priority fields
  - Keyword highlighting in results
  - Case-insensitive matching
  - Configurable result limits

- **Data Export**
  - CSV export for spreadsheet analysis
  - JSON export with structured data
  - Date range filtering
  - Statistics preview before export
  - File output with automatic naming

- **Gamification**
  - 9 achievement system with progress tracking
  - Streak tracking (current and longest)
  - Motivational messages
  - Progress bars for locked achievements
  - Achievement unlock notifications
  
  **Achievements:**
  - 🎯 Getting Started (first entry)
  - 🔥 Week Warrior (7-day streak)
  - ⭐ Monthly Master (30-day streak)
  - 💯 Century Club (100-day streak)
  - 📈 Halfway There (50 total entries)
  - 🏆 Centennial (100 total entries)
  - 👑 Year of Tracking (365 total entries)
  - 🧘 Zen Master (stress ≤3 for week)
  - 💰 In the Black (30 days positive)

- **Statistics & Analytics**
  - Financial summaries (income, expenses, net)
  - Work patterns (hours, stress levels)
  - Wellbeing metrics (sleep, exercise, social)
  - Trend analysis (stable, increasing, decreasing)
  - Configurable time periods (7, 30, 365 days)

#### CLI Interface
- **13 Commands** implemented:
  - `tracker new` - Create entry (interactive or flags)
  - `tracker edit` - Edit entry (interactive or flags)
  - `tracker show` - Display entry with feedback
  - `tracker list` - Browse multiple entries
  - `tracker search` - Full-text search with highlighting
  - `tracker export` - Export to CSV/JSON
  - `tracker stats` - View statistics
  - `tracker achievements` - View progress & achievements
  - `tracker config` - Manage settings
  - `tracker onboard` - Interactive setup wizard
  - `tracker server` - Start REST API
  - `tracker mcp` - Start MCP server

- **Rich Terminal UI**
  - Color-coded outputs
  - Progress bars and spinners
  - Formatted tables
  - Interactive prompts
  - Error handling with helpful messages

#### REST API
- **5 Routers** with 15+ endpoints:
  - **Auth**: `/auth/register`, `/auth/login`
  - **Entries**: CRUD operations on `/entries/`
  - **Feedback**: `/feedback/{date}`, `/feedback/{date}/regenerate`
  - **Stats**: `/stats/` with date range filtering
  - **Export**: `/export/{csv,json,stats}`

- **Features**:
  - JWT authentication (90-day expiry)
  - Bearer token authorization
  - Pydantic validation
  - OpenAPI documentation at `/docs`
  - ReDoc at `/redoc`
  - Health check endpoint
  - CORS support

#### MCP Server
- **8 Tools** for AI agents:
  - `create_entry` - Create new daily entry
  - `get_entry` - Retrieve entry by date
  - `list_entries` - Browse entries with pagination
  - `get_statistics` - Analyze trends
  - `search_entries` - Full-text search
  - `update_entry` - Edit existing entry
  - `get_feedback` - Retrieve AI feedback
  - `regenerate_feedback` - Generate new feedback

- **4 Resources**:
  - `entry://{date}` - Individual entries
  - `entries://recent` - Recent entries
  - `stats://summary` - Statistics summary
  - `config://settings` - Configuration

- **3 Prompts**:
  - `daily_reflection` - Guided daily reflection
  - `weekly_review` - Week-in-review analysis
  - `goal_setting` - Goal planning assistant

#### Infrastructure
- **Docker Support**:
  - Multi-stage Dockerfile (builder + runtime)
  - docker-compose.yml with nginx option
  - Health checks and restart policies
  - Volume management for persistence
  - Environment variable configuration

- **CI/CD Pipeline**:
  - GitHub Actions workflow
  - Automated testing with pytest
  - Code coverage with Codecov
  - Security scanning (Bandit, Safety, Trivy)
  - Docker image building and publishing
  - Auto-deployment on tags
  - GitHub Release creation

- **Documentation**:
  - User Guide (600+ lines)
  - API Documentation (900+ lines)
  - Deployment Guide (900+ lines)
  - Docker Guide (600+ lines)
  - CI/CD documentation
  - Architecture diagrams
  - Code examples

#### Developer Experience
- **Modern Python Stack**:
  - Python 3.12+ required
  - uv package manager (10-100x faster)
  - Type hints throughout
  - Pydantic v2 validation
  - SQLAlchemy 2.0 ORM

- **Code Quality**:
  - Ruff for linting and formatting
  - mypy for type checking
  - pytest for testing
  - 41 passing unit tests
  - Integration test suite

- **Security**:
  - bcrypt password hashing
  - JWT token authentication
  - Input validation with Pydantic
  - SQL injection protection (ORM)
  - Environment variable management
  - No hardcoded secrets

### Technical Details

**Database:**
- SQLite with SQLAlchemy 2.0
- Automatic migrations
- Audit trail (created_at, updated_at)
- Efficient indexing

**Dependencies:**
- FastAPI 0.109.0 - Web framework
- Click 8.1.7 - CLI framework
- Rich 13.7.0 - Terminal UI
- SQLAlchemy 2.0.25 - ORM
- Pydantic 2.5.3 - Validation
- bcrypt 4.1.2 - Password hashing
- PyJWT 2.8.0 - Token authentication
- OpenAI, Anthropic, OpenRouter SDKs

**Performance:**
- Lazy loading for large datasets
- Database connection pooling
- Efficient query patterns
- Streaming responses for large exports

**Deployment:**
- systemd service configuration
- Nginx reverse proxy
- Let's Encrypt SSL/TLS
- UFW firewall setup
- Automated backups
- Health monitoring

### Testing
- 41 unit tests passing
- Integration tests for API
- End-to-end CLI tests
- Manual validation for all features
- CI/CD automated testing

### Known Limitations
- Single-user desktop application (multi-user planned for v2.0)
- Local-only storage (cloud sync planned)
- CLI-first (web UI planned)
- No data migration from other apps (import planned)

### Migration Notes
- First release, no migrations needed
- Database auto-created on first run
- Configuration via interactive onboarding

---

## Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality (backward compatible)
- **PATCH** version for bug fixes (backward compatible)

### Release Checklist
- [ ] Update version in `pyproject.toml`
- [ ] Update this CHANGELOG with new entries
- [ ] Run full test suite: `pytest`
- [ ] Build and test Docker image
- [ ] Create git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] CI/CD auto-deploys and creates GitHub Release
- [ ] Announce release on GitHub Discussions

### Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting changes.

---

**Changelog Format:**
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for bug fixes
- **Security** for vulnerability fixes

[Unreleased]: https://github.com/yourusername/tracker/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/tracker/releases/tag/v1.0.0
