"""Shared UI formatters for Tracker CLI"""

import os
from typing import Dict, Any, List
from rich.table import Table
from rich import box

from tracker.cli.ui.console import get_console
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tracker.services.natural_commands import ParsedIntent


def render_diff(diff) -> str:
    """Render diff preview as a table

    Args:
        diff: AdjustmentDiff object with changes, before, after

    Returns:
        Formatted table string
    """
    console = get_console()

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Before", style="red", width=15)
    table.add_column("After", style="green", width=15)
    table.add_column("Effective", style="yellow", width=12)

    changes = diff.changes
    for change in changes:
        # Parse change description for table
        if "from" in change.lower():
            parts = change.split(" from ")
            if len(parts) == 2:
                field = parts[0].replace("Change ", "").replace("Set ", "")
                before_after = parts[1].split(" to ")
                if len(before_after) == 2:
                    table.add_row(field, before_after[0], before_after[1], "Today")
        else:
            table.add_row(change, "-", "Applied", "Today")

    # Capture table output
    from io import StringIO
    from rich.console import Console as RichConsole

    string_buffer = StringIO()
    temp_console = RichConsole(file=string_buffer, width=console.width, legacy_windows=False)
    temp_console.print(table)

    return string_buffer.getvalue()


def render_forecast(rows: List[Dict[str, Any]]) -> str:
    """Render forecast as a table

    Args:
        rows: List of forecast day dictionaries

    Returns:
        Formatted table string
    """
    console = get_console()

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Day", style="yellow", width=10)
    table.add_column("Events", style="white", width=40)
    table.add_column("Change", style="green", width=12)
    table.add_column("Balance", style="blue", width=12)

    for day in rows:
        events_text = []
        day_change = 0

        for event in day.get('events', []):
            event_type = event.get('type', '')
            description = event.get('description', '')

            if event_type == 'income':
                events_text.append(f"💰 {description}")
                day_change -= float(event.get('amount', 0))
            elif event_type in ['bill', 'transfer']:
                events_text.append(f"💸 {description}")
                day_change += float(event.get('amount', 0))
            elif event_type == 'essential':
                events_text.append(f"🛒 {description}")
                day_change += float(event.get('amount', 0))
            elif event_type == 'recorded':
                events_text.append(f"📝 {description}")
                day_change += float(event.get('amount', 0))

        # Format events
        events_str = "\n".join(events_text[:3])  # Show max 3 events
        if len(events_text) > 3:
            events_str += f"\n+{len(events_text) - 3} more"

        # Format balance
        balance = day.get('end_balance_bank', 0)
        balance_str = f"${balance:.2f}" if balance >= 0 else f"[red]${balance:.2f}[/]"

        table.add_row(
            day.get('date', '').strftime("%m/%d") if hasattr(day.get('date'), 'strftime') else str(day.get('date', '')),
            day.get('day_name', '')[:3],
            events_str,
            f"${day_change:.2f}",
            balance_str,
        )

    # Capture table output
    from io import StringIO
    from rich.console import Console as RichConsole

    string_buffer = StringIO()
    temp_console = RichConsole(file=string_buffer, width=console.width, legacy_windows=False)
    temp_console.print(table)

    return string_buffer.getvalue()


