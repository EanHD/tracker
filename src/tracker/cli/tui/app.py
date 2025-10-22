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
        "[bold cyan]Tracker🔏[/bold cyan]\n"
        "[dim]Select an option below[/dim]",
        border_style="cyan"
    ))
    console.print()
    console.print("  [bold cyan]1.[/bold cyan] 📝 New Entry")
    console.print("  [bold cyan]2.[/bold cyan] 👁  View Entries")
    console.print("  [bold cyan]3.[/bold cyan] 🔍 Search Entries")
    console.print("  [bold cyan]4.[/bold cyan] 📊 Statistics")
    console.print("  [bold cyan]5.[/bold cyan] 🏆 Achievements")
    console.print("  [bold cyan]6.[/bold cyan] ⚙️ Configuration")
    console.print("  [bold cyan]7.[/bold cyan] 📤 Export Data")
    console.print("  [bold cyan]8.[/bold cyan] 👤 Profile")
    console.print("  [bold cyan]9.[/bold cyan] ❓ Help")
    console.print("  [bold red]0.[/bold red] ❌ Exit")
    console.print()


def handle_new_entry():
    """Handle new entry creation"""
    console.print("\n[bold cyan]📝 Creating New Entry[/bold cyan]\n")
    
    from tracker.cli.commands.new import new as new_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(new_cmd, [], catch_exceptions=False, standalone_mode=False)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_view_entries():
    """Handle viewing entries"""
    from datetime import date, timedelta
    from tracker.core.database import SessionLocal
    from tracker.services.entry_service import EntryService
    from rich.table import Table
    
    console.print("\n[bold cyan]👁️  View Entries[/bold cyan]\n")
    
    with SessionLocal() as db:
        service = EntryService(db)
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        entries = service.list_entries(
            user_id=1,
            start_date=start_date,
            end_date=end_date
        )
        
        if not entries:
            console.print("[yellow]No entries found in the last 30 days[/yellow]\n")
            console.print("[dim]Press Enter to continue...[/dim]")
            input()
            return
        
        # Display entries in a numbered list
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Date", width=12)
        table.add_column("Income", justify="right", width=10)
        table.add_column("Expenses", justify="right", width=10)
        table.add_column("Balance", justify="right", width=10)
        table.add_column("Stress", justify="center", width=8)
        table.add_column("Priority", width=25)
        
        for idx, entry in enumerate(entries, 1):
            total_income = entry.income_today + entry.side_income
            total_expenses = entry.bills_due_today + entry.food_spent + entry.gas_spent
            balance = total_income - total_expenses
            
            # Color code balance
            balance_color = "green" if balance >= 0 else "red"
            balance_str = f"[{balance_color}]${balance:.2f}[/]"
            
            # Color code stress
            stress = entry.stress_level
            stress_color = "green" if stress <= 3 else "yellow" if stress <= 6 else "red"
            stress_str = f"[{stress_color}]{stress}/10[/]"
            
            table.add_row(
                str(idx),
                str(entry.date),
                f"${total_income:.2f}",
                f"${total_expenses:.2f}",
                balance_str,
                stress_str,
                entry.priority or "[dim]none[/dim]"
            )
        
        console.print(table)
        console.print()
        
        # Ask if user wants to view details
        choice = Prompt.ask(
            "Enter entry number to view details (or press Enter to go back)",
            default=""
        )
        
        if choice and choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(entries):
                show_entry_detail(entries[idx - 1])
            else:
                console.print("[red]Invalid entry number[/red]")
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
        

