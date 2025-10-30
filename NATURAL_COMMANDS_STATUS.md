# Natural Language Financial Commands - Implementation Status

## ✅ COMPLETED

### 1. Natural Language Parser (natural_commands.py)
- ✅ Pattern matching for financial commands (no AI/LLM needed)
- ✅ Entity resolution with alias mapping
- ✅ Actions supported:
  - `payoff` - "I paid off my Slate credit card"
  - `change_amount` - "Lower EarnIn to 300 next week"
  - `defer` - "Defer WestLake one week"
  - `add_installment` - "Add Klarna AutoZone 22.97 on 2025-11-08"
  - `cancel` - "Cancel Netflix"
- ✅ Amount extraction ($150, 150.00, etc.)
- ✅ Date extraction (YYYY-MM-DD, "next week", "tomorrow")
- ✅ Fuzzy entity matching with alternatives

### 2. Entity Aliases
- ✅ Debt accounts: slate → Chase Slate, freedom → Chase Freedom, etc.
- ✅ Recurring bills: earnin → EarnIn, snapon → SnapOn, etc.
- ✅ Providers: klarna, affirm, autozone, oreilly

### 3. Safety System
- ✅ Diff preview with before/after snapshots
- ✅ Change descriptions in human-readable format
- ✅ Warnings for risky operations
- ✅ Safe flag to prevent dangerous changes

### 4. Audit Logging
- ✅ Full audit records with timestamps
- ✅ Stores: user_text, parsed_intent, before/after snapshots
- ✅ Saved to ~/.config/tracker/audits/
- ✅ Unique audit IDs for rollback

### 5. Entry Scanning
- ✅ `scan_entry_text()` - Detects financial changes in journal text
- ✅ Pattern matching for "paid off", "closed", etc.

## 🔨 REMAINING TASKS (2-3 hours)

### CLI Commands

Need to create these commands in `cashflow.py`:

1. **`tracker adjust "<text>"`** (30 min)
   ```bash
   tracker adjust "I paid off my Slate credit card"
   tracker adjust "Lower EarnIn to 300 next week" --dry-run
   tracker adjust "Add Klarna AutoZone 22.97 on 2025-11-08" --yes
   ```
   - Call `parse_command()`
   - Call `create_diff()`
   - Show diff preview
   - Confirm (unless --yes)
   - Call `apply_adjustment()`
   - Save audit
   - Run forecast (unless --no-forecast)

2. **`tracker scan-entry --date YYYY-MM-DD`** (15 min)
   ```bash
   tracker scan-entry --date 2025-10-27
   ```
   - Read entry text from DailyEntry
   - Call `scan_entry_text()`
   - Show detected intents
   - Offer to apply each

3. **`tracker review-week --end YYYY-MM-DD`** (15 min)
   ```bash
   tracker review-week --end 2025-10-27
   ```
   - Scan all entries from past 7 days
   - Aggregate detected changes
   - Show summary

4. **`tracker revert --audit <audit_id>`** (20 min)
   ```bash
   tracker revert --audit 2025-10-27-143022
   ```
   - Load audit file
   - Restore before_snapshot
   - Save revert audit
   - Confirm success

### App.py Integration (1 hour)

Add to TUI:
1. New "Natural Commands" menu item
2. Text input field
3. Show parsed result + diff
4. Apply/Cancel buttons
5. In "New Entry" view: scan for financial mentions
6. Show inline suggestion banner

### Tests (30 min)

```python
def test_parse_payoff():
    intent = parse_command("I paid off my slate credit card")
    assert intent.action == "payoff"
    assert intent.entity_name == "Chase Slate"

def test_parse_change_amount():
    intent = parse_command("Lower EarnIn to 300 next week")
    assert intent.action == "change_amount"
    assert intent.parameters["new_amount"] == 300.0

def test_create_diff_payoff():
    # Test diff generation
    
def test_apply_adjustment():
    # Test actual application

def test_audit_and_revert():
    # Test rollback
```

## Example Workflows

### Workflow 1: Pay Off Debt
```bash
$ tracker adjust "I paid off my Slate credit card"

📋 Parsed Command:
  Action: payoff
  Entity: Chase Slate (debt)
  
📊 Proposed Changes:
  ✓ Set Chase Slate balance to $0.00
  ✓ Mark Chase Slate as closed
  ✓ Remove future minimum payments

⚠️  This will modify your profile. Continue? [y/N]: y

✅ Applied successfully!
   Audit ID: 2025-10-27-143022
   
🔮 Running 7-day forecast...
   [forecast output]
```

### Workflow 2: Change Recurring Amount
```bash
$ tracker adjust "Lower EarnIn to 300 next week"

📋 Parsed Command:
  Action: change_amount
  Entity: EarnIn (recurring)
  Parameters:
    new_amount: $300.00
    effective_date: 2025-11-01
  
📊 Proposed Changes:
  ✓ Change EarnIn from $600.00 to $300.00
  ✓ Effective date: 2025-11-01

Continue? [y/N]: y

✅ Applied successfully!
```

### Workflow 3: Scan Entry
```bash
$ tracker scan-entry --date 2025-10-27

📖 Scanning entry from 2025-10-27...

🔍 Detected financial changes:
  1. "paid off slate" → Payoff Chase Slate
     Confidence: 80%
     
Apply this change? [y/N]: y

✅ Applied successfully!
```

## File Structure

```
src/tracker/
├── services/
│   ├── natural_commands.py          [✅ CREATED]
│   │   ├── parse_command()           [✅]
│   │   ├── resolve_entity()          [✅]
│   │   ├── create_diff()             [✅]
│   │   ├── apply_adjustment()        [✅]
│   │   ├── save_audit()              [✅]
│   │   └── scan_entry_text()         [✅]
│   │
│   ├── cashflow_config.py            [✅ EXISTS]
│   └── finance/
│       ├── forecast.py               [✅ EXISTS]
│       └── loops.py                  [✅ EXISTS]
│
├── cli/commands/
│   └── cashflow.py                   [⏳ NEEDS: adjust, scan-entry, review-week, revert]
│
└── core/
    └── models.py                     [✅ EXISTS]

~/.config/tracker/
├── cashflow.toml                     [✅ EXISTS]
└── audits/                           [⏳ AUTO-CREATED]
    └── 2025-10-27-143022.json        [⏳ EXAMPLE]
```

## Safety Features

1. **Always Preview First**
   - Show before/after
   - List all changes
   - Show warnings

2. **Require Confirmation**
   - Unless --yes flag
   - Clear prompt

3. **Audit Everything**
   - Full snapshots
   - Reversible
   - Timestamped

4. **Validate Changes**
   - No negative amounts
   - Preserve special rules (Snap-On reserve/clear)
   - Check entity exists

5. **Idempotent**
   - Re-running same command = no-op
   - Safe to retry

## Integration with Existing Systems

- ✅ Uses `cashflow_config.py` for config I/O
- ✅ Uses `UserProfile.financial_info` for debt data
- ✅ Integrates with `forecast.py` for post-change forecasts
- ✅ Respects SnapOn reserve-then-clear rules
- ✅ Provider-agnostic (no hardcoded brands)

## Next Steps (Priority Order)

1. Add CLI commands (1 hour)
2. Test with real commands (30 min)
3. Integrate into TUI (1 hour)
4. Write unit tests (30 min)
5. Update docs (15 min)

**Total remaining: ~3 hours**

---
**Last Updated:** October 27, 2025
**Status:** Parser complete, CLI integration pending
