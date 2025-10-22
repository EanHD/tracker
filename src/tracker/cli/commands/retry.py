"""Retry AI feedback generation for an entry"""

from datetime import date, datetime, timedelta

import click
from rich.console import Console

from tracker.core.database import SessionLocal
from tracker.services.entry_service import EntryService
from tracker.services.feedback_service import FeedbackService

console = Console()


@click.command()
@click.argument("date_arg", required=False)
def retry(date_arg):
    """
    Retry AI feedback generation for an entry
    
    DATE can be:
    - YYYY-MM-DD format (e.g., 2025-10-21)
    - 'today' (default)
    - 'yesterday'
    - Relative like '-1', '-2' for days ago
    
    Examples:
        tracker retry today
        tracker retry 2025-10-21
        tracker retry yesterday
        tracker retry -1
    """
    
    # Parse date argument
    try:
        entry_date = _parse_date_arg(date_arg)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        return
    
    db = SessionLocal()
    
    try:
        # Get the entry
        entry_service = EntryService(db)
        
        # Get default user
        user = entry_service.get_default_user()
        if not user:
            console.print("[red]Error: No user found. Please run 'tracker init' first.[/red]")
            return
        
        # Fetch entry
        entry = entry_service.get_entry_by_date(user.id, entry_date)
        
        if not entry:
            console.print(f"[red]Error: No entry found for {entry_date}[/red]")
            return
        
        console.print(f"\n[cyan]Regenerating AI feedback for {entry.date}...[/cyan]")
        
        # Regenerate feedback
        feedback_service = FeedbackService(db)
        
        try:
            feedback = feedback_service.generate_feedback(entry.id, regenerate=True)
            
            if feedback.status == "completed":
                console.print("[green]✓ Feedback generated successfully![/green]\n")
                
                # Display the feedback
                from tracker.cli.ui.display import display_entry
                display_entry(entry, show_feedback=True)
            else:
                console.print(f"[yellow]Warning: Feedback status is '{feedback.status}'[/yellow]")
                if feedback.error_message:
                    console.print(f"[yellow]Error: {feedback.error_message}[/yellow]")
        
        except Exception as e:
            console.print(f"[red]Error generating feedback: {e}[/red]")
            console.print("\n[yellow]Tips:[/yellow]")
            console.print("  • Make sure your AI configuration is correct: [cyan]tracker config show[/cyan]")
            console.print("  • Check that your AI service is running (for local provider)")
            console.print("  • Verify your API key is valid (for cloud providers)")
            console.print("  • Try again in a moment if it's a temporary issue")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
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
