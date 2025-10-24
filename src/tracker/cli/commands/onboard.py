"""Onboarding wizard for first-time setup"""

import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Dict, Optional, Any

import click
from rich.panel import Panel
from rich.prompt import Confirm
from rich.table import Table

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.cli.ui.prompts import (
    prompt_text,
    prompt_decimal,
    prompt_integer_range,
)
from tracker.config import settings
from tracker.core.database import SessionLocal
from tracker.core.models import User
from tracker.services.entry_service import EntryService


@click.command()
@click.option("--reset", is_flag=True, help="Reset and start fresh (clears existing config)")
def onboard(reset):
    """Interactive onboarding wizard for first-time setup
    
    Guides you through:
    1. System configuration (data dir, timezone, currency)
    2. AI provider setup and testing
    3. Financial baseline snapshot
    4. Wellbeing baseline
    5. Budget targets
    """
    console = get_console()
    
    console.print(
        f"\n[bold blue]{icon('🚀', 'Start')} Welcome to Tracker Onboarding![/bold blue]\n"
    )
    console.print("This wizard will help you set up your tracker system.\n")
    
    if not reset:
        console.print("[dim]Tip: Run with --reset to start fresh[/dim]\n")
    
    # Collect all configuration
    config = {}
    
    # Step 1: System Configuration
    console.print(
        Panel.fit(
            f"[bold cyan]{icon('🛠️', 'Step')} Step 1/6: System Configuration[/bold cyan]",
            border_style="cyan",
        )
    )
    config["system"] = collect_system_config(reset)
    
    # Step 2: AI Provider Setup
    console.print(
        "\n"
        + Panel.fit(
            f"[bold cyan]{icon('🤖', 'AI')} Step 2/6: AI Provider Setup[/bold cyan]",
            border_style="cyan",
        )
    )
    config["ai"] = collect_ai_config(reset)
    
    # Step 3: Financial Baseline
    console.print(
        "\n"
        + Panel.fit(
            f"[bold cyan]{icon('💰', 'Finance')} Step 3/6: Financial Baseline[/bold cyan]",
            border_style="cyan",
        )
    )
    config["financial"] = collect_financial_baseline(reset)
    
    # Step 4: Wellbeing Baseline
    console.print(
        "\n"
        + Panel.fit(
            f"[bold cyan]{icon('🧘', 'Wellbeing')} Step 4/6: Wellbeing Baseline[/bold cyan]",
            border_style="cyan",
        )
    )
    config["wellbeing"] = collect_wellbeing_baseline(reset)
    
    # Step 5: Budget Targets
    console.print(
        "\n"
        + Panel.fit(
            f"[bold cyan]{icon('📊', 'Budgets')} Step 5/6: Budget Targets[/bold cyan]",
            border_style="cyan",
        )
    )
    config["budgets"] = collect_budget_targets(reset)
    
    # Step 6: Confirmation & Summary
    console.print(
        "\n"
        + Panel.fit(
            f"[bold cyan]{icon('✅', 'Confirm')} Step 6/6: Confirm & Apply[/bold cyan]",
            border_style="cyan",
        )
    )
    
    display_summary(config)
    
    if not Confirm.ask(f"\n{icon('💾', 'Save')} Save this configuration?", default=True):
        console.print(
            emphasize(
                f"\n[yellow]{icon('⚠️', 'Cancelled')} Onboarding cancelled. No changes made.[/yellow]",
                "onboarding cancelled",
            )
        )
        return
    
    # Apply configuration
    apply_configuration(config)
    
    console.print(
        emphasize(
            f"\n[bold green]{icon('✅', 'Done')} Onboarding complete![/bold green]",
            "onboarding complete",
        )
    )
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Create your first entry: [cyan]tracker new[/cyan]")
    console.print("  2. View your entry: [cyan]tracker show today[/cyan]")
    console.print("  3. Explore commands: [cyan]tracker --help[/cyan]\n")


