# MCP Server Contract

**Protocol**: Model Context Protocol (MCP)  
**Version**: 1.0  
**Transport**: stdio, HTTP  
**Purpose**: Enable AI agents to interact with daily logging data

## Overview

The MCP server exposes daily entry and feedback operations as tools that AI agents can invoke. It provides a standardized interface for external AI systems to:
- Create and retrieve daily entries
- Access historical data for context
- Trigger feedback generation
- Query trends and statistics

## Connection Configuration

### Stdio Transport (Local Development)

```json
{
  "mcpServers": {
    "tracker": {
      "command": "python",
      "args": ["-m", "tracker.mcp.server"],
      "env": {
        "DATABASE_URL": "sqlite:///~/.config/tracker/tracker.db",
        "API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### HTTP Transport (Remote Access)

```json
{
  "mcpServers": {
    "tracker": {
      "url": "http://localhost:8001/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer your-jwt-token"
      }
    }
  }
}
```

## Tools

### create_entry

Create a new daily entry with financial and wellbeing data.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "date": {
      "type": "string",
      "format": "date",
      "description": "Entry date in YYYY-MM-DD format"
    },
    "cash_on_hand": {
      "type": "number",
      "description": "Liquid cash available"
    },
    "bank_balance": {
      "type": "number",
      "description": "Checking/current account balance"
    },
    "income_today": {
      "type": "number",
      "description": "Earnings for this day"
    },
    "bills_due_today": {
      "type": "number",
      "description": "Payments due or made"
    },
    "debts_total": {
      "type": "number",
      "description": "Total outstanding debt"
    },
    "hours_worked": {
      "type": "number",
      "minimum": 0,
      "maximum": 24,
      "description": "Job hours worked"
    },
    "side_income": {
      "type": "number",
      "description": "Gig or side work earnings"
    },
    "food_spent": {
      "type": "number",
      "description": "Food and grocery spending"
    },
    "gas_spent": {
      "type": "number",
      "description": "Transportation/gas cost"
    },
    "notes": {
      "type": "string",
      "description": "Free-form notes about the day"
    },
    "stress_level": {
      "type": "integer",
      "minimum": 1,
      "maximum": 10,
      "description": "Mental load rating (1-10)"
    },
    "priority": {
      "type": "string",
      "description": "What's top of mind today"
    }
  },
  "required": ["date", "stress_level"]
}
```

**Example Call**:
```json
{
  "tool": "create_entry",
  "arguments": {
    "date": "2025-10-21",
    "cash_on_hand": 142.35,
    "bank_balance": -53.21,
    "income_today": 420.00,
    "bills_due_today": 275.00,
    "debts_total": 18600.00,
    "hours_worked": 8.0,
    "side_income": 80.00,
    "food_spent": 22.17,
    "gas_spent": 38.55,
    "notes": "Paid Snap-On min. late. Worked overtime.",
    "stress_level": 6,
    "priority": "clear card debt"
  }
}
```

**Response**:
```json
{
  "success": true,
  "entry_id": 123,
  "date": "2025-10-21",
  "feedback_status": "pending",
  "message": "Entry created successfully. Generating motivational feedback..."
}
```

---

### get_entry

Retrieve a specific entry by date.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "date": {
      "type": "string",
      "format": "date",
      "description": "Entry date in YYYY-MM-DD format"
    }
  },
  "required": ["date"]
}
```

**Example Call**:
```json
{
  "tool": "get_entry",
  "arguments": {
    "date": "2025-10-21"
  }
}
```

**Response**:
```json
{
  "id": 123,
  "date": "2025-10-21",
  "cash_on_hand": 142.35,
  "bank_balance": -53.21,
  "income_today": 420.00,
  "bills_due_today": 275.00,
  "debts_total": 18600.00,
  "hours_worked": 8.0,
  "side_income": 80.00,
  "food_spent": 22.17,
  "gas_spent": 38.55,
  "notes": "Paid Snap-On min. late. Worked overtime.",
  "stress_level": 6,
  "priority": "clear card debt",
  "created_at": "2025-10-21T18:30:00Z",
  "feedback": {
    "content": "You're making incredible progress...",
    "status": "completed"
  }
}
```

---

### list_entries

List entries with optional date range filtering.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "start_date": {
      "type": "string",
      "format": "date",
      "description": "Filter from this date (inclusive)"
    },
    "end_date": {
      "type": "string",
      "format": "date",
      "description": "Filter until this date (inclusive)"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 30,
      "description": "Number of entries to return"
    }
  }
}
```

