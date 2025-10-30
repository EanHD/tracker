"""Cash flow tracking commands"""

import csv
import json
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional

import click
from sqlalchemy.orm import Session

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.core.database import SessionLocal
from tracker.core.models import CashFlowEvent, User
from tracker.services.cashflow_config import load_config, get_config_path, set_config_value, save_config, get_config_dir, get_config_dir
from tracker.services.finance.loops import (
    get_week_window,
    get_events_in_range,
    summarize_loops,
    end_of_week_cash,
    get_loop_delta_vs_prior_week,
    calculate_weeks_without_loop,
    get_essentials_total,
    format_cents_to_usd,
)
from tracker.services.finance.forecast import (
    forecast_week,
    tomorrow_budget,
    get_next_payday,
    calculate_gas_fills,
)
from tracker.services.natural_commands import (
    parse_command,
    create_diff,
    apply_adjustment,
    save_audit,
    scan_entry_text,
)
from tracker.core.models import DailyEntry, UserProfile


def get_default_user(db: Session) -> User:
    """Get the default user"""
    user = db.query(User).filter_by(username="default").first()
    if not user:
        raise click.ClickException("No default user found. Run 'tracker init' first.")
    return user


@click.group()
def cashflow():
    """Manage cash flow events and loops"""
    pass


@cashflow.command(name="add-event")
@click.option("--date", type=click.DateTime(formats=["%Y-%m-%d"]), default=str(date.today()), help="Event date (YYYY-MM-DD)")
@click.option("--type", "event_type", required=True, type=click.Choice([
    "income", "bill", "transfer", "spend", "advance", "repayment", "fee"
]), help="Event type")
@click.option("--provider", help="Provider name (e.g., advance_app, tool_truck)")
@click.option("--category", help="Category (e.g., gas, food, rent)")
@click.option("--amount", type=float, required=True, help="Amount in USD (positive for expenses, negative for income)")
@click.option("--account", help="Account name (e.g., chase, cash)")
@click.option("--memo", help="Optional notes")
def add_event(date: datetime, event_type: str, provider: Optional[str], category: Optional[str],
              amount: float, account: Optional[str], memo: Optional[str]):
    """Add a cash flow event"""
    console = get_console()
    
    db = SessionLocal()
    try:
        user = get_default_user(db)
        
        # Convert amount to cents
        amount_cents = int(Decimal(str(amount)) * 100)
        
        # Create event
        event = CashFlowEvent(
            user_id=user.id,
            event_date=date.date(),
            event_type=event_type,
            provider=provider,
            category=category,
            amount_cents=amount_cents,
            account=account,
            memo=memo,
        )
        
        db.add(event)
        db.commit()
        
        console.print(
            emphasize(
                f"\n{icon('✅', 'Added')} Event recorded: {event_type} {format_cents_to_usd(amount_cents)}",
                "event recorded",
            )
        )
        
        if provider:
            console.print(f"  Provider: {provider}")
        if category:
            console.print(f"  Category: {category}")
        if account:
            console.print(f"  Account: {account}")
        console.print(f"  Date: {event.event_date}")
        console.print()
        
    finally:
        db.close()


@cashflow.command(name="week")
@click.option("--end", "end_date", type=click.DateTime(formats=["%Y-%m-%d"]), 
              help="Week end date (defaults to today)")
