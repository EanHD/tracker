"""CLI menu application - text-based interactive loop"""

from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import textwrap

from tracker.cli.ui.console import emphasize, get_console, icon, qualitative_scale
from tracker.cli.ui.display import format_progress_bar


def _format_notes(notes):
    """Format notes with proper text wrapping for display"""
    if not notes:
        return ""
    
    console = get_console()
    console_width = console.width if hasattr(console, 'width') else 80
    wrap_width = max(console_width - 15, 40)  # Account for panel padding and ensure minimum width
    
    wrapped_lines = textwrap.wrap(
        notes,
        width=wrap_width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    
    return "\n".join(f"  {line}" for line in wrapped_lines)


def show_main_menu():
    """Display the main menu"""
    console = get_console()
    console.clear()
    console.print()
    console.print(Panel.fit(
        f"[bold cyan]Tracker{icon('🔏', '')}[/bold cyan]\n"
        "[dim]Select an option below[/dim]",
        border_style="cyan"
    ))
    console.print()
    console.print(f"  [bold cyan]1.[/bold cyan] {icon('📝 ', '')}New Entry")
    console.print(f"  [bold cyan]2.[/bold cyan] {icon('👁️ ', '')}View Entries")
    console.print(f"  [bold cyan]3.[/bold cyan] {icon('🔍 ', '')}Search Entries")
    console.print(f"  [bold cyan]4.[/bold cyan] {icon('💬 ', '')}Chats")
    console.print(f"  [bold cyan]5.[/bold cyan] {icon('📊 ', '')}Statistics")
    console.print(f"  [bold cyan]6.[/bold cyan] {icon('🏆 ', '')}Achievements")
    console.print(f"  [bold cyan]7.[/bold cyan] {icon('⚙️ ', '')}Configuration")
    console.print(f"  [bold cyan]8.[/bold cyan] {icon('📤 ', '')}Export Data")
    console.print(f"  [bold cyan]9.[/bold cyan] {icon('👤 ', '')}Profile")
    console.print(f"  [bold cyan]h.[/bold cyan] {icon('❓ ', '')}Help")
    console.print(f"  [bold red]0.[/bold red] {icon('❌ ', '')}Exit")
    console.print()


def handle_new_entry():
    """Handle new entry creation"""
    console = get_console()
    console.print(f"\n[bold cyan]{icon('📝', 'New')} Creating New Entry[/bold cyan]\n")
    
    try:
        # Import the new command
        from tracker.cli.commands.new import new as new_cmd
        
        # Call the Click command's callback function directly
        # This bypasses Click's context/argument parsing and runs the actual logic
        # Works perfectly with interactive prompts since we're in the same process
        new_cmd.callback(quick=False, no_feedback=False, yes=False, date=None, cash=None, bank=None, income=None, bills=None, debt=None, hours=None, side=None, food=None, gas=None, stress=None, priority=None, notes=None)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Entry creation cancelled[/yellow]")
    except SystemExit:
        # Normal exit from command
        pass
    except Exception as e:
        console.print(f"\n[red]Error creating entry: {e}[/red]")
    
    console.print("\n[dim]Press Enter to continue...[/dim]")
    input()


def handle_view_entries():
    """Handle viewing entries"""
    from datetime import date, timedelta
    from tracker.core.database import SessionLocal
    from tracker.services.entry_service import EntryService
    from rich.table import Table
    
    console = get_console()
    console.print(f"\n[bold cyan]{icon('👁️', 'View')}  View Entries[/bold cyan]\n")
    
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
        
        # Display entries in a numbered list - responsive to terminal width
        is_narrow = console.width < 80
        
        table = Table(show_header=True, header_style="bold cyan", box=None if is_narrow else None)
        table.add_column("#", style="dim", width=3)
        table.add_column("Date", width=10 if is_narrow else 12)
        
        if not is_narrow:
            table.add_column("Income", justify="right", width=10)
            table.add_column("Expenses", justify="right", width=10)
            table.add_column("Balance", justify="right", width=10)
            table.add_column("Stress", justify="center", width=8)
            table.add_column("Priority", width=25)
        else:
            # Narrow mode: combine columns
            table.add_column("Net", justify="right", width=9)
            table.add_column("Stress", justify="center", width=7)
            table.add_column("Priority", width=20, no_wrap=False)
        
        for idx, entry in enumerate(entries, 1):
            total_income = entry.income_today + entry.side_income
            total_expenses = entry.bills_due_today + entry.food_spent + entry.gas_spent
            balance = total_income - total_expenses
            
            # Color code balance
            balance_color = "green" if balance >= 0 else "red"
            balance_label = "positive balance" if balance >= 0 else "negative balance"
            balance_str = emphasize(f"[{balance_color}]${balance:.2f}[/]", balance_label)
            
            # Color code stress
            stress = entry.stress_level
            stress_color = "green" if stress <= 3 else "yellow" if stress <= 6 else "red"
            stress_descriptor = qualitative_scale(
                stress,
                low=range(0, 4),
                medium=range(4, 7),
                high=range(7, 11),
            )
            stress_str = emphasize(
                f"[{stress_color}]{stress}/10[/]",
                f"{stress_descriptor} stress" if stress_descriptor != "unknown" else None,
            )
            
            if not is_narrow:
                table.add_row(
                    str(idx),
                    str(entry.date),
                    f"${total_income:.2f}",
                    f"${total_expenses:.2f}",
                    balance_str,
                    stress_str,
                    entry.priority or "[dim]none[/dim]"
                )
            else:
                # Narrow mode: show less info per row
                priority_short = (entry.priority[:17] + "...") if entry.priority and len(entry.priority) > 20 else (entry.priority or "")
                table.add_row(
                    str(idx),
                    str(entry.date),
                    balance_str,
                    stress_str,
                    priority_short or "[dim]none[/dim]"
                )
        
        console.print(table)
        console.print()
        
        # Ask if user wants to view details
        choice = Prompt.ask(
            "Enter # for details, 'e' to edit, 'r' to remove, or Enter to go back",
            default="",
            console=console,
        )
        
        if choice and choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(entries):
                selected_entry = entries[idx - 1]
                show_entry_detail(selected_entry)
            else:
                console.print("[red]Invalid entry number[/red]")
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
        elif choice.lower() == 'e':
            # Edit mode
            entry_num = Prompt.ask("Enter entry number to edit", default="")
            if entry_num.isdigit():
                idx = int(entry_num)
                if 1 <= idx <= len(entries):
                    selected_entry = entries[idx - 1]
                    from tracker.cli.commands.edit import edit as edit_cmd
                    try:
                        edit_cmd.callback(
                            entry_date=selected_entry.date,
                            stress=None, income=None, bills=None, hours=None,
                            side_income=None, food=None, gas=None, cash=None,
                            bank=None, debts=None, notes=None, priority=None,
                            regenerate_feedback=False
                        )
                    except KeyboardInterrupt:
                        console.print("\n[yellow]Edit cancelled[/yellow]")
                    except Exception as e:
                        console.print(f"\n[red]Error: {e}[/red]")
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                else:
                    console.print("[red]Invalid entry number[/red]")
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
        elif choice.lower() == 'r':
            # Remove mode
            entry_num = Prompt.ask("Enter entry number to remove", default="")
            if entry_num.isdigit():
                idx = int(entry_num)
                if 1 <= idx <= len(entries):
                    selected_entry = entries[idx - 1]
                    if Confirm.ask(f"Delete entry for {selected_entry.date}? This cannot be undone.", default=False):
                        from tracker.core.database import SessionLocal
                        db = SessionLocal()
                        try:
                            from tracker.services.entry_service import EntryService
                            service = EntryService(db)
                            service.delete_entry(selected_entry.id, user_id=1)
                            console.print(f"\n[green]{icon('✓', 'Deleted')} Entry for {selected_entry.date} has been removed[/green]")
                        except Exception as e:
                            console.print(f"\n[red]Error deleting entry: {e}[/red]")
                        finally:
                            db.close()
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                else:
                    console.print("[red]Invalid entry number[/red]")
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()

def show_entry_detail(entry):
    """Show detailed view of an entry"""
    from tracker.core.database import SessionLocal
    from tracker.services.feedback_service import FeedbackService
    from rich.panel import Panel
    
    console = get_console()
    console.clear()
    console.print()
    
    # Calculate totals
    total_income = entry.income_today + entry.side_income
    total_expenses = entry.bills_due_today + entry.food_spent + entry.gas_spent
    balance = total_income - total_expenses
    
    is_narrow = console.width < 80
    
    # Build detail view - responsive layout
    if not is_narrow:
        detail = f"""[bold cyan]{icon('📅', 'Date')} Entry for {entry.date}[/bold cyan]

[bold]{icon('💰', 'Finance')} Financial Summary[/bold]
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

[bold]{icon('📊', 'Work')} Work & Wellbeing[/bold]
  Hours Worked:    {entry.hours_worked}
  Stress Level:    {entry.stress_level}/10
  Priority:        {entry.priority or '[dim]none[/dim]'}

[bold]{icon('📝', 'Notes')} Notes[/bold]
{_format_notes(entry.notes) or '[dim]No notes for this day[/dim]'}
"""
    else:
        # Narrow view - compact format
        detail = f"""[bold cyan]{icon('📅', '')} {entry.date}[/bold cyan]

[bold]{icon('💰', '')} Financial[/bold]
  Income: ${total_income:.2f}
  Expenses: ${total_expenses:.2f}
  Balance: {'[green]' if balance >= 0 else '[red]'}${balance:.2f}[/]

[bold]{icon('📊', '')} Work[/bold]
  Hours: {entry.hours_worked}
  Stress: {entry.stress_level}/10
  Priority: {entry.priority or '[dim]none[/dim]'}

[bold]{icon('📝', '')} Notes[/bold]
{_format_notes(entry.notes) or '[dim]none[/dim]'}
"""
    
    console.print(Panel(detail, border_style="cyan", padding=(1, 1) if is_narrow else (1, 2)))
    
    # Get AI feedback if available
    with SessionLocal() as db:
        feedback_service = FeedbackService(db)
        feedback = feedback_service.get_feedback_by_entry(entry.id)
        
        if feedback:
            from rich.markdown import Markdown
            
            console.print()
            
            # Render feedback as Markdown
            md = Markdown(feedback.content)
            
            # Create panel with Markdown content
            feedback_panel = Panel(
                md,
                title=f"[bold cyan]{icon('💬', 'Feedback')}Feedback[/bold cyan]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(feedback_panel)
            
            # Show metadata below
            console.print(f"[dim]Generated: {feedback.created_at.strftime('%Y-%m-%d %H:%M')}[/dim]")
        else:
            console.print("\n[dim]No feedback available for this entry[/dim]")
    
    # Offer to continue conversation about this entry
    console.print()
    if Confirm.ask(f"{icon('💬', '')} Continue conversation about this entry?", default=False):
        _start_entry_chat(entry.id)
    else:
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
    
    console = get_console()
    console.print(f"\n[bold cyan]{icon('🔍', 'Search')} Search Entries[/bold cyan]")
    query = Prompt.ask("Enter search term (date, text, or number)", console=console)
    
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
        
        is_narrow = console.width < 80
        
        table = Table(show_header=True, header_style="bold cyan", box=None if is_narrow else None)
        table.add_column("#", style="dim", width=3)
        table.add_column("Date", width=10 if is_narrow else 12)
        
        if not is_narrow:
            table.add_column("Income", justify="right", width=10)
            table.add_column("Expenses", justify="right", width=10)
            table.add_column("Stress", justify="center", width=8)
            table.add_column("Priority", width=30)
        else:
            table.add_column("Net", justify="right", width=9)
            table.add_column("Stress", justify="center", width=7)
            table.add_column("Priority", width=20, no_wrap=False)
        
        for idx, entry in enumerate(entries, 1):
            total_income = entry.income_today + entry.side_income
            total_expenses = entry.bills_due_today + entry.food_spent + entry.gas_spent
            balance = total_income - total_expenses
            
            stress = entry.stress_level
            stress_color = "green" if stress <= 3 else "yellow" if stress <= 6 else "red"
            stress_str = f"[{stress_color}]{stress}/10[/]"
            
            balance_color = "green" if balance >= 0 else "red"
            balance_str = f"[{balance_color}]${balance:.2f}[/]"
            
            if not is_narrow:
                table.add_row(
                    str(idx),
                    str(entry.date),
                    f"${total_income:.2f}",
                    f"${total_expenses:.2f}",
                    stress_str,
                    entry.priority or "[dim]none[/dim]"
                )
            else:
                priority_short = (entry.priority[:17] + "...") if entry.priority and len(entry.priority) > 20 else (entry.priority or "")
                table.add_row(
                    str(idx),
                    str(entry.date),
                    balance_str,
                    stress_str,
                    priority_short or "[dim]none[/dim]"
                )
        
        console.print(table)
        console.print()
        
        # Ask if user wants to view details
        choice = Prompt.ask(
            "Enter # for details, 'e' to edit, 'r' to remove, or Enter to go back",
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
        elif choice.lower() == 'e':
            # Edit mode
            entry_num = Prompt.ask("Enter entry number to edit", default="")
            if entry_num.isdigit():
                idx = int(entry_num)
                if 1 <= idx <= len(entries):
                    selected_entry = entries[idx - 1]
                    from tracker.cli.commands.edit import edit as edit_cmd
                    try:
                        edit_cmd.callback(
                            entry_date=selected_entry.date,
                            stress=None, income=None, bills=None, hours=None,
                            side_income=None, food=None, gas=None, cash=None,
                            bank=None, debts=None, notes=None, priority=None,
                            regenerate_feedback=False
                        )
                    except KeyboardInterrupt:
                        console.print("\n[yellow]Edit cancelled[/yellow]")
                    except Exception as e:
                        console.print(f"\n[red]Error: {e}[/red]")
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                else:
                    console.print("[red]Invalid entry number[/red]")
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
        elif choice.lower() == 'r':
            # Remove mode
            entry_num = Prompt.ask("Enter entry number to remove", default="")
            if entry_num.isdigit():
                idx = int(entry_num)
                if 1 <= idx <= len(entries):
                    selected_entry = entries[idx - 1]
                    if Confirm.ask(f"Delete entry for {selected_entry.date}? This cannot be undone.", default=False):
                        from tracker.core.database import SessionLocal
                        db = SessionLocal()
                        try:
                            from tracker.services.entry_service import EntryService
                            service = EntryService(db)
                            service.delete_entry(selected_entry.id, user_id=1)
                            console.print(f"\n[green]{icon('✓', 'Deleted')} Entry for {selected_entry.date} has been removed[/green]")
                        except Exception as e:
                            console.print(f"\n[red]Error deleting entry: {e}[/red]")
                        finally:
                            db.close()
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                else:
                    console.print("[red]Invalid entry number[/red]")
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()


def handle_stats():
    """Handle statistics"""
    console = get_console()
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
    console = get_console()
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


def _open_chat_native(chat_id: int):
    """Open a chat directly without CliRunner"""
    from tracker.core.database import engine
    from tracker.services.chat import ChatService
    from sqlalchemy.orm import Session
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    
    console = get_console()
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)
        
        chat_obj = chat_service.get_chat(chat_id)
        if not chat_obj:
            console.print(f"\n[red]{icon('❌ ', '')}Chat {chat_id} not found[/red]\n")
            console.print("[dim]Press Enter to continue...[/dim]")
            input()
            return
        
        # Display chat header
        console.print(f"\n[bold cyan]{icon('💬 ', '')}{chat_obj.title}[/bold cyan]")
        if chat_obj.entry_id:
            console.print(f"[dim]Linked to Entry #{chat_obj.entry_id}[/dim]")
        console.print(f"[dim]Created: {chat_obj.created_at.strftime('%Y-%m-%d %H:%M')}[/dim]\n")
        
        # Display message history
        if chat_obj.messages:
            for msg in chat_obj.messages:
                if msg.role == "user":
                    # Render user messages as Markdown
                    md = Markdown(msg.content)
                    console.print(Panel(
                        md,
                        title=f"{icon('👤 ', '')}You",
                        title_align="left",
                        border_style="blue",
                        padding=(0, 1)
                    ))
                elif msg.role == "assistant":
                    # Render AI messages as Markdown
                    md = Markdown(msg.content)
                    console.print(Panel(
                        md,
                        title=f"{icon('💭 ', '')}Tracker",
                        title_align="left",
                        border_style="green",
                        padding=(0, 1)
                    ))
                console.print()
        
        # Interactive chat loop
        _chat_loop_native(console, chat_service, chat_id)


def _start_entry_chat(entry_id: int):
    """Start or continue a chat linked to a specific entry"""
    from tracker.core.database import engine
    from tracker.services.chat import ChatService
    from sqlalchemy.orm import Session
    
    console = get_console()
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)
        
        try:
            # Get or create chat for this entry
            chat_obj = chat_service.get_or_create_entry_chat(entry_id)
            
            console.print(f"\n[bold cyan]{icon('💬', '')} {chat_obj.title}[/bold cyan]")
            if chat_obj.messages:
                console.print(f"[dim]Continuing conversation ({len(chat_obj.messages)} messages)[/dim]\n")
            else:
                console.print(f"[dim]Starting new conversation about this entry[/dim]\n")
            
            # Display existing messages if any
            if chat_obj.messages:
                from rich.markdown import Markdown
                for msg in chat_obj.messages:
                    if msg.role == "user":
                        md = Markdown(msg.content)
                        console.print(Panel(
                            md,
                            title=f"{icon('👤 ', '')}You",
                            title_align="left",
                            border_style="blue",
                            padding=(0, 1)
                        ))
                    elif msg.role == "assistant":
                        md = Markdown(msg.content)
                        console.print(Panel(
                            md,
                            title=f"{icon('💭 ', '')}Tracker",
                            title_align="left",
                            border_style="green",
                            padding=(0, 1)
                        ))
                    console.print()
            
            # Start chat loop
            _chat_loop_native(console, chat_service, chat_obj.id)
            
        except ValueError as e:
            console.print(f"\n[red]{icon('❌ ', '')}Error: {e}[/red]\n")
            console.print("[dim]Press Enter to continue...[/dim]")
            input()


def _start_new_chat():
    """Start a new standalone chat"""
    from tracker.core.database import engine
    from tracker.services.chat import ChatService
    from sqlalchemy.orm import Session
    
    console = get_console()
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)
        
        console.print(f"\n[bold cyan]{icon('💬', '')} New Chat[/bold cyan]\n")
        title = Prompt.ask("[cyan]Chat title[/cyan]", default="General Conversation")
        
        chat_obj = chat_service.create_chat(title=title)
        console.print(f"\n[bold cyan]{icon('💬', '')} {title}[/bold cyan]")
        console.print(f"[dim]Chat ID: {chat_obj.id}[/dim]\n")
        console.print(f"[dim]What's on your mind?[/dim]\n")
        
        # Start chat loop
        _chat_loop_native(console, chat_service, chat_obj.id)