def show_entry_detail(entry):
    """Show detailed view of an entry"""
    from tracker.core.database import SessionLocal
    from tracker.services.feedback_service import FeedbackService
    from rich.panel import Panel
    
    console.clear()
    console.print()
    
    # Calculate totals
    total_income = entry.income_today + entry.side_income
    total_expenses = entry.bills_due_today + entry.food_spent + entry.gas_spent
    balance = total_income - total_expenses
    
    # Build detail view
    detail = f"""[bold cyan]📅 Entry for {entry.date}[/bold cyan]

[bold]💰 Financial Summary[/bold]
  Income Today:    ${entry.income_today:.2f}
  Side Income:     ${entry.side_income:.2f}
  ─────────────────────────────
  Total Income:    [green]${total_income:.2f}[/green]
  
  Bills Due:       ${entry.bills_due_today:.2f}
  Food Spent:      ${entry.food_spent:.2f}
  Gas Spent:       ${entry.gas_spent:.2f}
  ─────────────────────────────
  Total Expenses:  [red]${total_expenses:.2f}[/red]
  
  Net Balance:     {'[green]' if balance >= 0 else '[red]'}${balance:.2f}[/]

[bold]📊 Work & Wellbeing[/bold]
  Hours Worked:    {entry.hours_worked}
  Stress Level:    {entry.stress_level}/10
  Priority:        {entry.priority or '[dim]none[/dim]'}

[bold]📝 Notes[/bold]
{entry.notes or '[dim]No notes for this day[/dim]'}
"""
    
    console.print(Panel(detail, border_style="cyan", padding=(1, 2)))
    
    # Get AI feedback if available
    with SessionLocal() as db:
        feedback_service = FeedbackService(db)
        feedback = feedback_service.get_feedback_by_entry(entry.id)
        
        if feedback:
            console.print()
            feedback_text = f"""[bold cyan]💬 Feedback[/bold cyan]

{feedback.content}

[dim]Generated: {feedback.created_at.strftime('%Y-%m-%d %H:%M')}[/dim]
"""
            console.print(Panel(feedback_text, border_style="blue", padding=(1, 2)))
        else:
            console.print("\n[dim]No AI feedback available for this entry[/dim]")
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_search():
    """Handle search"""
    from datetime import datetime
    from tracker.core.database import SessionLocal
    from tracker.services.history_service import HistoryService
    from tracker.core.models import DailyEntry
    from rich.table import Table
    from sqlalchemy import cast, String
    
    console.print("\n[bold cyan]🔍 Search Entries[/bold cyan]")
    query = Prompt.ask("Enter search term (date, text, or number)")
    
    if not query:
        return
    
    with SessionLocal() as db:
        # Try to search by date first
        entries = []
        
        # Check if it's a date search (YYYY-MM-DD or partial)
        try:
            # Try full date
            search_date = datetime.strptime(query, "%Y-%m-%d").date()
            entry = db.query(DailyEntry).filter(
                DailyEntry.user_id == 1,
                DailyEntry.date == search_date
            ).first()
            if entry:
                entries = [entry]
        except ValueError:
            # Try partial date matching (like "10-21" or "21")
            if query.replace("-", "").isdigit():
                # Search dates containing this pattern
                date_pattern = f"%{query}%"
                entries = db.query(DailyEntry).filter(
                    DailyEntry.user_id == 1,
                    cast(DailyEntry.date, String).like(date_pattern)
                ).order_by(DailyEntry.date.desc()).all()
        
        # If no date matches, search in notes and priority
        if not entries:
            service = HistoryService(db)
            entries = service.search_entries(1, query, limit=20)
        
        if not entries:
            console.print(f"\n[yellow]No entries found matching '[cyan]{query}[/cyan]'[/yellow]\n")
            console.print("[dim]Press Enter to continue...[/dim]")
            input()
            return
        
        # Display results
        console.print(f"\n[bold]Found {len(entries)} {'entry' if len(entries) == 1 else 'entries'}[/bold]\n")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Date", width=12)
        table.add_column("Income", justify="right", width=10)
        table.add_column("Expenses", justify="right", width=10)
        table.add_column("Stress", justify="center", width=8)
        table.add_column("Priority", width=30)
        
        for idx, entry in enumerate(entries, 1):
            total_income = entry.income_today + entry.side_income
            total_expenses = entry.bills_due_today + entry.food_spent + entry.gas_spent
            
            stress = entry.stress_level
            stress_color = "green" if stress <= 3 else "yellow" if stress <= 6 else "red"
            stress_str = f"[{stress_color}]{stress}/10[/]"
            
            table.add_row(
                str(idx),
                str(entry.date),
                f"${total_income:.2f}",
                f"${total_expenses:.2f}",
                stress_str,
                entry.priority or "[dim]none[/dim]"
            )
        
        console.print(table)
        console.print()
        
        # Ask if user wants to view details
        choice = Prompt.ask(
            "Enter entry number to view details (or press Enter to go back)",
            default=""
        )
        
        if choice and choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(entries):
                show_entry_detail(entries[idx - 1])
            else:
                console.print("[red]Invalid entry number[/red]")
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()


def handle_stats():
    """Handle statistics"""
    console.print("\n[bold cyan]📊 Statistics[/bold cyan]\n")
    
    from tracker.cli.commands.stats import stats as stats_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(stats_cmd, [], catch_exceptions=False)
    
    # Print the output
    if result.output:
        print(result.output)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_achievements():
    """Handle achievements"""
    console.print("\n[bold cyan]🏆 Achievements[/bold cyan]\n")
    
    from tracker.cli.commands.achievements import achievements as ach_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(ach_cmd, [], catch_exceptions=False)
    
    # Print the output
    if result.output:
        print(result.output)
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_config():
    """Handle configuration"""
    console.print("\n[bold cyan]⚙️ Configuration[/bold cyan]\n")
    
    from tracker.cli.commands.config import config as config_cmd
    from click.testing import CliRunner
    
    runner = CliRunner()
    result = runner.invoke(config_cmd, ['show'], catch_exceptions=False)
    
    # Print the output
    if result.output:
        print(result.output)
    
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
        
        # Print the output
        if result.output:
            print(result.output)
    elif choice == "2":
        from tracker.cli.commands.export import export as export_cmd
        from click.testing import CliRunner
        
        runner = CliRunner()
        result = runner.invoke(export_cmd, ['--format', 'json'], catch_exceptions=False)
        
        # Print the output
        if result.output:
            print(result.output)
    
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
    
    # Print the output
    if result.output:
        print(result.output)
    
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
