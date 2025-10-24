"""CLI commands for user profile management"""

import json
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from tracker.core.database import get_db
from tracker.services.profile_service import ProfileService


console = Console()


@click.group()
def profile():
    """Manage your user profile and preferences"""
    pass


@profile.command()
@click.option("--user-id", default=1, help="User ID")
def setup(user_id: int):
    """Interactive profile setup wizard"""
    console.print(Panel.fit(
        "[bold cyan]Welcome to Tracker Profile Setup![/bold cyan]\n\n"
        "The more Tracker knows about you, the smarter and more personalized its feedback becomes.\n"
        "All sensitive data is encrypted and stored locally.",
        border_style="cyan"
    ))
    
    db = next(get_db())
    service = ProfileService(db)
    
    # Step 1: Basic Info
    console.print("\n[bold]Step 1: Basic Information[/bold]")
    nickname = Prompt.ask("What should I call you?", default="")
    
    console.print("\n[italic]Preferred tone for feedback:[/italic]")
    console.print("  1. Casual & friendly")
    console.print("  2. Professional & direct")
    console.print("  3. Encouraging & supportive")
    console.print("  4. Stoic & analytical")
    tone_choice = Prompt.ask("Choose", choices=["1", "2", "3", "4"], default="1")
    tone_map = {"1": "casual", "2": "professional", "3": "encouraging", "4": "stoic"}
    preferred_tone = tone_map[tone_choice]
    
    console.print("\n[italic]How much context do you want to share?[/italic]")
    console.print("  1. Basic - Just spending & stress tracking")
    console.print("  2. Personal - Include work, bills, and goals")
    console.print("  3. Deep - Full context for richest insights")
    depth_choice = Prompt.ask("Choose", choices=["1", "2", "3"], default="1")
    depth_map = {"1": "basic", "2": "personal", "3": "deep"}
    context_depth = depth_map[depth_choice]
    
    service.update_basic_info(user_id, nickname, preferred_tone, context_depth)
    console.print("[green]✓[/green] Basic info saved!")
    
    # Step 2: Emotional Baseline
    console.print("\n[bold]Step 2: Emotional Baseline[/bold]")
    baseline_energy = int(Prompt.ask(
        "On average, what's your energy level? (1-10)",
        default="5"
    ))
    baseline_stress = float(Prompt.ask(
        "On average, what's your stress level? (1-10)",
        default="5"
    ))
    
    stress_triggers_input = Prompt.ask(
        "What are your main stress triggers? (comma-separated)",
        default=""
    )
    stress_triggers = [t.strip() for t in stress_triggers_input.split(",") if t.strip()]
    
    calming_activities_input = Prompt.ask(
        "What calms you down? (comma-separated)",
        default=""
    )
    calming_activities = [a.strip() for a in calming_activities_input.split(",") if a.strip()]
    
    service.update_emotional_context(
        user_id,
        stress_triggers=stress_triggers,
        calming_activities=calming_activities,
        baseline_energy=baseline_energy,
        baseline_stress=baseline_stress
    )
    console.print("[green]✓[/green] Emotional baseline saved!")
    
    # Optional deeper setup
    if context_depth in ["personal", "deep"]:
        if Confirm.ask("\nWould you like to set up work & financial info now?", default=False):
            setup_work_info(service, user_id)
            setup_financial_info(service, user_id)
            setup_goals(service, user_id)
    
    console.print(Panel.fit(
        "[bold green]Profile setup complete![/bold green]\n\n"
        f"Context depth: {context_depth}\n"
        "You can update your profile anytime with 'tracker profile update'",
        border_style="green"
    ))


