"""List entries command"""

from datetime import date, timedelta

import click
from rich.console import Console
from rich.table import Table

from tracker.cli.ui.display import display_error, format_currency, get_stress_color
from tracker.core.database import SessionLocal
from tracker.services.entry_service import EntryService
from tracker.services.history_service import HistoryService

console = Console()


@click.command()
@click.option("--days", type=int, default=7, help="Number of days to show")
@click.option("--limit", type=int, default=50, help="Maximum entries to show")
@click.option("--start", type=click.DateTime(formats=["%Y-%m-%d"]), help="Start date")
@click.option("--end", type=click.DateTime(formats=["%Y-%m-%d"]), help="End date")
def list(days, limit, start, end):
    """List recent entries"""
    
    db = SessionLocal()
    try:
        # Get user
        entry_service = EntryService(db)
        user = entry_service.get_default_user()
        if not user:
            display_error("No user found. Please run 'tracker init' first.")
            return
        
        # Get entries
        history_service = HistoryService(db)
        
        # Determine date range
        if start:
            start_date = start.date()
        elif not end:
            start_date = date.today() - timedelta(days=days-1)
        else:
            start_date = None
        
        end_date = end.date() if end else None
        
        entries = history_service.list_entries(
            user.id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        if not entries:
            console.print("\n[yellow]No entries found for the specified range.[/yellow]\n")
            console.print("Create your first entry: [cyan]tracker new[/cyan]\n")
            return
        
        # Create table
        table = Table(title=f"📊 Your Entries ({len(entries)} total)")
        
        table.add_column("Date", style="cyan", no_wrap=True)
        table.add_column("Income", style="green", justify="right")
        table.add_column("Bills", style="yellow", justify="right")
        table.add_column("Spending", style="magenta", justify="right")
        table.add_column("Hours", justify="right")
        table.add_column("Stress", justify="center")
        table.add_column("AI", justify="center", style="dim")
        table.add_column("Priority", style="dim", max_width=25)
        
        for entry in entries:
            spending = entry.food_spent + entry.gas_spent
            stress_color = get_stress_color(entry.stress_level)
            
            # Check feedback status
            if hasattr(entry, 'feedback') and entry.feedback:
                if entry.feedback.status == 'completed':
                    ai_status = "✓"
                elif entry.feedback.status == 'pending':
                    ai_status = "⏳"
                elif entry.feedback.status == 'failed':
                    ai_status = "✗"
                else:
                    ai_status = "-"
            else:
                ai_status = "-"
            
            table.add_row(
                str(entry.date),
                format_currency(entry.income_today),
                format_currency(entry.bills_due_today),
                format_currency(spending),
                str(entry.hours_worked),
                f"[{stress_color}]{entry.stress_level}/10[/{stress_color}]",
                ai_status,
                entry.priority or "-"
            )
        
        console.print("\n")
        console.print(table)
        console.print("\n")
        
        # Show quick stats
        total_income = sum(e.income_today for e in entries)
        total_bills = sum(e.bills_due_today for e in entries)
        total_spending = sum(e.food_spent + e.gas_spent for e in entries)
        avg_stress = sum(e.stress_level for e in entries) / len(entries)
        
        console.print(f"💰 Total income: [green]{format_currency(total_income)}[/green]")
        console.print(f"📄 Total bills: [yellow]{format_currency(total_bills)}[/yellow]")
        console.print(f"🛒 Total spending: [magenta]{format_currency(total_spending)}[/magenta]")
        console.print(f"😰 Average stress: [{get_stress_color(int(avg_stress))}]{avg_stress:.1f}/10[/]")
        console.print()
        
    except Exception as e:
        display_error(f"Failed to list entries: {e}")
    finally:
        db.close()
