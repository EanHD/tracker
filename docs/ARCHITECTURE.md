# Tracker Architecture - Multi-Mode Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERACTION LAYER                        │
├─────────────────┬─────────────────┬───────────────────┬─────────────┤
│                 │                 │                   │             │
│   CLI Commands  │  TUI Interface  │   REST API       │  MCP Server │
│   (Click)       │  (Textual)      │   (FastAPI)      │  (MCP)      │
│                 │                 │                   │             │
│  tracker new    │  tracker tui    │  tracker server  │ tracker mcp │
│  tracker show   │    ┌─────┐     │    ┌──────┐      │             │
│  tracker list   │    │Menu │     │    │OpenAPI│     │             │
│  tracker stats  │    └──┬──┘     │    │ Docs │     │             │
│  tracker export │       │         │    └──────┘     │             │
│       ...       │   8 Screens     │   JWT Auth      │  AI Agents  │
│                 │                 │                  │             │
└────────┬────────┴────────┬────────┴─────────┬────────┴──────┬──────┘
         │                 │                  │                │
         └─────────────────┴──────────┬───────┴────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │      BUSINESS LOGIC LAYER          │
                    │         (Services)                 │
                    ├────────────────────────────────────┤
                    │  • EntryService                    │
                    │  • GamificationService             │
                    │  • AIFeedbackService               │
                    │  • ExportService                   │
                    │  • AuthService                     │
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │      DATA ACCESS LAYER             │
                    │     (Models & Schemas)             │
                    ├────────────────────────────────────┤
                    │  • SQLAlchemy ORM Models           │
                    │  • Pydantic Schemas                │
                    │  • Database Session Management     │
                    └─────────────────┬──────────────────┘
                                      │
                    ┌─────────────────▼─────────────────┐
                    │      PERSISTENCE LAYER             │
                    │       (SQLite Database)            │
                    ├────────────────────────────────────┤
                    │  ~/.tracker/tracker.db             │
                    │  • entries                         │
                    │  • users                           │
                    │  • achievements                    │
                    │  • user_stats                      │
                    └────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL INTEGRATIONS                           │
├─────────────┬─────────────┬──────────────┬─────────────┬───────────┤
│   OpenAI    │ Anthropic   │ OpenRouter   │   Local AI  │  Custom   │
│   GPT-4     │  Claude     │  Various     │   Models    │  Frontend │
└─────────────┴─────────────┴──────────────┴─────────────┴───────────┘
```

## Component Details

### CLI Commands Layer
- **Technology**: Click framework
- **Entry Point**: `tracker.cli.main:cli`
- **Files**: `src/tracker/cli/commands/*.py`
- **Features**: 
  - Fast execution
  - Scriptable
  - Composable with Unix tools
  - 15+ commands

### TUI Interface Layer (NEW)
- **Technology**: Textual framework
- **Entry Point**: `tracker tui`
- **Files**: `src/tracker/cli/tui/**/*.py`
- **Screens**:
  1. Main Menu
  2. New Entry (form)
  3. View Entries (table)
  4. Search (search + results)
  5. Statistics (dashboard)
  6. Achievements (progress)
  7. Configuration (settings view)
  8. Export (export options)
  9. Profile (user info)
- **Features**:
  - Full-screen interface
  - Keyboard navigation
  - Real-time validation
  - Visual feedback

### REST API Layer
- **Technology**: FastAPI
- **Entry Point**: `tracker server`
- **Files**: `src/tracker/api/**/*.py`
- **Endpoints**: 
  - Entries CRUD
  - Statistics
  - Achievements
  - Authentication
  - AI feedback
- **Features**:
  - JWT authentication
  - OpenAPI documentation
  - CORS support
  - Async operations

### MCP Server Layer
- **Technology**: Model Context Protocol
- **Entry Point**: `tracker mcp`
- **Files**: `src/tracker/mcp/**/*.py`
- **Purpose**: AI agent integration

### Business Logic Layer
- **Files**: `src/tracker/services/**/*.py`
- **Services**:
  - `EntryService`: CRUD operations for entries
  - `GamificationService`: Achievements, streaks, points
  - `AIFeedbackService`: AI provider integration
  - `ExportService`: CSV/JSON export
  - `AuthService`: User authentication
- **Shared**: Used by ALL interaction layers

### Data Access Layer
- **ORM**: SQLAlchemy 2.0
- **Models**: `src/tracker/core/models.py`
- **Schemas**: `src/tracker/core/schemas.py`
- **Database**: SQLite with Alembic migrations

### Configuration
- **Files**: `src/tracker/config.py`, `.env`
- **Sources**: Environment variables, .env file, defaults
- **Settings**: AI provider, database path, API keys, etc.
- **Shared**: Same config across all modes

## Data Flow Examples

### Creating Entry via TUI
```
User fills form in TUI
    ↓
