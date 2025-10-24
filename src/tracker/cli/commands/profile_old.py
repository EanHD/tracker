"""Profile management command - view and manage character sheet"""

import click
from rich.panel import Panel
from rich.table import Table

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.core.database import SessionLocal
from tracker.services.character_service import CharacterSheetService
from tracker.services.entry_service import EntryService


@click.group()
def profile():
    """View and manage your personalized character profile"""
    pass


@profile.command()
@click.option("--lookback-days", default=30, help="Number of days to analyze")
def show(lookback_days):
    """Display your current character profile"""
    
    db = SessionLocal()
    
    try:
        console = get_console()
        # Get default user
        entry_service = EntryService(db)
        user = entry_service.get_default_user()
        if not user:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} No user found. Please run 'tracker init' first.[/red]",
                    "no user found",
                )
            )
            return
        
        # Build character sheet
        char_service = CharacterSheetService(db)
        try:
            character_sheet = char_service.analyze_and_update_profile(
                user_id=user.id,
                lookback_days=lookback_days
            )
        except Exception as e:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} Error building character profile: {e}[/red]",
                    "profile build error",
                )
            )
            console.print(
                emphasize(
                    f"\n[yellow]{icon('💡', 'Tip')} Try creating some entries first with 'tracker new'[/yellow]",
                    "tip create entries",
                )
            )
            return
        
        # Display character sheet
        console.print(
            f"\n[bold cyan]{icon('📊', 'Profile')} Your Character Profile[/bold cyan]\n"
        )
        
        # Meta stats
        meta_table = Table(show_header=False, box=None, padding=(0, 2))
        meta_table.add_column("Label", style="bold")
        meta_table.add_column("Value")
        
        meta_table.add_row("Total entries", str(character_sheet.total_entries))
        meta_table.add_row("Current streak", f"{character_sheet.entry_streak} days")
        meta_table.add_row("Longest streak", f"{character_sheet.longest_streak} days")
        
        console.print(
            Panel(meta_table, title=f"{icon('📈', 'Stats')} Tracking Stats", border_style="cyan")
        )
        
        # Financial personality
        financial_table = Table(show_header=False, box=None, padding=(0, 2))
        financial_table.add_column("Label", style="bold")
        financial_table.add_column("Value")
        
        has_financial = False
        if character_sheet.financial_personality:
            financial_table.add_row("Personality", character_sheet.financial_personality)
            has_financial = True
        if character_sheet.typical_income_range:
            financial_table.add_row("Income range", character_sheet.typical_income_range)
            has_financial = True
        if character_sheet.debt_situation:
            financial_table.add_row("Debt situation", character_sheet.debt_situation)
            has_financial = True
        
        if character_sheet.money_stressors:
            stressors = ", ".join(character_sheet.money_stressors[:3])
            if len(character_sheet.money_stressors) > 3:
                stressors += "..."
            financial_table.add_row("Stressors", stressors)
            has_financial = True
        
        if character_sheet.money_wins:
            wins = ", ".join(character_sheet.money_wins[:3])
            if len(character_sheet.money_wins) > 3:
                wins += "..."
            financial_table.add_row("Recent wins", wins)
            has_financial = True
        
        if has_financial:
            console.print(
                Panel(
                    financial_table,
                    title=f"{icon('💰', 'Finance')} Financial Profile",
                    border_style="green",
                )
            )
        
        # Work character
        work_table = Table(show_header=False, box=None, padding=(0, 2))
        work_table.add_column("Label", style="bold")
        work_table.add_column("Value")
        
        has_work = False
        if character_sheet.work_style:
            work_table.add_row("Work style", character_sheet.work_style)
            has_work = True
        if character_sheet.side_hustle_status:
            work_table.add_row("Side hustle", character_sheet.side_hustle_status)
            has_work = True
        
        if character_sheet.career_goals:
            goals = ", ".join(character_sheet.career_goals[:2])
            if len(character_sheet.career_goals) > 2:
                goals += "..."
            work_table.add_row("Career goals", goals)
            has_work = True
        
        if has_work:
            console.print(
                Panel(
                    work_table,
                    title=f"{icon('💼', 'Work')} Work Profile",
                    border_style="blue",
                )
            )
        
        # Wellbeing
        wellbeing_table = Table(show_header=False, box=None, padding=(0, 2))
        wellbeing_table.add_column("Label", style="bold")
        wellbeing_table.add_column("Value")
        
        has_wellbeing = False
        if character_sheet.stress_pattern:
            wellbeing_table.add_row("Stress pattern", character_sheet.stress_pattern)
            has_wellbeing = True
        if character_sheet.baseline_stress is not None:
            wellbeing_table.add_row("Baseline stress", f"{character_sheet.baseline_stress:.1f}/10")
            has_wellbeing = True
        
        if character_sheet.stress_triggers:
            triggers = ", ".join(character_sheet.stress_triggers[:3])
            if len(character_sheet.stress_triggers) > 3:
                triggers += "..."
            wellbeing_table.add_row("Triggers", triggers)
            has_wellbeing = True
        
        if has_wellbeing:
            console.print(
                Panel(
                    wellbeing_table,
                    title=f"{icon('🧘', 'Wellbeing')} Wellbeing Profile",
                    border_style="magenta",
                )
            )
        
        # Goals
        goals_table = Table(show_header=False, box=None, padding=(0, 2))
        goals_table.add_column("Label", style="bold")
        goals_table.add_column("Value")
        
        has_goals = False
        if character_sheet.short_term_goals:
            short = ", ".join(character_sheet.short_term_goals[:2])
            if len(character_sheet.short_term_goals) > 2:
                short += "..."
            goals_table.add_row("Short-term goals", short)
            has_goals = True
        
        if character_sheet.long_term_aspirations:
            long = ", ".join(character_sheet.long_term_aspirations[:2])
            if len(character_sheet.long_term_aspirations) > 2:
                long += "..."
            goals_table.add_row("Long-term goals", long)
            has_goals = True
        
        if has_goals:
            console.print(
                Panel(
                    goals_table,
                    title=f"{icon('🎯', 'Goals')} Goals",
                    border_style="yellow",
                )
            )
        
        # Life patterns
        if character_sheet.priorities:
            priorities = ", ".join(character_sheet.priorities[:3])
            if len(character_sheet.priorities) > 3:
                priorities += "..."
            console.print(
                emphasize(
                    f"\n[bold]{icon('⭐', 'Focus')} Current priorities:[/bold] {priorities}",
                    "current priorities",
                )
            )
        
        console.print(
            f"\n[dim]{icon('🗓️', 'Timeline')} Profile analyzed from last {lookback_days} days of entries[/dim]"
        )
        console.print(
            "[dim]Use 'tracker profile update' to manually edit your profile[/dim]\n"
        )
    
    except Exception as e:
        get_console().print(
            emphasize(f"[red]{icon('❌', 'Error')} Error: {e}[/red]", "profile error")
        )
    finally:
        db.close()