def _show_transcript(console, chat_service, chat_id: int):
    """Show chat transcript in scrollable pager-style view"""
    from rich.panel import Panel
    from rich.markdown import Markdown
    import subprocess
    import tempfile
    import os
    
    # Get chat with messages
    chat_obj = chat_service.get_chat(chat_id)
    if not chat_obj or not chat_obj.messages:
        console.print("\n[yellow]No messages in this chat yet[/yellow]\n")
        console.print("[dim]Press Enter to continue...[/dim]")
        input()
        return
    
    # Build transcript content as renderable string
    from io import StringIO
    from rich.console import Console as RichConsole
    
    # Create a string buffer to capture the output
    string_buffer = StringIO()
    temp_console = RichConsole(file=string_buffer, width=console.width, legacy_windows=False)
    
    # Render header
    temp_console.print()
    temp_console.print(Panel.fit(
        f"[bold cyan]{icon('💬', '')} {chat_obj.title}[/bold cyan]\n"
        f"[dim]{len(chat_obj.messages)} messages[/dim]",
        border_style="cyan"
    ))
    temp_console.print()
    
    # Render all messages
    for msg in chat_obj.messages:
        if msg.role == "user":
            md = Markdown(msg.content)
            temp_console.print(Panel(
                md,
                title=f"{icon('👤 ', '')}You",
                title_align="left",
                border_style="blue",
                padding=(0, 1)
            ))
        elif msg.role == "assistant":
            md = Markdown(msg.content)
            temp_console.print(Panel(
                md,
                title=f"{icon('💭 ', '')}Tracker",
                title_align="left",
                border_style="green",
                padding=(0, 1)
            ))
        temp_console.print()
    
    # Get the rendered content
    transcript_content = string_buffer.getvalue()
    
    # Try to use less for scrolling, fallback to simple display
    try:
        # Create a temporary file with the transcript
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            # Strip ANSI codes for less compatibility
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            clean_content = ansi_escape.sub('', transcript_content)
            f.write(clean_content)
            temp_file = f.name
        
        # Use less if available
        subprocess.run(['less', '-R', temp_file], check=True)
        os.unlink(temp_file)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        # Fallback: clear screen and display with prompt
        console.clear()
        console.print(transcript_content)
        console.print("[dim]Press Enter to return to chat...[/dim]")
        input()


