"""
MCP Server for Daily Logging Tracker

Provides MCP tools, resources, and prompts for AI agent integration.
Supports both stdio (for local development with Claude Desktop) and HTTP transports.
"""

import logging
import os
from datetime import date, datetime, timedelta
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource, Prompt, PromptMessage
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from tracker.core.database import Base
from tracker.core.models import DailyEntry, User
from tracker.core.schemas import EntryCreate
from tracker.services.entry_service import EntryService
from tracker.services.feedback_service import FeedbackService
from tracker.services.history_service import HistoryService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp_server = Server("tracker")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///~/.config/tracker/tracker.db")
# Expand user home directory
if DATABASE_URL.startswith("sqlite:///~/"):
    home = os.path.expanduser("~")
    DATABASE_URL = DATABASE_URL.replace("sqlite:///~/", f"sqlite:///{home}/")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Will be closed by caller


def get_or_create_user(db: Session) -> User:
    """
    Get the default user for MCP operations.
    For MCP, we use a system user or the first available user.
    """
    user = db.query(User).first()
    if not user:
        # Create a default MCP user
        from tracker.core.auth import get_password_hash
        user = User(
            username="mcp_user",
            email="mcp@localhost",
            hashed_password=get_password_hash("mcp_default_password"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# Tool Definitions

@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="create_entry",
            description="Create a new daily entry with financial and wellbeing data",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "format": "date",
                        "description": "Entry date in YYYY-MM-DD format",
                    },
                    "cash_on_hand": {
                        "type": "number",
                        "description": "Liquid cash available",
                    },
                    "bank_balance": {
                        "type": "number",
                        "description": "Checking/current account balance",
                    },
                    "income_today": {
                        "type": "number",
                        "description": "Earnings for this day",
                    },
                    "bills_due_today": {
                        "type": "number",
                        "description": "Payments due or made",
                    },
                    "debts_total": {
                        "type": "number",
                        "description": "Total outstanding debt",
                    },
                    "hours_worked": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 24,
                        "description": "Job hours worked",
                    },
                    "side_income": {
                        "type": "number",
                        "description": "Gig or side work earnings",
                    },
                    "food_spent": {
                        "type": "number",
                        "description": "Food and grocery spending",
                    },
                    "gas_spent": {
                        "type": "number",
                        "description": "Transportation/gas cost",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Free-form notes about the day",
                    },
                    "stress_level": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Mental load rating (1-10)",
                    },
                    "priority": {
                        "type": "string",
                        "description": "What's top of mind today",
                    },
                },
                "required": ["date", "stress_level"],
            },
        ),
        Tool(
            name="get_entry",
            description="Retrieve a specific entry by date",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "format": "date",
                        "description": "Entry date in YYYY-MM-DD format",
                    },
                },
                "required": ["date"],
            },
        ),
        Tool(
            name="list_entries",
            description="List entries with optional date range filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Filter from this date (inclusive)",
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Filter until this date (inclusive)",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 30,
                        "description": "Number of entries to return",
                    },
                },
            },
        ),
        Tool(
            name="get_trends",
            description="Get aggregate statistics and trends for a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Start of analysis period",
                    },
                    "end_date": {
                        "type": "string",
                        "format": "date",
                        "description": "End of analysis period",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        ),
        Tool(
            name="generate_feedback",
            description="Explicitly trigger AI feedback generation for an entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "format": "date",
                        "description": "Entry date to generate feedback for",
                    },
                    "regenerate": {
                        "type": "boolean",
                        "default": False,
                        "description": "Force regeneration if feedback already exists",
                    },
                    "custom_prompt": {
                        "type": "string",
                        "description": "Optional custom instructions for feedback generation",
                    },
                },
                "required": ["date"],
            },
        ),
        Tool(
            name="search_entries",
            description="Full-text search across entry notes",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (searches notes field)",
                    },
                    "limit": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 20,
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle MCP tool calls."""
    db = get_db()
    try:
        user = get_or_create_user(db)
        
        if name == "create_entry":
            return await handle_create_entry(db, user, arguments)
        elif name == "get_entry":
            return await handle_get_entry(db, user, arguments)
        elif name == "list_entries":
            return await handle_list_entries(db, user, arguments)
        elif name == "get_trends":
            return await handle_get_trends(db, user, arguments)
        elif name == "generate_feedback":
            return await handle_generate_feedback(db, user, arguments)
        elif name == "search_entries":
            return await handle_search_entries(db, user, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    finally:
        db.close()


async def handle_create_entry(db: Session, user: User, args: dict) -> list[TextContent]:
    """Handle create_entry tool call."""
    entry_service = EntryService(db)
    
    # Parse date
    entry_date = datetime.strptime(args["date"], "%Y-%m-%d").date()
    
    # Check if entry already exists
    existing = entry_service.get_entry_by_date(user.id, entry_date)
    if existing:
        return [
            TextContent(
                type="text",
                text=f"Error: Entry already exists for {entry_date}. Use update endpoint or delete first.",
            )
        ]
    
    # Create entry schema
    entry_data = EntryCreate(
        date=entry_date,
        cash_on_hand=args.get("cash_on_hand"),
        bank_balance=args.get("bank_balance"),
        income_today=args.get("income_today"),
        bills_due_today=args.get("bills_due_today"),
        debts_total=args.get("debts_total"),
        hours_worked=args.get("hours_worked"),
        side_income=args.get("side_income"),
        food_spent=args.get("food_spent"),
        gas_spent=args.get("gas_spent"),
        notes=args.get("notes"),
        stress_level=args["stress_level"],
        priority=args.get("priority"),
    )
    
    # Create entry
    entry = entry_service.create_entry(user.id, entry_data)
    
    # Trigger feedback generation asynchronously
    feedback_service = FeedbackService(db)
    try:
        feedback = feedback_service.generate_feedback(entry.id)
        feedback_status = "completed"
    except Exception as e:
        logger.error(f"Feedback generation failed: {e}")
        feedback_status = "failed"
    
    result = {
        "success": True,
        "entry_id": entry.id,
        "date": str(entry.date),
        "feedback_status": feedback_status,
        "message": "Entry created successfully." + (
            " Motivational feedback generated." if feedback_status == "completed" 
            else " Feedback generation failed."
        ),
    }
    
    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_entry(db: Session, user: User, args: dict) -> list[TextContent]:
    """Handle get_entry tool call."""
    entry_service = EntryService(db)
    entry_date = datetime.strptime(args["date"], "%Y-%m-%d").date()
    
    entry = entry_service.get_entry_by_date(user.id, entry_date)
    if not entry:
        return [
            TextContent(
                type="text",
                text=f"Error: No entry found for date {entry_date}",
            )
        ]
    
    # Build response with entry and feedback
    result = {
        "id": entry.id,
        "date": str(entry.date),
        "cash_on_hand": float(entry.cash_on_hand) if entry.cash_on_hand else None,
        "bank_balance": float(entry.bank_balance) if entry.bank_balance else None,
        "income_today": float(entry.income_today) if entry.income_today else None,
        "bills_due_today": float(entry.bills_due_today) if entry.bills_due_today else None,
        "debts_total": float(entry.debts_total) if entry.debts_total else None,
        "hours_worked": float(entry.hours_worked) if entry.hours_worked else None,
        "side_income": float(entry.side_income) if entry.side_income else None,
        "food_spent": float(entry.food_spent) if entry.food_spent else None,
        "gas_spent": float(entry.gas_spent) if entry.gas_spent else None,
        "notes": entry.notes,
        "stress_level": entry.stress_level,
        "priority": entry.priority,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
        "feedback": {
            "content": entry.feedback.content if entry.feedback else None,
            "status": "completed" if entry.feedback else "none",
        },
    }
    
    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_list_entries(db: Session, user: User, args: dict) -> list[TextContent]:
    """Handle list_entries tool call."""
    history_service = HistoryService(db)
    
    # Parse dates if provided
    start_date = (
        datetime.strptime(args["start_date"], "%Y-%m-%d").date()
        if args.get("start_date")
        else None
    )
    end_date = (
        datetime.strptime(args["end_date"], "%Y-%m-%d").date()
        if args.get("end_date")
        else None
    )
    limit = args.get("limit", 30)
    
    # Get entries
    entries = history_service.list_entries(
        user.id, start_date=start_date, end_date=end_date, limit=limit
    )
    
    # Build simplified response
    result = {
        "entries": [
            {
                "date": str(entry.date),
                "stress_level": entry.stress_level,
                "income_today": float(entry.income_today) if entry.income_today else 0.0,
                "priority": entry.priority,
                "has_feedback": entry.feedback is not None,
            }
            for entry in entries
        ],
        "total": len(entries),
    }
    
    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_get_trends(db: Session, user: User, args: dict) -> list[TextContent]:
    """Handle get_trends tool call."""
    history_service = HistoryService(db)
    
    # Parse dates
    start_date = datetime.strptime(args["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(args["end_date"], "%Y-%m-%d").date()
    
    # Get statistics
    stats = history_service.get_statistics(user.id, start_date, end_date)
    
    # Calculate days logged
    entries = history_service.list_entries(
        user.id, start_date=start_date, end_date=end_date
    )
    days_logged = len(entries)
    
    # Get trends for stress level
    trends = history_service.get_trends(user.id, days=(end_date - start_date).days + 1)
    
    # Determine stress trend
    if len(trends) >= 2:
        recent_avg = sum(t["value"] for t in trends[-7:]) / min(7, len(trends[-7:]))
        older_avg = sum(t["value"] for t in trends[:7]) / min(7, len(trends[:7]))
        if recent_avg < older_avg - 0.5:
            stress_trend = "decreasing"
        elif recent_avg > older_avg + 0.5:
            stress_trend = "increasing"
        else:
            stress_trend = "stable"
    else:
        stress_trend = "insufficient_data"
    
    result = {
        "period": {
            "start_date": str(start_date),
            "end_date": str(end_date),
            "days_logged": days_logged,
        },
        "financials": {
            "total_income": float(stats.get("total_income", 0)),
            "total_bills": float(stats.get("total_bills", 0)),
            "avg_daily_income": float(stats.get("avg_income", 0)),
            "debt_change": 0,  # Would need to calculate from first/last entry
        },
        "wellbeing": {
            "avg_stress_level": float(stats.get("avg_stress", 0)),
            "stress_trend": stress_trend,
            "avg_hours_worked": float(stats.get("avg_hours", 0)),
        },
        "insights": [],
    }
    
    # Generate insights
    if stress_trend == "decreasing":
        result["insights"].append("Stress levels trending down - great progress!")
    elif stress_trend == "increasing":
        result["insights"].append("Stress levels rising - consider stress management strategies")
    
    if result["financials"]["avg_daily_income"] > 0:
        result["insights"].append(
            f"Income stable, averaging ${result['financials']['avg_daily_income']:.2f}/day"
        )
    
    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_generate_feedback(db: Session, user: User, args: dict) -> list[TextContent]:
    """Handle generate_feedback tool call."""
    entry_service = EntryService(db)
    feedback_service = FeedbackService(db)
    
    # Parse date
    entry_date = datetime.strptime(args["date"], "%Y-%m-%d").date()
    
    # Get entry
    entry = entry_service.get_entry_by_date(user.id, entry_date)
    if not entry:
        return [
            TextContent(
                type="text",
                text=f"Error: No entry found for date {entry_date}",
            )
        ]
    
    # Check if feedback exists
    regenerate = args.get("regenerate", False)
    if entry.feedback and not regenerate:
        return [
            TextContent(
                type="text",
                text=f"Feedback already exists for {entry_date}. Use regenerate=true to force regeneration.",
            )
        ]
    
    # Generate feedback
    try:
        custom_prompt = args.get("custom_prompt")
        feedback = feedback_service.generate_feedback(entry.id, custom_instructions=custom_prompt)
        result = {
            "feedback_id": feedback.id,
            "status": "completed",
            "message": "Feedback generated successfully",
            "content": feedback.content,
        }
    except Exception as e:
        logger.error(f"Feedback generation failed: {e}")
        result = {
            "status": "failed",
            "message": f"Feedback generation failed: {str(e)}",
        }
    
    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def handle_search_entries(db: Session, user: User, args: dict) -> list[TextContent]:
    """Handle search_entries tool call."""
    history_service = HistoryService(db)
    
    query = args["query"]
    limit = args.get("limit", 20)
    
    # Use search_entries method
    results = history_service.search_entries(user.id, query, limit=limit)
    
    # Build response
    result = {
        "results": [
            {
                "date": str(entry.date),
                "notes": entry.notes,
                "stress_level": entry.stress_level,
                "relevance_score": 1.0,  # Placeholder - would need proper scoring
            }
            for entry in results
        ],
        "total": len(results),
    }
    
    import json
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


# Resource Definitions

@mcp_server.list_resources()
async def list_resources() -> list[Resource]:
    """List all available MCP resources."""
    return [
        Resource(
            uri="entry://date/{date}",
            name="Entry by date",
            mimeType="application/json",
            description="Access a specific entry by date (YYYY-MM-DD)",
        ),
        Resource(
            uri="entry://history/{start}/{end}",
            name="Entry history range",
            mimeType="application/json",
            description="Access entries for a date range (start and end in YYYY-MM-DD)",
        ),
    ]


@mcp_server.read_resource()
async def read_resource(uri: str) -> str:
    """Read MCP resource by URI."""
    db = get_db()
    try:
        user = get_or_create_user(db)
        
        if uri.startswith("entry://date/"):
            date_str = uri.replace("entry://date/", "")
            return await read_entry_resource(db, user, date_str)
        elif uri.startswith("entry://history/"):
            # Parse start/end from URI like entry://history/2025-10-01/2025-10-21
            parts = uri.replace("entry://history/", "").split("/")
            if len(parts) != 2:
                raise ValueError("Invalid history URI format. Expected: entry://history/start/end")
            return await read_history_resource(db, user, parts[0], parts[1])
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    finally:
        db.close()


async def read_entry_resource(db: Session, user: User, date_str: str) -> str:
    """Read entry resource for a specific date."""
    entry_service = EntryService(db)
    entry_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    
    entry = entry_service.get_entry_by_date(user.id, entry_date)
    if not entry:
        raise ValueError(f"No entry found for date {date_str}")
    
    result = {
        "uri": f"entry://date/{date_str}",
        "mimeType": "application/json",
        "content": {
            "date": str(entry.date),
            "financials": {
                "cash_on_hand": float(entry.cash_on_hand) if entry.cash_on_hand else None,
                "bank_balance": float(entry.bank_balance) if entry.bank_balance else None,
                "income_today": float(entry.income_today) if entry.income_today else None,
                "bills_due_today": float(entry.bills_due_today) if entry.bills_due_today else None,
                "debts_total": float(entry.debts_total) if entry.debts_total else None,
                "side_income": float(entry.side_income) if entry.side_income else None,
                "food_spent": float(entry.food_spent) if entry.food_spent else None,
                "gas_spent": float(entry.gas_spent) if entry.gas_spent else None,
            },
            "work": {
                "hours_worked": float(entry.hours_worked) if entry.hours_worked else None,
            },
            "wellbeing": {
                "stress_level": entry.stress_level,
                "priority": entry.priority,
                "notes": entry.notes,
            },
        },
    }
    
    import json
    return json.dumps(result, indent=2)


async def read_history_resource(db: Session, user: User, start_str: str, end_str: str) -> str:
    """Read history resource for a date range."""
    history_service = HistoryService(db)
    
    start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
    
    entries = history_service.list_entries(user.id, start_date=start_date, end_date=end_date)
    
    result = {
        "uri": f"entry://history/{start_str}/{end_str}",
        "mimeType": "application/json",
        "content": [
            {
                "date": str(entry.date),
                "stress_level": entry.stress_level,
                "income_today": float(entry.income_today) if entry.income_today else 0.0,
                "bills_due_today": float(entry.bills_due_today) if entry.bills_due_today else 0.0,
                "hours_worked": float(entry.hours_worked) if entry.hours_worked else 0.0,
                "priority": entry.priority,
                "notes": entry.notes,
            }
            for entry in entries
        ],
    }
    
    import json
    return json.dumps(result, indent=2)


# Prompt Definitions

@mcp_server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List all available MCP prompts."""
    return [
        Prompt(
            name="analyze_financial_progress",
            description="Generate insights about financial progress over time",
            arguments=[
                {"name": "start_date", "description": "Start date (YYYY-MM-DD)", "required": True},
                {"name": "end_date", "description": "End date (YYYY-MM-DD)", "required": True},
            ],
        ),
        Prompt(
            name="motivational_feedback",
            description="Generate motivational feedback for a single entry",
            arguments=[
                {"name": "date", "description": "Entry date (YYYY-MM-DD)", "required": True},
            ],
        ),
    ]


