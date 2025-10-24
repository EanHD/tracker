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
    console.print("[dim]Press Enter to accept, or type 'back' to go to previous question[/dim]\n")
    
    # Nickname with review
    while True:
        nickname = Prompt.ask("What should I call you?", default="")
        console.print(f"[dim]You entered: {nickname or '(blank)'}[/dim]")
        if Confirm.ask("Is this correct?", default=True):
            break
    
    # Tone with review
    while True:
        console.print("\n[italic]Preferred tone for feedback:[/italic]")
        console.print("  1. Casual & friendly")
        console.print("  2. Professional & direct")
        console.print("  3. Encouraging & supportive")
        console.print("  4. Stoic & analytical")
        tone_choice = Prompt.ask("Choose", choices=["1", "2", "3", "4"], default="1")
        tone_map = {"1": "casual", "2": "professional", "3": "encouraging", "4": "stoic"}
        preferred_tone = tone_map[tone_choice]
        console.print(f"[dim]You chose: {preferred_tone}[/dim]")
        if Confirm.ask("Is this correct?", default=True):
            break
    
    # Context depth with review
    while True:
        console.print("\n[italic]How much context do you want to share?[/italic]")
        console.print("  1. Basic - Just spending & stress tracking")
        console.print("  2. Personal - Include work, bills, and goals")
        console.print("  3. Deep - Full context for richest insights")
        depth_choice = Prompt.ask("Choose", choices=["1", "2", "3"], default="1")
        depth_map = {"1": "basic", "2": "personal", "3": "deep"}
        context_depth = depth_map[depth_choice]
        console.print(f"[dim]You chose: {context_depth}[/dim]")
        if Confirm.ask("Is this correct?", default=True):
            break
    
    service.update_basic_info(user_id, nickname, preferred_tone, context_depth)
    console.print("[green]✓[/green] Basic info saved!")
    
    # Step 2: Emotional Baseline
    console.print("\n[bold]Step 2: Emotional Baseline[/bold]")
    console.print("[dim]You can correct any mistakes before saving[/dim]\n")
    
    while True:
        baseline_energy = int(Prompt.ask(
            "On average, what's your energy level? (1-10)",
            default="5"
        ))
        console.print(f"[dim]You entered: {baseline_energy}/10[/dim]")
        if Confirm.ask("Is this correct?", default=True):
            break
    
    while True:
        baseline_stress = float(Prompt.ask(
            "On average, what's your stress level? (1-10)",
            default="5"
        ))
        console.print(f"[dim]You entered: {baseline_stress}/10[/dim]")
        if Confirm.ask("Is this correct?", default=True):
            break
    
    while True:
        stress_triggers_input = Prompt.ask(
            "What are your main stress triggers? (comma-separated)",
            default=""
        )
        stress_triggers = [t.strip() for t in stress_triggers_input.split(",") if t.strip()]
        console.print(f"[dim]Triggers: {', '.join(stress_triggers) if stress_triggers else '(none)'}[/dim]")
        if Confirm.ask("Is this correct?", default=True):
            break
    
    while True:
        calming_activities_input = Prompt.ask(
            "What calms you down? (comma-separated)",
            default=""
        )
        calming_activities = [a.strip() for a in calming_activities_input.split(",") if a.strip()]
        console.print(f"[dim]Activities: {', '.join(calming_activities) if calming_activities else '(none)'}[/dim]")
        if Confirm.ask("Is this correct?", default=True):
            break
    
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
    
    # Get current profile to show values
    try:
        summary = service.get_profile_summary(user_id)
        basic = summary["basic_info"]
        emotional = summary["emotional_baseline"]
    except:
        console.print("[yellow]No profile found. Please run 'tracker profile setup' first.[/yellow]")
        return
    
    console.print("\n[bold cyan]Update Profile[/bold cyan]")
    console.print("[dim]Choose a section, then update individual fields[/dim]\n")
    console.print("[bold]What would you like to update?[/bold]")
    console.print("  1. Basic info (nickname, tone, context depth)")
    console.print("  2. Emotional baseline (energy, stress, triggers)")
    console.print("  3. Work information")
    console.print("  4. Financial information")
    console.print("  5. Goals")
    console.print("  6. Lifestyle")
    
    choice = Prompt.ask("Choose section", choices=["1", "2", "3", "4", "5", "6"])
    
    console.print("\n[dim]Press Enter to keep current value, or type new value[/dim]\n")
    
    if choice == "1":
        console.print("[bold]Basic Information[/bold]\n")
        
        current_nickname = basic.get('nickname', 'Not set')
        console.print(f"[dim]Current: {current_nickname}[/dim]")
        nickname = Prompt.ask("Nickname (or Enter to keep)", default="")
        
        current_tone = basic.get('preferred_tone', 'Not set')
        console.print(f"\n[dim]Current: {current_tone}[/dim]")
        console.print("1=casual, 2=professional, 3=encouraging, 4=stoic")
        tone_choice = Prompt.ask("Tone (or Enter to keep)", default="")
        
        current_depth = basic.get('context_depth', 'basic')
        console.print(f"\n[dim]Current: {current_depth}[/dim]")
        console.print("1=basic, 2=personal, 3=deep")
        depth_choice = Prompt.ask("Context depth (or Enter to keep)", default="")
        
        # Apply updates
        if nickname:
            service.update_basic_info(user_id, nickname=nickname)
            console.print("[green]✓ Nickname updated[/green]")
        if tone_choice in ["1", "2", "3", "4"]:
            tone_map = {"1": "casual", "2": "professional", "3": "encouraging", "4": "stoic"}
            service.update_basic_info(user_id, preferred_tone=tone_map[tone_choice])
            console.print("[green]✓ Tone updated[/green]")
        if depth_choice in ["1", "2", "3"]:
            depth_map = {"1": "basic", "2": "personal", "3": "deep"}
            service.update_basic_info(user_id, context_depth=depth_map[depth_choice])
            console.print("[green]✓ Context depth updated[/green]")
            
    elif choice == "2":
        console.print("[bold]Emotional Baseline[/bold]\n")
        
        current_energy = emotional.get('energy', 5)
        console.print(f"[dim]Current: {current_energy}/10[/dim]")
        baseline_energy = Prompt.ask("Average energy (1-10, or Enter to keep)", default="")
        
        current_stress = emotional.get('stress', 5)
        console.print(f"\n[dim]Current: {current_stress}/10[/dim]")
        baseline_stress = Prompt.ask("Average stress (1-10, or Enter to keep)", default="")
        
        # Get current triggers as comma-separated string
        try:
            import json
            current_triggers = json.loads(emotional.get('stress_triggers', '[]')) if isinstance(emotional.get('stress_triggers'), str) else emotional.get('stress_triggers', [])
            current_triggers_str = ', '.join(current_triggers) if current_triggers else ''
        except:
            current_triggers_str = ''
        
        console.print(f"\n[dim]Current triggers: {current_triggers_str or 'None'}[/dim]")
        console.print("[dim]Stress triggers (comma-separated, edit to add/remove)[/dim]")
        triggers_input = Prompt.ask("Triggers", default=current_triggers_str)
        
        # Get current activities as comma-separated string
        try:
            current_activities = json.loads(emotional.get('calming_activities', '[]')) if isinstance(emotional.get('calming_activities'), str) else emotional.get('calming_activities', [])
            current_activities_str = ', '.join(current_activities) if current_activities else ''
        except:
            current_activities_str = ''
        
        console.print(f"\n[dim]Current activities: {current_activities_str or 'None'}[/dim]")
        console.print("[dim]Calming activities (comma-separated, edit to add/remove)[/dim]")
        activities_input = Prompt.ask("Activities", default=current_activities_str)
        
        # Apply updates
        updates = {}
        if baseline_energy:
            updates['baseline_energy'] = int(baseline_energy)
            console.print("[green]✓ Energy updated[/green]")
        if baseline_stress:
            updates['baseline_stress'] = float(baseline_stress)
            console.print("[green]✓ Stress updated[/green]")
        if triggers_input != current_triggers_str:
            updates['stress_triggers'] = [t.strip() for t in triggers_input.split(",") if t.strip()]
            console.print("[green]✓ Triggers updated[/green]")
        if activities_input != current_activities_str:
            updates['calming_activities'] = [a.strip() for a in activities_input.split(",") if a.strip()]
            console.print("[green]✓ Activities updated[/green]")
        
        if updates:
            service.update_emotional_context(user_id, **updates)
            
    elif choice == "3":
        _edit_work_info_cli(service, user_id)
    elif choice == "4":
        _edit_financial_info_cli(service, user_id)
    elif choice == "5":
        _edit_goals_cli(service, user_id)
    elif choice == "6":
        console.print("[yellow]Lifestyle update coming soon![/yellow]")
    
    console.print("\n[green]✓ Profile updated![/green]")


def _edit_work_info_cli(service: ProfileService, user_id: int):
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
    console.print("[green]✓ Work info updated[/green]")


def _edit_financial_info_cli(service: ProfileService, user_id: int):
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
    console.print("[green]✓ Financial info updated[/green]")


def _edit_goals_cli(service: ProfileService, user_id: int):
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
    console.print("[green]✓ Goals updated[/green]")


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
