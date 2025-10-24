"""TUI command - Launch interactive menu interface"""

import click

from tracker.cli.ui.console import emphasize, get_console, icon


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
        get_console().print(
            emphasize(f"\n[yellow]{icon('👋', 'Goodbye')} Goodbye![/yellow]", "tui exit")
        )
    except Exception as e:
        get_console().print(
            emphasize(f"[red]{icon('❌', 'Error')} Error: {e}[/red]", "tui error")
        )
