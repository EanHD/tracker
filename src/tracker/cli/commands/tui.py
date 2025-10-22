"""TUI command - Launch interactive terminal interface"""

import click
from rich.console import Console

console = Console()


@click.command()
def tui():
    """Launch interactive TUI (Terminal User Interface)
    
    The TUI provides a full-screen menu-driven interface for:
    - Creating new entries
    - Viewing and searching entries
    - Checking statistics and achievements
    - Managing configuration
    - Exporting data
    
    Use arrow keys to navigate, hotkeys for quick access, and ESC to go back.
    """
    try:
        from tracker.cli.tui.app import run_tui
        run_tui()
    except KeyboardInterrupt:
        console.print("\n[yellow]TUI closed[/yellow]")
    except Exception as e:
        console.print(f"[red]Error launching TUI: {e}[/red]")
        console.print("\n[dim]Hint: Make sure textual is installed:[/dim]")
        console.print("[cyan]uv pip install textual[/cyan]")
