"""New entry command"""

from datetime import date
from decimal import Decimal

import click

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.cli.ui.display import (
    display_entry_preview,
    display_error,
    display_info,
    display_success,
)
from tracker.cli.ui.prompts import (
    prompt_date,
    prompt_decimal,
    prompt_integer_range,
    prompt_text,
)
from tracker.core.database import SessionLocal
from tracker.core.schemas import EntryCreate
from tracker.services.entry_service import EntryService
from tracker.config import settings


def _check_onboarding_needed() -> bool:
    """Check if onboarding is needed (first time use)"""
    
    # Check if AI provider is configured
    try:
        api_key = settings.get_ai_api_key()
        
        # If provider is local, we don't need an API key
        if settings.ai_provider == "local":
            return False
        
        # For other providers, we need an API key
        if not api_key:
            return True
        
        return False
    except Exception:
        return True


def _trigger_onboarding():
    """Trigger the onboarding wizard"""
    from tracker.cli.commands.onboard import onboard
    from click.testing import CliRunner
    
    console = get_console()
    console.print(
        emphasize(
            f"\n[yellow]{icon('👋', 'Welcome')} Let's set up your tracker.[/yellow]",
            "start onboarding",
        )
    )
    console.print("[dim]This is a one-time setup wizard.[/dim]\n")
    
    if not click.confirm("Start onboarding now?", default=True):
        console.print(
            emphasize(
                f"\n[yellow]{icon('⚠️', 'Skip')} Skipping onboarding. You can run it later with: tracker onboard[/yellow]",
                "onboarding skipped",
            )
        )
        console.print(
            "[dim]Note: Feedback will not be available until you complete onboarding.[/dim]\n"
        )
        return False
    
    # Run onboarding
    console.print()
    runner = CliRunner()
    result = runner.invoke(onboard, [])
    
    if result.exit_code == 0:
        console.print(
            emphasize(
                f"\n[green]{icon('✅', 'Done')} Onboarding complete![/green]\n",
                "onboarding complete",
            )
        )
        return True
    else:
        console.print(
            emphasize(
                f"\n[yellow]{icon('⚠️', 'Incomplete')} Onboarding incomplete. You can run it later with: tracker onboard[/yellow]\n",
                "onboarding incomplete",
            )
        )
        return False


@click.command()
@click.option("--quick", is_flag=True, help="Quick mode with fewer prompts")
@click.option("--no-feedback", is_flag=True, help="Skip feedback generation")
@click.option("--date", type=click.DateTime(formats=["%Y-%m-%d"]), help="Entry date (YYYY-MM-DD)")
@click.option("--cash", type=float, help="Cash on hand")
@click.option("--bank", type=float, help="Bank balance")
@click.option("--income", type=float, help="Income today")
@click.option("--bills", type=float, help="Bills due today")
@click.option("--debt", type=float, help="Total debt")
@click.option("--hours", type=float, help="Hours worked")
@click.option("--side", type=float, help="Side income")
@click.option("--food", type=float, help="Food spent")
@click.option("--gas", type=float, help="Gas spent")
@click.option("--stress", type=int, help="Stress level (1-10)")
@click.option("--priority", type=str, help="Today's priority")
@click.option("--notes", type=str, help="Journal entry for the day")
def new(quick, no_feedback, **kwargs):
    """Create a new daily entry"""
    
    # Check if onboarding is needed (first time use)
    if _check_onboarding_needed():
        _trigger_onboarding()
    
    console = get_console()
    console.print(
        f"\n[bold blue]{icon('📝', 'New')} Create New Entry[/bold blue]\n"
    )
    
    # Check if using non-interactive mode (all flags provided)
    non_interactive = all([
        kwargs.get('date'),
        kwargs.get('stress') is not None,
    ])
    
    if non_interactive:
        # Non-interactive mode - use provided flags
        entry_data = _create_from_flags(kwargs)
    else:
        # Interactive mode
        entry_data = _interactive_entry(quick)
    
    if not entry_data:
        return
    
    # Review and edit loop
    while True:
        # Show preview
        display_entry_preview(entry_data)
        
        console.print("\n[bold]What would you like to do?[/bold]")
        console.print(f"[1] {icon('💾', 'Save')} Save this entry")
        console.print(f"[2] {icon('✏️', 'Edit')} Edit a field")
        console.print(f"[3] {icon('❌', 'Cancel')} Cancel")
        
        choice = click.prompt("Choose", type=click.Choice(['1', '2', '3']), default='1')
        
        if choice == '1':
            # Save entry
            _save_entry(entry_data, no_feedback)
            return
        elif choice == '3':
            console.print(
                emphasize(f"[yellow]{icon('⚠️', 'Cancelled')} Entry cancelled.[/yellow]", "entry cancelled")
            )
            return
        else:
            # Edit a field
            entry_data = _edit_entry_data(entry_data, quick)
            if entry_data is None:
                console.print(
                    emphasize(
                        f"[yellow]{icon('⚠️', 'Cancelled')} Entry cancelled.[/yellow]",
                        "entry cancelled",
                    )
                )
                return