def _chat_loop_native(console, chat_service, chat_id: int):
    """Interactive chat loop for TUI"""
    from rich.panel import Panel
    from rich.markdown import Markdown
    from types import SimpleNamespace

    def _coerce_msg(message):
        """Normalize message objects from ORM or temp placeholders."""
        if isinstance(message, SimpleNamespace):
            return message.role, message.content
        if isinstance(message, dict):
            return message.get("role"), message.get("content")
        return getattr(message, "role", None), getattr(message, "content", "")

    def _render_messages(messages):
        """Render the last few chat messages as panels."""
        recent_messages = messages[-6:]
        for msg in recent_messages:
            role, content = _coerce_msg(msg)
            if content is None:
                content = ""
            if role == "user":
                md = Markdown(content)
                console.print(Panel(
                    md,
                    title=f"{icon('👤 ', '')}You",
                    title_align="left",
                    border_style="blue",
                    padding=(0, 1)
                ))
            elif role == "assistant":
                md = Markdown(content)
                console.print(Panel(
                    md,
                    title=f"{icon('💭 ', '')}Tracker",
                    title_align="left",
                    border_style="green",
                    padding=(0, 1)
                ))
            console.print()

    def _refresh_view(*, extra_messages=None):
        """Clear screen and show recent messages, with optional pending ones."""
        chat_obj = chat_service.get_chat(chat_id)
        messages = list(chat_obj.messages) if chat_obj and chat_obj.messages else []
        if extra_messages:
            messages.extend(extra_messages)
        console.clear(reset=False)  # Use reset=False to reduce flicker
        if messages:
            _render_messages(messages)
        else:
            console.print("[dim]Start the conversation with your first message.[/dim]\n")

    def _show_hint():
        console.print("[dim]'exit' to quit | 'clear' to clear | 'transcript' to view history[/dim]")

    # Initial render
    _refresh_view()
    _show_hint()
    
    while True:
        try:
            user_input = Prompt.ask(f"{icon('💬 ', '')}You")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                console.print(f"\n[yellow]{icon('👋 ', '')}Chat saved. Returning to menu...[/yellow]\n")
                console.print("[dim]Press Enter to continue...[/dim]")
                input()
                break
            
            if user_input.lower() == 'clear':
                _refresh_view()
                _show_hint()
                continue  # Just loop again, which clears
            
            if user_input.lower() == 'transcript':
                _show_transcript(console, chat_service, chat_id)
                _refresh_view()
                _show_hint()
                continue
            
            if not user_input.strip():
                _refresh_view()
                _show_hint()
                continue
            
            # Show user message immediately so history stays visible
            pending_user = SimpleNamespace(role="user", content=user_input)
            _refresh_view(extra_messages=[pending_user])
            console.print()
            
            try:
                with console.status(f"[dim]{icon('⏳ ', '')}Thinking...[/dim]", spinner="dots"):
                    chat_service.send_message(chat_id, user_input)
                # Only refresh after successful message to minimize screen clearing
                _refresh_view()
                _show_hint()
            except Exception as e:
                console.print(f"\n[red]{icon('❌ ', '')}Error: {e}[/red]\n")
                console.print("[dim]Check that your provider is configured and running[/dim]\n")
                if not Confirm.ask("Try again?", default=True):
                    console.print("[dim]Press Enter to continue...[/dim]")
                    input()
                    break
                # Only refresh on error if user wants to try again
                _refresh_view()
                _show_hint()
                continue
        
        except KeyboardInterrupt:
            console.print(f"\n\n[yellow]{icon('👋 ', '')}Chat saved. Returning to menu...[/yellow]\n")
            console.print("[dim]Press Enter to continue...[/dim]")
            input()
            break
        except EOFError:
            break