@profile.command()
@click.option("--lookback-days", default=30, help="Number of days to analyze")
def analyze(lookback_days):
    """Force re-analysis of your profile from recent entries"""
    
    db = SessionLocal()
    
    try:
        console = get_console()
        # Get default user
        entry_service = EntryService(db)
        user = entry_service.get_default_user()
        if not user:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} No user found. Please run 'tracker init' first.[/red]",
                    "no user found",
                )
            )
            return
        
        console.print(
            emphasize(
                f"\n[cyan]{icon('🔄', 'Analyze')} Analyzing last {lookback_days} days of entries...[/cyan]",
                "analyzing entries",
            )
        )
        
        # Analyze and update profile
        char_service = CharacterSheetService(db)
        try:
            character_sheet = char_service.analyze_and_update_profile(
                user_id=user.id,
                lookback_days=lookback_days
            )
            
            console.print(
                emphasize(
                    f"[green]{icon('✅', 'Success')} Profile updated successfully![/green]\n",
                    "profile updated",
                )
            )
            console.print(
                "Run [cyan]tracker profile show[/cyan] to view your updated profile"
            )
        
        except Exception as e:
            console.print(
                emphasize(
                    f"[red]{icon('❌', 'Error')} Error analyzing profile: {e}[/red]",
                    "profile analyze error",
                )
            )
    
    except Exception as e:
        get_console().print(
            emphasize(f"[red]{icon('❌', 'Error')} Error: {e}[/red]", "profile command error")
        )
    finally:
        db.close()


@profile.command()
def update():
    """Manually update your profile preferences (coming soon)"""
    console = get_console()
    
    console.print(
        emphasize(
            f"\n[yellow]{icon('🚧', 'Coming soon')} Manual profile editing is coming soon![/yellow]",
            "manual update coming soon",
        )
    )
    console.print("\nFor now, your profile is automatically built from your entries.")
    console.print(
        f"Keep logging entries with [cyan]tracker new[/cyan] to build a rich profile.\n"
    )
    console.print("[dim]Future features will include:[/dim]")
    console.print("  • Manual goal setting")
    console.print("  • Communication style preferences")
    console.print("  • Custom feedback preferences")
    console.print("  • Priority customization\n")
