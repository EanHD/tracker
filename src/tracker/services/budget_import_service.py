"""Budget CSV import and mapping service"""

import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from tracker.core.paths import get_config_dir, get_data_dir
from tracker.core.database import SessionLocal
from tracker.services.cashflow_config import load_config, save_config
from tracker.services.profile_service import ProfileService
from tracker.services.finance.forecast import forecast_week
from tracker.core.models import User


@dataclass
class BudgetItem:
    """Represents a parsed budget item"""
    name: str
    amount_monthly: float
    rate_percent: Optional[float] = None
    total_balance: Optional[float] = None
    item_type: str = "unknown"
    due_day: Optional[int] = None
    frequency: str = "monthly"  # monthly, weekly, etc.


@dataclass
class BudgetData:
    """Complete budget data structure"""
    source_file: str
    last_modified: datetime
    items: List[BudgetItem]
    mapped_fields: Dict[str, Any]
    unmapped_items: List[BudgetItem]
    summary: Dict[str, Any]


class BudgetImportService:
    """Service for importing and mapping budget CSV files"""

    def __init__(self):
        self.config_dir = get_config_dir()
        self.data_dir = get_data_dir()

    def detect_budget_files(self) -> List[Path]:
        """Detect available budget CSV files"""
        candidates = []

        # Check ~/Documents/Tracker/
        documents_dir = Path.home() / "Documents" / "Tracker"
        if documents_dir.exists():
            for pattern in ["Current Budget*.csv", "budget.csv", "*budget*.csv"]:
                candidates.extend(documents_dir.glob(pattern))

        # Check ./data/
        if self.data_dir.exists():
            for pattern in ["*budget*.csv", "Current Budget*.csv", "budget.csv"]:
                candidates.extend(self.data_dir.glob(pattern))

        # Remove duplicates and sort by modification time
        seen = set()
        unique_candidates = []
        for path in sorted(candidates, key=lambda x: x.stat().st_mtime, reverse=True):
            if path not in seen:
                seen.add(path)
                unique_candidates.append(path)

        return unique_candidates

    def parse_budget_csv(self, csv_path: Path) -> BudgetData:
        """Parse budget CSV and return structured data"""
        items = []
        mapped_fields = {}
        unmapped_items = []

        with open(csv_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(f, delimiter=delimiter)

            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue

                item = self._parse_row(row)
                if item:
                    items.append(item)

        # Map fields to Tracker structure
        mapped_fields, unmapped_items = self._map_budget_fields(items)

        # Calculate summary
        summary = self._calculate_summary(items, mapped_fields)

        return BudgetData(
            source_file=str(csv_path),
            last_modified=datetime.fromtimestamp(csv_path.stat().st_mtime),
            items=items,
            mapped_fields=mapped_fields,
            unmapped_items=unmapped_items,
            summary=summary
        )

    def _parse_row(self, row: Dict[str, str]) -> Optional[BudgetItem]:
        """Parse a single CSV row into BudgetItem"""
        # Clean and normalize row data
        cleaned = {k.strip(): v.strip() for k, v in row.items() if k and v}

        if not cleaned:
            return None

        # Extract name
        name = cleaned.get('Name', cleaned.get('name', 'Unknown'))

        # Extract amount (monthly)
        amount_str = cleaned.get('$/Month', cleaned.get('$/month', cleaned.get('Amount', '0')))
        try:
            amount_monthly = float(amount_str.replace('$', '').replace(',', ''))
        except (ValueError, AttributeError):
            amount_monthly = 0.0

        # Extract rate
        rate_str = cleaned.get('%rate', cleaned.get('Rate', ''))
        rate_percent = None
        if rate_str:
            try:
                rate_percent = float(rate_str.replace('%', ''))
            except (ValueError, AttributeError):
                pass

        # Extract total balance
        total_str = cleaned.get('Total', cleaned.get('Balance', ''))
        total_balance = None
        if total_str:
            try:
                total_balance = float(total_str.replace('$', '').replace(',', ''))
            except (ValueError, AttributeError):
                pass

        # Extract type
        item_type = cleaned.get('Type', cleaned.get('type', 'unknown')).lower()

        # Extract due day from Date column
        due_day = None
        date_str = cleaned.get('Date', cleaned.get('date', ''))
        if date_str:
            try:
                # Try to extract day number
                day_match = ''.join(c for c in date_str if c.isdigit())
                if day_match:
                    due_day = int(day_match)
            except (ValueError, AttributeError):
                pass

        # Determine frequency (default monthly, but detect weekly patterns)
        frequency = "monthly"
        if "week" in name.lower() or "/week" in str(amount_str).lower():
            frequency = "weekly"

        return BudgetItem(
            name=name,
            amount_monthly=amount_monthly,
            rate_percent=rate_percent,
            total_balance=total_balance,
            item_type=item_type,
            due_day=due_day,
            frequency=frequency
        )

    def _map_budget_fields(self, items: List[BudgetItem]) -> Tuple[Dict[str, Any], List[BudgetItem]]:
        """Map budget items to Tracker's internal structure"""
        mapped = {
            'payroll': {'net_pay_usd': None},
            'recurring_weekly': {},
            'recurring_monthly': {},
            'essentials': {},
            'installments': {},
            'debt_total_usd': 0.0
        }
        unmapped = []

        # Common mappings
        name_mappings = {
            # Income
            'snap-on': ('recurring_weekly', 'SnapOn'),
            'snap on': ('recurring_weekly', 'SnapOn'),
            'earnin': ('recurring_weekly', 'EarnIn'),
            'advance': ('recurring_weekly', 'EarnIn'),

            # Essentials
            'gas': ('essentials', 'gas.fill_cost_usd'),
            'fuel': ('essentials', 'gas.fill_cost_usd'),
            'food': ('essentials', 'food_weekly_usd'),
            'groceries': ('essentials', 'food_weekly_usd'),
            'pets': ('essentials', 'pets_weekly_usd'),
            'cat': ('essentials', 'pets_weekly_usd'),

            # Bills
            'rent': ('recurring_monthly', 'Rent'),
            'mortgage': ('recurring_monthly', 'Rent'),
            't-mobile': ('recurring_monthly', 'T-Mobile'),
            'verizon': ('recurring_monthly', 'Verizon'),
            'netflix': ('recurring_monthly', 'Netflix'),
            'spotify': ('recurring_monthly', 'Spotify'),
            'aaa': ('recurring_monthly', 'AAA'),
            'insurance': ('recurring_monthly', 'Insurance'),
        }

        for item in items:
            name_lower = item.name.lower()
            mapped_to = None

            # Check exact mappings
            for key, (section, field) in name_mappings.items():
                if key in name_lower:
                    mapped_to = (section, field)
                    break

            # Special handling for credit cards and loans
            if not mapped_to:
                if item.item_type in ['credit card', 'loan', 'debt']:
                    if item.total_balance and item.total_balance > 0:
                        # Add to installments
                        installment_key = item.name.replace(' ', '_').replace('-', '_')
                        mapped['installments'][installment_key] = {
                            'balance': item.total_balance,
                            'min_payment': item.amount_monthly,
                            'interest_rate': item.rate_percent or 0.0,
                            'name': item.name
                        }
                        mapped['debt_total_usd'] += item.total_balance
                        mapped_to = ('installments', installment_key)
                    elif item.amount_monthly > 0:
                        # Monthly bill
                        bill_key = item.name.replace(' ', '_').replace('-', '_')
                        mapped['recurring_monthly'][bill_key] = item.amount_monthly
                        mapped_to = ('recurring_monthly', bill_key)

            # Income detection
            if not mapped_to and item.amount_monthly > 500:  # Assume high amounts are income
                if not mapped['payroll']['net_pay_usd']:
                    mapped['payroll']['net_pay_usd'] = item.amount_monthly
                    mapped_to = ('payroll', 'net_pay_usd')

            # Weekly recurring
            if not mapped_to and item.frequency == 'weekly':
                weekly_key = item.name.replace(' ', '_').replace('-', '_')
                mapped['recurring_weekly'][weekly_key] = item.amount_monthly
                mapped_to = ('recurring_weekly', weekly_key)

            # If not mapped, add to unmapped
            if not mapped_to:
                unmapped.append(item)

        return mapped, unmapped

    def _calculate_summary(self, items: List[BudgetItem], mapped: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate budget summary statistics"""
        total_income = mapped['payroll'].get('net_pay_usd', 0) or 0
        total_expenses = 0

        # Sum recurring weekly (convert to monthly for comparison)
        for amount in mapped['recurring_weekly'].values():
            if isinstance(amount, (int, float)):
                total_expenses += amount * 4.33  # Average weeks per month

        # Sum recurring monthly
        for amount in mapped['recurring_monthly'].values():
            if isinstance(amount, (int, float)):
                total_expenses += amount

        # Sum essentials
        for key, amount in mapped['essentials'].items():
            if isinstance(amount, (int, float)):
                if 'weekly' in key:
                    total_expenses += amount * 4.33
                else:
                    total_expenses += amount

        # Count items
        income_sources = 1 if total_income > 0 else 0
        recurring_bills = len(mapped['recurring_weekly']) + len(mapped['recurring_monthly'])
        essentials = len([k for k in mapped['essentials'].keys() if mapped['essentials'][k]])
        debts = len(mapped['installments'])

        return {
            'total_income_monthly': total_income,
            'total_expenses_monthly': total_expenses,
            'net_position_monthly': total_income - total_expenses,
            'income_sources': income_sources,
            'recurring_bills': recurring_bills,
            'essentials': essentials,
            'debts_recorded': debts,
            'total_items': len(items),
            'mapped_items': len(items) - len(mapped.get('unmapped_items', []))
        }

    def sync_budget_to_config(self, budget_data: BudgetData, user_id: int = 1) -> bool:
        """Sync parsed budget data to Tracker config and profile"""
        try:
            # Load current config
            config = load_config()
            if not config:
                return False

            # Update config with mapped fields
            mapped = budget_data.mapped_fields

            # Update payroll
            if mapped['payroll']['net_pay_usd']:
                config.payroll.net_pay_usd = mapped['payroll']['net_pay_usd']

            # Update recurring weekly
            for key, amount in mapped['recurring_weekly'].items():
                if hasattr(config.recurring_weekly, key):
                    setattr(config.recurring_weekly, key, amount)

            # Update recurring monthly
            for key, amount in mapped['recurring_monthly'].items():
                if hasattr(config.recurring_monthly, key):
                    setattr(config.recurring_monthly, key, amount)

            # Update essentials
            for key, amount in mapped['essentials'].items():
                if hasattr(config.essentials, key):
                    setattr(config.essentials, key, amount)

            # Update installments
            config.installments = mapped['installments']

            # Save config
            save_config(config)

            # Update profile
            db = SessionLocal()
            try:
                service = ProfileService(db)
                user = db.query(User).filter_by(username="default").first()
                if user:
                    # Update financial info
                    financial_data = {
                        'monthly_income': mapped['payroll']['net_pay_usd'] or 0,
                        'debts': [{'name': k, 'balance': v['balance'], 'min_payment': v['min_payment'], 'interest_rate': v['interest_rate']}
                                for k, v in mapped['installments'].items()]
                    }
                    service.update_financial_info(user.id, financial_data)  # type: ignore

                    # Update debt total in profile
                    profile_path = self.config_dir / "profile.json"
                    if profile_path.exists():
                        with open(profile_path, 'r') as f:
                            profile_data = json.load(f)
                    else:
                        profile_data = {}

                    profile_data['debt_total_usd'] = mapped['debt_total_usd']
                    profile_data['last_budget_sync'] = datetime.now().isoformat()

                    with open(profile_path, 'w') as f:
                        json.dump(profile_data, f, indent=2)

            finally:
                db.close()

            # Write audit log
            self._write_sync_audit(budget_data)

            return True

        except Exception as e:
            print(f"Error syncing budget: {e}")
            return False

    def _write_sync_audit(self, budget_data: BudgetData):
        """Write audit log for budget sync"""
        audit_dir = self.config_dir / "audits"
        audit_dir.mkdir(exist_ok=True)

        audit_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'budget_import',
            'source_file': budget_data.source_file,
            'file_modified': budget_data.last_modified.isoformat(),
            'summary': budget_data.summary,
            'mapped_fields': budget_data.mapped_fields,
            'unmapped_items': [{'name': item.name, 'amount': item.amount_monthly, 'type': item.item_type}
                             for item in budget_data.unmapped_items]
        }

        audit_file = audit_dir / f"CSV_IMPORT_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        with open(audit_file, 'w') as f:
            json.dump(audit_data, f, indent=2, default=str)

    def get_last_sync_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the last budget sync"""
        audit_dir = self.config_dir / "audits"
        if not audit_dir.exists():
            return None

        # Find most recent CSV import audit
        audit_files = list(audit_dir.glob("CSV_IMPORT_*.json"))
        if not audit_files:
            return None

        latest_audit = max(audit_files, key=lambda x: x.stat().st_mtime)
        with open(latest_audit, 'r') as f:
            return json.load(f)

    def manual_budget_entry(self) -> Dict[str, Any]:
        """Interactive manual budget entry"""
        print("\n🧮 Manual Budget Entry")
        print("Enter your financial information:")

        # Income
        weekly_pay = float(input("Weekly net pay ($): ") or "0")

        # Essentials
        gas_weekly = float(input("Gas/fuel weekly ($): ") or "0")
        food_weekly = float(input("Food/groceries weekly ($): ") or "0")
        pets_weekly = float(input("Pets weekly ($): ") or "0")

        # Recurring bills
        print("\nRecurring monthly bills (press Enter when done):")
        recurring_monthly = {}
        while True:
            bill_name = input("Bill name (or Enter to finish): ").strip()
            if not bill_name:
                break
            bill_amount = float(input(f"Monthly amount for {bill_name} ($): ") or "0")
            recurring_monthly[bill_name] = bill_amount

        # Debts
        debt_total = float(input("\nTotal debt balance ($): ") or "0")

        return {
            'payroll': {'net_pay_usd': weekly_pay},
            'essentials': {
                'gas.fill_cost_usd': gas_weekly,
                'food_weekly_usd': food_weekly,
                'pets_weekly_usd': pets_weekly
            },
            'recurring_monthly': recurring_monthly,
            'debt_total_usd': debt_total
        }