def render_audit_summary() -> str:
    """Render last 3 audit summaries

    Returns:
        Formatted audit summary string
    """
    from tracker.config import get_config_dir
    import json
    from pathlib import Path
    from datetime import datetime

    console = get_console()
    audit_dir = get_config_dir() / "audits"

    if not audit_dir.exists():
        return "[dim]No audits found[/dim]"

    # Get last 3 audit files
    audit_files = sorted(audit_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:3]

    if not audit_files:
        return "[dim]No audits found[/dim]"

    from rich.table import Table

    table = Table(box=None, show_header=True, header_style="bold cyan")
    table.add_column("Date", style="cyan", width=12)
    table.add_column("Action", style="white", width=25)
    table.add_column("Changes", style="green", width=40)

    for audit_file in audit_files:
        try:
            with open(audit_file, 'r') as f:
                audit_data = json.load(f)

            timestamp = audit_data.get('timestamp', '')
            if timestamp:
                date_obj = datetime.fromisoformat(timestamp)
                date_str = date_obj.strftime("%m/%d %H:%M")
            else:
                date_str = "Unknown"

            user_text = audit_data.get('user_text', 'Unknown')
            changes = audit_data.get('changes_applied', [])

            # Truncate long descriptions
            action = user_text[:22] + "..." if len(user_text) > 25 else user_text
            changes_str = "; ".join(changes[:2])  # Show first 2 changes
            if len(changes) > 2:
                changes_str += f" (+{len(changes) - 2} more)"

            table.add_row(date_str, action, changes_str)

        except Exception:
            table.add_row("Error", "Could not read audit", "")

    # Capture table output
    from io import StringIO
    from rich.console import Console as RichConsole

    string_buffer = StringIO()
    temp_console = RichConsole(file=string_buffer, width=console.width, legacy_windows=False)
    temp_console.print(table)

    return string_buffer.getvalue()


def render_parse_summary(intent: Any) -> str:
    """Render parsed intent summary as formatted text

    Args:
        intent: ParsedIntent object

    Returns:
        Formatted summary string
    """
    console = get_console()

    lines = []
    lines.append(f"Action: {intent.action.title()}")
    lines.append(f"Entity: {intent.entity_name} ({intent.entity_type})")

    if intent.parameters:
        params = []
        for key, value in intent.parameters.items():
            if key == "new_amount":
                params.append(f"Amount: ${value:.2f}")
            elif key == "effective_date":
                params.append(f"Effective: {value}")
            elif key == "amount":
                params.append(f"Amount: ${value:.2f}")
            elif key == "date":
                params.append(f"Date: {value}")
            elif key == "provider":
                params.append(f"Provider: {value}")
            elif key == "delay_days":
                params.append(f"Delay: {value} days")
            else:
                params.append(f"{key.title()}: {value}")
        lines.append("Parameters: " + ", ".join(params))

    return "\n".join(lines)


def get_generic_examples(config) -> List[str]:
    """Get generic examples for help screen, avoiding personal provider names.

    Args:
        config: Cashflow config dict

    Returns:
        List of example sentences
    """
    # Check for demo mode
    if os.environ.get("TRACKER_MODE") == "demo":
        return [
            "I paid off my credit card",
            "Lower my weekly advance to 300 next Thursday",
            "Defer my car loan payment one week",
            "Add a new installment purchase for 22.97 due next week",
            "Cancel my subscription service",
        ]

    # If no config or no providers, use static defaults
    providers = config.providers
    if not providers:
        return [
            "I paid off my credit card",
            "Lower my weekly advance to 300 next Thursday",
            "Defer my car loan payment one week",
            "Add a new installment purchase for 22.97 due next week",
            "Cancel my subscription service",
        ]

    # Map provider types to generic categories
    type_to_category = {
        "advance": "weekly advance",
        "auto_debit": "tool payment",
        "subscription": "subscription service",
        "bill": "recurring bill",
        "transfer": "bank transfer",
        "income": "paycheck",
    }

    # Collect unique categories from providers
    categories = set()
    for provider_config in providers.values():
        provider_type = provider_config.type
        if provider_type in type_to_category:
            categories.add(type_to_category[provider_type])

    # Generate examples based on available categories
    examples = []

    if "weekly advance" in categories:
        examples.append("Lower my weekly advance to 300 next Thursday")

    if "tool payment" in categories:
        examples.append("Defer my tool payment one week")

    if "subscription service" in categories:
        examples.append("Cancel my subscription service")

    if "recurring bill" in categories:
        examples.append("I paid off my recurring bill")

    # Always include some general examples
    examples.extend([
        "I paid off my credit card",
        "Add a new installment purchase for 22.97 due next week",
    ])

    # Limit to 5 examples
    return examples[:5]