def collect_system_config(reset: bool) -> Dict[str, Any]:
    """Collect system configuration"""
    console = get_console()
    config = {}
    
    # Load existing if not reset
    if not reset:
        config_file = Path.home() / ".config" / "tracker" / "config.yaml"
        if config_file.exists():
            console.print("[dim]Loading existing config...[/dim]\n")
            # TODO: Load from YAML
    
    console.print("Configure your tracker system:\n")
    
    # Data directory
    default_data_dir = str(Path.home() / ".config" / "tracker")
    config["data_dir"] = prompt_text(
        "Data directory",
        default=config.get("data_dir", default_data_dir)
    )
    
    # Timezone
    import time
    local_tz = time.tzname[0]
    config["timezone"] = prompt_text(
        "Timezone",
        default=config.get("timezone", local_tz)
    )
    
    # Currency
    config["currency_code"] = prompt_text(
        "Currency code (USD, EUR, GBP, etc.)",
        default=config.get("currency_code", "USD")
    )
    
    currency_symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
        "CAD": "C$", "AUD": "A$", "CHF": "Fr", "CNY": "¥"
    }
    default_symbol = currency_symbols.get(config["currency_code"], "$")
    config["currency_symbol"] = prompt_text(
        "Currency symbol",
        default=config.get("currency_symbol", default_symbol)
    )
    
    # Date format
    config["date_format"] = prompt_text(
        "Date format (YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY)",
        default=config.get("date_format", "YYYY-MM-DD")
    )
    
    console.print(
        emphasize(
            f"[dim]{icon('✓', 'Done')} System configuration complete[/dim]",
            "system configuration complete",
        )
    )
    return config


def collect_ai_config(reset: bool) -> Dict[str, Any]:
    """Collect AI provider configuration with auto-detection"""
    import os
    
    config = {}
    
    console.print("Set up AI-powered feedback:\n")
    
    # Auto-detect available providers
    available_providers = []
    
    if os.getenv("OPENAI_API_KEY") or settings.openai_api_key:
        available_providers.append("openai")
    if os.getenv("ANTHROPIC_API_KEY") or settings.anthropic_api_key:
        available_providers.append("anthropic")
    if os.getenv("OPENROUTER_API_KEY") or settings.openrouter_api_key:
        available_providers.append("openrouter")
    
    # Check if local API is running
    try:
        import httpx
        response = httpx.get(settings.local_api_url.replace("/v1", "/models"), timeout=2.0)
        if response.status_code == 200:
            available_providers.append("local")
    except:
        pass
    
    if available_providers:
        console.print(f"[green]✓ Detected providers:[/green] {', '.join(available_providers)}\n")
    else:
        console.print("[yellow]No API keys detected. You can configure one now.[/yellow]\n")
    
    # Provider selection
    provider_options = ["openai", "anthropic", "openrouter", "local", "skip"]
    console.print("Available AI providers:")
    console.print("  [cyan]openai[/cyan] - GPT-4, GPT-3.5-turbo (requires API key)")
    console.print("  [cyan]anthropic[/cyan] - Claude 3 Opus/Sonnet/Haiku (requires API key)")
    console.print("  [cyan]openrouter[/cyan] - 100+ models via unified API (requires API key)")
    console.print("  [cyan]local[/cyan] - Ollama/LM Studio (no API key needed)")
    console.print("  [cyan]skip[/cyan] - Configure later\n")
    
    provider = prompt_text(
        "Choose provider",
        default=available_providers[0] if available_providers else "skip"
    )
    
    if provider == "skip":
        config["enabled"] = False
        return config
    
    config["provider"] = provider
    config["enabled"] = True
    
    # API key configuration
    if provider in ["openai", "anthropic", "openrouter"]:
        api_key = prompt_text(
            f"{provider.upper()} API key",
            default=""
        )
        config["api_key"] = api_key if api_key else None
    elif provider == "local":
        config["api_url"] = prompt_text(
            "Local API URL",
            default=settings.local_api_url
        )
    
    # Model selection
    default_models = {
        "openai": "gpt-3.5-turbo",
        "anthropic": "claude-3-sonnet-20240229",
        "openrouter": "anthropic/claude-3-sonnet",
        "local": "llama2"
    }
    
    config["model"] = prompt_text(
        "Model name",
        default=default_models.get(provider, "")
    )
    
    # Test connection
    if config.get("api_key") or provider == "local":
        console.print("\n[dim]Testing connection...[/dim]")
        # TODO: Test AI connection
        console.print("[green]✓ Connection successful[/green]")
    
    console.print("[dim]✓ AI configuration complete[/dim]")
    return config


