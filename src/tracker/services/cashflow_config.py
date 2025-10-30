"""Cash flow configuration management

Manages weekly payroll, recurring bills, and installments in ~/.config/tracker/cashflow.toml
"""

import tomllib
from dataclasses import dataclass, field
from datetime import date as DateType
from pathlib import Path
from typing import Any, Optional

from tracker.config import get_config_dir


@dataclass
class PayrollConfig:
    """Payroll cadence configuration"""
    payday: str = "THURSDAY"  # Day of week for payday
    net_pay_usd: float = 1300.00  # Weekly net pay in USD
    payday_is_thursday: bool = True  # Backward compat
    week_start: str = "FRI"  # FRI-THU window by default


@dataclass
class RecurringWeeklyRule:
    """Special rules for weekly recurring items"""
    reserved_then_clears: bool = False
    reserve_day: str = "THURSDAY"
    clear_day: str = "FRIDAY"
    reserve_account: str = "acorns_checking"


@dataclass
class RecurringWeekly:
    """Weekly recurring bills"""
    EarnIn: float = 600.00
    SnapOn: float = 400.00
    ChaseTransfer: float = 180.00


@dataclass
class EssentialsGas:
    """Gas fill configuration"""
    fill_cost_usd: float = 55.00
    fill_frequency_days: int = 2
    workdays: list[str] = field(default_factory=lambda: ["TUE", "WED", "THU", "FRI", "SAT"])


@dataclass
class EssentialsConfig:
    """Essential recurring expenses"""
    food_weekly_usd: float = 125.00
    pets_weekly_usd: float = 60.00
    gas: EssentialsGas = field(default_factory=EssentialsGas)


@dataclass
class Installment:
    """Scheduled installment payment"""
    amount_usd: float
    date: str  # YYYY-MM-DD
    provider: str
    category: str


@dataclass
class AccountsConfig:
    """Account tracking"""
    primary: str = "chase"


@dataclass
class ProviderConfig:
    """Provider definition"""
    type: str  # 'advance', 'auto_debit', 'checking', etc.
    account: str
    

@dataclass
class LoopInclude:
    """Loop inclusion criteria"""
    event_type: str
    provider: Optional[str] = None


@dataclass
class LoopConfig:
    """Loop definition for paired cash flow events"""
    name: str
    includes: list[LoopInclude]


@dataclass
class WeeklyBudgetDefaults:
    """Default weekly budget amounts (backward compat)"""
    gas_usd: float = 150.0
    food_usd: float = 125.0
    

@dataclass
class DefaultsConfig:
    """Default values for various features"""
    weekly_budget: WeeklyBudgetDefaults = field(default_factory=WeeklyBudgetDefaults)


@dataclass
class CashFlowConfig:
    """Complete cash flow configuration"""
    payroll: PayrollConfig = field(default_factory=PayrollConfig)
    accounts: AccountsConfig = field(default_factory=AccountsConfig)
    providers: dict[str, ProviderConfig] = field(default_factory=dict)
    loops: list[LoopConfig] = field(default_factory=list)
    recurring_weekly: RecurringWeekly = field(default_factory=RecurringWeekly)
    recurring_weekly_rules: dict[str, RecurringWeeklyRule] = field(default_factory=dict)
    recurring_monthly: dict[str, float] = field(default_factory=dict)
    essentials: EssentialsConfig = field(default_factory=EssentialsConfig)
    installments: dict[str, Installment] = field(default_factory=dict)
    defaults: DefaultsConfig = field(default_factory=DefaultsConfig)
    
    # Essential categories for analytics
    essential_categories: set[str] = field(default_factory=lambda: {
        'gas', 'food', 'rent', 'utilities', 'insurance', 'subscription', 'pets'
    })


def get_config_path() -> Path:
    """Get the path to cashflow.toml"""
    return get_config_dir() / "cashflow.toml"


def write_user_config(path: Path) -> None:
    """Write user's real configuration to TOML file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    content = """# Tracker Cash Flow Configuration
# Ground truth: Your real weekly cadence and recurring bills

[payroll]
payday = "THURSDAY"      # Day of week for payday
net_pay_usd = 1300.00    # Weekly net pay deposited Thursday night

[accounts]
primary = "chase"

# Weekly recurring bills (every week)
[recurring.weekly]
EarnIn = 600.00          # Repayment Thursday night/Friday morning
SnapOn = 400.00          # Via Acorns - see special rule below
ChaseTransfer = 180.00   # End of week transfer

# Special handling for Snap-On (reserve-then-clear pattern)
[recurring.weekly_rules.SnapOn]
reserved_then_clears = true
reserve_day = "THURSDAY"       # Move $400 to Acorns Thursday
clear_day = "FRIDAY"           # Snap-On autopull Friday (already reserved)
reserve_account = "acorns_checking"

# Essential expenses
[essentials]
food_weekly_usd = 125.00      # Weekly food budget
pets_weekly_usd = 60.00       # Weekly pet expenses (cats)