def handle_chat():
    """Handle AI chat"""
    console = get_console()
    
    from tracker.cli.commands.chat import chat as chat_cmd
    from tracker.core.database import engine
    from tracker.services.chat import ChatService
    from sqlalchemy.orm import Session
    from rich.table import Table
    from click.testing import CliRunner
    
    # List chats first
    console.print("\n[bold cyan]💬 Chats[/bold cyan]\n")
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)
        chats = chat_service.list_chats()
        
        if not chats:
            console.print("[yellow]No chats found[/yellow]\n")
            console.print("  [cyan]1.[/cyan] Start New Chat")
            console.print("  [cyan]0.[/cyan] Back")
            
            choice = Prompt.ask("\nSelect option", choices=["0", "1"], default="0")
            
            if choice == "1":
                _start_new_chat()
            return
        
        # Display chats table - responsive
        is_narrow = console.width < 80
        
        table = Table(title=f"{icon('💬 ', '')}Your Chats", box=None if is_narrow else None)
        table.add_column("#", style="cyan", width=3)
        
        if not is_narrow:
            table.add_column("ID", style="dim", width=6)
            table.add_column("Title", style="bold")
            table.add_column("Type", width=12)
            table.add_column("Messages", justify="right", width=10)
            table.add_column("Last Updated", width=18)
        else:
            table.add_column("Title", style="bold", no_wrap=False)
            table.add_column("Msgs", justify="right", width=5)
            table.add_column("Updated", width=10)
        
        # Create mapping of selection numbers to chat IDs
        chat_map = {}
        for idx, chat_obj in enumerate(chats, 1):
            chat_type = f"{icon('📝 ', '')}Entry #{chat_obj.entry_id}" if chat_obj.entry_id else f"{icon('💭 ', '')}Standalone"
            msg_count = len(chat_obj.messages) if hasattr(chat_obj, 'messages') else 0
            title = chat_obj.title
            
            if not is_narrow:
                table.add_row(
                    str(idx),
                    str(chat_obj.id),
                    title,
                    chat_type,
                    str(msg_count),
                    chat_obj.updated_at.strftime("%Y-%m-%d %H:%M")
                )
            else:
                title_short = (title[:25] + "...") if len(title) > 28 else title
                table.add_row(
                    str(idx),
                    title_short,
                    str(msg_count),
                    chat_obj.updated_at.strftime("%m-%d %H:%M")
                )
            chat_map[str(idx)] = chat_obj.id
        
        console.print(table)
        console.print()
        
        # Show options
        console.print("  [cyan]#[/cyan] Enter chat number to open")
        console.print("  [cyan]n[/cyan] Start New Chat")
        console.print("  [cyan]0[/cyan] Back")
        
        # Build choices dynamically
        choices = ["0", "n"] + [str(i) for i in range(1, len(chats) + 1)]
        choice = Prompt.ask("\nSelect option", choices=choices, default="0")
        
        if choice == "0":
            return
        elif choice == "n":
            # New chat - create directly instead of using CliRunner
            _start_new_chat()
        elif choice.isdigit() and choice in chat_map:
            # Open selected chat directly
            chat_id = chat_map[choice]
            _open_chat_native(chat_id)


