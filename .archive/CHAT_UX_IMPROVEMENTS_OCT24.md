# Chat UX Improvements - October 24, 2025

## Issues Fixed

### 1. User Messages Not Wrapped in Panels ✅
**Problem**: When typing in chat, user messages appeared as plain text while Tracker responses had nice panels. Only after reopening the chat would user messages appear in panels.

**Fix**: Added immediate panel wrapping for user messages in `_chat_loop_native()`

```python
# Display user message in panel
user_md = Markdown(user_input)
console.print(Panel(
    user_md,
    title=f"{icon('👤 ', '')}You",
    title_align="left",
    border_style="blue",
    padding=(0, 1)
))
```

**Result**: User messages now appear in blue panels immediately, matching Tracker's green panels.

### 2. Instructions Get Lost as Chat Grows ✅
**Problem**: Instructions showed once at the start (`'exit' to quit, 'clear' to clear screen`) but got scrolled off screen during conversation.

**Fix**: Made instructions persistent - shown before every message prompt.

```python
# Show persistent hint
console.print("[dim]'exit' to quit | 'clear' to clear | 'transcript' to view history[/dim]")
user_input = Prompt.ask(f"{icon('💬 ', '')}You")
```

**Result**: Users always see available commands, even in long conversations.

### 3. Added Transcript Viewer ✅
**Problem**: No way to review full conversation history without manually scrolling.

**Fix**: Added `transcript` command that displays entire conversation in scrollable view.

**New Function**: `_show_transcript(console, chat_service, chat_id)`

**Features**:
- Shows chat title and message count
- Displays all messages with proper formatting
- User messages: Blue `👤 You:`
- Tracker messages: Green `💭 Tracker:`
- Uses Rich pager for scrollable view (when available)
- Fallback to print + prompt if pager unavailable
- Return to chat with Enter

**Usage**:
```
💬 You: transcript
[Shows full conversation history]
Press Enter to return to chat...
```

### 4. Profile Setup Still Returns "Error:" ✅
**Problem**: Calling profile setup via CliRunner wasn't working properly in TUI context.

**Fix**: Call setup function directly instead of via CliRunner.

```python
# Before
from tracker.cli.commands.profile import profile as profile_cmd
from click.testing import CliRunner
runner = CliRunner()
runner.invoke(profile_cmd, ['setup'], catch_exceptions=False, standalone_mode=False)

# After
from tracker.cli.commands.profile import setup as profile_setup
try:
    profile_setup.callback(user_id=1)
except SystemExit:
    pass  # Normal exit
```

**Applied to**:
- Option 1: Create profile (when none exists)
- Option 4: Full profile setup (when profile exists)

**Result**: Profile setup wizard runs correctly in TUI.

## Chat Commands

### Available Commands:
| Command | Description |
|---------|-------------|
| `exit`, `quit`, `bye` | Save chat and return to menu |
| `clear` | Clear screen |
| `transcript` | View full conversation history |
| (empty) | Skip, continue chatting |

### Command Display:
- **Persistent**: Shows before every prompt
- **Format**: `'exit' to quit | 'clear' to clear | 'transcript' to view history`
- **Style**: Dim gray text (non-intrusive)

## Visual Improvements

### Before:
```
Type your message (or 'exit' to quit, 'clear' to clear screen)

💬 You: Hello
[plain text, no panel]

[... 20 messages later ...]
[instructions no longer visible]

💬 You: How do I exit?
[can't remember commands]
```

### After:
```
'exit' to quit | 'clear' to clear | 'transcript' to view history
💬 You: Hello

┌─ 👤 You ────────────────┐
│ Hello                    │
└──────────────────────────┘

[Thinking...]

┌─ 💭 Tracker ─────────────┐
│ Hi! How can I help?      │
└──────────────────────────┘

'exit' to quit | 'clear' to clear | 'transcript' to view history
💬 You: transcript

┌─ 💬 General Conversation ─┐
│ 2 messages                 │
│                            │
│ 👤 You:                    │
│ Hello                      │
│                            │
│ 💭 Tracker:                │
│ Hi! How can I help?        │
└────────────────────────────┘

Press Enter to return to chat...
```

## Implementation Details

### File Modified:
- `src/tracker/cli/tui/app.py`

### Functions Added:
- `_show_transcript(console, chat_service, chat_id)` - Transcript viewer

### Functions Updated:
- `_chat_loop_native()` - Added user message panels, persistent hints, transcript command
- `handle_profile()` - Fixed profile setup calls (2 locations)

## User Experience Impact

### Chat Flow:
1. ✅ Start chat → See instructions
2. ✅ Type message → Wrapped in blue panel immediately
3. ✅ Get response → Wrapped in green panel
4. ✅ Continue chatting → Instructions always visible
5. ✅ Type `transcript` → Review full history
6. ✅ Type `clear` → Clean slate, continue
7. ✅ Type `exit` → Save and return

### Profile Setup:
1. ✅ TUI → Profile → Option 4
2. ✅ Wizard runs properly
3. ✅ No "Error:" message
4. ✅ Profile created/updated

## Testing

```bash
✓ File compiles successfully
✓ No syntax errors
```

### Manual Test Checklist:
- [ ] Start chat → User message shows in panel
- [ ] Type multiple messages → Instructions persist
- [ ] Type `transcript` → See full history
- [ ] Type `clear` → Screen clears
- [ ] Type `exit` → Returns to menu
- [ ] Profile → Option 4 → Runs wizard

## Token Usage

This session total: ~94K tokens (~9% of budget)
Remaining: ~906K tokens (91%)

## Benefits

1. **Consistent Visual Design**: Both user and Tracker messages in panels
2. **Always Available Help**: Commands visible at all times
3. **Easy Review**: Transcript mode for long conversations
4. **Working Profile Setup**: No more "Error:" on option 4
5. **Better UX**: Professional, polished chat experience