def _create_from_flags(kwargs) -> dict:
    """Create entry data from command-line flags"""
    return {
        'date': kwargs['date'].date() if kwargs['date'] else date.today(),
        'cash_on_hand': Decimal(str(kwargs['cash'])) if kwargs.get('cash') is not None else None,
        'bank_balance': Decimal(str(kwargs['bank'])) if kwargs.get('bank') is not None else None,
        'income_today': Decimal(str(kwargs.get('income', 0))),
        'bills_due_today': Decimal(str(kwargs.get('bills', 0))),
        'debts_total': Decimal(str(kwargs['debt'])) if kwargs.get('debt') is not None else None,
        'hours_worked': Decimal(str(kwargs.get('hours', 0))),
        'side_income': Decimal(str(kwargs.get('side', 0))),
        'food_spent': Decimal(str(kwargs.get('food', 0))),
        'gas_spent': Decimal(str(kwargs.get('gas', 0))),
        'stress_level': kwargs['stress'],
        'priority': kwargs.get('priority'),
        'notes': kwargs.get('notes'),
    }


def _interactive_entry(quick: bool) -> dict:
    """Interactive entry creation with prompts"""
    
    try:
        console = get_console()
        # Date
        entry_date = prompt_date(
            "📅 Date (YYYY-MM-DD): ",
            default=date.today()
        )
        
        console.print(
            f"\n[bold cyan]{icon('💰', 'Finance')} Financial Information[/bold cyan]"
        )
        
        # Required fields in quick mode
        if quick:
            cash_on_hand = prompt_decimal("Cash on hand: $", required=False, allow_negative=True)
            bank_balance = prompt_decimal("Bank balance: $", required=False, allow_negative=True)
            income_today = prompt_decimal("Income today: $", default="")
            bills_due_today = Decimal("0")
            debts_total = prompt_decimal("Total debt: $", required=False)
            hours_worked = prompt_decimal("Hours worked: ", default="")
            side_income = Decimal("0")
            food_spent = Decimal("0")
            gas_spent = Decimal("0")
        else:
            cash_on_hand = prompt_decimal("Cash on hand: $", required=False, allow_negative=True)
            bank_balance = prompt_decimal("Bank balance: $", required=False, allow_negative=True)
            income_today = prompt_decimal("Income today: $", default="")
            bills_due_today = prompt_decimal("Bills due today: $", default="")
            debts_total = prompt_decimal("Total debt: $", required=False)
            
            console.print(f"\n[bold cyan]{icon('💼', 'Work')} Work[/bold cyan]")
            hours_worked = prompt_decimal("Hours worked: ", default="")
            side_income = prompt_decimal("Side income: $", default="")
            
            console.print(f"\n[bold cyan]{icon('🛒', 'Spending')} Spending[/bold cyan]")
            food_spent = prompt_decimal("Food spent: $", default="")
            gas_spent = prompt_decimal("Gas spent: $", default="")
        
        console.print(f"\n[bold cyan]{icon('🧘', 'Wellbeing')} Wellbeing[/bold cyan]")
        stress_level = prompt_integer_range("Stress level (1-10): ", 1, 10)
        priority = prompt_text("Today's priority: ", default="")
        
        if not quick:
            console.print(f"\n[bold cyan]{icon('📝', 'Journal')} Journal[/bold cyan]")
            notes = prompt_text("How was your day? (optional, press Enter twice to finish): ", multiline=True)
        else:
            notes = None
        
        return {
            'date': entry_date,
            'cash_on_hand': cash_on_hand,
            'bank_balance': bank_balance,
            'income_today': income_today,
            'bills_due_today': bills_due_today,
            'debts_total': debts_total,
            'hours_worked': hours_worked,
            'side_income': side_income,
            'food_spent': food_spent,
            'gas_spent': gas_spent,
            'stress_level': stress_level,
            'priority': priority if priority else None,
            'notes': notes,
        }
    
    except KeyboardInterrupt:
        console.print(
            emphasize(f"\n\n[yellow]{icon('⚠️', 'Cancelled')} Entry cancelled.[/yellow]", "entry cancelled")
        )
        return None
    except Exception as e:
        display_error(f"Error during input: {e}")
        return None