def handle_config():
    """Handle configuration"""
    console = get_console()
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
    console = get_console()
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


def _edit_profile_fields(console, service, user_id: int):
    """Edit individual profile fields one at a time"""
    from rich.table import Table
    
    # Get current profile
    try:
        summary = service.get_profile_summary(user_id)
        basic = summary["basic_info"]
        emotional = summary["emotional_baseline"]
    except:
        console.print("[yellow]No profile found. Create one first.[/yellow]")
        return
    
    console.print(f"\n[bold cyan]{icon('✏️', 'Edit')} Edit Profile[/bold cyan]")
    console.print("[dim]Choose a section, then update individual fields[/dim]\n")
    
    console.print("[bold]What would you like to update?[/bold]")
    console.print("  [cyan]1.[/cyan] Basic info (nickname, tone, context depth)")
    console.print("  [cyan]2.[/cyan] Emotional baseline (energy, stress, triggers)")
    console.print("  [cyan]3.[/cyan] Work information")
    console.print("  [cyan]4.[/cyan] Financial information")
    console.print("  [cyan]5.[/cyan] Goals")
    console.print("  [cyan]0.[/cyan] Back")
    
    choice = Prompt.ask("\nSelect section", choices=["0", "1", "2", "3", "4", "5"], default="0")
    
    if choice == "0":
        return
    
    console.print("\n[dim]Press Enter to keep current value, or type new value[/dim]\n")
    
    if choice == "1":
        # Basic Information
        console.print("[bold]Basic Information[/bold]\n")
        
        current_nickname = basic.get('nickname') or "Not set"
        console.print(f"[dim]Current: {current_nickname}[/dim]")
        new_nickname = Prompt.ask("Nickname", default="")
        if new_nickname:
            service.update_basic_info(user_id, nickname=new_nickname)
            console.print(f"[green]{icon('✓', '')} Updated![/green]")
        
        # Tone
        current_tone = basic.get('preferred_tone') or "Not set"
        console.print(f"\n[dim]Current: {current_tone}[/dim]")
        console.print("Preferred Tone: 1=casual, 2=professional, 3=encouraging, 4=stoic")
        tone_choice = Prompt.ask("Choose (or Enter to skip)", default="")
        if tone_choice in ["1", "2", "3", "4"]:
            tone_map = {"1": "casual", "2": "professional", "3": "encouraging", "4": "stoic"}
            service.update_basic_info(user_id, preferred_tone=tone_map[tone_choice])
            console.print(f"[green]{icon('✓', '')} Updated![/green]")
        
        # Context depth
        current_depth = basic.get('context_depth') or "basic"
        console.print(f"\n[dim]Current: {current_depth}[/dim]")
        console.print("Context Depth: 1=basic, 2=personal, 3=deep")
        depth_choice = Prompt.ask("Choose (or Enter to skip)", default="")
        if depth_choice in ["1", "2", "3"]:
            depth_map = {"1": "basic", "2": "personal", "3": "deep"}
            service.update_basic_info(user_id, context_depth=depth_map[depth_choice])
            console.print(f"[green]{icon('✓', '')} Updated![/green]")
    
    elif choice == "2":
        # Emotional Baseline
        console.print("[bold]Emotional Baseline[/bold]\n")
        
        current_energy = emotional.get('energy', 5)
        console.print(f"[dim]Current: {current_energy}/10[/dim]")
        new_energy = Prompt.ask("Average energy level (1-10, or Enter to skip)", default="")
        if new_energy:
            service.update_emotional_context(user_id, baseline_energy=int(new_energy))
            console.print(f"[green]{icon('✓', '')} Updated![/green]")
        
        current_stress = emotional.get('stress', 5)
        console.print(f"\n[dim]Current: {current_stress}/10[/dim]")
        new_stress = Prompt.ask("Average stress level (1-10, or Enter to skip)", default="")
        if new_stress:
            service.update_emotional_context(user_id, baseline_stress=float(new_stress))
            console.print(f"[green]{icon('✓', '')} Updated![/green]")
        
        # Get current triggers as comma-separated string
        try:
            import json
            current_triggers = json.loads(emotional.get('stress_triggers', '[]')) if isinstance(emotional.get('stress_triggers'), str) else emotional.get('stress_triggers', [])
            current_triggers_str = ', '.join(current_triggers) if current_triggers else ''
        except:
            current_triggers_str = ''
        
        console.print(f"\n[dim]Current triggers: {current_triggers_str or 'None'}[/dim]")
        console.print("[dim]Stress triggers (comma-separated, edit to add/remove)[/dim]")
        new_triggers = Prompt.ask("Triggers", default=current_triggers_str)
        if new_triggers != current_triggers_str:
            triggers = [t.strip() for t in new_triggers.split(",") if t.strip()]
            service.update_emotional_context(user_id, stress_triggers=triggers)
            console.print(f"[green]{icon('✓', '')} Updated![/green]")
        
        # Get current activities as comma-separated string
        try:
            current_activities = json.loads(emotional.get('calming_activities', '[]')) if isinstance(emotional.get('calming_activities'), str) else emotional.get('calming_activities', [])
            current_activities_str = ', '.join(current_activities) if current_activities else ''
        except:
            current_activities_str = ''
        
        console.print(f"\n[dim]Current activities: {current_activities_str or 'None'}[/dim]")
        console.print("[dim]Calming activities (comma-separated, edit to add/remove)[/dim]")
        new_activities = Prompt.ask("Activities", default=current_activities_str)
        if new_activities != current_activities_str:
            activities = [a.strip() for a in new_activities.split(",") if a.strip()]
            service.update_emotional_context(user_id, calming_activities=activities)
            console.print(f"[green]{icon('✓', '')} Updated![/green]")
    
    elif choice == "3":
        _edit_work_info(console, service, user_id)
    elif choice == "4":
        _edit_financial_info(console, service, user_id)
    elif choice == "5":
        _edit_goals(console, service, user_id)
    elif choice in ["6"]:
        console.print("\n[yellow]Lifestyle editing coming soon![/yellow]")
    
    console.print(f"\n[green]{icon('✅', 'Done')} Profile updated![/green]")


