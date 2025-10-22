"""New entry command"""

from datetime import date
from decimal import Decimal

import click
from rich.console import Console

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

console = Console()


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
    
    console.print("\n[yellow]👋 Welcome! Let's set up your tracker.[/yellow]")
    console.print("[dim]This is a one-time setup wizard.[/dim]\n")
    
    if not click.confirm("Start onboarding now?", default=True):
        console.print("\n[yellow]Skipping onboarding. You can run it later with: tracker onboard[/yellow]")
        console.print("[dim]Note: AI feedback will not be available until you complete onboarding.[/dim]\n")
        return False
    
    # Run onboarding
    console.print()
    runner = CliRunner()
    result = runner.invoke(onboard, [])
    
    if result.exit_code == 0:
        console.print("\n[green]✓ Onboarding complete![/green]\n")
        return True
    else:
        console.print("\n[yellow]⚠️  Onboarding incomplete. You can run it later with: tracker onboard[/yellow]\n")
        return False


@click.command()
@click.option("--quick", is_flag=True, help="Quick mode with fewer prompts")
@click.option("--no-feedback", is_flag=True, help="Skip AI feedback generation")
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
@click.option("--notes", type=str, help="Notes about the day")
def new(quick, no_feedback, **kwargs):
    """Create a new daily entry"""
    
    # Check if onboarding is needed (first time use)
    if _check_onboarding_needed():
        _trigger_onboarding()
    
    console.print("\n[bold blue]📝 Create New Entry[/bold blue]\n")
    
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
    
    # Show preview and confirm
    display_entry_preview(entry_data)
    
    if not click.confirm("\n💾 Save this entry?", default=True):
        console.print("[yellow]Entry cancelled.[/yellow]")
        return
    
    # Save entry
    _save_entry(entry_data, no_feedback)


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
        # Date
        entry_date = prompt_date(
            "📅 Date (YYYY-MM-DD): ",
            default=date.today()
        )
        
        console.print("\n[bold cyan]💰 Financial Information[/bold cyan]")
        
        # Required fields in quick mode
        if quick:
            cash_on_hand = prompt_decimal("Cash on hand: $", required=False, allow_negative=True)
            bank_balance = prompt_decimal("Bank balance: $", required=False, allow_negative=True)
            income_today = prompt_decimal("Income today: $", default="0")
            bills_due_today = Decimal("0")
            debts_total = prompt_decimal("Total debt: $", required=False)
            hours_worked = prompt_decimal("Hours worked: ", default="0")
            side_income = Decimal("0")
            food_spent = Decimal("0")
            gas_spent = Decimal("0")
        else:
            cash_on_hand = prompt_decimal("Cash on hand: $", required=False, allow_negative=True)
            bank_balance = prompt_decimal("Bank balance: $", required=False, allow_negative=True)
            income_today = prompt_decimal("Income today: $", default="0")
            bills_due_today = prompt_decimal("Bills due today: $", default="0")
            debts_total = prompt_decimal("Total debt: $", required=False)
            
            console.print("\n[bold cyan]💼 Work[/bold cyan]")
            hours_worked = prompt_decimal("Hours worked: ", default="0")
            side_income = prompt_decimal("Side income: $", default="0")
            
            console.print("\n[bold cyan]🛒 Spending[/bold cyan]")
            food_spent = prompt_decimal("Food spent: $", default="0")
            gas_spent = prompt_decimal("Gas spent: $", default="0")
        
        console.print("\n[bold cyan]🧘 Wellbeing[/bold cyan]")
        stress_level = prompt_integer_range("Stress level (1-10): ", 1, 10)
        priority = prompt_text("Today's priority: ", default="")
        
        if not quick:
            console.print("\n[bold cyan]📝 Notes[/bold cyan]")
            notes = prompt_text("Notes (optional, press Enter to skip): ", multiline=False)
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
        console.print("\n\n[yellow]Entry cancelled.[/yellow]")
        return None
    except Exception as e:
        display_error(f"Error during input: {e}")
        return None


def _save_entry(entry_data: dict, no_feedback: bool = False):
    """Save entry to database"""
    
    db = SessionLocal()
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
            console.print("\n[dim]Skipped AI feedback generation (--no-feedback flag)[/dim]")
        
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
    
    # Check if AI is configured (not needed for local provider)
    api_key = settings.get_ai_api_key()
    
    # For local provider, we don't need an API key
    if settings.ai_provider != "local" and not api_key:
        console.print("\n[yellow]💡 Tip: Configure AI feedback with: tracker onboard[/yellow]")
        return
    
    try:
        feedback_service = FeedbackService(db)
        
        # Show progress
        with FeedbackProgress("🤖 Generating AI feedback..."):
            feedback = feedback_service.regenerate_feedback(
                entry.id,
                settings.ai_provider,
                api_key,
                settings.ai_model,
                settings.local_api_url if settings.ai_provider == "local" else None
            )
        
        # Display feedback
        console.print()
        display_feedback(feedback)
        
    except Exception as e:
        console.print(f"\n[yellow]⚠️  Could not generate AI feedback: {e}[/yellow]")
        console.print("[dim]Your entry was saved successfully.[/dim]")