def _edit_entry_data(entry_data: dict, quick: bool) -> dict:
    """Allow user to edit specific fields"""
    console = get_console()
    
    # Map field numbers to field names
    fields = {
        '1': ('date', icon('📅', 'Date') + " Date", lambda: prompt_date("New date (YYYY-MM-DD): ", default=entry_data['date'])),
        '2': ('cash_on_hand', icon('💵', 'Cash') + " Cash on hand", lambda: prompt_decimal("New cash on hand: $", required=False, allow_negative=True)),
        '3': ('bank_balance', icon('🏦', 'Bank') + " Bank balance", lambda: prompt_decimal("New bank balance: $", required=False, allow_negative=True)),
        '4': ('income_today', icon('💰', 'Income') + " Income today", lambda: prompt_decimal("New income today: $", default="")),
        '5': ('bills_due_today', icon('📋', 'Bills') + " Bills due today", lambda: prompt_decimal("New bills due: $", default="")),
        '6': ('debts_total', icon('💳', 'Debt') + " Total debt", lambda: prompt_decimal("New total debt: $", required=False)),
        '7': ('hours_worked', icon('⏰', 'Hours') + " Hours worked", lambda: prompt_decimal("New hours worked: ", default="")),
        '8': ('side_income', icon('💼', 'Side income') + " Side income", lambda: prompt_decimal("New side income: $", default="")),
        '9': ('food_spent', icon('🍔', 'Food') + " Food spent", lambda: prompt_decimal("New food spent: $", default="")),
        '10': ('gas_spent', icon('⛽', 'Gas') + " Gas spent", lambda: prompt_decimal("New gas spent: $", default="")),
        '11': ('stress_level', icon('🧘', 'Stress') + " Stress level", lambda: prompt_integer_range("New stress level (1-10): ", 1, 10)),
        '12': ('priority', icon('🎯', 'Priority') + " Priority", lambda: prompt_text("New priority: ", default="")),
        '13': ('notes', icon('📝', 'Journal') + " Journal", lambda: prompt_text("How was your day?: ", multiline=True, default="")),
    }
    
    try:
        console.print("\n[bold cyan]Which field would you like to edit?[/bold cyan]")
        
        for num, (key, label, _) in fields.items():
            current_value = entry_data.get(key)
            if current_value is not None:
                if isinstance(current_value, Decimal):
                    display_val = f"${current_value}" if key not in ['hours_worked'] else str(current_value)
                else:
                    display_val = str(current_value)
            else:
                display_val = "[dim]not set[/dim]"
            
            console.print(f"[{num}] {label}: {display_val}")
        
        console.print("[0] ← Go back without changes")
        
        choice = click.prompt(
            "\nField to edit",
            type=click.Choice(['0'] + list(fields.keys())),
            default='0'
        )
        
        if choice == '0':
            return entry_data
        
        # Get the field info
        field_key, field_label, prompt_func = fields[choice]
        
        console.print(f"\n[bold]Editing: {field_label}[/bold]")
        console.print(f"[dim]Current value: {entry_data.get(field_key)}[/dim]")
        
        # Get new value
        new_value = prompt_func()
        
        # Update the entry data
        entry_data[field_key] = new_value
        
        console.print(
            emphasize(
                f"[green]{icon('✅', 'Updated')} Updated {field_label}[/green]\n",
                "field updated",
            )
        )
        
        return entry_data
    
    except KeyboardInterrupt:
        console.print(
            emphasize(f"\n[yellow]{icon('⚠️', 'Cancelled')} Edit cancelled.[/yellow]", "edit cancelled")
        )
        return entry_data
    except Exception as e:
        display_error(f"Error editing field: {e}")
        return entry_data