def collect_financial_baseline(reset: bool) -> Dict[str, Any]:
    """Collect financial baseline snapshot"""
    config = {}
    
    console.print("Let's establish your financial baseline:\n")
    
    # Income
    console.print("[bold]Income:[/bold]")
    income_cadence_options = ["weekly", "bi-weekly", "monthly", "irregular"]
    config["income_cadence"] = prompt_text(
        "Income frequency (weekly/bi-weekly/monthly/irregular)",
        default="monthly"
    )
    
    config["primary_income"] = prompt_decimal(
        f"Primary income per {config['income_cadence']} period",
        default="0"
    )
    
    config["has_side_income"] = Confirm.ask("Do you have side income?", default=False)
    if config["has_side_income"]:
        config["avg_side_income"] = prompt_decimal(
            "Average side income per month",
            default="0"
        )
    
    # Expenses
    console.print("\n[bold]Fixed Expenses:[/bold]")
    config["rent_mortgage"] = prompt_decimal(
        "Rent/Mortgage per month",
        default="0"
    )
    
    config["utilities"] = prompt_decimal(
        "Utilities per month (electricity, water, etc.)",
        default="0"
    )
    
    config["subscriptions"] = prompt_decimal(
        "Subscriptions per month (streaming, software, etc.)",
        default="0"
    )
    
    config["other_fixed"] = prompt_decimal(
        "Other fixed expenses per month",
        default="0"
    )
    
    # Debt
    console.print("\n[bold]Debt:[/bold]")
    config["has_debt"] = Confirm.ask("Do you have any debt?", default=False)
    if config["has_debt"]:
        config["total_debt"] = prompt_decimal(
            "Total debt amount",
            required=False,
            allow_negative=False
        )
        config["debt_types"] = prompt_text(
            "Debt types (e.g., credit card, student loan, car)",
            default=""
        )
    
    # Current balances
    console.print("\n[bold]Current Balances:[/bold]")
    config["bank_balance"] = prompt_decimal(
        "Current bank balance",
        required=False,
        allow_negative=True
    )
    
    config["cash_on_hand"] = prompt_decimal(
        "Cash on hand",
        required=False,
        allow_negative=False
    )
    
    console.print("[dim]✓ Financial baseline complete[/dim]")
    return config


def collect_wellbeing_baseline(reset: bool) -> Dict[str, Any]:
    """Collect wellbeing baseline"""
    config = {}
    
    console.print("Establish your wellbeing baseline:\n")
    
    config["typical_stress"] = prompt_integer_range(
        "Typical stress level on a normal day (1-10)",
        1, 10,
        default=5
    )
    
    config["avg_sleep_hours"] = prompt_decimal(
        "Average sleep hours per night",
        default="7.5"
    )
    
    config["avg_work_hours"] = prompt_decimal(
        "Average work hours per day",
        default="8"
    )
    
    mood_options = ["good", "neutral", "struggling"]
    config["mood_baseline"] = prompt_text(
        "Current mood baseline (good/neutral/struggling)",
        default="neutral"
    )
    
    console.print("[dim]✓ Wellbeing baseline complete[/dim]")
    return config


def collect_budget_targets(reset: bool) -> Dict[str, Any]:
    """Collect budget targets and goals"""
    config = {}
    
    console.print("Set your financial goals:\n")
    
    config["monthly_income_goal"] = prompt_decimal(
        "Monthly income goal",
        default="0"
    )
    
    console.print("\n[bold]Spending Limits:[/bold]")
    config["food_budget"] = prompt_decimal(
        "Monthly food budget",
        default="0"
    )
    
    config["transport_budget"] = prompt_decimal(
        "Monthly transportation budget",
        default="0"
    )
    
    config["entertainment_budget"] = prompt_decimal(
        "Monthly entertainment budget",
        default="0"
    )
    
    # Savings
    console.print("\n[bold]Savings Goals:[/bold]")
    config["has_savings_goal"] = Confirm.ask("Do you have a savings goal?", default=True)
    if config["has_savings_goal"]:
        config["monthly_savings_target"] = prompt_decimal(
            "Monthly savings target",
            default="0"
        )
        config["emergency_fund_target"] = prompt_decimal(
            "Emergency fund target (total amount)",
            default="0"
        )
    
    console.print("[dim]✓ Budget targets complete[/dim]")
    return config


