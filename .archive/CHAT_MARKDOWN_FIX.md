# Chat Markdown Rendering Fix

## Summary
Fixed chat messages to properly render Markdown formatting. Previously, **bold** and *italic* text was showing as raw markdown (`**bold**`) instead of being formatted.

## Issues Fixed

### 1. Markdown Not Rendering
**Problem**: Chat messages displayed raw markdown syntax
- `**bold**` showed as `**bold**` instead of **bold**
- `*italic*` showed as `*italic*` instead of *italic*
- Lists weren't formatted properly

**Solution**: Wrapped message content in `rich.markdown.Markdown()` before displaying

### 2. `Prompt.confirm` Error
**Problem**: Code used `Prompt.confirm()` which doesn't exist
**Solution**: Changed to `Confirm.ask()` (correct Rich API)

### 3. UserProfile.priorities AttributeError
**Problem**: Chat service tried to access non-existent `priorities` field on UserProfile
**Solution**: Removed the reference from `chat.py` (field doesn't exist in model)

## Changes Made

### File: `src/tracker/cli/tui/app.py`

#### Message History Display
```python
from rich.markdown import Markdown

# Before
console.print(Panel(
    msg.content,  # Plain text
    title=f"👤 You",
    ...
))

# After  
md = Markdown(msg.content)  # Parse markdown
console.print(Panel(
    md,  # Rendered markdown
    title=f"👤 You",
    ...
))
```

#### New Message Responses
```python
# Before
console.print(Panel(
    response,  # Plain text response
    ...
))

# After
md = Markdown(response)  # Parse markdown
console.print(Panel(
    md,  # Rendered markdown
    ...
))
```

#### Error Handling Fix
```python
# Before
if not Prompt.confirm("Try again?", default=True):

# After
if not Confirm.ask("Try again?", default=True):
```

### File: `src/tracker/services/chat.py`

Removed non-existent field reference:
```python
# Removed these lines:
if profile.priorities:
    context_parts.append(f"Priorities: {profile.priorities}")
```

## Markdown Support

Now supports all standard Markdown formatting:

### Text Formatting
- **Bold**: `**text**` or `__text__`
- *Italic*: `*text*` or `_text_`
- `Code`: `` `code` ``
- ~~Strikethrough~~: `~~text~~`

### Lists
```markdown
- Unordered item 1
- Unordered item 2

1. Ordered item 1
2. Ordered item 2
```

### Headings
```markdown
# H1
## H2
### H3
```

### Blockquotes
```markdown
> This is a quote
```

### Code Blocks
````markdown
```python
def hello():
    print("Hello!")
```
````

## Testing Results

✅ User messages render markdown correctly  
✅ AI responses render markdown correctly  
✅ Message history displays formatted  
✅ New messages display formatted  
✅ Lists render with proper bullets/numbers  
✅ Bold and italic text renders properly  
✅ Code blocks render with syntax highlighting  
✅ No more AttributeErrors  

## Examples

### Before Fix
```
**Bold Text Tip**: Focus on one aspect

- Item 1
- Item 2
```

### After Fix
**Bold Text Tip**: Focus on one aspect

• Item 1
• Item 2

## Benefits

1. **Better Readability**: Formatted text is easier to read
2. **Rich Formatting**: AI can use emphasis, lists, code examples
3. **Professional Look**: Messages look polished and organized
4. **Consistent Experience**: Matches how AI feedback displays elsewhere in app

## Usage

Just type markdown in your chat messages:

```
Can you give me **3 important tips** with a list?

I need help with:
- Budgeting
- Saving money
- Managing debt
```

Both your messages and AI responses will render with proper formatting!

## Notes

- Markdown rendering happens automatically
- No configuration needed
- Works in both TUI and CLI chat modes
- Existing chat history will render with formatting when reopened
- All Rich Markdown features are supported