def _save_entry(entry_data: dict, no_feedback: bool = False):
    """Save entry to database"""
    
    db = SessionLocal()
    console = get_console()
    try:
        service = EntryService(db)
        
        # Get default user
        user = service.get_default_user()
        if not user:
            display_error("No user found. Please run 'tracker init' first.")
            return
        
        # Create schema instance
        entry_create = EntryCreate(**entry_data)
        
        # Save entry
        entry = service.create_entry(user.id, entry_create)
        
        display_success(f"Entry saved for {entry.date}!")
        
        console.print(f"[dim]Entry ID: {entry.id}[/dim]")
        
        # Try to generate AI feedback if configured and not skipped
        if not no_feedback:
            _generate_feedback_if_configured(db, entry)
        else:
            console.print("\n[dim]Skipped feedback generation (--no-feedback flag)[/dim]")
        
        console.print(f"\n[cyan]View your entry:[/cyan] tracker show {entry.date}")
        
    except ValueError as e:
        display_error(str(e))
    except Exception as e:
        display_error(f"Failed to save entry: {e}")
    finally:
        db.close()


def _generate_feedback_if_configured(db, entry):
    """Generate AI feedback if API key is configured"""
    from tracker.config import settings
    from tracker.services.feedback_service import FeedbackService
    from tracker.cli.ui.progress import FeedbackProgress
    from tracker.cli.ui.display import display_feedback
    console = get_console()
    
    # Check if AI is configured (not needed for local provider)
    api_key = settings.get_ai_api_key()
    
    # For local provider, we don't need an API key
    if settings.ai_provider != "local" and not api_key:
        console.print(
            emphasize(
                f"\n[yellow]{icon('💡', 'Tip')} Configure feedback with: tracker onboard[/yellow]",
                "configure ai tip",
            )
        )
        return
    
    try:
        feedback_service = FeedbackService(db)
        
        # Show progress
        with FeedbackProgress(f"{icon('🤖', 'AI')} Generating feedback..."):
            feedback = feedback_service.generate_feedback(entry.id, regenerate=False)
        
        # Display feedback
        console.print()
        display_feedback(feedback)
        
    except Exception as e:
        console.print(
            emphasize(
                f"\n[yellow]{icon('⚠️', 'Warning')} Could not generate feedback: {e}[/yellow]",
                "feedback generation failed",
            )
        )
        console.print("[dim]Your entry was saved successfully.[/dim]")
        console.print(f"\n[cyan]To retry feedback generation:[/cyan] tracker retry {entry.date}")
        console.print(f"[cyan]To check configuration:[/cyan] tracker config show")
