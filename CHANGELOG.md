# Changelog

## [0.2.0] - 2025-10-25

### Added
- **AI Conversations**: Dedicated `tracker chat` command group plus TUI chat menu with transcript viewer and context-rich conversations.
- **Profile Enhancements**: Field-by-field editing, confirmation flow, and shared logic between CLI and TUI for consistent updates.
- **Philosophy Engine**: Context service and reference docs that bring curated financial principles into AI guidance.
- **Documentation Set**: Comprehensive reference guides (`PHILOSOPHY_*`, `PROFILE_*`, `USER_PROFILE_SYSTEM.md`, `TUI_*`) now tracked and curated for contributors.

### Changed
- **TUI Experience**: Chats, statistics, achievements, configuration, export, and profile screens now use shared console helpers; chat screen preserves history while the AI responds.
- **CLI Polishing**: Rich spinners during AI calls, consistent emoji/icon usage, and accessible console configuration across commands.
- **Quick Reference**: Expanded with chat workflow cheatsheet and updated recommendations for newcomers.
- **README**: Expanded Quick Start with chat usage, clarified mode guidance, and highlighted multi-provider AI setup.

### Fixed
- Ensured TUI chat prompt no longer flickers when waiting for responses.
- Removed stray cached bytecode, export artifacts, and other local-only files from the repository view.
- Normalized money input defaults and wrapped multiline prompts for better terminal readability.

## [0.1.0] - 2024-10-22

### Added
- **Interactive TUI Mode**: Full-screen terminal interface using Textual
  - 8 functional screens (New Entry, View Entries, Search, Statistics, Achievements, Configuration, Export, Profile)
  - Keyboard navigation with arrow keys and hotkeys
  - Real-time form validation
  - Beautiful, consistent styling
- **Default TUI Launch**: Running `tracker` without arguments now launches the interactive TUI
- **Multi-Mode Architecture**: Three ways to interact with the application
  - CLI commands for quick operations and automation
  - Interactive TUI for visual, menu-driven experience
  - REST API server for custom frontends
- **Comprehensive Documentation**:
  - TUI usage guide
  - Mode comparison guide
  - Architecture documentation
  - Quick reference card

### Changed
- `tracker` command now launches TUI by default (was just help text)
- `tracker tui` command still available for explicit TUI launch
- Updated README with multi-mode usage examples

### Technical
- Added Textual dependency (>=0.40.0)
- All modes share same database and business logic
- Can run CLI, TUI, and server simultaneously

### Documentation
- docs/TUI_MODE.md - Complete TUI usage guide
- docs/USAGE_MODES.md - Mode comparison and recommendations
- docs/ARCHITECTURE.md - System architecture
- QUICK_REFERENCE.md - Quick reference card