def setup_work_info(service: ProfileService, user_id: int):
    """Setup work information"""
    console.print("\n[bold]Work Information[/bold]")
    
    job_title = Prompt.ask("Job title", default="")
    employment_type = Prompt.ask(
        "Employment type",
        choices=["hourly", "salary"],
        default="hourly"
    )
    pay_schedule = Prompt.ask(
        "Pay schedule",
        choices=["weekly", "biweekly", "monthly"],
        default="biweekly"
    )
    hours_per_week = float(Prompt.ask("Typical hours per week", default="40"))
    commute_minutes = int(Prompt.ask("Commute time (minutes)", default="0"))
    
    work_data = {
        "job_title": job_title,
        "employment_type": employment_type,
        "pay_schedule": pay_schedule,
        "typical_hours_per_week": hours_per_week,
        "commute_minutes": commute_minutes,
        "side_gigs": []
    }
    
    if Confirm.ask("Do you have side gigs?", default=False):
        side_gigs = []
        while True:
            gig_name = Prompt.ask("Side gig name (or 'done')")
            if gig_name.lower() == "done":
                break
            gig_income = float(Prompt.ask(f"Typical monthly income from {gig_name}"))
            side_gigs.append({"name": gig_name, "typical_income": gig_income})
        work_data["side_gigs"] = side_gigs
    
    service.update_work_info(user_id, work_data)
    console.print("[green]✓[/green] Work info saved!")


def setup_financial_info(service: ProfileService, user_id: int):
    """Setup financial information"""
    console.print("\n[bold]Financial Information[/bold]")
    
    monthly_income = float(Prompt.ask("Typical monthly net income", default="0"))
    
    financial_data = {
        "monthly_income": monthly_income,
        "income_sources": [],
        "recurring_bills": [],
        "debts": []
    }
    
    if Confirm.ask("Add recurring bills?", default=False):
        bills = []
        while True:
            bill_name = Prompt.ask("Bill name (or 'done')")
            if bill_name.lower() == "done":
                break
            bill_amount = float(Prompt.ask(f"Amount for {bill_name}"))
            bill_due_day = int(Prompt.ask(f"Day of month {bill_name} is due"))
            bills.append({
                "name": bill_name,
                "amount": bill_amount,
                "due_day": bill_due_day
            })
        financial_data["recurring_bills"] = bills
    
    if Confirm.ask("Add debts to track?", default=False):
        debts = []
        while True:
            debt_name = Prompt.ask("Debt name (or 'done')")
            if debt_name.lower() == "done":
                break
            debt_balance = float(Prompt.ask(f"Current balance for {debt_name}"))
            debt_min = float(Prompt.ask(f"Minimum payment for {debt_name}"))
            debt_rate = float(Prompt.ask(f"Interest rate for {debt_name} (%)", default="0"))
            debts.append({
                "name": debt_name,
                "balance": debt_balance,
                "min_payment": debt_min,
                "interest_rate": debt_rate
            })
        financial_data["debts"] = debts
    
    service.update_financial_info(user_id, financial_data)
    console.print("[green]✓[/green] Financial info saved!")


def setup_goals(service: ProfileService, user_id: int):
    """Setup goals"""
    console.print("\n[bold]Goals[/bold]")
    
    goals_data = {"short_term": [], "long_term": []}
    
    if Confirm.ask("Add short-term goals? (next 3-6 months)", default=False):
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
    
    if Confirm.ask("Add long-term goals?", default=False):
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
    console.print("[green]✓[/green] Goals saved!")