def _edit_work_info(console, service, user_id: int):
    """Edit work information field by field"""
    console.print("[bold]Work Information[/bold]\n")
    console.print("[dim]Enter new value or press Enter to keep current[/dim]\n")
    
    # Get current work info
    try:
        summary = service.get_profile_summary(user_id)
        work = summary.get("work", {})
    except:
        work = {}
    
    # Job title
    current = work.get('job_title', 'Not set')
    console.print(f"[dim]Current: {current}[/dim]")
    job_title = Prompt.ask("Job title", default=work.get('job_title', ''))
    
    # Employment type
    current = work.get('employment_type', 'Not set')
    console.print(f"\n[dim]Current: {current}[/dim]")
    console.print("1=hourly, 2=salary")
    emp_choice = Prompt.ask("Employment type", default="")
    employment_type = {"1": "hourly", "2": "salary"}.get(emp_choice, work.get('employment_type', 'hourly'))
    
    # Pay schedule
    current = work.get('pay_schedule', 'Not set')
    console.print(f"\n[dim]Current: {current}[/dim]")
    console.print("1=weekly, 2=biweekly, 3=monthly")
    pay_choice = Prompt.ask("Pay schedule", default="")
    pay_schedule = {"1": "weekly", "2": "biweekly", "3": "monthly"}.get(pay_choice, work.get('pay_schedule', 'biweekly'))
    
    # Hours per week
    current = work.get('typical_hours_per_week', 'Not set')
    console.print(f"\n[dim]Current: {current}[/dim]")
    hours_str = Prompt.ask("Typical hours per week", default=str(work.get('typical_hours_per_week', 40)))
    hours_per_week = float(hours_str) if hours_str else 40
    
    # Commute
    current = work.get('commute_minutes', 'Not set')
    console.print(f"\n[dim]Current: {current}[/dim]")
    commute_str = Prompt.ask("Commute time (minutes)", default=str(work.get('commute_minutes', 0)))
    commute_minutes = int(commute_str) if commute_str else 0
    
    work_data = {
        "job_title": job_title,
        "employment_type": employment_type,
        "pay_schedule": pay_schedule,
        "typical_hours_per_week": hours_per_week,
        "commute_minutes": commute_minutes,
        "side_gigs": work.get('side_gigs', [])
    }
    
    # Side gigs
    console.print(f"\n[dim]Current side gigs: {len(work.get('side_gigs', []))}[/dim]")
    if Confirm.ask("Update side gigs?", default=False):
        console.print("[dim]Enter side gigs (type 'done' when finished)[/dim]")
        side_gigs = []
        while True:
            gig_name = Prompt.ask("Side gig name (or 'done')")
            if gig_name.lower() == "done":
                break
            gig_income = float(Prompt.ask(f"Monthly income from {gig_name}"))
            side_gigs.append({"name": gig_name, "typical_income": gig_income})
        work_data["side_gigs"] = side_gigs
    
    service.update_work_info(user_id, work_data)
    console.print(f"[green]{icon('✓', '')} Work info updated![/green]")


