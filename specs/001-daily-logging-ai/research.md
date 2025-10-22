# Research & Technology Decisions

**Feature**: Daily Logging App with AI Agent Integration  
**Date**: 2025-10-21  
**Purpose**: Document technology choices, rationale, and alternatives considered

## CLI Framework

### Decision: Click + Rich + Prompt Toolkit

**Rationale**:
- **Click**: Industry-standard for Python CLIs, excellent command/subcommand support, automatic help generation
- **Rich**: Beautiful terminal UI with tables, panels, progress bars, syntax highlighting - makes the CLI "feel good to use"
- **Prompt Toolkit**: Advanced interactive prompts with auto-completion, validation, history navigation

**Alternatives Considered**:
- **Typer**: More modern, type-hint based, but Click is more mature and flexible for complex command structures
- **Argparse**: Standard library but verbose and lacks the polish of Click
- **Textual**: Full TUI framework - too heavy for this use case, would complicate navigation

**Implementation Notes**:
- Rich's `Panel` for entry display with color-coded stress levels
- Rich's `Table` for history views with column sorting
- Prompt Toolkit for the interactive "new entry" flow with field validation
- Click's command groups for logical organization (`tracker new`, `tracker view`, etc.)

## API Framework

### Decision: FastAPI + Uvicorn

**Rationale**:
- **FastAPI**: Modern async framework with automatic OpenAPI docs, Pydantic validation, excellent performance
- **Type safety**: Leverages Python type hints for request/response validation
- **Auto documentation**: `/docs` endpoint with interactive API explorer out-of-the-box
- **Async support**: Native async/await for non-blocking AI operations
- **Dependency injection**: Clean pattern for database sessions and authentication

**Alternatives Considered**:
- **Flask**: Mature but synchronous, requires extensions for OpenAPI, less modern architecture
- **Django REST**: Too heavy, includes ORM we're already using separately, overkill for this scope
- **Starlette**: FastAPI is built on Starlette, so we get its benefits with better DX

**Implementation Notes**:
- APIRouter for modular endpoint organization
- BackgroundTasks for async AI feedback generation
- JWT authentication via `python-jose`
- CORS middleware for future web frontend support

## Database & ORM

### Decision: SQLAlchemy 2.0 + SQLite (with PostgreSQL migration path)

**Rationale**:
- **SQLite**: Perfect for single-user, local-first approach - zero configuration, file-based
- **SQLAlchemy 2.0**: Modern ORM with type safety, relationship handling, migration support via Alembic
- **Async support**: SQLAlchemy 2.0 supports async drivers for scalability
- **Migration path**: Can swap SQLite for PostgreSQL by changing connection string (same ORM code)

**Alternatives Considered**:
- **Raw SQL**: More control but verbose, error-prone, no migration management
- **Peewee/Pony**: Simpler ORMs but less ecosystem support, harder PostgreSQL migration
- **Direct file storage (JSON)**: Simple but no ACID guarantees, no indexing, manual encryption

**Implementation Notes**:
- SQLCipher for encryption at rest (transparent SQLite encryption)
- Alembic for schema migrations
- Async session with `asyncio` support for API layer
- Foreign keys enabled for referential integrity

## Encryption

### Decision: SQLCipher + Fernet (symmetric)

**Rationale**:
- **SQLCipher**: Transparent database encryption at rest, integrates seamlessly with SQLite
- **Fernet**: Cryptography library's symmetric encryption for field-level encryption of specific sensitive fields
- **Key management**: Store key in OS keychain (keyring library) or environment variable

**Alternatives Considered**:
- **Full disk encryption**: OS-level but doesn't protect if DB file is copied
- **Application-level only**: More control but reinventing the wheel
- **Asymmetric encryption**: Overkill for single-user scenario, key management complexity

**Implementation Notes**:
- Encrypt financial fields (cash_on_hand, bank_balance, debts_total) at field level
- SQLCipher for full database protection as second layer
- Key derivation from user password or secure random generation

## AI Integration

### Decision: Multi-provider support (OpenAI + Anthropic + OpenRouter + Local) via unified interface

**Rationale**:
- **Flexibility**: Users choose their preferred AI provider and API key
- **Cost control**: Different providers have different pricing models
- **OpenRouter**: Access to 100+ models through one API, competitive pricing
- **Local models**: Privacy-first option using Ollama, LM Studio, or llama.cpp
- **Resilience**: Fallback to alternative provider if primary fails
- **Future-proof**: Easy to add new providers (Gemini, Azure OpenAI)

**Supported Providers**:
1. **OpenAI**: GPT-4, GPT-3.5-turbo - Industry standard, best quality
2. **Anthropic**: Claude 3 (Opus, Sonnet, Haiku) - Strong reasoning, long context
3. **OpenRouter**: Unified gateway to 100+ models - Cost-effective, model variety
4. **Local**: Ollama/LM Studio compatible - Privacy, no API costs, offline support

**Alternatives Considered**:
- **Single provider lock-in**: Simpler but limits user choice
- **LangChain**: Heavy framework, unnecessary for simple prompt/response pattern
- **Local models only**: Privacy benefit but requires technical setup, slower inference
- **Local models**: Privacy benefit but resource-intensive, complex setup