**Example Call**:
```json
{
  "tool": "list_entries",
  "arguments": {
    "start_date": "2025-10-01",
    "end_date": "2025-10-21",
    "limit": 10
  }
}
```

**Response**:
```json
{
  "entries": [
    {
      "date": "2025-10-21",
      "stress_level": 6,
      "income_today": 420.00,
      "priority": "clear card debt",
      "has_feedback": true
    },
    {
      "date": "2025-10-20",
      "stress_level": 7,
      "income_today": 380.00,
      "priority": "catch up on bills",
      "has_feedback": true
    }
  ],
  "total": 21
}
```

---

### get_trends

Get aggregate statistics and trends for a date range.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "start_date": {
      "type": "string",
      "format": "date",
      "description": "Start of analysis period"
    },
    "end_date": {
      "type": "string",
      "format": "date",
      "description": "End of analysis period"
    }
  },
  "required": ["start_date", "end_date"]
}
```

**Example Call**:
```json
{
  "tool": "get_trends",
  "arguments": {
    "start_date": "2025-10-01",
    "end_date": "2025-10-21"
  }
}
```

**Response**:
```json
{
  "period": {
    "start_date": "2025-10-01",
    "end_date": "2025-10-21",
    "days_logged": 21
  },
  "financials": {
    "total_income": 8820.00,
    "total_bills": 5775.00,
    "avg_daily_income": 420.00,
    "debt_change": -200.00
  },
  "wellbeing": {
    "avg_stress_level": 5.8,
    "stress_trend": "decreasing",
    "avg_hours_worked": 8.2
  },
  "insights": [
    "Stress levels trending down over past week",
    "Income stable, averaging $420/day",
    "Debt reduced by $200 in this period"
  ]
}
```

---

### generate_feedback

Explicitly trigger AI feedback generation for an entry.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "date": {
      "type": "string",
      "format": "date",
      "description": "Entry date to generate feedback for"
    },
    "regenerate": {
      "type": "boolean",
      "default": false,
      "description": "Force regeneration if feedback already exists"
    },
    "custom_prompt": {
      "type": "string",
      "description": "Optional custom instructions for feedback generation"
    }
  },
  "required": ["date"]
}
```

**Example Call**:
```json
{
  "tool": "generate_feedback",
  "arguments": {
    "date": "2025-10-21",
    "regenerate": false,
    "custom_prompt": "Focus on acknowledging the overtime work"
  }
}
```

**Response**:
```json
{
  "feedback_id": 456,
  "status": "pending",
  "message": "Feedback generation started",
  "estimated_time": "5-10 seconds"
}
```

---

### search_entries

Full-text search across entry notes.

**Input Schema**:
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query (searches notes field)"
    },
    "limit": {
      "type": "integer",
      "minimum": 1,
      "maximum": 100,
      "default": 20
    }
  },
  "required": ["query"]
}
```

**Example Call**:
```json
{
  "tool": "search_entries",
  "arguments": {
    "query": "overtime",
    "limit": 10
  }
}
```

**Response**:
```json
{
  "results": [
    {
      "date": "2025-10-21",
      "notes": "Paid Snap-On min. late. Worked overtime.",
      "stress_level": 6,
      "relevance_score": 0.95
    },
    {
      "date": "2025-10-15",
      "notes": "Double shift, overtime pay will help with bills.",
      "stress_level": 7,
      "relevance_score": 0.88
    }
  ],
  "total": 2
}
```

---

## Resources

MCP resources provide read-only access to entry data for AI context building.

### entry://date/{date}

Access a specific entry as an MCP resource.

**URI Template**: `entry://date/2025-10-21`

