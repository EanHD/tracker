# Financial Forecasting & Budget Prediction - Implementation Plan

## Status: IN PROGRESS

This document tracks the implementation of comprehensive forecasting features for weekly cadence, recurring bills, and daily budget predictions.

## Your Requirements

### Weekly Cadence
- **Payday:** Every Thursday night
- **Net Pay:** $1,300 per week
- **Week Window:** Friday → Thursday

### Weekly Recurring Bills
1. **EarnIn Repayment:** $600/week (Thursday night/Friday morning)
2. **Snap-On:** $400/week 
   - Thursday: Reserve $400 (transfer to Acorns)
   - Friday: Actual autopull (don't double-count!)
3. **Chase Transfer:** $180/week (Thursday)

### Essentials
- **Gas:** $55 every 2 days (~3 fills/week)
- **Food:** $125/week baseline
- **Pets:** $60/week (variable)

### To Add Later
- **Klarna Installments:** Generic scheduled payments system
  - AutoZone: $22.97 (Nov 8, Nov 22)
  - O'Reilly: $18.46 (Nov 19, Dec 19, Jan 19, 2026)

## Implementation Progress

### ✅ COMPLETED

1. **Cash Flow Event Model** - `CashFlowEvent` table exists
2. **Basic Config System** - `cashflow.toml` support
3. **Provider-Agnostic Loops** - Generic loop tracking

### 🔨 IN PROGRESS

1. **Enhanced Config Schema** (`cashflow_config.py`)
   - ✅ Added `PayrollConfig` with weekly fields
   - ✅ Added `RecurringItem` dataclass
   - ✅ Added `RecurringConfig` (weekly/biweekly/monthly)
   - ✅ Added `EssentialsConfig` (gas frequency, food, pets)
   - ⏳ Need to update TOML read/write functions

2. **Forecast Engine** (`finance/forecast.py`)
   - ✅ Created forecast module
   - ✅ Implemented `forecast_week()` - daily balance predictions
   - ✅ Implemented `tomorrow_budget()` - next-day estimate
   - ✅ Implemented reserve-then-clear logic for Snap-On
   - ✅ Gas fill frequency calculation
   - ⏳ Need CLI commands to use it

### 📋 TODO (High Priority)

1. **Update Config Loading** (`cashflow_config.py`)
   ```python
   # Add to load_config():
   - Parse recurring.weekly items
   - Parse essentials config
   - Parse payroll.net_pay and payday_weekly
   ```

2. **Update Config Writing** (`cashflow_config.py`)
   ```toml
   [payroll]
   payday_weekly = "Thursday"
   net_pay = 1300.00
   
   [[recurring.weekly]]
   name = "EarnIn"
   amount = 600.00
   
   [[recurring.weekly]]
   name = "Snap-On"
   amount = 400.00
   reserve_then_clear = true
   provider = "acorns"
   
   [[recurring.weekly]]
   name = "Chase Transfer"
   amount = 180.00
   
   [essentials]
   gas_fill_cost = 55.00
   gas_fill_frequency_days = 2
   food_weekly = 125.00
   pets_weekly = 60.00
   ```

3. **Add CLI Commands** (`cli/commands/cashflow.py`)
   ```bash
   # Setup commands
   tracker cashflow setup-weekly     # Interactive wizard
   tracker cashflow add-recurring --name EarnIn --amount 600 --frequency weekly
   
   # Forecast commands
   tracker cashflow forecast         # Show 7-day forecast with daily breakdown
   tracker cashflow tomorrow         # Tomorrow's budget estimate
   tracker cashflow next-week        # Next week forecast
   
   # Correction commands
   tracker cashflow fix-snapon       # Migrate $1300/month or $326/week to $400/week
   ```

4. **Migration Script**
   ```python
   # Find and fix any Snap-On entries
   - Search profile for monthly Snap-On $1300
   - Search cashflow events for $326/week
   - Update to $400/week
   - Log audit trail
   ```

5. **Scheduled Installments** (for Klarna)
   ```python
   # New model or config section
   [[scheduled_payments]]
   name = "AutoZone"
   amount = 22.97
   provider = "klarna"
   dates = ["2024-11-08", "2024-11-22"]
   
   [[scheduled_payments]]
   name = "O'Reilly"
   amount = 18.46
   provider = "klarna"
   dates = ["2024-11-19", "2024-12-19", "2025-01-19"]
   ```

### 📋 TODO (Medium Priority)

6. **Bill Reminders**
   ```python
   # Check upcoming bills and show warnings
   tracker cashflow reminders        # Show bills due in next 7 days
   tracker cashflow upcoming         # All upcoming scheduled payments
   ```

7. **Balance Tracking**
   ```python
   # Use latest DailyEntry bank_balance and cash_on_hand
   # Or prompt user to set starting balance
   tracker cashflow set-balance --bank 500 --cash 50
   ```

8. **Tests**
   ```python
   test_forecast_week_with_reserve_then_clear()
   test_snapon_not_double_counted()
   test_earnin_included_thursday()
   test_gas_fills_every_2_days()
   test_weekly_net_pay_1300()
   ```

### 📋 TODO (Low Priority)

9. **Documentation**
   - Update CASHFLOW_GUIDE.md with forecasting
   - Add examples of forecast output
   - Document reserve-then-clear semantics

10. **UI Enhancements**
    - Pretty table output for daily forecast
    - Color coding (green=income, red=bills, yellow=warnings)
    - Balance trend visualization

## Current File Structure

```
src/tracker/
├── services/
│   ├── cashflow_config.py          [MODIFIED - needs completion]
│   └── finance/
│       ├── loops.py                 [EXISTS]
│       └── forecast.py              [NEW - needs CLI integration]
├── cli/commands/
│   └── cashflow.py                  [EXISTS - needs new commands]
└── core/
    └── models.py                    [HAS CashFlowEvent]
```

## Next Steps (Priority Order)

1. **Complete Config Read/Write**
   - Update `load_config()` to parse recurring and essentials
   - Update `write_default_config()` with your specific values
   - Test config loading

2. **Add Setup Command**
   ```bash
   tracker cashflow setup-weekly
   ```
   Interactive wizard that sets:
   - Payday to Thursday, $1300
   - EarnIn $600/week
   - Snap-On $400/week (with reserve flag)
   - Chase Transfer $180/week
   - Gas $55 every 2 days
   - Food $125/week
   - Pets $60/week

3. **Add Forecast Commands**
   ```bash
   tracker cashflow forecast      # Daily breakdown for this week
   tracker cashflow tomorrow      # Tomorrow's budget estimate
   ```

4. **Run Migration**
   ```bash
   tracker cashflow fix-snapon    # Fix any existing wrong values
   ```

5. **Test Everything**
   - Run forecast with your config
   - Verify Snap-On shows reserve Thu, clear Fri
   - Verify no double-counting
   - Verify gas fills every 2 days

## Testing Plan

### Manual Tests

1. Set up config with your values
2. Run `tracker cashflow forecast`
3. Verify output shows:
   - Thursday: Paycheck $1300, EarnIn -$600, Snap-On reserve -$400, Chase -$180
   - Friday: Snap-On clear (note: already reserved, $0 change)
   - Gas fills on expected days
   - Daily food budget ~$17.86
   - End-of-week projected balance

4. Run `tracker cashflow tomorrow`
5. Verify shows correct bills for tomorrow

### Automated Tests

```python
def test_weekly_forecast_thursday_payday():
    # Setup config with Thursday payday
    # Run forecast
    # Assert Thursday shows $1300 income
    # Assert EarnIn $600 on Thursday
    # Assert Snap-On reserve Thursday, clear Friday
    # Assert no double-count

def test_reserve_then_clear_snapon():
    # Thursday: balance -= 400
    # Friday: balance unchanged (note about already reserved)
    # Net over 2 days = -400, not -800
```

## Known Issues

1. **Config Loading Not Updated** - `load_config()` doesn't parse new fields yet
2. **No CLI Commands Yet** - Forecast functions exist but no CLI to call them
3. **No Migration Tool** - Need to find/fix existing Snap-On data
4. **No Scheduled Payments** - Klarna installments need data structure

## Quick Commands Reference (Once Complete)

```bash
# One-time setup
tracker cashflow setup-weekly

# Daily use
tracker cashflow tomorrow              # What's tomorrow look like?
tracker cashflow forecast              # This week's daily breakdown

# Weekly review
tracker cashflow week                  # Actual vs forecast

# Fixes
tracker cashflow fix-snapon            # Migrate old Snap-On data
tracker cashflow set-balance --bank 500   # Update starting balance
```

## Architecture

```
User Config (cashflow.toml)
  ↓
CashFlowConfig (dataclasses)
  ↓
Forecast Engine (forecast.py)
  ├→ Get latest balance from DailyEntry
  ├→ Calculate gas fills (every 2 days)
  ├→ Apply weekly recurring (Thursday events)
  ├→ Handle reserve-then-clear (Snap-On)
  └→ Generate daily predictions
  ↓
CLI Commands (cashflow.py)
  └→ Pretty formatted output
```

## Summary

**Implemented:** Core forecast engine with reserve-then-clear logic, config schema extended

**Needed:** Config read/write completion, CLI commands, migration tool, tests

**Estimate:** 2-3 hours to complete remaining items

---

**Last Updated:** October 27, 2025
**Status:** Core engine complete, CLI integration pending
