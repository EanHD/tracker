"""Achievements command - View gamification progress"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich.table import Table

from tracker.core.database import SessionLocal
from tracker.services.gamification_service import GamificationService

console = Console()


@click.command()
def achievements():
    """
    View achievements and progress
    
    Shows your logging streak, unlocked achievements, and progress
    toward next milestones.
    
    Examples:
    
      # View all achievements
      tracker achievements
    """
    db = SessionLocal()
    service = GamificationService(db)
    
    try:
        # Get summary
        summary = service.get_summary(1)  # TODO: Get actual user
        
        # Display streak info
        streak_panel = Panel(
            f"[bold cyan]{summary['streak']['current']}[/bold cyan] day streak\n"
            f"[dim]Longest: {summary['streak']['longest']} days[/dim]\n\n"
            f"{summary['streak']['message']}",
            title="🔥 Current Streak",
            border_style="cyan"
        )
        console.print(streak_panel)
        console.print()
        
        # Display achievement progress
        achievements_text = (
            f"[bold]{summary['achievements']['unlocked']}/{summary['achievements']['total']}[/bold] "
            f"achievements unlocked ([cyan]{summary['achievements']['percent']}%[/cyan])"
        )
        console.print(achievements_text)
        console.print()
        
        # Display next milestone if available
        if summary['next_milestone']:
            milestone = summary['next_milestone']
            console.print("[bold yellow]Next Milestone:[/bold yellow]")
            console.print(f"  {milestone['icon']} {milestone['name']}")
            console.print(f"  [dim]{milestone['description']}[/dim]")
            
            # Progress bar
            with Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console
            ) as progress:
                progress.add_task(
                    "Progress",
                    total=100,
                    completed=milestone['progress_percent']
                )
            console.print()
        
        # Get all achievements
        all_achievements = service.get_achievements(1)  # TODO: Get actual user
        
        # Separate unlocked and locked
        unlocked = [a for a in all_achievements if a.unlocked_at is not None]
        locked = [a for a in all_achievements if a.unlocked_at is None]
        
        # Display unlocked achievements
        if unlocked:
            console.print("[bold green]🏆 Unlocked Achievements:[/bold green]\n")
            
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Icon", style="bold")
            table.add_column("Name", style="bold green")
            table.add_column("Description", style="dim")
            
            for achievement in unlocked:
                table.add_row(
                    achievement.icon,
                    achievement.name,
                    achievement.description
                )
            
            console.print(table)
            console.print()
        
        # Display locked achievements
        if locked:
            console.print("[bold dim]🔒 Locked Achievements:[/bold dim]\n")
            
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Icon", style="dim")
            table.add_column("Name", style="dim")
            table.add_column("Description", style="dim")
            table.add_column("Progress", justify="right")
            
            for achievement in locked:
                progress_bar = create_mini_progress_bar(achievement.progress, width=10)
                table.add_row(
                    achievement.icon,
                    achievement.name,
                    achievement.description,
                    f"{progress_bar} {int(achievement.progress * 100)}%"
                )
            
            console.print(table)
            console.print()
        
        # Display total stats
        console.print(f"[dim]Total entries: {summary['total_entries']}[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        db.close()


def create_mini_progress_bar(progress: float, width: int = 10) -> str:
    """
    Create a mini text progress bar
    
    Args:
        progress: Progress value (0.0 to 1.0)
        width: Bar width in characters
        
    Returns:
        Progress bar string
    """
    filled = int(progress * width)
    empty = width - filled
    return f"[cyan]{'█' * filled}[/][dim]{'░' * empty}[/]"