def week_summary(end_date: Optional[datetime]):
    """Show weekly cash flow summary"""
    console = get_console()
    
    # Load config
    config = load_config()
    
    # Determine week window
    if end_date:
        reference_date = end_date.date()
    else:
        reference_date = date.today()
    
    start, end = get_week_window(
        reference_date,
        config.payroll.week_start,
        config.payroll.payday_is_thursday,
    )
    
    db = SessionLocal()
    try:
        user = get_default_user(db)
        
        console.print(f"\n[bold blue]{icon('📊', 'Week')} Week Summary: {start} → {end}[/bold blue]")
        
        cadence = "Thu payroll cadence" if config.payroll.payday_is_thursday else f"{config.payroll.week_start} week start"
        console.print(f"[dim]({cadence})[/dim]\n")
        
        # Get all events
        events = get_events_in_range(db, user.id, start, end)
        
        if not events:
            console.print(emphasize(
                f"{icon('ℹ️', 'Info')} No events recorded for this week",
                "no events",
            ))
            console.print()
            return
        
        # Calculate income
        income_events = [e for e in events if e.amount_cents < 0]  # Negative = inflow
        income_total = abs(sum(e.amount_cents for e in income_events))
        
        console.print(f"[bold cyan]Income:[/bold cyan] {format_cents_to_usd(-income_total)}")
        
        # Calculate essentials
        essentials_total = get_essentials_total(events, config.essential_categories)
        console.print(f"\n[bold cyan]Essentials:[/bold cyan]")
        
        by_category = {}
        for event in events:
            if event.category and event.category in config.essential_categories and event.amount_cents > 0:
                if event.category not in by_category:
                    by_category[event.category] = 0
                by_category[event.category] += event.amount_cents
        
        for cat, amount in sorted(by_category.items()):
            console.print(f"  {cat.capitalize():12} {format_cents_to_usd(amount)}")
        
        # Loop summaries
        loop_summaries = summarize_loops(db, user.id, config, start, end)
        
        if loop_summaries:
            console.print(f"\n[bold cyan]Loops:[/bold cyan]")
            
            for loop_name, summary in loop_summaries.items():
                if summary["used"]:
                    inflow_str = format_cents_to_usd(-summary["inflow_cents"]) if summary["inflow_cents"] < 0 else "$0.00"
                    outflow_str = format_cents_to_usd(summary["outflow_cents"])
                    net_str = format_cents_to_usd(summary["total_cents"])
                    
                    console.print(f"  {loop_name}:")
                    console.print(f"    +{inflow_str} inflow / -{outflow_str} outflow → net {net_str}")
                    
                    # Get prior week delta
                    prior_start = start - timedelta(days=7)
                    prior_end = end - timedelta(days=7)
                    delta = get_loop_delta_vs_prior_week(
                        db, user.id, config, loop_name,
                        (start, end), (prior_start, prior_end)
                    )
                    
                    if delta["direction"] == "increase":
                        change_str = f"↑ {format_cents_to_usd(abs(delta['delta_cents']))} vs last week"
                    elif delta["direction"] == "decrease":
                        change_str = f"↓ {format_cents_to_usd(abs(delta['delta_cents']))} vs last week"
                    else:
                        change_str = "same as last week"
                    
                    console.print(f"    [dim]({change_str})[/dim]")
        
        # End of week cash calculations
        # Note: For a real implementation, we'd need starting balance tracking
        # For now, we'll show relative changes
        console.print(f"\n[bold cyan]Net Change This Week:[/bold cyan]")
        
        net_change = -income_total + essentials_total
        for summary in loop_summaries.values():
            net_change += summary["total_cents"]
        
        console.print(f"  With loops:    {format_cents_to_usd(-net_change)}")
        
        # Calculate without loops (exclude loop inflows)
        net_without_loops = -income_total + essentials_total
        for summary in loop_summaries.values():
            # Only add outflows, not inflows
            net_without_loops += summary["outflow_cents"]
        
        console.print(f"  Without loops: {format_cents_to_usd(-net_without_loops)}")
        
        strain = net_change - net_without_loops
        if strain != 0:
            console.print(f"  [yellow]Loop strain:   {format_cents_to_usd(abs(strain))}[/yellow]")
        
        console.print()
        
    finally:
        db.close()


@cashflow.command(name="month")
@click.option("--month", type=click.DateTime(formats=["%Y-%m"]), 
              default=datetime.now().strftime("%Y-%m"), help="Month (YYYY-MM)")
