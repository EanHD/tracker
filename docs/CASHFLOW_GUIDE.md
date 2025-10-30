# Cash Flow Loop Tracking Guide

The Tracker app now includes a powerful, provider-agnostic cash flow tracking system that helps you understand how repeating money loops (like payday advances, auto-debits, BNPL, etc.) affect your weekly finances.

## Table of Contents

1. [Core Concepts](#core-concepts)
2. [Getting Started](#getting-started)
3. [Configuration](#configuration)
4. [CLI Commands](#cli-commands)
5. [Use Cases & Examples](#use-cases--examples)
6. [Analytics Explained](#analytics-explained)

## Core Concepts

### Cash Flow Events

Every money movement is recorded as an **event** with:
- **Date**: When it happened
- **Type**: `income`, `bill`, `transfer`, `spend`, `advance`, `repayment`, or `fee`
- **Provider**: User-defined (e.g., "advance_app", "tool_truck", "acorns_checking")
- **Category**: Optional classification (e.g., "gas", "food", "rent")
- **Amount**: In USD (positive = outflow/expense, negative = inflow/income)
- **Account**: Which account (e.g., "chase", "cash")
- **Memo**: Optional notes

### Loops

A **loop** is a set of related cash flow events that form a cycle. For example:
- **Pay advance loop**: You get an advance (inflow) → Later you repay it (outflow)
- **Tool truck loop**: Auto-debit for tool payments (recurring outflow)
- **BNPL loop**: Buy now pay later transactions and their payments

Loops help you see the **true financial impact** of these arrangements by showing:
- How much they add to your available cash short-term
- How much they strain your budget long-term
- Whether you're increasing or decreasing usage over time

### Week Windows

By default, the system uses a **Thursday payroll cadence** with a **Fri→Thu week**. This aligns with most bi-weekly or weekly paychecks that hit on Thursday night.

You can customize this in the config to match your actual payroll schedule.

## Getting Started

### 1. Initialize Database (if not done)

```bash
tracker init
```

### 2. View Default Configuration

```bash
tracker cashflow config-show
```

This shows your providers, loops, and settings at:
```
~/.config/tracker/cashflow.toml
```

### 3. Add Your First Event

You can add events using plain English sentences at the main menu prompt or in the Help screen:

**Plain Sentence Examples:**
- "I spent $45.50 on gas at Shell station"
- "Got paycheck of $1200"
- "Received $200 advance from EarnIn"
- "Paid $400 to Snap-On for tools"

**Or use CLI commands:**
```bash
# Record gas spending
tracker cashflow add-event --type spend --category gas --amount 45.50 --account chase --memo "Fill up"

# Record income
tracker cashflow add-event --type income --amount -1200 --account chase --memo "Paycheck"

# Record an advance (part of a loop)
tracker cashflow add-event --type advance --provider my_advance_app --amount -200 --account chase
```

### 4. View Your Week

```bash
tracker cashflow week
```

## Configuration

Configuration is stored in `~/.config/tracker/cashflow.toml`.

### Full Example Config

```toml
# Tracker Cash Flow Configuration

[payroll]
payday_is_thursday = true   # Thursday night payroll
week_start = "FRI"          # Week runs Fri→Thu

[accounts]
primary = "chase"

# Define your providers (no brand names hardcoded!)
[providers.my_advance_app]
type = "advance"
account = "chase"

[providers.tool_truck]
type = "auto_debit"
account = "acorns_checking"

[providers.gym]
type = "subscription"
account = "chase"

# Define loops to track paired events
[[loops]]
name = "advance_loop"
includes = [
  { event_type = "advance", provider = "my_advance_app" },
  { event_type = "repayment", provider = "my_advance_app" }
]

[[loops]]
name = "tool_payments"
includes = [
  { event_type = "bill", provider = "tool_truck" }
]

[defaults.weekly_budget]
gas_usd = 150.0
food_usd = 125.0
```

### Modifying Config

```bash
# Change Thursday payroll setting
tracker cashflow config-set payroll.payday_is_thursday false

# Update weekly gas budget
tracker cashflow config-set defaults.weekly_budget.gas_usd 175.0

# View current config
tracker cashflow config-show
```

## CLI Commands

### `tracker cashflow add-event`

Record a cash flow event.

**Options:**
- `--date YYYY-MM-DD`: Event date (defaults to today)
- `--type`: Required. One of: income, bill, transfer, spend, advance, repayment, fee
- `--provider TEXT`: Provider name (must match config)
- `--category TEXT`: Category (gas, food, rent, etc.)
- `--amount FLOAT`: Required. Amount in USD (positive=expense, negative=income)
- `--account TEXT`: Account name
- `--memo TEXT`: Optional notes

**Examples:**

```bash
# Basic spending
tracker cashflow add-event --type spend --category food --amount 85 --account chase

# Advance (negative because it's an inflow)
tracker cashflow add-event --type advance --provider my_advance_app --amount -200 --account chase

# Repayment
tracker cashflow add-event --type repayment --provider my_advance_app --amount 50 --account chase

# Backdated event
tracker cashflow add-event --type income --amount -1200 --date 2025-10-23 --account chase
```

### `tracker cashflow week`

Show weekly summary with loop analysis.

**Options:**
- `--end YYYY-MM-DD`: Week end date (defaults to current week)

**Output includes:**
- Income total for the week
- Essentials breakdown (gas, food, rent, etc.)
- Per-loop summaries showing inflows, outflows, and net impact
- Week-over-week comparison for each loop
- End-of-week cash with and without loops (shows "loop strain")

### `tracker cashflow month`

Show monthly report with extended analysis.

**Options:**
- `--month YYYY-MM`: Month to report (defaults to current month)

**Output includes:**
- Loop overview: weeks used, total inflows/outflows, strain
- Streak tracking: current and best streaks without each loop
- Top spending categories
- Recommendations for reducing loop usage

### `tracker cashflow import`

Import events from CSV file.

**CSV Format:**
```
date,type,provider,category,amount,account,memo
2025-10-20,spend,gas,,45.50,chase,Shell station
2025-10-21,income,,,,-1200,chase,Paycheck
2025-10-22,advance,my_advance_app,,-200,chase,Emergency
```

**Usage:**
```bash
tracker cashflow import transactions.csv
```

### `tracker cashflow config-show`

Display current configuration.

### `tracker cashflow config-set`

Update a configuration value.

**Examples:**
```bash
tracker cashflow config-set payroll.week_start "MON"
tracker cashflow config-set defaults.weekly_budget.food_usd 150.0
```

## Use Cases & Examples

### Scenario 1: Tracking Payday Advance Apps

**Setup:**

Edit `~/.config/tracker/cashflow.toml`:

```toml
[providers.earnin]
type = "advance"
account = "checking"

[[loops]]
name = "earnin_advances"
includes = [
  { event_type = "advance", provider = "earnin" },
  { event_type = "repayment", provider = "earnin" },
  { event_type = "fee", provider = "earnin" }
]
```

**Usage:**

**Plain sentences:**
- "Got $150 advance from EarnIn on 2025-10-20"
- "Repaid $150 to EarnIn on 2025-10-23"
- "Paid $10 fee to EarnIn on 2025-10-23"

**Or CLI commands:**
```bash
# Get advance
tracker cashflow add-event --type advance --provider earnin --amount -150 --date 2025-10-20

# Pay it back on payday
tracker cashflow add-event --type repayment --provider earnin --amount 150 --date 2025-10-23

# Optional tip/fee
tracker cashflow add-event --type fee --provider earnin --amount 10 --date 2025-10-23

# See the impact
tracker cashflow week
```

**Analysis:**

The week summary will show:
- Short-term boost: +$150 from advance
- Long-term cost: -$160 in repayment+fees
- Net strain: -$10 this week

### Scenario 2: Tool Truck Auto-Debit

**Setup:**

```toml
[providers.snap_on]
type = "auto_debit"
account = "checking"

[[loops]]
name = "tool_payments"
includes = [
  { event_type = "bill", provider = "snap_on" }
]
```

**Usage:**

**Plain sentence:**
- "Paid $400 bill to Snap-On for tools on 2025-10-24"

**Or CLI command:**
```bash
# Weekly debit
tracker cashflow add-event --type bill --provider snap_on --amount 400 --date 2025-10-24 --category tools

# View monthly trend
tracker cashflow month --month 2025-10
```

### Scenario 3: Multiple Loops

Track all your loops together:

```bash
# Regular income
tracker cashflow add-event --type income --amount -1000 --date 2025-10-23

# Essentials
tracker cashflow add-event --type spend --category gas --amount 50 --date 2025-10-24
tracker cashflow add-event --type spend --category food --amount 120 --date 2025-10-25

# Advance loop
tracker cashflow add-event --type advance --provider app1 --amount -200 --date 2025-10-24

# Tool payment loop
tracker cashflow add-event --type bill --provider tools --amount 400 --date 2025-10-25

# BNPL loop
tracker cashflow add-event --type repayment --provider affirm --amount 75 --date 2025-10-26

# See everything
tracker cashflow week
```

## Analytics Explained

### End-of-Week Cash (With vs Without Loops)

The system calculates two scenarios:

1. **With loops**: Includes all inflows and outflows
2. **Without loops**: Excludes loop inflows but keeps outflows

**Example:**

```
Income:             $1,000
Gas:                -$50
Food:               -$120
Advance inflow:     +$200  (loop)
Advance repayment:  -$0    (not due yet)
Tool payment:       -$400  (loop)

With loops:    $1,000 - $50 - $120 + $200 - $400 = $630
Without loops: $1,000 - $50 - $120 - $400 = $430
Loop strain:   $200 (the advance you'll need to repay)
```

This shows you're relying on the advance to stay afloat. Without it, you'd be $200 short.

### Loop Trends

Week-over-week comparison shows:
- ↑ = Usage increased (more strain)
- ↓ = Usage decreased (improving)
- same = No change

### Streaks

Tracking weeks without using a loop:
- **Current streak**: Consecutive weeks from now going backward
- **Best streak**: Longest streak ever

Helps you see progress in breaking loop dependency.

### Recommendations

The monthly report suggests specific reductions:
```
Recommendations:
  → Reduce earnin_advances usage by $100 next month
  → Reduce tool_payments usage by $100 next month
```

## Advanced: CSV Bulk Import

Create a spreadsheet with all your transactions:

**transactions.csv:**
```csv
date,type,provider,category,amount,account,memo
2025-10-01,income,,,,-2000,chase,Paycheck 1
2025-10-01,bill,rent,,1200,chase,Rent
2025-10-02,spend,,gas,45,chase,Gas
2025-10-03,spend,,food,30,chase,Groceries
2025-10-05,advance,app1,,-150,chase,Emergency advance
2025-10-10,spend,,food,40,chase,Groceries
2025-10-15,income,,,,-2000,chase,Paycheck 2
2025-10-15,repayment,app1,,150,chase,Repay advance
2025-10-15,fee,app1,,10,chase,Advance fee
```

Import:
```bash
tracker cashflow import transactions.csv
```

## Tips for Success

1. **Record everything**: The more complete your data, the better the insights
2. **Use consistent providers**: Stick to the same provider names (defined in config)
3. **Set realistic budgets**: Update weekly_budget defaults to match your actual needs
4. **Review weekly**: Run `tracker cashflow week` every Friday to stay aware
5. **Track month-to-month**: Use `tracker cashflow month` to see long-term trends
6. **Use plain sentences for quick entry**: Type natural language sentences like "Spent $50 on food" directly at the main menu prompt or in the Help screen for faster data entry
7. **No judgment**: This tool is descriptive, not prescriptive - it shows reality so you can make informed decisions

## Sign Convention Reference

**Important:** The system uses a consistent sign convention:

- **Positive amount** = Outflow/Expense (money leaving your account)
  - Examples: $50 for gas, $400 for tool payment, $150 loan repayment
- **Negative amount** = Inflow/Income (money entering your account)
  - Examples: -$1200 paycheck, -$200 advance, -$50 refund

This convention makes it easy to calculate net changes:
```
Net change = -Inflows + Outflows
If positive → you spent more than you earned
If negative → you earned more than you spent
```

## Troubleshooting

### Config not found

If you see errors about missing config:
```bash
# This will create the default config
tracker cashflow config-show
```

### Wrong week window

If your week doesn't match your pay schedule:
```bash
# Change to Monday-Sunday week
tracker cashflow config-set payroll.week_start "MON"
tracker cashflow config-set payroll.payday_is_thursday false
```

### Provider not recognized

Make sure the provider exists in your config:
```bash
tracker cashflow config-show
```

Then add it manually to `~/.config/tracker/cashflow.toml`.

## Next Steps

- Set up your actual providers and loops in the config
- Import historical data if available
- Establish a weekly review habit
- Track progress month-over-month
- Use insights to make informed financial decisions

---

For more help: `tracker cashflow --help`
