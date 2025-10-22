"""CLI menu application - text-based interactive loop"""

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def show_main_menu():
    """Display the main menu"""
    console.clear()
    console.print()
    console.print(Panel.fit(
        "[bold cyan]🎯 Daily Tracker[/bold cyan]\n"
        "[dim]Select an option below[/dim]",
        border_style="cyan"
    ))
    console.print()
    console.print("  [bold cyan]1.[/bold cyan] 📝 New Entry")
    console.print("  [bold cyan]2.[/bold cyan] 👁️  View Entries")
    console.print("  [bold cyan]3.[/bold cyan] 🔍 Search Entries")
    console.print("  [bold cyan]4.[/bold cyan] 📊 Statistics")
    console.print("  [bold cyan]5.[/bold cyan] 🏆 Achievements")
    console.print("  [bold cyan]6.[/bold cyan] ⚙️  Configuration")
    console.print("  [bold cyan]7.[/bold cyan] 📤 Export Data")
    console.print("  [bold cyan]8.[/bold cyan] 👤 Profile")
    console.print("  [bold cyan]9.[/bold cyan] ❓ Help")
    console.print("  [bold red]0.[/bold red] ❌ Exit")
    console.print()


def handle_new_entry():
    """Handle new entry creation"""
    console.print("\n[bold cyan]📝 Creating New Entry[/bold cyan]")
    console.print("[dim]Running CLI command...[/dim]\n")
    
    from tracker.cli.commands.new import new as new_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(new_cmd, [], catch_exceptions=False, standalone_mode=False)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_view_entries():
    """Handle viewing entries"""
    console.print("\n[bold cyan]👁️  View Entries[/bold cyan]\n")
    
    from tracker.cli.commands.list import list as list_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(list_cmd, ['--days', '30'], catch_exceptions=False)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_search():
    """Handle search"""
    console.print("\n[bold cyan]🔍 Search Entries[/bold cyan]")
    query = Prompt.ask("Enter search term")
    
    if query:
        from tracker.cli.commands.search import search as search_cmd
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(search_cmd, [query], catch_exceptions=False)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_stats():
    """Handle statistics"""
    console.print("\n[bold cyan]📊 Statistics[/bold cyan]\n")
    
    from tracker.cli.commands.stats import stats as stats_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(stats_cmd, [], catch_exceptions=False)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_achievements():
    """Handle achievements"""
    console.print("\n[bold cyan]🏆 Achievements[/bold cyan]\n")
    
    from tracker.cli.commands.achievements import achievements as ach_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(ach_cmd, [], catch_exceptions=False)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_config():
    """Handle configuration"""
    console.print("\n[bold cyan]⚙️  Configuration[/bold cyan]\n")
    
    from tracker.cli.commands.config import config as config_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(config_cmd, ['show'], catch_exceptions=False)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_export():
    """Handle export"""
    console.print("\n[bold cyan]📤 Export Data[/bold cyan]")
    console.print("\n1. Export to CSV")
    console.print("2. Export to JSON")
    console.print("0. Back")
    
    choice = Prompt.ask("\nSelect format", choices=["1", "2", "0"], default="0")
    
    if choice == "1":
        from tracker.cli.commands.export import export as export_cmd
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(export_cmd, ['--format', 'csv'], catch_exceptions=False)
    elif choice == "2":
        from tracker.cli.commands.export import export as export_cmd
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(export_cmd, ['--format', 'json'], catch_exceptions=False)
    
    if choice != "0":
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()


def handle_profile():
    """Handle profile"""
    console.print("\n[bold cyan]👤 Profile[/bold cyan]\n")
    
    from tracker.cli.commands.profile import profile as profile_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(profile_cmd, ['show'], catch_exceptions=False)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_help():
    """Show help"""
    console.print("\n[bold cyan]❓ Help[/bold cyan]\n")
    console.print("This is a menu-driven interface for Tracker.")
    console.print("\nYou can also use direct CLI commands:")
    console.print("  [cyan]tracker new[/cyan]           - Create new entry")
    console.print("  [cyan]tracker show today[/cyan]    - Show today's entry")
    console.print("  [cyan]tracker list[/cyan]          - List recent entries")
    console.print("  [cyan]tracker stats[/cyan]         - View statistics")
    console.print("  [cyan]tracker --help[/cyan]        - Full command list")
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def run_tui():
    """Run the CLI menu application"""
    while True:
        try:
            show_main_menu()
            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], default="0")
            
            if choice == "0":
                console.print("\n[yellow]👋 Goodbye![/yellow]\n")
                break
            elif choice == "1":
                handle_new_entry()
            elif choice == "2":
                handle_view_entries()
            elif choice == "3":
                handle_search()
            elif choice == "4":
                handle_stats()
            elif choice == "5":
                handle_achievements()
            elif choice == "6":
                handle_config()
            elif choice == "7":
                handle_export()
            elif choice == "8":
                handle_profile()
            elif choice == "9":
                handle_help()
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("\n[dim]Press Enter to continue...[/dim]")
            input()
