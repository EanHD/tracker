"""Unit tests for entry service"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from tracker.core.schemas import EntryCreate
from tracker.services.entry_service import EntryService


def test_create_entry(db_session, test_user):
    """Test creating a new entry"""
    service = EntryService(db_session)
    
    entry_data = EntryCreate(
        date=date.today(),
        cash_on_hand=Decimal("100.00"),
        bank_balance=Decimal("-50.00"),
        income_today=Decimal("400.00"),
        bills_due_today=Decimal("200.00"),
        debts_total=Decimal("15000.00"),
        hours_worked=Decimal("8.0"),
        side_income=Decimal("50.00"),
        food_spent=Decimal("25.00"),
        gas_spent=Decimal("30.00"),
        stress_level=5,
        priority="Pay bills",
        notes="Good day at work",
    )
    
    entry = service.create_entry(test_user.id, entry_data)
    
    assert entry.id is not None
    assert entry.date == date.today()
    assert entry.stress_level == 5
    assert entry.cash_on_hand == Decimal("100.00")
    assert entry.bank_balance == Decimal("-50.00")
    assert entry.debts_total == Decimal("15000.00")
    assert entry.priority == "Pay bills"
    assert entry.notes == "Good day at work"


def test_create_duplicate_entry(db_session, test_user):
    """Test that creating duplicate entry for same date raises error"""
    service = EntryService(db_session)
    
    entry_data = EntryCreate(
        date=date.today(),
        stress_level=5,
    )
    
    # Create first entry
    service.create_entry(test_user.id, entry_data)
    
    # Try to create duplicate
    with pytest.raises(ValueError, match="already exists"):
        service.create_entry(test_user.id, entry_data)


def test_get_entry_by_date(db_session, test_user):
    """Test retrieving entry by date"""
    service = EntryService(db_session)
    
    entry_data = EntryCreate(
        date=date.today(),
        stress_level=7,
    )
    
    created_entry = service.create_entry(test_user.id, entry_data)
    
    # Retrieve entry
    entry = service.get_entry_by_date(test_user.id, date.today())
    
    assert entry is not None
    assert entry.id == created_entry.id
    assert entry.stress_level == 7


def test_get_nonexistent_entry(db_session, test_user):
    """Test that retrieving nonexistent entry returns None"""
    service = EntryService(db_session)
    
    entry = service.get_entry_by_date(test_user.id, date.today() - timedelta(days=10))
    
    assert entry is None


def test_entry_validation_stress_level(db_session, test_user):
    """Test that stress level validation works"""
    service = EntryService(db_session)
    
    # Valid stress level
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = service.create_entry(test_user.id, entry_data)
    assert entry.stress_level == 5
    
    # Invalid stress level (too low)
    with pytest.raises(ValueError):
        EntryCreate(date=date.today(), stress_level=0)
    
    # Invalid stress level (too high)
    with pytest.raises(ValueError):
        EntryCreate(date=date.today(), stress_level=11)


def test_entry_validation_hours_worked(db_session, test_user):
    """Test that hours worked validation works"""
    service = EntryService(db_session)
    
    # Valid hours
    entry_data = EntryCreate(
        date=date.today(),
        stress_level=5,
        hours_worked=Decimal("8.0")
    )
    entry = service.create_entry(test_user.id, entry_data)
    assert entry.hours_worked == Decimal("8.0")
    
    # Invalid hours (too many)
    with pytest.raises(ValueError):
        EntryCreate(
            date=date.today(),
            stress_level=5,
            hours_worked=Decimal("25.0")
        )


def test_entry_encryption(db_session, test_user):
    """Test that sensitive fields are encrypted"""
    service = EntryService(db_session)
    
    entry_data = EntryCreate(
        date=date.today(),
        cash_on_hand=Decimal("150.50"),
        bank_balance=Decimal("-75.25"),
        debts_total=Decimal("20000.00"),
        stress_level=6,
    )
    
    entry = service.create_entry(test_user.id, entry_data)
    
    # Check that encrypted columns exist
    assert entry.cash_on_hand_encrypted is not None
    assert entry.bank_balance_encrypted is not None
    assert entry.debts_total_encrypted is not None
    
    # Check that decryption works via properties
    assert entry.cash_on_hand == Decimal("150.50")
    assert entry.bank_balance == Decimal("-75.25")
    assert entry.debts_total == Decimal("20000.00")