def _edit_financial_info(console, service, user_id: int):
    """Edit financial information field by field"""
    console.print("[bold]Financial Information[/bold]\n")
    console.print("[dim]Enter new value or press Enter to keep current[/dim]\n")
    
    # Get current financial info
    try:
        summary = service.get_profile_summary(user_id)
        financial = summary.get("financial", {})
    except:
        financial = {}
    
    # Monthly income
    current = financial.get('monthly_income', 'Not set')
    console.print(f"[dim]Current: ${current}[/dim]")
    income_str = Prompt.ask("Monthly net income", default=str(financial.get('monthly_income', 0)))
    monthly_income = float(income_str) if income_str else 0
    
    financial_data = {
        "monthly_income": monthly_income,
        "income_sources": financial.get('income_sources', []),
        "recurring_bills": financial.get('recurring_bills', []),
        "debts": financial.get('debts', [])
    }
    
    # Recurring bills
    console.print(f"\n[dim]Current recurring bills: {len(financial.get('recurring_bills', []))}[/dim]")
    if Confirm.ask("Update recurring bills?", default=False):
        console.print("[dim]Enter bills (type 'done' when finished)[/dim]")
        bills = []
        while True:
            bill_name = Prompt.ask("Bill name (or 'done')")
            if bill_name.lower() == "done":
                break
            bill_amount = float(Prompt.ask(f"Amount for {bill_name}"))
            bill_due_day = int(Prompt.ask(f"Day of month due"))
            bills.append({"name": bill_name, "amount": bill_amount, "due_day": bill_due_day})
        financial_data["recurring_bills"] = bills
    
    # Debts
    console.print(f"\n[dim]Current debts tracked: {len(financial.get('debts', []))}[/dim]")
    if Confirm.ask("Update debts?", default=False):
        console.print("[dim]Enter debts (type 'done' when finished)[/dim]")
        debts = []
        while True:
            debt_name = Prompt.ask("Debt name (or 'done')")
            if debt_name.lower() == "done":
                break
            debt_balance = float(Prompt.ask(f"Current balance"))
            debt_min = float(Prompt.ask(f"Minimum payment"))
            debt_rate = float(Prompt.ask(f"Interest rate (%)", default="0"))
            debts.append({
                "name": debt_name,
                "balance": debt_balance,
                "min_payment": debt_min,
                "interest_rate": debt_rate
            })
        financial_data["debts"] = debts
    
    service.update_financial_info(user_id, financial_data)
    console.print(f"[green]{icon('✓', '')} Financial info updated![/green]")


def _edit_goals(console, service, user_id: int):
    """Edit goals field by field"""
    console.print("[bold]Goals[/bold]\n")
    console.print("[dim]Enter new goals or press Enter to keep current[/dim]\n")
    
    # Get current goals
    try:
        summary = service.get_profile_summary(user_id)
        goals = summary.get("goals", {})
    except:
        goals = {}
    
    goals_data = {
        "short_term": goals.get('short_term', []),
        "long_term": goals.get('long_term', [])
    }
    
    # Short-term goals
    console.print(f"[dim]Current short-term goals: {len(goals.get('short_term', []))}[/dim]")
    if Confirm.ask("Update short-term goals? (3-6 months)", default=False):
        console.print("[dim]Enter goals (type 'done' when finished)[/dim]")
        short_term = []
        while True:
            goal = Prompt.ask("Goal (or 'done')")
            if goal.lower() == "done":
                break
            target_date = Prompt.ask("Target date (YYYY-MM-DD)", default="")
            target_amount = Prompt.ask("Target amount ($)", default="0")
            short_term.append({
                "goal": goal,
                "target_date": target_date,
                "target_amount": float(target_amount) if target_amount else 0
            })
        goals_data["short_term"] = short_term
    
    # Long-term goals
    console.print(f"\n[dim]Current long-term goals: {len(goals.get('long_term', []))}[/dim]")
    if Confirm.ask("Update long-term goals? (6+ months)", default=False):
        console.print("[dim]Enter goals (type 'done' when finished)[/dim]")
        long_term = []
        while True:
            goal = Prompt.ask("Goal (or 'done')")
            if goal.lower() == "done":
                break
            target_date = Prompt.ask("Target date (YYYY-MM-DD)", default="")
            target_amount = Prompt.ask("Target amount ($)", default="0")
            long_term.append({
                "goal": goal,
                "target_date": target_date,
                "target_amount": float(target_amount) if target_amount else 0
            })
        goals_data["long_term"] = long_term
    
    service.update_goals(user_id, goals_data)
    console.print(f"[green]{icon('✓', '')} Goals updated![/green]")


