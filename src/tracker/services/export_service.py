"""
Export Service - Export entries to various formats

Supports CSV and JSON export formats for data portability.
"""

import csv
import json
from datetime import date, datetime
from decimal import Decimal
from io import StringIO
from pathlib import Path
from typing import List, Optional

from sqlalchemy.orm import Session

from tracker.core.models import DailyEntry
from tracker.services.history_service import HistoryService


class ExportService:
    """Service for exporting entry data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.history_service = HistoryService(db)
    
    def export_to_csv(
        self,
        user_id: int,
        filepath: Optional[Path] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> str:
        """
        Export entries to CSV format
        
        Args:
            user_id: User ID
            filepath: Optional file path to write to
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            CSV string content (also written to file if filepath provided)
        """
        # Get entries
        entries = self.history_service.list_entries(
            user_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000,  # Get all entries
            sort_desc=False  # Oldest first for exports
        )
        
        # Create CSV content
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'date',
            'cash_on_hand',
            'bank_balance',
            'income_today',
            'bills_due_today',
            'debts_total',
            'hours_worked',
            'side_income',
            'food_spent',
            'gas_spent',
            'notes',
            'stress_level',
            'priority',
            'created_at',
            'updated_at'
        ])
        
        # Write entries
        for entry in entries:
            writer.writerow([
                entry.date.isoformat(),
                self._format_decimal(entry.cash_on_hand),
                self._format_decimal(entry.bank_balance),
                self._format_decimal(entry.income_today),
                self._format_decimal(entry.bills_due_today),
                self._format_decimal(entry.debts_total),
                self._format_decimal(entry.hours_worked),
                self._format_decimal(entry.side_income),
                self._format_decimal(entry.food_spent),
                self._format_decimal(entry.gas_spent),
                entry.notes or '',
                entry.stress_level,
                entry.priority or '',
                entry.created_at.isoformat() if entry.created_at else '',
                entry.updated_at.isoformat() if entry.updated_at else ''
            ])
        
        csv_content = output.getvalue()
        
        # Write to file if path provided
        if filepath:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(csv_content)
        
        return csv_content
    
    def export_to_json(
        self,
        user_id: int,
        filepath: Optional[Path] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        pretty: bool = True
    ) -> str:
        """
        Export entries to JSON format
        
        Args:
            user_id: User ID
            filepath: Optional file path to write to
            start_date: Optional start date filter
            end_date: Optional end date filter
            pretty: Pretty-print JSON with indentation
            
        Returns:
            JSON string content (also written to file if filepath provided)
        """
        # Get entries
        entries = self.history_service.list_entries(
            user_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000,  # Get all entries
            sort_desc=False  # Oldest first for exports
        )
        
        # Build export data
        export_data = {
            "exported_at": datetime.utcnow().isoformat(),
            "entry_count": len(entries),
            "date_range": {
                "start": start_date.isoformat() if start_date else entries[0].date.isoformat() if entries else None,
                "end": end_date.isoformat() if end_date else entries[-1].date.isoformat() if entries else None
            },
            "entries": [
                {
                    "date": entry.date.isoformat(),
                    "financials": {
                        "cash_on_hand": self._format_decimal(entry.cash_on_hand),
                        "bank_balance": self._format_decimal(entry.bank_balance),
                        "income_today": self._format_decimal(entry.income_today),
                        "bills_due_today": self._format_decimal(entry.bills_due_today),
                        "debts_total": self._format_decimal(entry.debts_total),
                        "side_income": self._format_decimal(entry.side_income),
                        "food_spent": self._format_decimal(entry.food_spent),
                        "gas_spent": self._format_decimal(entry.gas_spent)
                    },
                    "work": {
                        "hours_worked": self._format_decimal(entry.hours_worked)
                    },
                    "wellbeing": {
                        "stress_level": entry.stress_level,
                        "priority": entry.priority,
                        "notes": entry.notes
                    },
                    "metadata": {
                        "created_at": entry.created_at.isoformat() if entry.created_at else None,
                        "updated_at": entry.updated_at.isoformat() if entry.updated_at else None
                    }
                }
                for entry in entries
            ]
        }
        
        # Convert to JSON
        json_content = json.dumps(
            export_data,
            indent=2 if pretty else None,
            ensure_ascii=False
        )
        
        # Write to file if path provided
        if filepath:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(json_content)
        
        return json_content
    
    def _format_decimal(self, value: Optional[Decimal]) -> Optional[float]:
        """Convert Decimal to float for JSON serialization"""
        return float(value) if value is not None else None
    
    def get_export_stats(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        Get statistics about what would be exported
        
        Args:
            user_id: User ID
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Dictionary with export statistics
        """
        entries = self.history_service.list_entries(
            user_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000
        )
        
        if not entries:
            return {
                "entry_count": 0,
                "date_range": None,
                "earliest_date": None,
                "latest_date": None
            }
        
        # Sort to get date range
        dates = [entry.date for entry in entries]
        
        return {
            "entry_count": len(entries),
            "date_range": {
                "start": min(dates).isoformat(),
                "end": max(dates).isoformat()
            },
            "earliest_date": min(dates).isoformat(),
            "latest_date": max(dates).isoformat(),
            "estimated_csv_size_kb": len(entries) * 0.5,  # Rough estimate
            "estimated_json_size_kb": len(entries) * 1.0  # Rough estimate
        }