@profile.command()
@click.option("--user-id", default=1, help="User ID")
def view(user_id: int):
    """View your current profile"""
    db = next(get_db())
    service = ProfileService(db)
    
    summary = service.get_profile_summary(user_id)
    
    # Basic Info
    table = Table(title="Your Profile", show_header=True, header_style="bold cyan")
    table.add_column("Section", style="cyan")
    table.add_column("Details", style="white")
    
    basic = summary["basic_info"]
    table.add_row(
        "Basic Info",
        f"Nickname: {basic['nickname']}\n"
        f"Tone: {basic['preferred_tone']}\n"
        f"Context Depth: {basic['context_depth']}"
    )
    
    stats = summary["stats"]
    table.add_row(
        "Stats",
        f"Total Entries: {stats['total_entries']}\n"
        f"Current Streak: {stats['current_streak']} days\n"
        f"Longest Streak: {stats['longest_streak']} days"
    )
    
    emotional = summary["emotional_baseline"]
    table.add_row(
        "Emotional Baseline",
        f"Energy: {emotional['energy']}/10\n"
        f"Stress: {emotional['stress']}/10"
    )
    
    if "work" in summary:
        work = summary["work"]
        table.add_row(
            "Work",
            f"Title: {work.get('job_title', 'N/A')}\n"
            f"Type: {work.get('employment_type', 'N/A')}\n"
            f"Hours/week: {work.get('typical_hours_per_week', 'N/A')}"
        )
    
    if "financial" in summary and summary["financial"]:
        financial = summary["financial"]
        debt_count = len(financial.get("debts", []))
        bill_count = len(financial.get("recurring_bills", []))
        table.add_row(
            "Financial",
            f"Monthly Income: ${financial.get('monthly_income', 0):.2f}\n"
            f"Recurring Bills: {bill_count}\n"
            f"Debts Tracked: {debt_count}"
        )
    
    if "goals" in summary and summary["goals"]:
        goals = summary["goals"]
        st_count = len(goals.get("short_term", []))
        lt_count = len(goals.get("long_term", []))
        table.add_row(
            "Goals",
            f"Short-term: {st_count}\n"
            f"Long-term: {lt_count}"
        )
    
    console.print(table)


@profile.command()
@click.option("--user-id", default=1, help="User ID")
def update(user_id: int):
    """Update specific parts of your profile"""
    db = next(get_db())
    service = ProfileService(db)
    
    console.print("[bold]What would you like to update?[/bold]")
    console.print("  1. Basic info (nickname, tone, privacy)")
    console.print("  2. Emotional baseline")
    console.print("  3. Work information")
    console.print("  4. Financial information")
    console.print("  5. Goals")
    console.print("  6. Lifestyle")
    
    choice = Prompt.ask("Choose section", choices=["1", "2", "3", "4", "5", "6"])
    
    if choice == "1":
        nickname = Prompt.ask("Nickname (leave blank to keep current)", default="")
        if nickname:
            service.update_basic_info(user_id, nickname=nickname)
    elif choice == "2":
        baseline_energy = Prompt.ask("Average energy (1-10)", default="")
        baseline_stress = Prompt.ask("Average stress (1-10)", default="")
        if baseline_energy:
            service.update_emotional_context(user_id, baseline_energy=int(baseline_energy))
        if baseline_stress:
            service.update_emotional_context(user_id, baseline_stress=float(baseline_stress))
    elif choice == "3":
        setup_work_info(service, user_id)
    elif choice == "4":
        setup_financial_info(service, user_id)
    elif choice == "5":
        setup_goals(service, user_id)
    elif choice == "6":
        console.print("[yellow]Lifestyle update coming soon![/yellow]")
    
    console.print("[green]✓[/green] Profile updated!")


@profile.command()
@click.option("--user-id", default=1, help="User ID")
def checkin(user_id: int):
    """Monthly check-in to update profile"""
    db = next(get_db())
    service = ProfileService(db)
    
    if not service.needs_monthly_checkin(user_id):
        console.print("[yellow]You don't need a monthly check-in yet![/yellow]")
        return
    
    console.print(Panel.fit(
        "[bold cyan]Monthly Check-In[/bold cyan]\n\n"
        "Let's make sure your profile is up to date!",
        border_style="cyan"
    ))
    
    if Confirm.ask("Have your bills or debts changed?", default=False):
        setup_financial_info(service, user_id)
    
    if Confirm.ask("Has your work situation changed?", default=False):
        setup_work_info(service, user_id)
    
    if Confirm.ask("Want to update your goals?", default=False):
        setup_goals(service, user_id)
    
    service.mark_monthly_checkin_complete(user_id)
    console.print("[green]✓[/green] Monthly check-in complete!")


if __name__ == "__main__":
    profile()