NewEntryScreen collects data
    ↓
Validates input locally
    ↓
Calls EntryService.create_entry()
    ↓
SQLAlchemy creates Entry model
    ↓
Commits to SQLite database
    ↓
Returns Entry object
    ↓
TUI shows success notification
```

### Creating Entry via CLI
```
User runs: tracker new --income 150
    ↓
Click parses arguments
    ↓
Calls EntryService.create_entry()
    ↓
SQLAlchemy creates Entry model
    ↓
Commits to SQLite database
    ↓
Returns Entry object
    ↓
CLI prints success message
```

### Creating Entry via API
```
Frontend sends POST /api/v1/entries
    ↓
FastAPI validates JWT token
    ↓
Pydantic validates request body
    ↓
Calls EntryService.create_entry()
    ↓
SQLAlchemy creates Entry model
    ↓
Commits to SQLite database
    ↓
Returns Entry object as JSON
    ↓
Frontend receives response
```

## Simultaneous Use

All three modes can run simultaneously:

```
Terminal 1: tracker tui          # Interactive entry creation
Terminal 2: tracker server       # API for custom frontend
Terminal 3: tracker show today   # CLI for quick checks

Browser:    http://localhost:5703/docs  # API documentation
Frontend:   Custom React/Vue app         # Web interface
```

They all share:
- ✅ Same database file
- ✅ Same business logic (services)
- ✅ Same models and schemas
- ✅ Same configuration
- ✅ Immediate consistency

## Technology Stack

### Core
- **Python**: 3.11+
- **Package Manager**: uv (10-100x faster than pip)
- **Build System**: Hatchling

### CLI Layer
- **Click**: 8.1.7+ (command framework)
- **Rich**: 13.7.0+ (terminal formatting)
- **Prompt Toolkit**: 3.0.43+ (interactive prompts)
- **Textual**: 0.40.0+ (TUI framework) ⭐ NEW

### API Layer
- **FastAPI**: 0.109.0+ (web framework)
- **Uvicorn**: 0.27.0+ (ASGI server)
- **Pydantic**: 2.5.3+ (data validation)

### Database
- **SQLAlchemy**: 2.0.25+ (ORM)
- **Alembic**: 1.13.1+ (migrations)
- **SQLite**: 3.x (database)

### AI Integration
- **OpenAI**: 1.10.0+ (GPT models)
- **Anthropic**: 0.18.0+ (Claude models)
- **MCP**: 0.9.0+ (agent protocol)

### Development
- **pytest**: 7.4.4+ (testing)
- **black**: 24.1.0+ (formatting)
- **ruff**: 0.1.14+ (linting)
- **mypy**: 1.8.0+ (type checking)

## Design Principles

1. **Separation of Concerns**
   - UI layers are thin wrappers
   - Business logic in services
   - Data access through ORM

2. **Single Source of Truth**
   - One database for all modes
   - Shared configuration
   - Shared models and schemas

3. **DRY (Don't Repeat Yourself)**
   - Services reused across modes
   - Common validation logic
   - Shared constants and enums

4. **User Choice**
   - Multiple interaction paradigms
   - Use what fits your workflow
   - Switch modes anytime

5. **Extensibility**
   - Easy to add new commands
   - Easy to add new screens
   - Easy to add new endpoints

## Benefits

### For Users
- Choose the mode that fits their workflow
- Consistent data across all modes
- Professional, polished experience
- No vendor lock-in

### For Developers
- Clean architecture
- Testable components
- Type safety with Pydantic and mypy
- Modern Python best practices

### For Operations
- Single codebase to maintain
- Docker support
- Environment-based configuration
- Logging and monitoring ready

## Future Considerations

### Potential Additions
1. **Web Frontend**: React/Vue SPA using REST API
2. **Mobile App**: React Native/Flutter using REST API
3. **Desktop App**: Electron wrapper around TUI
4. **Browser Extension**: Quick entry from anywhere
5. **CLI Plugins**: Extend with custom commands
6. **TUI Plugins**: Add custom screens
7. **API Webhooks**: Integrate with external services

All would use the existing business logic layer!
