"""Retry AI feedback generation for an entry"""

import click
from rich.console import Console

from tracker.core.database import get_db
from tracker.services.entry_service import EntryService
from tracker.services.feedback_service import FeedbackService

console = Console()


@click.command()
@click.argument("date")
def retry(date: str):
    """
    Retry AI feedback generation for an entry
    
    DATE: The date of the entry (YYYY-MM-DD or today/yesterday)
    
    Examples:
        tracker retry today
        tracker retry 2025-10-21
        tracker retry yesterday
    """
    
    db = get_db()
    
    try:
        # Get the entry
        entry_service = EntryService(db)
        entry = entry_service.get_entry_by_date_string(date)
        
        if not entry:
            console.print(f"[red]Error: No entry found for {date}[/red]")
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
