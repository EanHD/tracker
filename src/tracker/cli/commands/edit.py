"""Edit command - Modify existing entries"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

import click
from rich.table import Table

from tracker.cli.ui.console import (
    emphasize,
    get_console,
    icon,
    qualitative_scale,
)
from tracker.cli.ui.prompts import (
    prompt_decimal,
    prompt_integer_range,
    prompt_text,
    prompt_yes_no,
)
from tracker.core.database import SessionLocal
from tracker.core.schemas import EntryUpdate
from tracker.services.entry_service import EntryService
from tracker.services.feedback_service import FeedbackService


@click.command()
@click.argument("entry_date", type=click.DateTime(formats=["%Y-%m-%d"]), required=False)
@click.option("--stress", type=int, help="Update stress level (1-10)")
@click.option("--income", type=float, help="Update income today")
@click.option("--bills", type=float, help="Update bills due today")
@click.option("--hours", type=float, help="Update hours worked")
@click.option("--side-income", type=float, help="Update side income")
@click.option("--food", type=float, help="Update food spending")
@click.option("--gas", type=float, help="Update gas spending")
@click.option("--cash", type=float, help="Update cash on hand")
@click.option("--bank", type=float, help="Update bank balance")
@click.option("--debts", type=float, help="Update total debts")
@click.option("--notes", type=str, help="Update journal entry")
@click.option("--priority", type=str, help="Update priority")
@click.option("--regenerate-feedback", is_flag=True, help="Regenerate feedback after editing")
def edit(
    entry_date: Optional[datetime],
    stress: Optional[int],
    income: Optional[float],
    bills: Optional[float],
    hours: Optional[float],
    side_income: Optional[float],
    food: Optional[float],
    gas: Optional[float],
    cash: Optional[float],
    bank: Optional[float],
    debts: Optional[float],
    notes: Optional[str],
    priority: Optional[str],
    regenerate_feedback: bool,
):
    """
    Edit an existing entry
    
    ENTRY_DATE: Date to edit (YYYY-MM-DD). Defaults to today if not provided.
    
    Examples:
    
      # Interactive mode - prompts for each field
      tracker edit 2025-10-20
      
      # Quick mode - specify fields directly
      tracker edit today --stress 5 --income 450
      
      # Edit multiple fields
      tracker edit 2025-10-20 --stress 7 --bills 300 --notes "Paid rent"
      
      # Regenerate feedback after substantial edits
      tracker edit today --stress 3 --regenerate-feedback
    """
    db = SessionLocal()
    service = EntryService(db)
    
    try:
        console = get_console()
        # Parse date
        if entry_date:
            target_date = entry_date.date()
        else:
            target_date = date.today()
        
        # Get existing entry
        entry = service.get_entry_by_date(1, target_date)  # TODO: Get actual user
        if not entry:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} No entry found for {target_date}[/red]",
                    "entry not found",
                )
            )
            console.print(
                emphasize(
                    f"[yellow]{icon('➕', 'Create')} Create one first:[/yellow] tracker new",
                    "create entry hint",
                )
            )
            return
        
        # Display current entry
        console.print(
            f"\n[bold blue]{icon('✏️', 'Edit')} Editing entry for {target_date}[/bold blue]\n"
        )
        display_current_entry(entry)
        
        # Determine edit mode
        has_cli_flags = any([
            stress, income, bills, hours, side_income, 
            food, gas, cash, bank, debts, notes, priority
        ])
        
        if has_cli_flags:
            # Quick mode - use provided flags
            update_data = build_update_from_flags(
                stress, income, bills, hours, side_income,
                food, gas, cash, bank, debts, notes, priority
            )
        else:
            # Interactive mode - prompt for each field
            update_data = prompt_for_updates(entry)
        
        # Check if any changes were made
        if not update_data:
            console.print(
                emphasize(
                    f"[yellow]{icon('ℹ️', 'Info')} No changes made.[/yellow]",
                    "no changes made",
                )
            )
            return
        
        # Show diff
        console.print(f"\n[bold yellow]{icon('📝', 'Review')} Proposed changes:[/bold yellow]")
        diff = service.get_entry_diff(entry, update_data)
        display_diff(diff)
        
        # Confirm
        if not prompt_yes_no("\nSave these changes?", default=True):
            console.print(
                emphasize(
                    f"[yellow]{icon('⚠️', 'Cancelled')} Edit cancelled.[/yellow]",
                    "edit cancelled",
                )
            )
            return
        
        # Apply updates
        updated_entry = service.update_entry(entry.id, update_data, user_id=1)  # TODO: Get actual user
        if not updated_entry:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} Failed to update entry.[/red]",
                    "update failed",
                )
            )
            return
        
        console.print(
            emphasize(
                f"\n[green]{icon('✅', 'Success')} Entry updated for {target_date}[/green]",
                "entry updated",
            )
        )
        
        # Regenerate feedback if requested or substantial changes
        substantial_change = getattr(updated_entry, '_substantial_change', False)
        if regenerate_feedback or substantial_change:
            if substantial_change and not regenerate_feedback:
                console.print(
                    emphasize(
                        f"\n[yellow]{icon('⚠️', 'Heads up')} Substantial changes detected.[/yellow]",
                        "substantial changes detected",
                    )
                )
                if prompt_yes_no("Regenerate feedback?", default=True):
                    regenerate_feedback = True
            
            if regenerate_feedback:
                console.print(
                    emphasize(
                        f"\n[cyan]{icon('💭')} Regenerating feedback...[/cyan]",
                        "regenerating feedback",
                    )
                )
                try:
                    feedback_service = FeedbackService(db)
                    feedback = feedback_service.generate_feedback(updated_entry.id, regenerate=True)
                    console.print(
                        emphasize(
                            f"[green]{icon('✅', 'Done')} Feedback regenerated[/green]",
                            "feedback regenerated",
                        )
                    )
                except Exception as e:
                    console.print(
                        emphasize(
                            f"[yellow]{icon('⚠️', 'Warning')} Warning: Feedback generation failed: {e}[/yellow]",
                            "feedback generation failed",
                        )
                    )
        
    except Exception as e:
        get_console().print(
            emphasize(f"[red]{icon('❌', 'Error')} Error: {e}[/red]", "edit error")
        )
    finally:
        db.close()


def display_current_entry(entry):
    """Display current entry values"""
    console = get_console()
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Field")
    table.add_column("Current Value")
    
    # Financial fields
    table.add_row("Cash on hand", f"${entry.cash_on_hand or 0:.2f}")
    table.add_row("Bank balance", f"${entry.bank_balance or 0:.2f}")
    table.add_row("Income today", f"${entry.income_today:.2f}")
    table.add_row("Bills due", f"${entry.bills_due_today:.2f}")
    table.add_row("Total debts", f"${entry.debts_total or 0:.2f}")
    
    # Work fields
    table.add_row("Hours worked", f"{entry.hours_worked}")
    table.add_row("Side income", f"${entry.side_income:.2f}")
    
    # Spending fields
    table.add_row("Food spent", f"${entry.food_spent:.2f}")
    table.add_row("Gas spent", f"${entry.gas_spent:.2f}")
    
    # Wellbeing fields
    stress_descriptor = qualitative_scale(
        entry.stress_level,
        low=range(0, 4),
        medium=range(4, 7),
        high=range(7, 11),
    )
    table.add_row(
        "Stress level",
        emphasize(
            f"{entry.stress_level}/10",
            f"{stress_descriptor} stress" if stress_descriptor != "unknown" else None,
        ),
    )
    table.add_row("Priority", entry.priority or "[dim]none[/dim]")
    table.add_row("Journal", entry.notes or "[dim]none[/dim]")
    
    console.print(table)


def build_update_from_flags(
    stress, income, bills, hours, side_income,
    food, gas, cash, bank, debts, notes, priority
) -> EntryUpdate:
    """Build EntryUpdate from CLI flags"""
    data = {}
    
    if stress is not None:
        data['stress_level'] = stress
    if income is not None:
        data['income_today'] = Decimal(str(income))
    if bills is not None:
        data['bills_due_today'] = Decimal(str(bills))
    if hours is not None:
        data['hours_worked'] = Decimal(str(hours))
    if side_income is not None:
        data['side_income'] = Decimal(str(side_income))
    if food is not None:
        data['food_spent'] = Decimal(str(food))
    if gas is not None:
        data['gas_spent'] = Decimal(str(gas))
    if cash is not None:
        data['cash_on_hand'] = Decimal(str(cash))
    if bank is not None:
        data['bank_balance'] = Decimal(str(bank))
    if debts is not None:
        data['debts_total'] = Decimal(str(debts))
    if notes is not None:
        data['notes'] = notes
    if priority is not None:
        data['priority'] = priority
    
    return EntryUpdate(**data)


def prompt_for_updates(entry) -> Optional[EntryUpdate]:
    """Prompt user for field updates interactively"""
    console = get_console()
    console.print(
        emphasize(
            f"\n[yellow]{icon('⌨️', 'Input')} Press Enter to keep current value, or type new value:[/yellow]\n",
            "press enter to keep values",
        )
    )
    
    updates = {}
    
    # Financial fields
    console.print(f"[bold cyan]{icon('💰', 'Finance')} Financial[/bold cyan]")
    cash = prompt_decimal("Cash on hand: $", default=str(entry.cash_on_hand) if entry.cash_on_hand is not None else None, allow_negative=False)
    if cash != entry.cash_on_hand:
        updates['cash_on_hand'] = cash
    
    bank = prompt_decimal("Bank balance: $", default=str(entry.bank_balance) if entry.bank_balance is not None else None, allow_negative=True)
    if bank != entry.bank_balance:
        updates['bank_balance'] = bank
    
    income = prompt_decimal("Income today: $", default=str(entry.income_today))
    if income != entry.income_today:
        updates['income_today'] = income
    
    bills = prompt_decimal("Bills due today: $", default=str(entry.bills_due_today))
    if bills != entry.bills_due_today:
        updates['bills_due_today'] = bills
    
    debts = prompt_decimal("Total debts: $", default=str(entry.debts_total) if entry.debts_total is not None else None, allow_negative=True)
    if debts != entry.debts_total:
        updates['debts_total'] = debts
    
    # Work fields
    console.print(f"\n[bold cyan]{icon('💼', 'Work')} Work[/bold cyan]")
    hours = prompt_decimal("Hours worked: ", default=str(entry.hours_worked))
    if hours != entry.hours_worked:
        updates['hours_worked'] = hours
    
    side = prompt_decimal("Side income: $", default=str(entry.side_income))
    if side != entry.side_income:
        updates['side_income'] = side
    
    # Spending fields
    console.print(f"\n[bold cyan]{icon('🛒', 'Spending')} Spending[/bold cyan]")
    food = prompt_decimal("Food spent: $", default=str(entry.food_spent))
    if food != entry.food_spent:
        updates['food_spent'] = food
    
    gas = prompt_decimal("Gas spent: $", default=str(entry.gas_spent))
    if gas != entry.gas_spent:
        updates['gas_spent'] = gas
    
    # Wellbeing fields
    console.print(f"\n[bold cyan]{icon('🧘', 'Wellbeing')} Wellbeing[/bold cyan]")
    stress = prompt_integer_range("Stress level (1-10): ", default=str(entry.stress_level), min_val=1, max_val=10)
    if stress != entry.stress_level:
        updates['stress_level'] = stress
    
    priority = prompt_text("Priority: ", default=entry.priority or "")
    if priority != (entry.priority or ""):
        updates['priority'] = priority if priority else None
    
    console.print(f"\n[bold cyan]{icon('📓', 'Journal')} Journal[/bold cyan]")
    notes = prompt_text("How was your day?: ", default=entry.notes or "", multiline=True)
    if notes != (entry.notes or ""):
        updates['notes'] = notes if notes else None
    
    if not updates:
        return None
    
    return EntryUpdate(**updates)


def display_diff(diff: dict):
    """Display changes in a formatted table"""
    if not diff:
        get_console().print("[dim]No changes[/dim]")
        return
    
    table = Table(show_header=True, header_style="bold yellow")
    table.add_column("Field")
    table.add_column("Old Value", style="red")
    table.add_column("New Value", style="green")
    
    for field, (old, new) in diff.items():
        # Format field name
        field_name = field.replace('_', ' ').title()
        
        # Format values
        if isinstance(old, Decimal) or isinstance(new, Decimal):
            old_str = f"${old:.2f}" if old is not None else "none"
            new_str = f"${new:.2f}" if new is not None else "none"
        else:
            old_str = str(old) if old is not None else "none"
            new_str = str(new) if new is not None else "none"
        
        table.add_row(field_name, old_str, new_str)
    
    get_console().print(table)
