# Chat Feature Documentation

## Overview
The Tracker app now includes a comprehensive AI chat feature that allows you to have conversations with AI about your finances, wellbeing, and daily reflections.

## Key Features

### 1. **Two Types of Chats**
- **Standalone Conversations**: General chats for venting, brainstorming, or discussing anything
- **Entry-Linked Chats**: Conversations tied to specific journal entries with full context

### 2. **Context-Aware AI**
The AI assistant has access to:
- **User Profile**: Communication style, priorities, stress triggers
- **Journal Entry Data** (for entry-linked chats): Income, expenses, hours worked, stress levels, notes
- **Conversation History**: Full context of the ongoing chat

### 3. **Clean Organization**
- Human-readable titles for easy identification
- List view showing chat type, message count, and last updated time
- Filter chats by type (standalone vs entry-linked)

## CLI Commands

### Create a New Chat
```bash
# Start a standalone conversation
tracker chat new

# Create a chat linked to a specific entry
tracker chat new --entry-id 123
```

### List All Chats
```bash
# Show all chats
tracker chat list

# Show only standalone chats
tracker chat list --standalone

# Show only entry-linked chats
tracker chat list --entry-linked
```

### Open an Existing Chat
```bash
tracker chat open <chat_id>
```

### Manage Chats
```bash
# Rename a chat
tracker chat rename <chat_id>

# Delete a chat
tracker chat delete <chat_id>
```

## Chat Interface

When in a chat session:
- Type your message and press Enter to send
- Type `exit` or `quit` to leave the chat
- Type `clear` to clear the screen
- Press `Ctrl+C` to exit

All messages are automatically saved to the database.

## Example Usage

### Starting a General Conversation
```bash
$ tracker chat new
Chat title (General Conversation): Financial Planning
💬 New Chat: Financial Planning
Chat ID: 1
💬 You: I'm worried about my spending habits
```

### Chatting About a Specific Entry
```bash
$ tracker chat new --entry-id 5
💬 Chat for Entry #5
💬 You: Why was my stress so high on this day?
# AI responds with insights based on that day's entry
```

### Viewing Your Chats
```bash
$ tracker chat list
💬 Your Chats
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Title                ┃ Type          ┃ Messages ┃ Last Updated     ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ 2  │ Chat: October 21     │ 📝 Entry #1   │ 3        │ 2025-10-23 00:06 │
│ 1  │ Financial Planning   │ 💭 Standalone │ 5        │ 2025-10-23 00:04 │
└────┴──────────────────────┴───────────────┴──────────┴──────────────────┘
```

## Technical Details

### Database Models
- **Chat**: Stores chat metadata (title, timestamps, entry link)
- **ChatMessage**: Individual messages with role (user/assistant/system) and content

### AI Provider Support
Works with all supported AI providers:
- **Local**: Ollama, LM Studio, llama.cpp (perfect for testing)
- **OpenAI**: GPT models
- **Anthropic**: Claude models
- **OpenRouter**: 100+ models via unified API

### Privacy
- All chat messages are stored locally in your SQLite database
- Entry-linked chats automatically pull relevant context without exposing unnecessary data
- Only the current conversation context is sent to the AI

## Use Cases

1. **Financial Counseling**: "Help me create a budget for next month"
2. **Stress Management**: "Why do I feel so stressed when my spending increases?"
3. **Goal Planning**: "What steps should I take to reduce my debt?"
4. **Entry Reflection**: "Looking at my entry from last Tuesday, what patterns do you notice?"
5. **General Venting**: "I'm frustrated with my job situation"

## Tips

- **Be specific**: The more detail you provide, the better the AI can help
- **Use entry-linked chats**: When discussing a specific day, link the chat to that entry for full context
- **Review your chats**: Use `tracker chat list` to see your conversation history
- **Rename chats**: Give chats meaningful names to stay organized
- **Clean up**: Delete old chats you no longer need

## Future Enhancements

Planned features:
- Export chat conversations
- Search within chats
- Chat analytics (most discussed topics, sentiment tracking)
- Voice input support
- Multi-turn reasoning for complex financial planning

## Testing with Local AI

To test without using API tokens:
1. Install Ollama: `https://ollama.ai`
2. Pull a model: `ollama pull llama3.2:3b`
3. Configure tracker: `tracker config setup` (select "local")
4. Start chatting: `tracker chat new`

The local models work great for testing and provide fast responses!
