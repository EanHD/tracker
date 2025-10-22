"""Unit tests for history service"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from tracker.core.schemas import EntryCreate
from tracker.services.entry_service import EntryService
from tracker.services.history_service import HistoryService


def test_list_entries(db_session, test_user):
    """Test listing entries"""
    
    # Create multiple entries
    entry_service = EntryService(db_session)
    
    for i in range(5):
        entry_data = EntryCreate(
            date=date.today() - timedelta(days=i),
            stress_level=5 + i,
            income_today=Decimal("100") * (i + 1)
        )
        entry_service.create_entry(test_user.id, entry_data)
    
    # List all
    history_service = HistoryService(db_session)
    entries = history_service.list_entries(test_user.id, limit=10)
    
    assert len(entries) == 5
    # Should be ordered by date descending
    assert entries[0].date > entries[-1].date


def test_list_entries_with_date_filter(db_session, test_user):
    """Test listing entries with date range filter"""
    
    entry_service = EntryService(db_session)
    
    # Create entries over 10 days
    for i in range(10):
        entry_data = EntryCreate(
            date=date.today() - timedelta(days=i),
            stress_level=5
        )
        entry_service.create_entry(test_user.id, entry_data)
    
    # Filter last 5 days
    history_service = HistoryService(db_session)
    start_date = date.today() - timedelta(days=4)
    
    entries = history_service.list_entries(
        test_user.id,
        start_date=start_date
    )
    
    assert len(entries) == 5


def test_get_statistics(db_session, test_user):
    """Test statistics calculation"""
    
    entry_service = EntryService(db_session)
    
    # Create entries with known values
    for i in range(3):
        entry_data = EntryCreate(
            date=date.today() - timedelta(days=i),
            income_today=Decimal("400"),
            bills_due_today=Decimal("200"),
            food_spent=Decimal("25"),
            gas_spent=Decimal("30"),
            hours_worked=Decimal("8"),
            stress_level=5 + i
        )
        entry_service.create_entry(test_user.id, entry_data)
    
    # Get statistics
    history_service = HistoryService(db_session)
    stats = history_service.get_statistics(test_user.id)
    
    assert stats["count"] == 3
    assert stats["income"]["total"] == Decimal("1200")
    assert stats["income"]["average"] == Decimal("400")
    assert stats["bills"]["total"] == Decimal("600")
    assert stats["spending"]["total"] == Decimal("165")  # (25+30) * 3
    assert stats["work"]["total_hours"] == Decimal("24")
    assert stats["wellbeing"]["average_stress"] == 6.0  # (5+6+7) / 3


def test_get_trends(db_session, test_user):
    """Test trend data extraction"""
    
    entry_service = EntryService(db_session)
    
    # Create entries with increasing stress
    for i in range(5):
        entry_data = EntryCreate(
            date=date.today() - timedelta(days=4-i),
            stress_level=3 + i
        )
        entry_service.create_entry(test_user.id, entry_data)
    
    # Get stress trend
    history_service = HistoryService(db_session)
    trend = history_service.get_trends(test_user.id, days=5, metric="stress_level")
    
    assert len(trend) == 5
    assert trend[0]["value"] == 3
    assert trend[-1]["value"] == 7


def test_search_entries(db_session, test_user):
    """Test searching entries by notes"""
    
    entry_service = EntryService(db_session)
    
    # Create entries with different notes
    entries_data = [
        ("Paid bills today", "pay bills"),
        ("Worked overtime", "work hard"),
        ("Paid Snap-On debt", "pay bills"),
    ]
    
    for i, (notes, priority) in enumerate(entries_data):
        entry_data = EntryCreate(
            date=date.today() - timedelta(days=i),
            stress_level=5,
            notes=notes,
            priority=priority
        )
        entry_service.create_entry(test_user.id, entry_data)
    
    # Search for "paid"
    history_service = HistoryService(db_session)
    results = history_service.search_entries(test_user.id, "paid")
    
    assert len(results) == 2
    
    # Search for "overtime"
    results = history_service.search_entries(test_user.id, "overtime")
    assert len(results) == 1


def test_get_streak_info(db_session, test_user):
    """Test streak calculation"""
    
    entry_service = EntryService(db_session)
    
    # Create consecutive entries
    for i in range(5):
        entry_data = EntryCreate(
            date=date.today() - timedelta(days=i),
            stress_level=5
        )
        entry_service.create_entry(test_user.id, entry_data)
    
    # Get streak info
    history_service = HistoryService(db_session)
    streak = history_service.get_streak_info(test_user.id)
    
    assert streak["current_streak"] >= 5
    assert streak["longest_streak"] >= 5
    assert streak["total_entries"] == 5


def test_statistics_empty_entries(db_session, test_user):
    """Test statistics with no entries"""
    
    history_service = HistoryService(db_session)
    stats = history_service.get_statistics(test_user.id)
    
    assert stats["count"] == 0
