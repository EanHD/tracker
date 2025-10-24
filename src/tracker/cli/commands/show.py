"""Show entry command"""

from datetime import date, datetime, timedelta

import click

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.cli.ui.display import display_entry, display_error, display_info
from tracker.core.database import SessionLocal
from tracker.services.entry_service import EntryService


@click.command()
@click.argument("date_arg", required=False)
@click.option("--no-feedback", is_flag=True, help="Hide AI feedback")
def show(date_arg, no_feedback):
    """
    Show a daily entry
    
    DATE can be:
    - YYYY-MM-DD format (e.g., 2025-10-21)
    - 'today' (default)
    - 'yesterday'
    - Relative like '-1', '-2' for days ago
    
    By default, AI feedback is shown if available.
    Use --no-feedback to hide it.
    """
    
    # Parse date argument
    try:
        entry_date = _parse_date_arg(date_arg)
    except ValueError as e:
        display_error(str(e))
        return
    
    # Get entry
    db = SessionLocal()
    try:
        console = get_console()
        service = EntryService(db)
        
        # Get default user
        user = service.get_default_user()
        if not user:
            display_error("No user found. Please run 'tracker init' first.")
            return
        
        # Fetch entry
        entry = service.get_entry_by_date(user.id, entry_date)
        
        if not entry:
            display_info(f"No entry found for {entry_date}")
            console.print(
                emphasize(
                    f"\n[cyan]{icon('➕', 'Create')} Create one:[/cyan] tracker new --date {entry_date}",
                    "create entry tip",
                )
            )
            return
        
        # Display entry
        console.print()
        display_entry(entry, show_feedback=not no_feedback)
        
    except Exception as e:
        display_error(f"Failed to fetch entry: {e}")
    finally:
        db.close()


def _parse_date_arg(date_arg: str) -> date:
    """Parse date argument into date object"""
    
    if not date_arg or date_arg.lower() == "today":
        return date.today()
    
    if date_arg.lower() == "yesterday":
        return date.today() - timedelta(days=1)
    
    # Check if it's a relative date like -1, -2
    if date_arg.startswith("-") and date_arg[1:].isdigit():
        days_ago = int(date_arg[1:])
        return date.today() - timedelta(days=days_ago)
    
    # Try parsing as YYYY-MM-DD
    try:
        return datetime.strptime(date_arg, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(
            f"Invalid date format: {date_arg}. "
            "Use YYYY-MM-DD, 'today', 'yesterday', or '-N' for N days ago."
        )