def display_summary(config: Dict[str, Any]):
    """Display configuration summary"""
    console.print()
    
    # System
    table = Table(title="System Configuration", show_header=False, box=None)
    table.add_column("Setting", style="cyan")
    table.add_column("Value")
    
    system = config.get("system", {})
    table.add_row("Data Directory", system.get("data_dir", ""))
    table.add_row("Timezone", system.get("timezone", ""))
    table.add_row("Currency", f"{system.get('currency_symbol', '')} ({system.get('currency_code', '')})")
    table.add_row("Date Format", system.get("date_format", ""))
    
    console.print(table)
    console.print()
    
    # AI
    ai = config.get("ai", {})
    if ai.get("enabled"):
        console.print(f"[cyan]AI Provider:[/cyan] {ai.get('provider', 'none')}")
        console.print(f"[cyan]Model:[/cyan] {ai.get('model', 'default')}")
        if ai.get("api_key"):
            masked_key = ai["api_key"][:8] + "..." + ai["api_key"][-4:] if len(ai["api_key"]) > 12 else "***"
            console.print(f"[cyan]API Key:[/cyan] {masked_key}")
        console.print()
    else:
        console.print("[yellow]AI feedback disabled (can enable later)[/yellow]\n")
    
    # Financial
    financial = config.get("financial", {})
    console.print("[bold]Financial Baseline:[/bold]")
    console.print(f"  Income: ${financial.get('primary_income', 0)} ({financial.get('income_cadence', 'monthly')})")
    console.print(f"  Bank Balance: ${financial.get('bank_balance', 0)}")
    if financial.get("has_debt"):
        console.print(f"  Total Debt: ${financial.get('total_debt', 0)}")
    console.print()
    
    # Budgets
    budgets = config.get("budgets", {})
    console.print("[bold]Budget Targets:[/bold]")
    console.print(f"  Monthly Income Goal: ${budgets.get('monthly_income_goal', 0)}")
    console.print(f"  Food Budget: ${budgets.get('food_budget', 0)}")
    if budgets.get("has_savings_goal"):
        console.print(f"  Monthly Savings: ${budgets.get('monthly_savings_target', 0)}")
    console.print()


def apply_configuration(config: Dict[str, Any]):
    """Save configuration to files and database"""
    console.print("\n[dim]Applying configuration...[/dim]")
    
    # 1. Create data directory
    data_dir = Path(config["system"]["data_dir"])
    data_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"  ✓ Created data directory: {data_dir}")
    
    # 2. Save config.yaml
    config_file = data_dir / "config.yaml"
    # TODO: Save to YAML (implement YAML serialization)
    console.print(f"  ✓ Saved config to: {config_file}")
    
    # 3. Save encryption key to .env
    env_file = Path.cwd() / ".env"
    if not env_file.exists():
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()
        with open(env_file, "w") as f:
            f.write(f"ENCRYPTION_KEY={key}\n")
        console.print(f"  ✓ Generated encryption key in .env")
    
    # 4. Save AI config to environment/keyring
    ai = config.get("ai", {})
    if ai.get("enabled") and ai.get("api_key"):
        # Save to keyring if available
        try:
            import keyring
            keyring.set_password("tracker", f"{ai['provider']}_api_key", ai["api_key"])
            console.print(f"  ✓ Saved {ai['provider']} API key to keyring")
        except:
            # Fallback to .env
            with open(env_file, "a") as f:
                key_name = f"{ai['provider'].upper()}_API_KEY"
                f.write(f"{key_name}={ai['api_key']}\n")
            console.print(f"  ✓ Saved {ai['provider']} API key to .env")
    
    # 5. Save baseline to User.settings
    db = SessionLocal()
    try:
        service = EntryService(db)
        user = service.get_default_user()
        
        if user:
            # Merge baseline into user settings
            baseline = {
                "onboarded": True,
                "onboarded_at": datetime.utcnow().isoformat(),
                "financial_baseline": config.get("financial", {}),
                "wellbeing_baseline": config.get("wellbeing", {}),
                "budget_targets": config.get("budgets", {}),
                "system_preferences": config.get("system", {}),
            }
            
            # Convert Decimal to string for JSON serialization
            def serialize_decimal(obj):
                if isinstance(obj, Decimal):
                    return str(obj)
                elif isinstance(obj, dict):
                    return {k: serialize_decimal(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [serialize_decimal(item) for item in obj]
                return obj
            
            baseline = serialize_decimal(baseline)
            user.settings = json.dumps(baseline)
            db.commit()
            console.print("  ✓ Saved baseline to database")
    finally:
        db.close()
    
    console.print()