def month_report(month: datetime):
    """Show monthly cash flow report"""
    console = get_console()
    
    # Load config
    config = load_config()
    
    # Determine month range
    month_start = date(month.year, month.month, 1)
    if month.month == 12:
        month_end = date(month.year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(month.year, month.month + 1, 1) - timedelta(days=1)
    
    db = SessionLocal()
    try:
        user = get_default_user(db)
        
        console.print(f"\n[bold blue]{icon('📊', 'Month')} {month.strftime('%B %Y')} Report[/bold blue]\n")
        
        # Get all events for the month
        events = get_events_in_range(db, user.id, month_start, month_end)
        
        if not events:
            console.print(emphasize(
                f"{icon('ℹ️', 'Info')} No events recorded for this month",
                "no events",
            ))
            console.print()
            return
        
        # Loop overview
        console.print("[bold cyan]Loop Overview:[/bold cyan]")
        
        loop_summaries = summarize_loops(db, user.id, config, month_start, month_end)
        
        for loop_name, summary in loop_summaries.items():
            if summary["used"]:
                weeks_used = len(set(e.event_date.isocalendar()[1] for e in summary["events"]))
                
                inflow_str = format_cents_to_usd(-summary["inflow_cents"]) if summary["inflow_cents"] < 0 else "$0.00"
                outflow_str = format_cents_to_usd(summary["outflow_cents"])
                strain = summary["outflow_cents"] + summary["inflow_cents"]
                strain_str = format_cents_to_usd(strain)
                
                console.print(f"  {loop_name}: {weeks_used} weeks used")
                console.print(f"    {inflow_str} inflow / {outflow_str} outflow")
                console.print(f"    Strain: {strain_str}")
                
                # Calculate streaks
                streaks = calculate_weeks_without_loop(
                    db, user.id, config, loop_name, month_end
                )
                console.print(f"    Current streak: {streaks['current_streak']} weeks without")
                console.print(f"    Best streak: {streaks['best_streak']} weeks")
                console.print()
        
        # Category breakdown
        console.print("[bold cyan]Top Categories:[/bold cyan]")
        
        category_totals = {}
        for event in events:
            if event.category and event.amount_cents > 0:  # Only outflows
                if event.category not in category_totals:
                    category_totals[event.category] = 0
                category_totals[event.category] += event.amount_cents
        
        # Sort by amount descending
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        
        for cat, amount in sorted_categories[:10]:  # Top 10
            console.print(f"  {cat.capitalize():15} {format_cents_to_usd(amount)}")
        
        console.print()
        
        # Nudges
        console.print("[bold cyan]Recommendations:[/bold cyan]")
        
        for loop_name, summary in loop_summaries.items():
            if summary["used"] and summary["total_cents"] > 0:
                # Loop is costing money
                reduction = min(10000, summary["total_cents"] // 2)  # Suggest reducing by half or $100
                console.print(f"  → Reduce {loop_name} usage by {format_cents_to_usd(reduction)} next month")
        
        console.print()
        
    finally:
        db.close()


@cashflow.command(name="import")
@click.argument("csv_file", type=click.Path(exists=True))
def import_events(csv_file: str):
    """Import events from CSV file
    
    CSV format: date,type,provider,category,amount,account,memo
    
    Amount should be positive for expenses, negative for income.
    """
    console = get_console()
    
    csv_path = Path(csv_file)
    
    db = SessionLocal()
    try:
        user = get_default_user(db)
        
        imported = 0
        errors = []
        
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Parse date
                    event_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    
                    # Parse amount
                    amount = Decimal(row['amount'])
                    amount_cents = int(amount * 100)
                    
                    # Create event
                    event = CashFlowEvent(
                        user_id=user.id,
                        event_date=event_date,
                        event_type=row['type'],
                        provider=row.get('provider') or None,
                        category=row.get('category') or None,
                        amount_cents=amount_cents,
                        account=row.get('account') or None,
                        memo=row.get('memo') or None,
                    )
                    
                    db.add(event)
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {e}")
        
        if imported > 0:
            db.commit()
            console.print(
                emphasize(
                    f"\n{icon('✅', 'Imported')} Imported {imported} events from {csv_path.name}",
                    f"{imported} events imported",
                )
            )
        
        if errors:
            console.print(f"\n[yellow]{icon('⚠️', 'Warnings')} Errors:[/yellow]")
            for error in errors[:10]:  # Show first 10 errors
                console.print(f"  {error}")
            if len(errors) > 10:
                console.print(f"  ... and {len(errors) - 10} more errors")
        
        console.print()
        
    finally:
        db.close()


@cashflow.command(name="config-show")
def config_show():
    """Show cash flow configuration"""
    console = get_console()
    
    config = load_config()
    config_path = get_config_path()
    
    console.print(f"\n[bold blue]{icon('⚙️', 'Config')} Cash Flow Configuration[/bold blue]")
    console.print(f"[dim]File: {config_path}[/dim]\n")
    
    # Payroll
    console.print("[bold cyan]Payroll:[/bold cyan]")
    console.print(f"  Payday on Thursday: {config.payroll.payday_is_thursday}")
    console.print(f"  Week start: {config.payroll.week_start}")
    
    # Accounts
    console.print("\n[bold cyan]Accounts:[/bold cyan]")
    console.print(f"  Primary: {config.accounts.primary}")
    
    # Providers
    if config.providers:
        console.print("\n[bold cyan]Providers:[/bold cyan]")
        for name, provider in config.providers.items():
            console.print(f"  {name}:")
            console.print(f"    Type: {provider.type}")
            console.print(f"    Account: {provider.account}")
    
    # Loops
    if config.loops:
        console.print("\n[bold cyan]Loops:[/bold cyan]")
        for loop in config.loops:
            console.print(f"  {loop.name}:")
            for include in loop.includes:
                provider_str = f", provider={include.provider}" if include.provider else ""
                console.print(f"    - {include.event_type}{provider_str}")
    
    # Defaults
    console.print("\n[bold cyan]Weekly Budget Defaults:[/bold cyan]")
    console.print(f"  Gas: ${config.defaults.weekly_budget.gas_usd:.2f}")
    console.print(f"  Food: ${config.defaults.weekly_budget.food_usd:.2f}")
    
    console.print()


@cashflow.command(name="config-set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set a configuration value
    
    Examples:
        tracker cashflow config-set payroll.payday_is_thursday true
        tracker cashflow config-set defaults.weekly_budget.gas_usd 175.0
    """
    console = get_console()
    
    # Parse value
    parsed_value = None
    if value.lower() in ("true", "yes", "1"):
        parsed_value = True
    elif value.lower() in ("false", "no", "0"):
        parsed_value = False
    else:
        try:
            # Try parsing as number
            if "." in value:
                parsed_value = float(value)
            else:
                parsed_value = int(value)
        except ValueError:
            # Keep as string
            parsed_value = value
    
    try:
        set_config_value(key, parsed_value)
        
        console.print(
            emphasize(
                f"\n{icon('✅', 'Set')} Configuration updated: {key} = {parsed_value}",
                "config updated",
            )
        )
        console.print(f"[dim]File: {get_config_path()}[/dim]\n")
        
    except Exception as e:
        console.print(
            f"\n[red]{icon('❌', 'Error')} Failed to set config: {e}[/red]\n"
        )
        raise click.ClickException(str(e))


@cashflow.command(name="adjust")
@click.argument("instruction")
@click.option("--dry-run", is_flag=True, help="Show diff without applying changes")
@click.option("--yes", is_flag=True, help="Auto-confirm changes")
@click.option("--effective", "effective_date", type=click.DateTime(formats=["%Y-%m-%d"]),
              help="Effective date for changes (YYYY-MM-DD)")
@click.option("--scope", type=click.Choice(["profile", "recurring", "installments", "debts", "all"]),
              default="all", help="Scope of changes to apply")
@click.option("--no-forecast", is_flag=True, help="Skip forecast after applying")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
def adjust_command(instruction: str, dry_run: bool, yes: bool, effective_date: Optional[datetime],
                   scope: str, no_forecast: bool, format: str):
    """Apply natural language financial adjustments

    Examples:
        tracker cashflow adjust "I paid off my Slate credit card"
        tracker cashflow adjust "Lower EarnIn to 300 next week" --dry-run
        tracker cashflow adjust "Add Klarna AutoZone 22.97 on 2025-11-08" --yes
    """
    console = get_console()

    db = SessionLocal()
    try:
        user = get_default_user(db)

        # Parse the command
        intent = parse_command(instruction)

        if intent.action == "unknown":
            console.print(f"\n[red]{icon('❌', 'Error')} Could not understand: {instruction}[/red]")
            console.print(f"[dim]Try: 'I paid off my Slate credit card' or 'Lower EarnIn to 300'[dim]\n")
            return

        # Show parsed intent
        console.print(f"\n[bold blue]{icon('🧠', 'Parsed')} Command Analysis[/bold blue]")
        console.print(f"Action: {intent.action}")
        console.print(f"Entity: {intent.entity_name} ({intent.entity_type})")

        if intent.parameters:
            console.print(f"Parameters: {intent.parameters}")

        if intent.ambiguous:
            console.print(f"[yellow]{icon('⚠️', 'Ambiguous')} Multiple matches found: {', '.join(intent.alternatives)}[/yellow]")
            console.print(f"[dim]Using: {intent.entity_name}[/dim]")

        # Create diff
        diff = create_diff(db, user.id, intent)

        if not diff.safe:
            console.print(f"\n[red]{icon('❌', 'Error')} Unsafe change detected:[/red]")
            for warning in diff.warnings:
                console.print(f"  • {warning}")
            return

        # Show diff preview
        console.print(f"\n[bold cyan]{icon('📊', 'Preview')} Proposed Changes[/bold cyan]")

        if format == "table":
            # Pretty table format
            from rich.table import Table
            from rich import box

            table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
            table.add_column("Field", style="cyan", width=20)
            table.add_column("Before", style="red", width=15)
            table.add_column("After", style="green", width=15)
            table.add_column("Effective", style="yellow", width=12)

            for change in diff.changes:
                # Parse change description for table
                if "from" in change.lower():
                    parts = change.split(" from ")
                    if len(parts) == 2:
                        field = parts[0].replace("Change ", "")
                        before_after = parts[1].split(" to ")
                        if len(before_after) == 2:
                            table.add_row(field, before_after[0], before_after[1], "Today")
                else:
                    table.add_row(change, "-", "Applied", "Today")

            console.print(table)
        else:
            # JSON format
            console.print(json.dumps({
                "intent": intent.__dict__,
                "changes": diff.changes,
                "warnings": diff.warnings,
                "before": diff.before,
                "after": diff.after,
            }, indent=2))

        # Confirmation
        if not dry_run and not yes:
            console.print(f"\n[yellow]{icon('⚠️', 'Confirm')} Apply these changes? [y/N]: [/yellow]", end="")
            response = input().strip().lower()
            if response not in ["y", "yes"]:
                console.print(f"\n[dim]Changes cancelled.[/dim]\n")
                return

        # Apply changes
        if not dry_run:
            success = apply_adjustment(db, user.id, diff)

            if success:
                # Save audit
                audit_id = save_audit(instruction, diff, user.id)

                console.print(f"\n[green]{icon('✅', 'Applied')} Changes applied successfully![/green]")
                console.print(f"Audit ID: {audit_id}")

                # Save last adjustment for easy access
                last_adjustment = {
                    "audit_id": audit_id,
                    "timestamp": datetime.now().isoformat(),
                    "instruction": instruction,
                    "changes": diff.changes,
                    "warnings": diff.warnings,
                }

                last_file = get_config_dir() / "last_adjustment.json"
                last_file.write_text(json.dumps(last_adjustment, indent=2))

                # Run forecast unless disabled
                if not no_forecast:
                    console.print(f"\n[blue]{icon('🔮', 'Forecast')} Running 7-day forecast...[/blue]")
                    config = load_config()
                    week_start = date.today()
                    if week_start.weekday() != 4:  # Not Friday
                        # Find next Friday
                        days_to_friday = (4 - week_start.weekday()) % 7
                        week_start = week_start + timedelta(days=days_to_friday)

                    forecast = forecast_week(db, user.id, config, week_start)

                    # Show forecast summary
                    console.print(f"\n[bold cyan]Week: {forecast['period']['start']} → {forecast['period']['end']}[/bold cyan]")
                    console.print(f"Net Change: {format_cents_to_usd(int(Decimal(forecast['summary']['net_change']) * 100))}")
                    console.print(f"End Balance: {format_cents_to_usd(int(Decimal(forecast['ending_balances']['bank']) * 100))}")

            else:
                console.print(f"\n[red]{icon('❌', 'Error')} Failed to apply changes[/red]\n")
        else:
            console.print(f"\n[dim]Dry run complete - no changes made.[/dim]\n")

    finally:
        db.close()


@cashflow.command(name="scan-entry")
@click.option("--date", "entry_date", type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(date.today()), help="Entry date to scan (YYYY-MM-DD)")
@click.option("--yes", is_flag=True, help="Auto-apply detected changes")
def scan_entry_command(entry_date: datetime, yes: bool):
    """Scan daily entry text for financial changes

    Examples:
        tracker cashflow scan-entry --date 2025-10-27
        tracker cashflow scan-entry --yes
    """
    console = get_console()

    db = SessionLocal()
    try:
        user = get_default_user(db)

        # Get entry
        entry = (
            db.query(DailyEntry)
            .filter_by(user_id=user.id, date=entry_date.date())
            .first()
        )

        if not entry:
            console.print(f"\n[red]{icon('❌', 'Error')} No entry found for {entry_date.date()}[/red]\n")
            return

        # Scan text
        intents = scan_entry_text(entry.journal_text or "")

        if not intents:
            console.print(f"\n[green]{icon('✅', 'Clean')} No financial changes detected in entry[/green]")
            console.print(f"[dim]Date: {entry_date.date()}[/dim]\n")
            return

        console.print(f"\n[bold blue]{icon('🔍', 'Scan')} Detected Changes in Entry[/bold blue]")
        console.print(f"Date: {entry_date.date()}")
        console.print(f"Entry: {entry.notes[:100]}{'...' if len(entry.notes) > 100 else ''}\n")

        # Show detected intents
        for i, intent in enumerate(intents, 1):
            console.print(f"[bold cyan]{i}. {intent.action.title()}: {intent.entity_name}[/bold cyan]")
            if intent.parameters:
                console.print(f"   Parameters: {intent.parameters}")

        # Confirmation
        if not yes:
            console.print(f"\n[yellow]{icon('⚠️', 'Confirm')} Apply {len(intents)} detected change(s)? [y/N]: [/yellow]", end="")
            response = input().strip().lower()
            if response not in ["y", "yes"]:
                console.print(f"\n[dim]Changes cancelled.[/dim]\n")
                return

        # Apply each intent
        applied = 0
        for intent in intents:
            diff = create_diff(db, user.id, intent)
            if diff.safe:
                success = apply_adjustment(db, user.id, diff)
                if success:
                    audit_id = save_audit(f"Auto-detected from entry {entry_date.date()}", diff, user.id)
                    console.print(f"  ✅ Applied: {intent.action} {intent.entity_name} (Audit: {audit_id})")
                    applied += 1

        console.print(f"\n[green]{icon('✅', 'Applied')} Applied {applied}/{len(intents)} changes[/green]\n")

    finally:
        db.close()


@cashflow.command(name="review-week")
@click.option("--end", "end_date", type=click.DateTime(formats=["%Y-%m-%d"]),
              default=str(date.today()), help="Week end date (YYYY-MM-DD)")
@click.option("--all", is_flag=True, help="Apply all detected changes without confirmation")
def review_week_command(end_date: datetime, all: bool):
    """Review and apply detected changes from the past week

    Examples:
        tracker cashflow review-week --end 2025-10-27
        tracker cashflow review-week --all
    """
    console = get_console()

    db = SessionLocal()
    try:
        user = get_default_user(db)

        # Get week range
        week_end = end_date.date()
        week_start = week_end - timedelta(days=6)

        console.print(f"\n[bold blue]{icon('📅', 'Review')} Weekly Review[/bold blue]")
        console.print(f"Period: {week_start} → {week_end}\n")

        # Get all entries in week
        entries = (
            db.query(DailyEntry)
            .filter(
                DailyEntry.user_id == user.id,
                DailyEntry.date >= week_start,
                DailyEntry.date <= week_end,
            )
            .order_by(DailyEntry.date)
            .all()
        )

        all_intents = []
        for entry in entries:
            intents = scan_entry_text(entry.notes or "")
            for intent in intents:
                intent.entry_date = entry.date
                all_intents.append(intent)

        if not all_intents:
            console.print(f"[green]{icon('✅', 'Clean')} No changes detected in weekly entries[/green]\n")
            return

        # Group by action type
        by_action = {}
        for intent in all_intents:
            if intent.action not in by_action:
                by_action[intent.action] = []
            by_action[intent.action].append(intent)

        console.print(f"[bold cyan]Detected Changes:[/bold cyan]")

        total_changes = 0
        for action, intents in by_action.items():
            console.print(f"\n  {action.title()} ({len(intents)}):")
            for intent in intents:
                console.print(f"    • {intent.entity_name} - {intent.entry_date}")
                total_changes += 1

        # Confirmation
        if not all:
            console.print(f"\n[yellow]{icon('⚠️', 'Confirm')} Apply {total_changes} change(s)? [y/N]: [/yellow]", end="")
            response = input().strip().lower()
            if response not in ["y", "yes"]:
                console.print(f"\n[dim]Changes cancelled.[/dim]\n")
                return

        # Apply all changes
        applied = 0
        for intent in all_intents:
            diff = create_diff(db, user.id, intent)
            if diff.safe:
                success = apply_adjustment(db, user.id, diff)
                if success:
                    audit_id = save_audit(f"Weekly review {week_start}→{week_end}", diff, user.id)
                    applied += 1

        console.print(f"\n[green]{icon('✅', 'Applied')} Applied {applied}/{total_changes} changes[/green]")
        console.print(f"[dim]Audit IDs logged for each change[/dim]\n")

    finally:
        db.close()


@cashflow.command(name="revert")
@click.argument("audit_id")
def revert_command(audit_id: str):
    """Revert changes from a specific audit

    Examples:
        tracker cashflow revert 2025-10-27-143022
    """
    console = get_console()

    # Find audit file
    audit_dir = get_config_dir() / "audits"
    audit_file = audit_dir / f"{audit_id}.json"

    if not audit_file.exists():
        console.print(f"\n[red]{icon('❌', 'Error')} Audit {audit_id} not found[/red]")
        console.print(f"[dim]Available audits in: {audit_dir}[/dim]\n")
        return

    # Load audit
    import json
    with open(audit_file, 'r') as f:
        audit_data = json.load(f)

    console.print(f"\n[bold blue]{icon('🔄', 'Revert')} Revert Audit {audit_id}[/bold blue]")
    console.print(f"Original command: {audit_data['user_text']}")
    console.print(f"Timestamp: {audit_data['timestamp']}")
    console.print(f"Changes: {len(audit_data['changes_applied'])} items\n")

    # Show what will be reverted
    console.print(f"[bold cyan]Will revert:[/bold cyan]")
    for change in audit_data['changes_applied']:
        console.print(f"  • {change}")

    # Confirmation
    console.print(f"\n[yellow]{icon('⚠️', 'Confirm')} Proceed with revert? [y/N]: [/yellow]", end="")
    response = input().strip().lower()
    if response not in ["y", "yes"]:
        console.print(f"\n[dim]Revert cancelled.[/dim]\n")
        return

    db = SessionLocal()
    try:
        user = get_default_user(db)

        # Restore before snapshot
        before = audit_data['before_snapshot']

        if 'debt' in before:
            # Restore debt in profile
            profile = db.query(UserProfile).filter_by(user_id=user.id).first()
            if profile and profile.financial_info:
                fi = profile.financial_info
                for debt in fi.get("debts_breakdown", []):
                    if debt["name"] == before['debt'].get("name"):
                        debt.update(before['debt'])
                        break
                profile.financial_info = fi
                db.commit()

        elif 'recurring' in before:
            # Restore recurring config
            config = load_config()
            for key, value in before['recurring'].items():
                setattr(config.recurring_weekly, key, value)
            save_config(config)

        elif 'installment' in before:
            # Remove installment
            config = load_config()
            # Find and remove the installment
            for name, inst in list(config.installments.items()):
                if inst.date == before['installment'].get('date'):
                    del config.installments[name]
                    break
            save_config(config)

        # Create revert audit
        revert_audit = {
            "timestamp": datetime.now().isoformat(),
            "user_text": f"REVERT of {audit_id}",
            "reverted_audit": audit_id,
            "before_snapshot": audit_data['after_snapshot'],
            "after_snapshot": before,
            "changes_applied": [f"REVERT: {change}" for change in audit_data['changes_applied']],
            "audit_id": f"REVERT-{audit_id}",
        }

        revert_file = audit_dir / f"REVERT-{audit_id}.json"
        revert_file.write_text(json.dumps(revert_audit, indent=2))

        console.print(f"\n[green]{icon('✅', 'Reverted')} Successfully reverted changes![/green]")
        console.print(f"Revert audit: REVERT-{audit_id}")
        console.print(f"[dim]Original audit preserved: {audit_id}[/dim]\n")

    finally:
        db.close()


@cashflow.command(name="forecast")
@click.option("--start", "start_date", type=click.DateTime(formats=["%Y-%m-%d"]),
              help="Forecast start date (defaults to next Friday)")
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
@click.option("--show-without-earnin", is_flag=True, help="Show forecast without EarnIn loop")
def forecast_command(start_date: Optional[datetime], format: str, show_without_earnin: bool):
    """Show 7-day financial forecast

    Examples:
        tracker cashflow forecast
        tracker cashflow forecast --start 2025-10-31 --format json
        tracker cashflow forecast --show-without-earnin
    """
    console = get_console()

    db = SessionLocal()
    try:
        user = get_default_user(db)
        config = load_config()

        # Determine start date (next Friday if not specified)
        if start_date:
            forecast_start = start_date.date()
        else:
            today = date.today()
            # Find next Friday
            days_to_friday = (4 - today.weekday()) % 7
            if days_to_friday == 0 and today.weekday() == 4:
                forecast_start = today  # Today is Friday
            else:
                forecast_start = today + timedelta(days=days_to_friday)

        console.print(f"\n[bold blue]{icon('🔮', 'Forecast')} 7-Day Forecast[/bold blue]")
        console.print(f"Period: {forecast_start} → {forecast_start + timedelta(days=6)}")
        if config.payroll.payday_is_thursday:
            console.print(f"[dim]Thursday payday cadence[/dim]\n")

        # Run forecast
        forecast = forecast_week(db, user.id, config, forecast_start)

        if format == "json":
            import json
            console.print(json.dumps(forecast, indent=2, default=str))
            return

        # Pretty table format
        from rich.table import Table
        from rich import box

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Day", style="yellow", width=10)
        table.add_column("Events", style="white", width=40)
        table.add_column("Change", style="green", width=12)
        table.add_column("Balance", style="blue", width=12)

        for day in forecast['daily_forecast']:
            events_text = []
            day_change = 0

            for event in day['events']:
                if event['type'] == 'income':
                    events_text.append(f"💰 {event['description']}")
                    day_change -= float(event['amount'])
                elif event['type'] in ['bill', 'transfer']:
                    events_text.append(f"💸 {event['description']}")
                    day_change += float(event['amount'])
                elif event['type'] == 'essential':
                    events_text.append(f"🛒 {event['description']}")
                    day_change += float(event['amount'])
                elif event['type'] == 'recorded':
                    events_text.append(f"📝 {event['description']}")
                    day_change += float(event['amount'])

            # Format events
            events_str = "\n".join(events_text[:3])  # Show max 3 events
            if len(events_text) > 3:
                events_str += f"\n+{len(events_text) - 3} more"

            # Format balance
            balance_str = format_cents_to_usd(int(day['end_balance_bank'] * 100))

            table.add_row(
                day['date'].strftime("%m/%d"),
                day['day_name'][:3],
                events_str,
                format_cents_to_usd(int(day['day_total'] * 100)),
                balance_str,
            )

        console.print(table)

        # Summary
        console.print(f"\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"  Starting Balance: {format_cents_to_usd(int(forecast['starting_balances']['bank'] * 100))}")
        console.print(f"  Ending Balance: {format_cents_to_usd(int(forecast['ending_balances']['bank'] * 100))}")
        console.print(f"  Net Change: {format_cents_to_usd(int(forecast['summary']['net_change'] * 100))}")

        if show_without_earnin:
            console.print(f"\n[yellow]Without EarnIn loop: {format_cents_to_usd(int(forecast['summary']['total_expenses'] * 100))}[/yellow]")

        console.print()

    finally:
        db.close()


@cashflow.command(name="tomorrow")
def tomorrow_command():
    """Show tomorrow's budget estimate

    Examples:
        tracker cashflow tomorrow
    """
    console = get_console()

    db = SessionLocal()
    try:
        user = get_default_user(db)
        config = load_config()

        tomorrow = date.today() + timedelta(days=1)

        console.print(f"\n[bold blue]{icon('📅', 'Tomorrow')} Tomorrow's Budget[/bold blue]")
        console.print(f"Date: {tomorrow.strftime('%A, %B %d, %Y')}\n")

        # Get budget estimate
        budget = tomorrow_budget(db, user.id, config)

        # Current balances
        console.print(f"[bold cyan]Current Balances:[/bold cyan]")
        console.print(f"  Bank: {format_cents_to_usd(int(budget['current_balances']['bank'] * 100))}")
        console.print(f"  Cash: {format_cents_to_usd(int(budget['current_balances']['cash'] * 100))}\n")

        # Expected events
        console.print(f"[bold cyan]Expected Events:[/bold cyan]")

        if not budget['expected_events']:
            console.print(f"  [green]No major events scheduled[/green]")
        else:
            for event in budget['expected_events']:
                if event['type'] == 'income':
                    console.print(f"  💰 {event['description']}: +{format_cents_to_usd(int(event['amount'] * 100))}")
                elif event['type'] in ['bill', 'transfer']:
                    console.print(f"  💸 {event['description']}: -{format_cents_to_usd(int(event['amount'] * 100))}")
                elif event['type'] == 'essential':
                    console.print(f"  🛒 {event['description']}: -{format_cents_to_usd(int(event['amount'] * 100))}")
                else:
                    console.print(f"  📝 {event['description']}")

        # Summary
        console.print(f"\n[bold cyan]Tomorrow's Summary:[/bold cyan]")
        console.print(f"  Total Outflow: -{format_cents_to_usd(int(budget['total_expected_outflow'] * 100))}")
        console.print(f"  Projected Balance: {format_cents_to_usd(int(budget['projected_end_balance'] * 100))}")

        available = max(0, budget['projected_end_balance'] - 50)  # $50 buffer
        console.print(f"  Available for Discretionary: {format_cents_to_usd(int(available * 100))}")

        console.print()

    finally:
        db.close()


@cashflow.command(name="setup-weekly")
def setup_weekly_command():
    """Interactive setup for weekly recurring bills and income

    Examples:
        tracker cashflow setup-weekly
    """
    console = get_console()

    console.print(f"\n[bold blue]{icon('⚙️', 'Setup')} Weekly Setup Wizard[/bold blue]")
    console.print(f"[dim]Set up your weekly income and recurring bills[/dim]\n")

    # Load current config
    config = load_config()

    # Check for Snap-On migration
    migration_needed = False
    if hasattr(config.recurring_weekly, 'SnapOn') and config.recurring_weekly.SnapOn != 400.00:
        migration_needed = True
        console.print(f"[yellow]{icon('⚠️', 'Migration')} Snap-On amount needs correction[/yellow]")
        console.print(f"Current: ${config.recurring_weekly.SnapOn:.2f}/week")
        console.print(f"Should be: $400.00/week\n")

    # Confirm values
    console.print(f"[bold cyan]Current Settings:[/bold cyan]")
    console.print(f"  Payday: {config.payroll.payday}")
    console.print(f"  Net Pay: ${config.payroll.net_pay_usd:.2f}")
    console.print(f"  EarnIn: ${config.recurring_weekly.EarnIn:.2f}/week")
    console.print(f"  Snap-On: ${config.recurring_weekly.SnapOn:.2f}/week")
    console.print(f"  Chase Transfer: ${config.recurring_weekly.ChaseTransfer:.2f}/week")
    console.print(f"  Gas: ${config.essentials.gas.fill_cost_usd:.2f} every {config.essentials.gas.fill_frequency_days} days")
    console.print(f"  Food: ${config.essentials.food_weekly_usd:.2f}/week")
    console.print(f"  Pets: ${config.essentials.pets_weekly_usd:.2f}/week\n")

    console.print(f"[yellow]{icon('⚠️', 'Confirm')} These values look correct? [Y/n]: [/yellow]", end="")
    response = input().strip().lower()

    if response in ["n", "no"]:
        console.print(f"\n[dim]Setup cancelled. Use 'tracker cashflow config-set' to modify values.[/dim]\n")
        return

    # Apply Snap-On migration if needed
    if migration_needed:
        console.print(f"\n[blue]{icon('🔄', 'Migration')} Correcting Snap-On to $400/week...[/blue]")
        config.recurring_weekly.SnapOn = 400.00

        # Add reserve-then-clear rule
        from tracker.services.cashflow_config import RecurringWeeklyRule
        config.recurring_weekly_rules["SnapOn"] = RecurringWeeklyRule(
            reserved_then_clears=True,
            reserve_day="THURSDAY",
            clear_day="FRIDAY",
            reserve_account="acorns_checking",
        )

        # Save config
        save_config(config)

        # Create migration audit
        import json
        audit_dir = get_config_dir() / "audits"
        audit_dir.mkdir(exist_ok=True)

        migration_audit = {
            "timestamp": datetime.now().isoformat(),
            "user_text": "setup-weekly migration",
            "type": "migration",
            "changes": [
                f"Corrected Snap-On from ${config.recurring_weekly.SnapOn:.2f}/week to $400.00/week",
                "Added Snap-On reserve-then-clear rule (Thu reserve → Fri clear)",
            ],
            "audit_id": f"MIGRATION-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        }

        migration_file = audit_dir / f"{migration_audit['audit_id']}.json"
        migration_file.write_text(json.dumps(migration_audit, indent=2))

        console.print(f"  ✅ Migration applied (Audit: {migration_audit['audit_id']})")

    # Show final summary
    console.print(f"\n[green]{icon('✅', 'Complete')} Weekly setup complete![/green]")
    console.print(f"\n[bold cyan]Your Weekly Schedule:[/bold cyan]")
    console.print(f"  Thursday: Payday ${config.payroll.net_pay_usd:.2f} + EarnIn -${config.recurring_weekly.EarnIn:.2f}")
    console.print(f"  Thursday: Snap-On reserve -${config.recurring_weekly.SnapOn:.2f} (→ Acorns)")
    console.print(f"  Friday: Snap-On clear (already reserved)")
    console.print(f"  Thursday: Chase transfer -${config.recurring_weekly.ChaseTransfer:.2f}")
    console.print(f"  Daily: Gas ~${config.essentials.gas.fill_cost_usd:.2f} every {config.essentials.gas.fill_frequency_days} days")
    console.print(f"  Weekly: Food ${config.essentials.food_weekly_usd:.2f}, Pets ${config.essentials.pets_weekly_usd:.2f}")

    console.print(f"\n[dim]Config saved to: {get_config_path()}[/dim]")
    console.print(f"[dim]Use 'tracker cashflow forecast' to see your weekly predictions[/dim]\n")
