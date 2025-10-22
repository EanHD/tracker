"""Entry service - Business logic for daily entries"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from tracker.core.models import DailyEntry, User
from tracker.core.schemas import EntryCreate, EntryUpdate


class EntryService:
    """Service for managing daily entries"""

    def __init__(self, db: Session):
        self.db = db

    def create_entry(
        self, user_id: int, entry_data: EntryCreate
    ) -> DailyEntry:
        """
        Create a new daily entry
        
        Args:
            user_id: ID of the user creating the entry
            entry_data: Entry data from schema
            
        Returns:
            Created DailyEntry
            
        Raises:
            ValueError: If entry already exists for date or validation fails
        """
        # Validate date is not in future
        if entry_data.date > date.today():
            raise ValueError("Cannot create entry for future date")

        # Check for duplicate
        existing = self.db.query(DailyEntry).filter(
            DailyEntry.user_id == user_id,
            DailyEntry.date == entry_data.date
        ).first()
        
        if existing:
            raise ValueError(f"Entry already exists for {entry_data.date}")

        # Create entry
        entry = DailyEntry(
            user_id=user_id,
            date=entry_data.date,
            income_today=entry_data.income_today,
            bills_due_today=entry_data.bills_due_today,
            hours_worked=entry_data.hours_worked,
            side_income=entry_data.side_income,
            food_spent=entry_data.food_spent,
            gas_spent=entry_data.gas_spent,
            notes=entry_data.notes,
            stress_level=entry_data.stress_level,
            priority=entry_data.priority,
        )

        # Set encrypted fields using property setters
        entry.cash_on_hand = entry_data.cash_on_hand
        entry.bank_balance = entry_data.bank_balance
        entry.debts_total = entry_data.debts_total

        try:
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
            return entry
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database error: {e}")

    def get_entry_by_date(
        self, user_id: int, entry_date: date
    ) -> Optional[DailyEntry]:
        """
        Get entry for a specific date
        
        Args:
            user_id: ID of the user
            entry_date: Date of the entry
            
        Returns:
            DailyEntry or None if not found
        """
        return self.db.query(DailyEntry).filter(
            DailyEntry.user_id == user_id,
            DailyEntry.date == entry_date
        ).first()

    def get_entry_by_id(self, entry_id: int) -> Optional[DailyEntry]:
        """Get entry by ID"""
        return self.db.query(DailyEntry).filter(DailyEntry.id == entry_id).first()

    def update_entry(
        self, entry_id: int, entry_data: EntryUpdate, user_id: Optional[int] = None
    ) -> Optional[DailyEntry]:
        """
        Update an existing entry with partial updates support
        
        Args:
            entry_id: ID of entry to update
            entry_data: EntryUpdate schema with fields to update
            user_id: Optional user ID for authorization check
            
        Returns:
            Updated DailyEntry or None if not found
            
        Raises:
            ValueError: If validation fails or unauthorized
        """
        entry = self.get_entry_by_id(entry_id)
        if not entry:
            return None
        
        # Authorization check
        if user_id is not None and entry.user_id != user_id:
            raise ValueError("Unauthorized: Cannot edit another user's entry")
        
        # Track if substantial changes were made (for feedback regeneration)
        substantial_fields = {'stress_level', 'income_today', 'bills_due_today', 
                             'hours_worked', 'notes', 'priority'}
        substantial_change = False
        
        # Update only provided fields (partial update support)
        update_data = entry_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            if value is not None:  # Only update non-None values
                # Handle encrypted fields with property setters
                if field in ('cash_on_hand', 'bank_balance', 'debts_total'):
                    setattr(entry, field, value)
                elif hasattr(entry, field):
                    old_value = getattr(entry, field)
                    if old_value != value and field in substantial_fields:
                        substantial_change = True
                    setattr(entry, field, value)
        
        # Preserve created_at, update updated_at
        entry.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(entry)
            
            # Return entry with metadata about the update
            entry._substantial_change = substantial_change  # type: ignore
            return entry
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Database error: {e}")

    def get_entry_diff(
        self, entry: DailyEntry, update_data: EntryUpdate
    ) -> dict[str, tuple]:
        """
        Get diff of changes between current entry and proposed updates
        
        Args:
            entry: Current DailyEntry
            update_data: Proposed EntryUpdate
            
        Returns:
            Dict mapping field names to (old_value, new_value) tuples
        """
        diff = {}
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, new_value in update_dict.items():
            if new_value is not None:
                old_value = getattr(entry, field, None)
                if old_value != new_value:
                    diff[field] = (old_value, new_value)
        
        return diff

    def delete_entry(self, entry_id: int) -> bool:
        """
        Delete an entry
        
        Args:
            entry_id: ID of entry to delete
            
        Returns:
            True if deleted, False if not found
        """
        entry = self.get_entry_by_id(entry_id)
        if not entry:
            return False

        self.db.delete(entry)
        self.db.commit()
        return True

    def get_default_user(self) -> Optional[User]:
        """Get the default user"""
        return self.db.query(User).filter(User.username == "default").first()

    def list_entries(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 100,
        offset: int = 0,
        sort_desc: bool = True
    ) -> List[DailyEntry]:
        """
        List entries with filtering and pagination
        
        Args:
            user_id: ID of the user
            start_date: Filter entries from this date (inclusive)
            end_date: Filter entries to this date (inclusive)
            limit: Maximum number of results
            offset: Number of results to skip
            sort_desc: Sort by date descending (newest first) if True
            
        Returns:
            List of DailyEntry objects
        """
        query = self.db.query(DailyEntry).filter(DailyEntry.user_id == user_id)
        
        # Apply date filters
        if start_date:
            query = query.filter(DailyEntry.date >= start_date)
        if end_date:
            query = query.filter(DailyEntry.date <= end_date)
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(DailyEntry.date.desc())
        else:
            query = query.order_by(DailyEntry.date.asc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        return query.all()

    def count_entries(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        """
        Count total entries matching filters
        
        Args:
            user_id: ID of the user
            start_date: Filter entries from this date (inclusive)
            end_date: Filter entries to this date (inclusive)
            
        Returns:
            Total count of matching entries
        """
        query = self.db.query(DailyEntry).filter(DailyEntry.user_id == user_id)
        
        if start_date:
            query = query.filter(DailyEntry.date >= start_date)
        if end_date:
            query = query.filter(DailyEntry.date <= end_date)
        
        return query.count()