**Implementation Notes**:
- Abstract `AIClient` interface in `services/ai_client.py`
- Provider-specific implementations: `OpenAIClient`, `AnthropicClient`, `OpenRouterClient`, `LocalClient`
- OpenRouter: Uses OpenAI-compatible API with custom base URL and model routing
- Local: OpenAI-compatible endpoint (http://localhost:1234/v1) for Ollama/LM Studio
- Configuration via environment variables: `AI_PROVIDER=openrouter`, `OPENROUTER_API_KEY=...`, `LOCAL_API_URL=...`
- Automatic provider detection based on available API keys in onboarding
- Prompt templates in `mcp/prompts.py` for consistent context framing
- Model selection per provider with sensible defaults

## MCP Server

### Decision: Official MCP Python SDK

**Rationale**:
- **Standard protocol**: Model Context Protocol is emerging standard for AI agent tool connectivity
- **Anthropic backing**: Developed by Anthropic, good long-term support
- **Type safety**: Python SDK includes type stubs for tool definitions
- **Transport flexibility**: Supports stdio and HTTP transports

**Alternatives Considered**:
- **Custom RPC**: Would need to reinvent protocol, authentication, discovery
- **Direct API calls**: MCP adds standardization, tool discovery, context management
- **LangChain agents**: Heavier framework, MCP is lighter and more focused

**Implementation Notes**:
- Tools: `create_entry`, `get_entry`, `list_entries`, `generate_feedback`
- Resources: Entry data exposed as MCP resources for AI context
- Stdio transport for local development, HTTP for remote AI agents
- Authentication via API tokens (reuse API auth layer)

## Authentication & Authorization

### Decision: JWT tokens with scope-based permissions

**Rationale**:
- **Stateless**: No session storage needed, scales horizontally
- **Standard**: JWT is industry standard, many libraries and tools support it
- **Scoped permissions**: Fine-grained access control (read vs write)
- **Expiration**: Built-in token expiry for security

**Alternatives Considered**:
- **API keys**: Simpler but no expiration, coarse-grained permissions
- **OAuth2**: Overkill for single-user, designed for third-party delegation
- **Session cookies**: Stateful, doesn't work well for CLI/MCP server access

**Implementation Notes**:
- `python-jose` for JWT encoding/decoding
- Scopes: `entries:read`, `entries:write`, `feedback:generate`
- Token generation: `tracker config generate-token`
- Expiration: 90 days default, configurable

## Testing Strategy

### Decision: Pytest + pytest-asyncio + HTTPX + pytest-mock

**Rationale**:
- **Pytest**: De facto Python testing standard, excellent fixture system
- **Async support**: pytest-asyncio for testing FastAPI and async services
- **HTTP testing**: HTTPX TestClient for API endpoint testing without running server
- **Mocking**: pytest-mock for isolating external dependencies (AI calls, etc.)

**Alternatives Considered**:
- **Unittest**: Standard library but verbose, less flexible than pytest
- **Nose**: Deprecated, pytest is the modern choice
- **Integration test only**: Need unit tests for fast feedback

**Implementation Notes**:
- Fixtures in `conftest.py`: test DB, mock AI client, authenticated API client
- Separate test DB file, reset between tests
- Mock AI responses for deterministic testing
- Coverage target: 80%+ for core services

## CLI UX Enhancements

### Research: Best Practices for "Feeling Good to Use"

**Findings**:
1. **Immediate feedback**: Progress spinners for async operations (Rich's `Status`)
2. **Color coding**: Stress levels (green=1-3, yellow=4-6, red=7-10), income vs expenses
3. **Smart defaults**: Auto-fill today's date, remember last values for optional fields
4. **Keyboard shortcuts**: Arrow keys for history navigation, Ctrl+C for graceful cancel
5. **Helpful errors**: Specific validation messages, not generic errors
6. **Quick actions**: `tracker new --quick` for rapid entry (less interactive)
7. **Visual separation**: Rich panels to separate entry sections visually
8. **Confirmation**: Show formatted preview before saving entry

**Inspired By**:
- **gh CLI**: Clean command structure, interactive prompts
- **npm**: Progress indicators, clear success/error states
- **homebrew**: Beautiful output formatting

**Cool Suggestions to Add**:
1. **Trends summary**: `tracker trends` - weekly/monthly summaries (avg stress, income, spending)
2. **Streak tracking**: Days logged consecutively, gamification element
3. **Quick stats**: Show quick stats when viewing entry (e.g., "5% less stressed than last week")
4. **Export**: `tracker export --format csv/json` for personal analysis
5. **Search**: `tracker search <query>` - full-text search in notes field
6. **Reminders**: Optional daily reminder notification (via `schedule` library)
7. **Templates**: Save entry templates for recurring patterns
8. **AI chat mode**: `tracker chat` - conversational interface for longer AI discussions
9. **Backup/restore**: `tracker backup` - encrypted backup to file or cloud storage
10. **Insights**: `tracker insights` - AI-generated weekly reflection on patterns observed

## Data Sync Strategy

### Decision: Shared SQLite database + file locking

**Rationale**:
- **Single source of truth**: All components read/write same DB file
- **No sync complexity**: No eventual consistency issues, immediate consistency
- **File locking**: SQLite handles concurrent access via file locking
- **Simple deployment**: Single database file, easy to backup/move

**Future Multi-User Considerations**:
- Migrate to PostgreSQL when hosting API publicly
- Keep ORM abstraction so migration is connection string change
- Add user_id to all tables for multi-tenancy
- Consider row-level security for PostgreSQL

**Implementation Notes**:
- Default DB location: `~/.config/tracker/tracker.db`
- CLI, API, MCP all use same database path from config
- WAL mode enabled for better concurrent access
- Regular vacuum operations for performance

## Configuration Management

### Decision: Environment variables + config file + CLI overrides + Interactive Onboarding

**Rationale**:
- **12-factor app**: Environment variables for secrets
- **User-friendly**: Config file (`~/.config/tracker/config.yaml`) for preferences
- **Flexibility**: CLI flags override config file which overrides env vars
- **Secure**: Secrets never in config file, only env vars or OS keychain
- **Onboarding wizard**: Interactive first-run experience to set up everything properly

**Implementation Notes**:
- `pydantic-settings` for unified config management
- Keyring library for API key storage (OS-native keychain)
- Config command: `tracker config set AI_PROVIDER openai`
- Validation on load with helpful error messages
- **Onboarding wizard** (`tracker onboard` or auto-triggered on first `tracker new`):
  1. System configuration (data dir, timezone, currency, encryption)
  2. AI provider setup with auto-detection and testing
  3. Financial baseline (income cadence, fixed expenses, debts, starting balances)
  4. Wellbeing baseline (typical stress/mood, sleep hours, work hours)
  5. Budget targets (monthly income goal, spending limits by category)
  6. Idempotent execution (safe to re-run, preserves existing data)
  7. Confirmation and summary before applying changes

## Onboarding Experience

### Decision: Interactive Wizard for First-Time Setup

**Rationale**:
- **Reduce friction**: Guide users through essential configuration step-by-step
- **Establish baseline**: Collect initial financial and wellbeing data for meaningful comparisons
- **Discover capabilities**: Introduce features (AI feedback, trends, budgets) during setup
- **Prevent errors**: Validate inputs and test connections before saving
- **Re-runnable**: Safe to execute multiple times, updates only changed values

**Wizard Flow**:

**Step 1: System Configuration**
- Data directory location (default: `~/.config/tracker`)
- Timezone for accurate date handling
- Currency symbol and code (USD, EUR, GBP, etc.)
- Encryption setup (generate key or use existing)
- Theme preferences (color scheme, date format)

**Step 2: AI Provider Setup**
- Auto-detect available providers (check for API keys in env)
- Interactive provider selection (OpenAI, Anthropic, OpenRouter, Local)
- API key entry with masking and validation
- Connection test with sample prompt
- Model selection (default: best balance of cost/quality)
- Fallback provider configuration (optional)

**Step 3: Financial Baseline**
- Income cadence (weekly, bi-weekly, monthly, irregular)
- Primary income amount and frequency
- Fixed recurring expenses (rent, bills, subscriptions)
- Current debt totals and types
- Starting bank balance and cash on hand
- Side income sources (if applicable)

**Step 4: Wellbeing Baseline**
- Typical stress level on a normal day (1-10)
- Average sleep hours per night
- Usual work hours per day
- Mood baseline (good, neutral, struggling)
- Health considerations affecting daily energy

**Step 5: Budget Targets**
- Monthly income goal
- Spending limits by category (food, transport, entertainment)
- Debt payoff targets and timeline
- Savings goals
- Emergency fund target

**Step 6: Confirmation & Summary**
- Display all collected information in organized panels
- Highlight what will be created (config files, database seeds, encryption keys)
- Allow editing any section before finalizing
- Confirm and apply changes
- Show next steps (create first entry, explore commands)

**Implementation Notes**:
- Command: `tracker onboard` or auto-run on first `init`
- Uses Rich panels and progress bars for visual appeal
- Saves to both `config.yaml` and database (User.settings JSON)
- Creates baseline entry marked as "setup snapshot" (excluded from trends)
- Validates all inputs with helpful error messages
- Stores sensitive data in keyring, non-sensitive in YAML
- Generates `.env` file with encryption key and optional API keys
- Safe to re-run: loads existing values as defaults, only updates changed fields

## Development Workflow

### Decision: Poetry + Black + Ruff + Pre-commit

**Rationale**:
- **Poetry**: Modern dependency management, better than pip + requirements.txt
- **Black**: Opinionated formatter, eliminates style debates
- **Ruff**: Fast linter (Rust-based), replaces flake8 + isort + pylint
- **Pre-commit**: Automated checks before commit (format, lint, type check)

**Implementation Notes**:
- `pyproject.toml` for all tool configuration
- Pre-commit hooks: black, ruff, mypy
- CI/CD ready: GitHub Actions workflow for tests + checks
