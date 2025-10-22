# Changelog

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
