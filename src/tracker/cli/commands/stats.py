"""Statistics command"""

from datetime import date, timedelta

import click
from rich.panel import Panel
from rich.table import Table

from tracker.cli.ui.console import (
    emphasize,
    get_console,
    icon,
    qualitative_scale,
)
from tracker.cli.ui.display import display_error, format_currency, get_stress_color
from tracker.core.database import SessionLocal
from tracker.services.entry_service import EntryService
from tracker.services.history_service import HistoryService


@click.command()
@click.option("--days", type=int, default=30, help="Number of days to analyze")
def stats(days):
    """Show statistics and trends"""
    
    db = SessionLocal()
    try:
        console = get_console()
        # Get user
        entry_service = EntryService(db)
        user = entry_service.get_default_user()
        if not user:
            display_error("No user found. Please run 'tracker init' first.")
            return
        
        # Get statistics
        history_service = HistoryService(db)
        start_date = date.today() - timedelta(days=days-1)
        
        statistics = history_service.get_statistics(user.id, start_date=start_date)
        streak_info = history_service.get_streak_info(user.id)
        
        if statistics["count"] == 0:
            console.print(
                emphasize(
                    f"\n[yellow]{icon('ℹ️', 'Info')} No entries found. Create one with:[/yellow] tracker new\n",
                    "no entries found",
                )
            )
            return
        
        console.print(
            f"\n[bold cyan]{icon('📊', 'Stats')} Statistics for last {days} days[/bold cyan]\n"
        )
        
        # Streak info
        console.print(f"[bold]{icon('🔥', 'Streak')} Logging Streak[/bold]")
        console.print(
            f"  Current streak: [green]{streak_info['current_streak']} days[/green]"
        )
        console.print(
            f"  Longest streak: [cyan]{streak_info['longest_streak']} days[/cyan]"
        )
        console.print(f"  Total entries: {streak_info['total_entries']}")
        console.print()
        
        # Financial summary
        lines = []
        lines.append(f"[bold cyan]{icon('💰', 'Finance')} Financial Summary[/bold cyan]")
        lines.append(f"  Total income: [green]{format_currency(statistics['income']['total'])}[/green]")
        lines.append(f"  Average income: {format_currency(statistics['income']['average'])}")
        lines.append(f"  Total bills: [yellow]{format_currency(statistics['bills']['total'])}[/yellow]")
        lines.append(f"  Total spending: [magenta]{format_currency(statistics['spending']['total'])}[/magenta]")
        lines.append("")
        lines.append(f"  [bold]Net income: {format_currency(statistics['net_income']['total'])}[/bold]")
        
        panel = Panel("\n".join(lines), border_style="cyan", padding=(1, 2))
        console.print(panel)
        console.print()
        
        # Work summary
        console.print(f"[bold cyan]{icon('💼', 'Work')} Work Summary[/bold cyan]")
        console.print(f"  Total hours: {statistics['work']['total_hours']}")
        console.print(f"  Average hours/day: {statistics['work']['average_hours']:.1f}")
        console.print(f"  Side income: {format_currency(statistics['work']['side_income_total'])}")
        console.print()
        
        # Wellbeing summary
        avg_stress = statistics['wellbeing']['average_stress']
        stress_color = get_stress_color(int(avg_stress))
        
        console.print(f"[bold cyan]{icon('🧘', 'Wellbeing')} Wellbeing Summary[/bold cyan]")
        stress_descriptor = qualitative_scale(
            int(round(avg_stress)),
            low=range(0, 4),
            medium=range(4, 7),
            high=range(7, 11),
        )
        console.print(
            emphasize(
                f"  Average stress: [{stress_color}]{avg_stress:.1f}/10[/{stress_color}]",
                f"{stress_descriptor} stress" if stress_descriptor != "unknown" else None,
            )
        )
        console.print(
            f"  Lowest stress: [green]{statistics['wellbeing']['min_stress']}/10[/green]"
        )
        console.print(
            f"  Highest stress: [red]{statistics['wellbeing']['max_stress']}/10[/red]"
        )
        console.print()
        
        # Create breakdown table
        table = Table(title="Daily Averages")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        
        table.add_row("Income", format_currency(statistics['income']['average']))
        table.add_row("Bills", format_currency(statistics['bills']['average']))
        table.add_row("Spending", format_currency(statistics['spending']['average']))
        table.add_row("Net", format_currency(statistics['net_income']['average']))
        table.add_row("Hours worked", f"{statistics['work']['average_hours']:.1f}")
        table.add_row(
            "Stress level",
            emphasize(
                f"{avg_stress:.1f}/10",
                f"{stress_descriptor} stress" if stress_descriptor != "unknown" else None,
            ),
        )
        
        console.print(table)
        console.print()
        
    except Exception as e:
        display_error(f"Failed to calculate statistics: {e}")
    finally:
        db.close()