**Resource Content**:
```json
{
  "uri": "entry://date/2025-10-21",
  "mimeType": "application/json",
  "content": {
    "date": "2025-10-21",
    "financials": {
      "cash_on_hand": 142.35,
      "bank_balance": -53.21,
      "income_today": 420.00,
      "bills_due_today": 275.00,
      "debts_total": 18600.00,
      "side_income": 80.00,
      "food_spent": 22.17,
      "gas_spent": 38.55
    },
    "work": {
      "hours_worked": 8.0
    },
    "wellbeing": {
      "stress_level": 6,
      "priority": "clear card debt",
      "notes": "Paid Snap-On min. late. Worked overtime."
    }
  }
}
```

---

### entry://history/{start}/{end}

Access a range of entries as an MCP resource.

**URI Template**: `entry://history/2025-10-01/2025-10-21`

**Resource Content**: Array of entry objects

---

## Prompts

MCP prompts provide reusable prompt templates for AI interactions.

### analyze_financial_progress

Generate insights about financial progress over time.

**Prompt Template**:
```
Analyze the user's financial progress from {start_date} to {end_date}.

Context:
- Total income: ${total_income}
- Total expenses: ${total_expenses}
- Debt change: ${debt_change}
- Average stress level: {avg_stress}

Provide:
1. Assessment of financial trajectory
2. Stress pattern analysis
3. Actionable suggestions for improvement
4. Encouraging observations about progress
```

---

### motivational_feedback

Generate motivational feedback for a single entry.

**Prompt Template**:
```
Generate supportive, empathetic motivational feedback for this daily entry:

Date: {date}
Financial snapshot:
  - Cash on hand: ${cash_on_hand}
  - Bank balance: ${bank_balance}
  - Income: ${income_today}
  - Bills: ${bills_due_today}
  - Total debt: ${debts_total}

Work: {hours_worked} hours ({side_income > 0 ? "including side income" : ""})
Spending: Food ${food_spent}, Gas ${gas_spent}
Stress level: {stress_level}/10
Priority: {priority}
Notes: {notes}

Guidelines:
- Acknowledge challenges without toxic positivity
- Celebrate wins, even small ones
- Provide perspective on progress
- Keep tone warm, supportive, non-judgmental
- Focus on effort and resilience, not outcomes
```

---

## Authentication

### API Key Authentication

For stdio transport, set `API_KEY` environment variable:
```bash
export API_KEY=your-api-key-here
```

### JWT Token Authentication

For HTTP transport, include JWT token in headers:
```json
{
  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Generate tokens via CLI:
```bash
tracker config generate-token --scopes entries:read,entries:write
```

---

## Error Handling

MCP server returns standard MCP error responses:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "No entry found for date 2025-10-21"
  }
}
```

**Error Codes**:
- `INVALID_PARAMS`: Tool called with invalid parameters
- `RESOURCE_NOT_FOUND`: Requested entry doesn't exist
- `DUPLICATE_RESOURCE`: Entry already exists for date
- `SERVICE_ERROR`: Internal server error
- `UNAUTHORIZED`: Authentication failed

---

## Usage Examples

### Claude Desktop Configuration

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tracker": {
      "command": "python",
      "args": ["-m", "tracker.mcp.server"],
      "env": {
        "DATABASE_URL": "sqlite:///Users/you/.config/tracker/tracker.db"
      }
    }
  }
}
```

### Agent Workflow Example

```
User: "Log today's entry: worked 9 hours, made $450, spent $30 on food. Stress is 5/10."

Agent: [calls create_entry tool]
{
  "date": "2025-10-21",
  "hours_worked": 9.0,
  "income_today": 450.00,
  "food_spent": 30.00,
  "stress_level": 5
}

Agent: "Entry logged! Generating motivational feedback..."
[feedback generates asynchronously]

Agent: "I've logged your entry for today. You worked 9 hours and earned $450 - that's great! 
Your stress level of 5/10 is moderate. Would you like to see how this compares to recent days?"

User: "Yes, show me the past week."

Agent: [calls get_trends tool]
{
  "start_date": "2025-10-15",
  "end_date": "2025-10-21"
}

Agent: [displays trends with insights]
```

---

## Performance Considerations

- **Tool execution time**: <100ms for entry operations, <10s for AI feedback
- **Resource caching**: Frequently accessed entries cached for 5 minutes
- **Rate limiting**: 10 feedback generations per hour per user
- **Concurrent requests**: MCP server handles one request at a time per session