[essentials.gas]
fill_cost_usd = 55.00         # Cost per gas fill
fill_frequency_days = 2       # Fill every 2 days
workdays = ["TUE", "WED", "THU", "FRI", "SAT"]  # Workweek schedule

# Scheduled installments (provider-agnostic, date-based)
[installments]
# Examples - add via CLI: tracker add-installment
# "AutoZone_2025-11-08" = { amount_usd = 22.97, date = "2025-11-08", provider = "klarna", category = "auto_parts" }
# "AutoZone_2025-11-22" = { amount_usd = 22.97, date = "2025-11-22", provider = "klarna", category = "auto_parts" }
# "OReilly_2025-11-19"  = { amount_usd = 18.46, date = "2025-11-19", provider = "klarna", category = "auto_parts" }

# Providers (for loop tracking)
[providers.earnin]
type = "advance"
account = "chase"

[providers.snapon]
type = "auto_debit"
account = "acorns_checking"

# Loops (for cash flow analysis)
[[loops]]
name = "earnin_loop"
includes = [
  { event_type = "advance", provider = "earnin" },
  { event_type = "repayment", provider = "earnin" }
]

[[loops]]
name = "snapon_loop"
includes = [
  { event_type = "bill", provider = "snapon" }
]
"""
    
    path.write_text(content)


def load_config() -> CashFlowConfig:
    """Load configuration from cashflow.toml, creating default if missing"""
    config_path = get_config_path()
    
    if not config_path.exists():
        write_user_config(config_path)
    
    with open(config_path, "rb") as f:
        data = tomllib.load(f)
    
    # Parse payroll config
    payroll_data = data.get("payroll", {})
    payroll = PayrollConfig(
        payday=payroll_data.get("payday", "THURSDAY"),
        net_pay_usd=payroll_data.get("net_pay_usd", 1300.00),
        payday_is_thursday=payroll_data.get("payday", "THURSDAY").upper() == "THURSDAY",
        week_start=payroll_data.get("week_start", "FRI"),
    )
    
    # Parse accounts config
    accounts_data = data.get("accounts", {})
    accounts = AccountsConfig(
        primary=accounts_data.get("primary", "chase"),
    )
    
    # Parse recurring weekly
    recurring_data = data.get("recurring", {})
    weekly_data = recurring_data.get("weekly", {})
    recurring_weekly = RecurringWeekly(
        EarnIn=weekly_data.get("EarnIn", 600.00),
        SnapOn=weekly_data.get("SnapOn", 400.00),
        ChaseTransfer=weekly_data.get("ChaseTransfer", 180.00),
    )
    
    # Parse recurring weekly rules
    rules_data = recurring_data.get("weekly_rules", {})
    recurring_weekly_rules = {}
    for name, rule_data in rules_data.items():
        recurring_weekly_rules[name] = RecurringWeeklyRule(
            reserved_then_clears=rule_data.get("reserved_then_clears", False),
            reserve_day=rule_data.get("reserve_day", "THURSDAY"),
            clear_day=rule_data.get("clear_day", "FRIDAY"),
            reserve_account=rule_data.get("reserve_account", "acorns_checking"),
        )
    
    # Parse essentials
    essentials_data = data.get("essentials", {})
    gas_data = essentials_data.get("gas", {})
    essentials = EssentialsConfig(
        food_weekly_usd=essentials_data.get("food_weekly_usd", 125.00),
        pets_weekly_usd=essentials_data.get("pets_weekly_usd", 60.00),
        gas=EssentialsGas(
            fill_cost_usd=gas_data.get("fill_cost_usd", 55.00),
            fill_frequency_days=gas_data.get("fill_frequency_days", 2),
            workdays=gas_data.get("workdays", ["TUE", "WED", "THU", "FRI", "SAT"]),
        ),
    )
    
    # Parse installments
    installments = {}
    installments_data = data.get("installments", {})
    for name, inst_data in installments_data.items():
        installments[name] = Installment(
            amount_usd=inst_data["amount_usd"],
            date=inst_data["date"],
            provider=inst_data["provider"],
            category=inst_data["category"],
        )
    
    # Parse providers
    providers = {}
    providers_data = data.get("providers", {})
    for name, prov_data in providers_data.items():
        providers[name] = ProviderConfig(
            type=prov_data.get("type", "generic"),
            account=prov_data.get("account", accounts.primary),
        )
    
    # Parse loops
    loops = []
    loops_data = data.get("loops", [])
    for loop_data in loops_data:
        includes = []
        for inc in loop_data.get("includes", []):
            includes.append(LoopInclude(
                event_type=inc["event_type"],
                provider=inc.get("provider"),
            ))
        
        loops.append(LoopConfig(
            name=loop_data["name"],
            includes=includes,
        ))
    
    # Parse defaults (backward compat)
    defaults_data = data.get("defaults", {})
    budget_data = defaults_data.get("weekly_budget", {})
    defaults = DefaultsConfig(
        weekly_budget=WeeklyBudgetDefaults(
            gas_usd=budget_data.get("gas_usd", 150.0),
            food_usd=budget_data.get("food_usd", 125.0),
        )
    )
    
    return CashFlowConfig(
        payroll=payroll,
        accounts=accounts,
        recurring_weekly=recurring_weekly,
        recurring_weekly_rules=recurring_weekly_rules,
        essentials=essentials,
        installments=installments,
        providers=providers,
        loops=loops,
        defaults=defaults,
    )


def save_config(config: CashFlowConfig, path: Optional[Path] = None) -> None:
    """Save configuration back to TOML file
    
    Args:
        config: Configuration to save
        path: Optional path (defaults to standard config path)
    """
    if path is None:
        path = get_config_path()
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build TOML content
    lines = []
    lines.append("# Tracker Cash Flow Configuration\n")
    lines.append("# Ground truth: Your real weekly cadence and recurring bills\n\n")
    
    # Payroll
    lines.append("[payroll]\n")
    lines.append(f'payday = "{config.payroll.payday}"\n')
    lines.append(f"net_pay_usd = {config.payroll.net_pay_usd}\n\n")
    
    # Accounts
    lines.append("[accounts]\n")
    lines.append(f'primary = "{config.accounts.primary}"\n\n')
    
    # Recurring weekly
    lines.append("# Weekly recurring bills (every week)\n")
    lines.append("[recurring.weekly]\n")
    lines.append(f"EarnIn = {config.recurring_weekly.EarnIn}\n")
    lines.append(f"SnapOn = {config.recurring_weekly.SnapOn}\n")
    lines.append(f"ChaseTransfer = {config.recurring_weekly.ChaseTransfer}\n\n")
    
    # Recurring weekly rules
    if config.recurring_weekly_rules:
        for name, rule in config.recurring_weekly_rules.items():
            lines.append(f"[recurring.weekly_rules.{name}]\n")
            lines.append(f"reserved_then_clears = {str(rule.reserved_then_clears).lower()}\n")
            lines.append(f'reserve_day = "{rule.reserve_day}"\n')
            lines.append(f'clear_day = "{rule.clear_day}"\n')
            lines.append(f'reserve_account = "{rule.reserve_account}"\n\n')
    
    # Essentials
    lines.append("# Essential expenses\n")
    lines.append("[essentials]\n")
    lines.append(f"food_weekly_usd = {config.essentials.food_weekly_usd}\n")
    lines.append(f"pets_weekly_usd = {config.essentials.pets_weekly_usd}\n\n")
    
    lines.append("[essentials.gas]\n")
    lines.append(f"fill_cost_usd = {config.essentials.gas.fill_cost_usd}\n")
    lines.append(f"fill_frequency_days = {config.essentials.gas.fill_frequency_days}\n")
    workdays_str = ", ".join(f'"{d}"' for d in config.essentials.gas.workdays)
    lines.append(f"workdays = [{workdays_str}]\n\n")
    
    # Installments
    lines.append("# Scheduled installments (provider-agnostic, date-based)\n")
    lines.append("[installments]\n")
    for name, inst in config.installments.items():
        lines.append(f'"{name}" = {{ amount_usd = {inst.amount_usd}, date = "{inst.date}", provider = "{inst.provider}", category = "{inst.category}" }}\n')
    lines.append("\n")
    
    # Providers
    lines.append("# Providers (for loop tracking)\n")
    for name, prov in config.providers.items():
        lines.append(f"[providers.{name}]\n")
        lines.append(f'type = "{prov.type}"\n')
        lines.append(f'account = "{prov.account}"\n\n')
    
    # Loops
    lines.append("# Loops (for cash flow analysis)\n")
    for loop in config.loops:
        lines.append("[[loops]]\n")
        lines.append(f'name = "{loop.name}"\n')
        lines.append("includes = [\n")
        for inc in loop.includes:
            if inc.provider:
                lines.append(f'  {{ event_type = "{inc.event_type}", provider = "{inc.provider}" }},\n')
            else:
                lines.append(f'  {{ event_type = "{inc.event_type}" }},\n')
        lines.append("]\n\n")
    
    path.write_text("".join(lines))


def set_config_value(key: str, value: Any) -> None:
    """Set a configuration value and save
    
    Args:
        key: Dotted key path (e.g., "payroll.net_pay_usd")
        value: Value to set
    """
    config = load_config()
    
    # Navigate to the value
    parts = key.split(".")
    obj = config
    
    for i, part in enumerate(parts[:-1]):
        if hasattr(obj, part):
            obj = getattr(obj, part)
        else:
            raise ValueError(f"Invalid config key: {key}")
    
    # Set the value
    final_key = parts[-1]
    if hasattr(obj, final_key):
        setattr(obj, final_key, value)
    else:
        raise ValueError(f"Invalid config key: {key}")
    
    # Save
    save_config(config)