@mcp_server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str]) -> PromptMessage:
    """Get a prompt template with filled arguments."""
    db = get_db()
    try:
        user = get_or_create_user(db)
        
        if name == "analyze_financial_progress":
            return await get_financial_progress_prompt(db, user, arguments)
        elif name == "motivational_feedback":
            return await get_motivational_feedback_prompt(db, user, arguments)
        else:
            raise ValueError(f"Unknown prompt: {name}")
    finally:
        db.close()


async def get_financial_progress_prompt(
    db: Session, user: User, args: dict[str, str]
) -> PromptMessage:
    """Generate financial progress analysis prompt."""
    history_service = HistoryService(db)
    
    start_date = datetime.strptime(args["start_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(args["end_date"], "%Y-%m-%d").date()
    
    stats = history_service.get_statistics(user.id, start_date, end_date)
    
    total_income = stats.get("total_income", 0)
    total_expenses = (
        stats.get("total_food", 0) + stats.get("total_gas", 0) + stats.get("total_bills", 0)
    )
    avg_stress = stats.get("avg_stress", 0)
    
    prompt_text = f"""Analyze the user's financial progress from {start_date} to {end_date}.

Context:
- Total income: ${total_income:.2f}
- Total expenses: ${total_expenses:.2f}
- Net: ${total_income - total_expenses:.2f}
- Average stress level: {avg_stress:.1f}/10

Provide:
1. Assessment of financial trajectory
2. Stress pattern analysis
3. Actionable suggestions for improvement
4. Encouraging observations about progress
"""
    
    return PromptMessage(role="user", content=TextContent(type="text", text=prompt_text))


async def get_motivational_feedback_prompt(
    db: Session, user: User, args: dict[str, str]
) -> PromptMessage:
    """Generate motivational feedback prompt for an entry."""
    entry_service = EntryService(db)
    
    entry_date = datetime.strptime(args["date"], "%Y-%m-%d").date()
    entry = entry_service.get_entry_by_date(user.id, entry_date)
    
    if not entry:
        raise ValueError(f"No entry found for date {entry_date}")
    
    prompt_text = f"""Generate supportive, empathetic motivational feedback for this daily entry:

Date: {entry.date}
Financial snapshot:
  - Cash on hand: ${entry.cash_on_hand or 0:.2f}
  - Bank balance: ${entry.bank_balance or 0:.2f}
  - Income: ${entry.income_today or 0:.2f}
  - Bills: ${entry.bills_due_today or 0:.2f}
  - Total debt: ${entry.debts_total or 0:.2f}

Work: {entry.hours_worked or 0} hours{' (including side income)' if entry.side_income else ''}
Spending: Food ${entry.food_spent or 0:.2f}, Gas ${entry.gas_spent or 0:.2f}
Stress level: {entry.stress_level}/10
Priority: {entry.priority or 'not specified'}
Notes: {entry.notes or 'none'}

Guidelines:
- Acknowledge challenges without toxic positivity
- Celebrate wins, even small ones
- Provide perspective on progress
- Keep tone warm, supportive, non-judgmental
- Focus on effort and resilience, not outcomes
"""
    
    return PromptMessage(role="user", content=TextContent(type="text", text=prompt_text))


# Main entry point for stdio server

async def main():
    """Run MCP server with stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
