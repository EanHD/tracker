# AI Assistant Guidelines for Tracker Project

This document contains guidelines for AI assistants (Claude, ChatGPT, etc.) working on this project.

## Project Organization

### Documentation Structure

**Keep in Root:**
- `README.md` - Main project overview and quick start
- `CHANGELOG.md` - Version history and changes
- `QUICK_REFERENCE.md` - Quick command reference
- Feature-specific guides that users reference:
  - `PHILOSOPHY_ENGINE.md`, `PHILOSOPHY_QUICK_REF.md`
  - `PROFILE_QUICK_REF.md`, `PROFILE_DOCS_INDEX.md`
  - `USER_PROFILE_SYSTEM.md`
  - `TUI_IMPLEMENTATION.md`, `TUI_NARROW_TERMINAL_GUIDE.md`, `TUI_RESPONSIVE_DESIGN.md`

**Archive in `.archive/`:**
- Implementation summaries
- Development session notes
- Commit messages
- Status updates
- Test results
- Temporary exports
- `*_SUMMARY.md`, `*_COMPLETE.md`, `*_FEATURE.md`, etc.

**Keep in `docs/`:**
- User-facing documentation
- Architecture guides
- API documentation
- Deployment guides

### Best Practices

1. **Update, Don't Duplicate**: When documentation needs updates, modify existing files rather than creating new ones.

2. **Stay Organized**: Keep development artifacts in `.archive/` to avoid cluttering the repository.

3. **User-Focused Documentation**: Root level docs should be useful to end users, not just developers.

4. **Efficiency**: Be mindful of token usage when making changes - focus on surgical, precise updates.

5. **Test After Changes**: Always test changes to ensure nothing breaks:
   ```bash
   # Quick validation
   tracker new --help
   tracker tui
   ```

## Common Issues and Solutions

### Money Input Fields
- Default values should be empty string `""` not `"0"`
- Empty input converts to `Decimal("0")` automatically
- This prevents users from typing `$0151` when forgetting to delete the 0

### Text Input Wrapping
- Enable `wrap_lines=True` for multiline prompts
- Prevents word cutting in narrow terminals

### AI Feedback Display
- Use "Tracker" instead of "AI Response" for consistency with chat
- Always provide retry instructions on failure
- Show config check option when generation fails

### Chat Integration
- View/Search entries offer "Continue conversation" option
- Retry command offers chat continuation after successful feedback
- Chat context includes:
  - User profile (nickname, preferred_tone, context_depth, stress_triggers, calming_activities)
  - Recent 7-day activity summary (for standalone chats)
  - Full entry details (for entry-linked chats)
- System prompt identifies as "Tracker" for consistency
- **Note**: UserProfile uses `nickname` not `display_name`
- **Commands**: `exit` to quit, `clear` to clear screen, `transcript` to view history
- User messages now wrapped in panels (consistent with Tracker responses)

### Mobile/Narrow Terminal Support
- TUI automatically adapts to terminal width < 80
- Tables should collapse or hide columns on narrow displays
- Test with: `COLUMNS=60 tracker tui`

## Current Architecture

### Key Components
- `src/tracker/cli/commands/` - CLI command implementations
- `src/tracker/cli/tui/` - Interactive TUI interface
- `src/tracker/cli/ui/` - Shared UI components (prompts, display, console)
- `src/tracker/services/` - Business logic layer
- `src/tracker/core/` - Database models and schemas

### Important Files
- `src/tracker/cli/commands/new.py` - Entry creation logic
- `src/tracker/cli/commands/retry.py` - AI feedback retry
- `src/tracker/cli/ui/prompts.py` - User input handling
- `src/tracker/cli/ui/display.py` - Output formatting
- `src/tracker/cli/tui/app.py` - TUI menu interface

## Recent Updates (October 2025)

1. ✅ Changed money input defaults from "0" to "" 
2. ✅ Added word wrapping for multiline text input
3. ✅ Replaced "AI Response" with "Tracker" in feedback display
4. ✅ Added retry prompt on AI generation failure
5. ✅ Cleaned up development artifacts to `.archive/`
6. ✅ Updated USER_GUIDE.md with TUI mode and retry command
7. ✅ Added "Continue conversation" option after viewing entries in TUI
8. ✅ Added "Continue conversation" option after retry command
9. ✅ Fixed "n" (new chat) error in TUI chat menu
10. ✅ Enhanced chat context with user profile + recent 7-day activity summary
11. ✅ Entry-linked chats now include full entry details in context
12. ✅ Fixed UserProfile attribute error (display_name → nickname)
13. ✅ Fixed profile setup option 4 import path error
14. ✅ Fixed profile setup to call directly (not via CliRunner)
15. ✅ Added user message panels in chat (consistent display)
16. ✅ Added persistent hint in chat ('exit' | 'clear' | 'transcript')
17. ✅ Added transcript viewer for scrollable chat history
18. ✅ Added TUI option 5: Edit Individual Profile Fields
19. ✅ Improved profile setup wizard with confirmation prompts
20. ✅ Enhanced profile update command with field-by-field editing
21. ✅ Unified TUI and CLI profile editing (section → fields)
22. ✅ Added field-by-field editing for Work/Financial/Goals sections
23. ✅ Fixed stress triggers/activities to show current list for editing
24. ✅ Fixed transcript mode formatting (no more ESC codes)
25. ✅ Fixed chat UI - user messages only show once (not persistent)
26. ✅ Made chat interface clean - screen clears between exchanges
27. ✅ Enhanced transcript mode with proper scrolling (uses 'less')

## Testing Checklist

Before considering work complete:

- [ ] Test `tracker new` command (both quick and detailed modes)
- [ ] Test TUI interface: `tracker tui`
- [ ] Verify money inputs don't show "0" by default
- [ ] Check multiline text input wraps properly
- [ ] Confirm AI feedback shows "Tracker" not "AI Response"
- [ ] Test retry command: `tracker retry yesterday`
- [ ] Verify retry offers chat continuation
- [ ] Test "Continue conversation" in TUI view/search
- [ ] Test new chat creation with "n" in TUI chat menu
- [ ] Test profile edit (TUI option 5) - field-by-field updates
- [ ] Test profile setup wizard - typo correction
- [ ] Test `tracker profile update` - field-by-field updates
- [ ] Verify narrow terminal support: `COLUMNS=60 tracker tui`

## Token Budget Awareness

When token budget is limited:
1. Make targeted, surgical changes
2. Avoid reading entire large files unnecessarily
3. Use grep/search to find specific code locations
4. Batch related changes together
5. Trust existing working code - don't refactor unnecessarily
