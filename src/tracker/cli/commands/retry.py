"""Retry feedback generation for an entry"""

from datetime import date, datetime, timedelta

import click
from rich.prompt import Confirm

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.core.database import SessionLocal
from tracker.services.entry_service import EntryService
from tracker.services.feedback_service import FeedbackService


@click.command()
@click.argument("date_arg", required=False)
def retry(date_arg):
    """
    Retry feedback generation for an entry
    
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
    console = get_console()
    try:
        entry_date = _parse_date_arg(date_arg)
    except ValueError as e:
        console.print(
            emphasize(f"[red]{icon('❌', 'Error')} Error: {e}[/red]", "retry date error")
        )
        return
    
    db = SessionLocal()
    
    try:
        # Get the entry
        entry_service = EntryService(db)
        
        # Get default user
        user = entry_service.get_default_user()
        if not user:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} No user found. Please run 'tracker init' first.[/red]",
                    "user missing",
                )
            )
            return
        
        # Fetch entry
        entry = entry_service.get_entry_by_date(user.id, entry_date)
        
        if not entry:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} No entry found for {entry_date}[/red]",
                    "entry not found",
                )
            )
            return
        
        console.print(
            f"\n[cyan]{icon('🔄', 'Regenerating')} Regenerating feedback for {entry.date}...[/cyan]"
        )
        
        # Regenerate feedback
        feedback_service = FeedbackService(db)
        
        try:
            feedback = feedback_service.generate_feedback(entry.id, regenerate=True)
            
            if feedback.status == "completed":
                console.print(
                    emphasize(
                        f"[green]{icon('✅', 'Success')} Feedback generated successfully![/green]\n",
                        "feedback regenerated",
                    )
                )
                
                # Display the feedback
                from tracker.cli.ui.display import display_entry
                display_entry(entry, show_feedback=True)
                
                # Offer to continue conversation
                console.print()
                if Confirm.ask(f"{icon('💬', '')} Continue conversation about this entry?", default=False):
                    from tracker.services.chat import ChatService
                    chat_service = ChatService(db, user_id=user.id)
                    
                    # Get or create chat for this entry
                    chat_obj = chat_service.get_or_create_entry_chat(entry.id)
                    
                    # Clear screen before starting chat for clean layout
                    console.clear()
                    console.print(f"[bold cyan]{icon('💬', '')} {chat_obj.title}[/bold cyan]")
                    console.print(f"[dim]Chat ID: {chat_obj.id}[/dim]\n")
                    
                    # Start chat loop
                    from tracker.cli.commands.chat import _chat_loop
                    _chat_loop(console, chat_service, chat_obj.id)
            else:
                console.print(
                    emphasize(
                        f"[yellow]{icon('⚠️', 'Warning')} Feedback status is '{feedback.status}'[/yellow]",
                        "feedback status warning",
                    )
                )
                if feedback.error_message:
                    console.print(f"[yellow]{feedback.error_message}[/yellow]")
        
        except Exception as e:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} Error generating feedback: {e}[/red]",
                    "feedback generation error",
                )
            )
            console.print("\n[yellow]Tips:[/yellow]")
            console.print("  • Make sure your configuration is correct: [cyan]tracker config show[/cyan]")
            console.print("  • Check that your service is running (for local provider)")
            console.print("  • Verify your API key is valid (for cloud providers)")
            console.print("  • Try again in a moment if it's a temporary issue")
    
    except Exception as e:
        console.print(
            emphasize(f"[red]{icon('❌', 'Error')} Error: {e}[/red]", "retry error")
        )
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
