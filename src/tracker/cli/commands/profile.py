"""Profile management command - view and manage character sheet"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from tracker.core.database import SessionLocal
from tracker.services.character_service import CharacterSheetService
from tracker.services.entry_service import EntryService

console = Console()


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
        # Get default user
        entry_service = EntryService(db)
        user = entry_service.get_default_user()
        if not user:
            console.print("[red]Error: No user found. Please run 'tracker init' first.[/red]")
            return
        
        # Build character sheet
        char_service = CharacterSheetService(db)
        try:
            character_sheet = char_service.analyze_and_update_profile(
                user_id=user.id,
                lookback_days=lookback_days
            )
        except Exception as e:
            console.print(f"[red]Error building character profile: {e}[/red]")
            console.print("\n[yellow]Tip: Try creating some entries first with 'tracker new'[/yellow]")
            return
        
        # Display character sheet
        console.print("\n[bold cyan]📊 Your Character Profile[/bold cyan]\n")
        
        # Meta stats
        meta_table = Table(show_header=False, box=None, padding=(0, 2))
        meta_table.add_column("Label", style="bold")
        meta_table.add_column("Value")
        
        meta_table.add_row("Total entries", str(character_sheet.total_entries))
        meta_table.add_row("Current streak", f"{character_sheet.entry_streak} days")
        meta_table.add_row("Longest streak", f"{character_sheet.longest_streak} days")
        
        console.print(Panel(meta_table, title="📈 Tracking Stats", border_style="cyan"))
        
        # Financial personality
        if character_sheet.financial_personality:
            financial_table = Table(show_header=False, box=None, padding=(0, 2))
            financial_table.add_column("Label", style="bold")
            financial_table.add_column("Value")
            
            if character_sheet.financial_personality.personality:
                financial_table.add_row("Personality", character_sheet.financial_personality.personality)
            if character_sheet.financial_personality.income_range:
                financial_table.add_row("Income range", character_sheet.financial_personality.income_range)
            if character_sheet.financial_personality.debt_situation:
                financial_table.add_row("Debt situation", character_sheet.financial_personality.debt_situation)
            
            if character_sheet.financial_personality.money_stressors:
                stressors = ", ".join(character_sheet.financial_personality.money_stressors[:3])
                if len(character_sheet.financial_personality.money_stressors) > 3:
                    stressors += "..."
                financial_table.add_row("Stressors", stressors)
            
            if character_sheet.financial_personality.financial_wins:
                wins = ", ".join(character_sheet.financial_personality.financial_wins[:3])
                if len(character_sheet.financial_personality.financial_wins) > 3:
                    wins += "..."
                financial_table.add_row("Recent wins", wins)
            
            console.print(Panel(financial_table, title="💰 Financial Profile", border_style="green"))
        
        # Work character
        if character_sheet.work_character:
            work_table = Table(show_header=False, box=None, padding=(0, 2))
            work_table.add_column("Label", style="bold")
            work_table.add_column("Value")
            
            if character_sheet.work_character.work_style:
                work_table.add_row("Work style", character_sheet.work_character.work_style)
            if character_sheet.work_character.side_hustle_status:
                work_table.add_row("Side hustle", character_sheet.work_character.side_hustle_status)
            
            if character_sheet.work_character.career_goals:
                goals = ", ".join(character_sheet.work_character.career_goals[:2])
                if len(character_sheet.work_character.career_goals) > 2:
                    goals += "..."
                work_table.add_row("Career goals", goals)
            
            console.print(Panel(work_table, title="💼 Work Profile", border_style="blue"))
        
        # Wellbeing
        if character_sheet.wellbeing:
            wellbeing_table = Table(show_header=False, box=None, padding=(0, 2))
            wellbeing_table.add_column("Label", style="bold")
            wellbeing_table.add_column("Value")
            
            if character_sheet.wellbeing.stress_pattern:
                wellbeing_table.add_row("Stress pattern", character_sheet.wellbeing.stress_pattern)
            if character_sheet.wellbeing.baseline_stress is not None:
                wellbeing_table.add_row("Baseline stress", f"{character_sheet.wellbeing.baseline_stress:.1f}/10")
            
            if character_sheet.wellbeing.stress_triggers:
                triggers = ", ".join(character_sheet.wellbeing.stress_triggers[:3])
                if len(character_sheet.wellbeing.stress_triggers) > 3:
                    triggers += "..."
                wellbeing_table.add_row("Triggers", triggers)
            
            console.print(Panel(wellbeing_table, title="🧘 Wellbeing Profile", border_style="magenta"))
        
        # Goals
        if character_sheet.growth_goals:
            goals_table = Table(show_header=False, box=None, padding=(0, 2))
            goals_table.add_column("Label", style="bold")
            goals_table.add_column("Value")
            
            if character_sheet.growth_goals.short_term_goals:
                short = ", ".join(character_sheet.growth_goals.short_term_goals[:2])
                if len(character_sheet.growth_goals.short_term_goals) > 2:
                    short += "..."
                goals_table.add_row("Short-term goals", short)
            
            if character_sheet.growth_goals.long_term_goals:
                long = ", ".join(character_sheet.growth_goals.long_term_goals[:2])
                if len(character_sheet.growth_goals.long_term_goals) > 2:
                    long += "..."
                goals_table.add_row("Long-term goals", long)
            
            console.print(Panel(goals_table, title="🎯 Goals", border_style="yellow"))
        
        # Life patterns
        if character_sheet.life_patterns and character_sheet.life_patterns.current_priorities:
            priorities = ", ".join(character_sheet.life_patterns.current_priorities[:3])
            if len(character_sheet.life_patterns.current_priorities) > 3:
                priorities += "..."
            console.print(f"\n[bold]Current priorities:[/bold] {priorities}")
        
        console.print(f"\n[dim]Profile analyzed from last {lookback_days} days of entries[/dim]")
        console.print("[dim]Use 'tracker profile update' to manually edit your profile[/dim]\n")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        db.close()


@profile.command()
@click.option("--lookback-days", default=30, help="Number of days to analyze")
def analyze(lookback_days):
    """Force re-analysis of your profile from recent entries"""
    
    db = SessionLocal()
    
    try:
        # Get default user
        entry_service = EntryService(db)
        user = entry_service.get_default_user()
        if not user:
            console.print("[red]Error: No user found. Please run 'tracker init' first.[/red]")
            return
        
        console.print(f"\n[cyan]Analyzing last {lookback_days} days of entries...[/cyan]")
        
        # Analyze and update profile
        char_service = CharacterSheetService(db)
        try:
            character_sheet = char_service.analyze_and_update_profile(
                user_id=user.id,
                lookback_days=lookback_days
            )
            
            console.print("[green]✓ Profile updated successfully![/green]\n")
            console.print("Run [cyan]tracker profile show[/cyan] to view your updated profile")
        
        except Exception as e:
            console.print(f"[red]Error analyzing profile: {e}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    finally:
        db.close()


@profile.command()
def update():
    """Manually update your profile preferences (coming soon)"""
    
    console.print("\n[yellow]Manual profile editing is coming soon![/yellow]")
    console.print("\nFor now, your profile is automatically built from your entries.")
    console.print("Keep logging entries with [cyan]tracker new[/cyan] to build a rich profile.\n")
    console.print("[dim]Future features will include:[/dim]")
    console.print("  • Manual goal setting")
    console.print("  • Communication style preferences")
    console.print("  • Custom feedback preferences")
    console.print("  • Priority customization\n")