def handle_profile():
    """Handle profile management"""
    from tracker.core.database import SessionLocal
    from tracker.services.profile_service import ProfileService
    from rich.table import Table
    from rich.panel import Panel
    
    console = get_console()
    
    with SessionLocal() as db:
        service = ProfileService(db)
        
        while True:
            console.clear()
            console.print()
            
            is_narrow = console.width < 80
            title_text = f"[bold cyan]{icon('👤', 'Profile')} Profile[/bold cyan]" if is_narrow else f"[bold cyan]{icon('👤', 'Profile')} User Profile[/bold cyan]\n[dim]Manage your personal information[/dim]"
            
            console.print(Panel.fit(
                title_text,
                border_style="cyan"
            ))
            console.print()
            
            # Try to get profile summary
            try:
                summary = service.get_profile_summary(1)
                
                # Display current profile - responsive
                is_narrow = console.width < 80
                
                table = Table(show_header=False, box=None, padding=(0, 1) if is_narrow else (0, 2))
                table.add_column("Field", style="cyan", width=18 if is_narrow else None)
                table.add_column("Value", style="white", no_wrap=False)
                
                basic = summary["basic_info"]
                table.add_row("Nickname", basic.get('nickname') or '[dim]Not set[/dim]')
                table.add_row("Tone", basic.get('preferred_tone') or '[dim]Not set[/dim]')
                table.add_row("Context", basic.get('context_depth') or 'basic')
                
                stats = summary["stats"]
                table.add_row("", "")  # Spacer
                table.add_row("Entries", str(stats['total_entries']))
                table.add_row("Streak", f"{stats['current_streak']} days")
                
                emotional = summary["emotional_baseline"]
                table.add_row("", "")  # Spacer
                
                # Format energy and stress with progress bars
                energy_val = float(emotional['energy'])
                stress_val = float(emotional['stress'])
                energy_bar = format_progress_bar(energy_val, width=12, show_value=True)
                stress_bar = format_progress_bar(stress_val, width=12, show_value=True)
                
                table.add_row("Energy", energy_bar)
                table.add_row("Stress", stress_bar)
                
                console.print(table)
                console.print()
                
                profile_exists = True
            except Exception:
                console.print("[yellow]No profile found[/yellow]\n")
                profile_exists = False
            
            # Show menu
            if profile_exists:
                console.print("  [cyan]1.[/cyan] Update Nickname")
                console.print("  [cyan]2.[/cyan] Update Tone & Preferences")
                console.print("  [cyan]3.[/cyan] Update Emotional Baseline")
                console.print("  [cyan]4.[/cyan] Full Profile Setup")
                console.print("  [cyan]5.[/cyan] Edit Individual Fields")
                console.print("  [cyan]0.[/cyan] Back")
                choices = ["0", "1", "2", "3", "4", "5"]
            else:
                console.print("  [cyan]1.[/cyan] Create Profile (Setup Wizard)")
                console.print("  [cyan]0.[/cyan] Back")
                choices = ["0", "1"]
            
            console.print()
            choice = Prompt.ask("Select option", choices=choices, default="0")
            
            if choice == "0":
                break
            elif choice == "1":
                if profile_exists:
                    # Update nickname
                    nickname = Prompt.ask("Enter new nickname (or press Enter to skip)", default="")
                    if nickname:
                        service.update_basic_info(1, nickname=nickname)
                        console.print(f"\n[green]{icon('✓', 'Success')} Nickname updated to '{nickname}'[/green]")
                        console.print("\n[dim]Press Enter to continue...[/dim]")
                        input()
                else:
                    # Run setup wizard directly
                    from tracker.cli.commands.profile import setup as profile_setup
                    try:
                        profile_setup.callback(user_id=1)
                    except SystemExit:
                        pass  # Normal exit
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
            elif choice == "2":
                # Update tone
                console.print("\n[bold]Preferred Tone[/bold]")
                console.print("  1. Casual & friendly")
                console.print("  2. Professional & direct")
                console.print("  3. Encouraging & supportive")
                console.print("  4. Stoic & analytical")
                tone_choice = Prompt.ask("Choose", choices=["1", "2", "3", "4"], default="1")
                tone_map = {"1": "casual", "2": "professional", "3": "encouraging", "4": "stoic"}
                preferred_tone = tone_map[tone_choice]
                
                console.print("\n[bold]Context Depth[/bold]")
                console.print("  1. Basic - Just spending & stress tracking")
                console.print("  2. Personal - Include work, bills, and goals")
                console.print("  3. Deep - Full context for richest insights")
                depth_choice = Prompt.ask("Choose", choices=["1", "2", "3"], default="1")
                depth_map = {"1": "basic", "2": "personal", "3": "deep"}
                context_depth = depth_map[depth_choice]
                
                service.update_basic_info(1, preferred_tone=preferred_tone, context_depth=context_depth)
                console.print(f"\n[green]{icon('✓', 'Success')} Preferences updated![/green]")
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
            elif choice == "3":
                # Update emotional baseline
                baseline_energy = int(Prompt.ask("Average energy level (1-10)", default="5"))
                baseline_stress = float(Prompt.ask("Average stress level (1-10)", default="5"))
                
                service.update_emotional_context(
                    1,
                    baseline_energy=baseline_energy,
                    baseline_stress=baseline_stress
                )
                console.print(f"\n[green]{icon('✓', 'Success')} Emotional baseline updated![/green]")
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
            elif choice == "4":
                # Run full setup directly
                from tracker.cli.commands.profile import setup as profile_setup
                try:
                    profile_setup.callback(user_id=1)
                except SystemExit:
                    pass  # Normal exit
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
            elif choice == "5":
                # Edit individual fields
                _edit_profile_fields(console, service, 1)
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()
            elif choice == "4_old":
                # Run full setup directly
                from tracker.cli.commands.profile import setup as profile_setup
                try:
                    profile_setup.callback(user_id=1)
                except SystemExit:
                    pass  # Normal exit
                console.print("\n[dim]Press Enter to continue...[/dim]")
                input()


def handle_help():
    """Show help"""
    console = get_console()
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
    console = get_console()
    while True:
        try:
            show_main_menu()
            choice = Prompt.ask("Select option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "h"], default="0")
            
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
                handle_chat()
            elif choice == "5":
                handle_stats()
            elif choice == "6":
                handle_achievements()
            elif choice == "7":
                handle_config()
            elif choice == "8":
                handle_export()
            elif choice == "9":
                handle_profile()
            elif choice == "h":
                handle_help()
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]👋 Goodbye![/yellow]\n")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print("\n[dim]Press Enter to continue...[/dim]")
            input()
