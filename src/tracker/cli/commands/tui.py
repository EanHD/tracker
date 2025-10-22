"""TUI command - Launch interactive menu interface"""

import click
from rich.console import Console

console = Console()


@click.command()
def tui():
    """Launch interactive menu interface
    
    A text-based menu system that stays running in a loop.
    Provides easy access to all Tracker commands:
    - Creating new entries
    - Viewing and searching entries
    - Checking statistics and achievements
    - Managing configuration
    - Exporting data
    
    Select options by number and press Enter. Type 0 to exit.
    """
    try:
        from tracker.cli.tui.app import run_tui
        run_tui()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
