# MCP Server Integration Guide

The Tracker MCP (Model Context Protocol) server enables AI agents like Claude Desktop to interact with your daily logging data. This allows for natural language entry creation, querying history, and generating insights.

## Overview

The MCP server exposes:
- **6 Tools**: Create entries, retrieve data, search, and generate feedback
- **2 Resources**: Access specific entries or date ranges
- **2 Prompts**: Pre-built templates for financial analysis and motivational feedback

## Quick Start

### 1. Start the MCP Server

```bash
tracker mcp serve
```

This starts the server in stdio mode, ready for Claude Desktop to connect.

### 2. Configure Claude Desktop

Add this to your Claude Desktop configuration:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "tracker": {
      "command": "python",
      "args": ["-m", "tracker.mcp.server"],
      "env": {
        "DATABASE_URL": "sqlite:///~/.config/tracker/tracker.db"
      }
    }
  }
}
```

**Important**: Replace `~` with your actual home directory path:
- macOS/Linux: `/Users/yourname` or `/home/yourname`
- Windows: `C:\\Users\\yourname`

### 3. Restart Claude Desktop

After adding the configuration, restart Claude Desktop to load the MCP server.

### 4. Test the Connection

In Claude Desktop, try:

```
Create a new entry for today:
- I worked 8 hours
- Made $420
- Spent $25 on food
- Stress level is 6/10
- Priority: pay off credit card
```

Claude will use the `create_entry` tool to save your data and automatically generate motivational feedback.

## Available Tools

### 1. create_entry

Create a new daily entry with financial and wellbeing data.

**Example prompts:**
- "Log today's entry: worked 9 hours, earned $450, spent $30 on food, stress is 5/10"
- "Create an entry for yesterday with income $380 and bills $200"

### 2. get_entry

Retrieve a specific entry by date.

**Example prompts:**
- "Show me my entry for October 15th"
- "What did I log yesterday?"

### 3. list_entries

List entries with optional date filtering.

**Example prompts:**
- "Show me all entries from last week"
- "List my entries for October"
- "What are my last 10 entries?"

### 4. get_trends

Get aggregate statistics and trends for a date range.

**Example prompts:**
- "Analyze my financial trends for the past month"
- "How has my stress level changed over the last two weeks?"
- "Show me my income trends for October"

### 5. generate_feedback

Explicitly trigger AI feedback generation for an entry.

**Example prompts:**
- "Generate feedback for today's entry"
- "Regenerate motivational feedback for October 15th"

### 6. search_entries

Full-text search across entry notes.

**Example prompts:**
- "Find entries where I mentioned overtime"
- "Search for days when I talked about debt"

## Resources

Resources provide read-only access to entry data for AI context building.

### entry://date/{date}

Access a specific entry as structured data.

**Example**: `entry://date/2025-10-21`

### entry://history/{start}/{end}

Access a range of entries.

**Example**: `entry://history/2025-10-01/2025-10-31`

## Prompts

Pre-built prompt templates for common AI interactions.

### analyze_financial_progress

Generate insights about financial progress over time.

**Usage in Claude**:
```
Analyze my financial progress from October 1st to October 21st
```

### motivational_feedback

Generate motivational feedback for a specific entry.

**Usage in Claude**:
```
Give me motivational feedback for my entry on October 15th
```

## Usage Examples

### Daily Logging Workflow

```
You: "Log today: worked 8 hours, earned $420, paid $275 in bills, 
      spent $22 on food and $38 on gas. Stress is 6/10. 
      Priority: clear credit card debt."

Claude: [Creates entry and generates feedback]
        "Entry logged for today! You earned $420 and paid $275 in bills - 
         that's $145 net positive. Your stress level of 6/10 is moderate..."
```

### Trend Analysis

```
You: "How have I been doing financially this month?"

Claude: [Calls get_trends tool]
        "Looking at your October data:
         - Total income: $8,820
         - Total bills: $5,775  
         - Net: +$3,045
         - Your stress levels are trending down from 7.2 to 5.8
         - You're making steady progress on debt reduction!"
```

### Historical Search

```
You: "Find all the days I worked overtime"

Claude: [Calls search_entries tool]
        "I found 3 entries mentioning overtime:
         - Oct 21: Worked overtime, earned extra $80
         - Oct 15: Double shift, overtime pay helps with bills
         - Oct 8: Overtime to catch up on expenses"
```

## Troubleshooting

### Server Won't Start

**Issue**: `ImportError: No module named 'mcp'`  
**Solution**: Ensure MCP SDK is installed:
```bash
uv pip install mcp>=0.9.0
```

**Issue**: Database connection error  
**Solution**: Verify DATABASE_URL in config points to existing database:
```bash
ls ~/.config/tracker/tracker.db
```

If database doesn't exist, initialize it:
```bash
tracker init
```

### Claude Desktop Not Connecting

**Issue**: MCP server not appearing in Claude Desktop  
**Solution**: 
1. Verify config file path is correct for your OS
2. Ensure JSON syntax is valid (no trailing commas)
3. Restart Claude Desktop completely
4. Check Claude Desktop logs for errors

**Issue**: Permission denied errors  
**Solution**: Ensure Python and tracker are in system PATH:
```bash
which python
which tracker
```

### Tools Not Working

**Issue**: "No entry found for date"  
**Solution**: The date may not exist in your database. List entries first:
```
You: "What entries do I have?"
```

**Issue**: Feedback generation fails  
**Solution**: Ensure AI provider is configured:
```bash
tracker config set-provider
```

## Advanced: HTTP Transport (Remote Access)

For remote AI agent access over HTTP (not yet implemented):

```bash
tracker mcp serve --http --host 0.0.0.0 --port 8001
```

This would enable:
- Web-based AI applications
- Multi-user access
- Cloud deployment

**Note**: HTTP transport is planned for a future release. For now, use stdio mode with Claude Desktop.

## Security Considerations

### Local stdio Mode (Current)

- MCP server runs as local process
- No network exposure
- Inherits user permissions
- Database access controlled by file permissions

### Best Practices

1. **Protect your config**: `claude_desktop_config.json` contains database path
2. **Use encryption**: Tracker encrypts sensitive fields (notes, priority)
3. **Regular backups**: MCP operations modify database directly
4. **API keys**: Store AI provider keys in keyring, not config files

## Performance

- **Tool execution time**: <100ms for entry operations
- **Feedback generation**: 5-10 seconds (depends on AI provider)
- **Resource caching**: Frequently accessed entries cached for 5 minutes
- **Rate limiting**: 10 feedback generations per hour recommended

## Next Steps

- Try the example prompts in Claude Desktop
- Create custom workflows for your logging routine
- Explore trend analysis for financial insights
- Use search to find patterns in your entries

For more details, see the [MCP Specification](../specs/001-daily-logging-ai/contracts/mcp-spec.md).
