"""Unit tests for feedback service"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from tracker.core.models import DailyEntry
from tracker.core.schemas import EntryCreate
from tracker.services.entry_service import EntryService
from tracker.services.feedback_service import FeedbackService


def test_create_feedback(db_session, test_user):
    """Test creating a feedback record"""
    
    # Create an entry first
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Create feedback
    feedback_service = FeedbackService(db_session)
    feedback = feedback_service.create_feedback(
        entry.id,
        "anthropic",
        "test-key"
    )
    
    assert feedback.id is not None
    assert feedback.entry_id == entry.id
    assert feedback.status == "pending"
    assert feedback.provider == "anthropic"


def test_create_duplicate_feedback(db_session, test_user):
    """Test that creating duplicate feedback updates existing"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Create first feedback
    feedback_service = FeedbackService(db_session)
    feedback1 = feedback_service.create_feedback(entry.id, "anthropic", "test-key")
    
    # Try to create again
    feedback2 = feedback_service.create_feedback(entry.id, "openai", "test-key-2")
    
    # Should be same record, updated
    assert feedback1.id == feedback2.id
    assert feedback2.provider == "openai"
    assert feedback2.status == "pending"


@patch('tracker.services.feedback_service.create_ai_client')
def test_generate_feedback_sync_success(mock_create_client, db_session, test_user):
    """Test successful feedback generation"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(
        date=date.today(),
        income_today=Decimal("400"),
        stress_level=5
    )
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Mock AI client
    mock_client = MagicMock()
    mock_client.generate_feedback.return_value = (
        "Great work today!",
        {
            "model": "claude-3-sonnet",
            "tokens_used": 100,
            "generation_time": 2.5
        }
    )
    mock_create_client.return_value = mock_client
    
    # Generate feedback
    feedback_service = FeedbackService(db_session)
    feedback = feedback_service.create_feedback(entry.id, "anthropic", "test-key")
    
    result = feedback_service.generate_feedback_sync(
        feedback.id,
        "anthropic",
        "test-key"
    )
    
    # Verify
    assert result.status == "completed"
    assert result.content == "Great work today!"
    assert result.model == "claude-3-sonnet"
    assert result.tokens_used == 100
    assert result.generation_time == 2.5
    assert result.error_message is None


@patch('tracker.services.feedback_service.create_ai_client')
def test_generate_feedback_sync_with_retry(mock_create_client, db_session, test_user):
    """Test feedback generation with retry on failure"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Mock AI client that fails once then succeeds
    mock_client = MagicMock()
    mock_client.generate_feedback.side_effect = [
        RuntimeError("API error"),
        ("Success!", {"model": "gpt-4", "tokens_used": 50, "generation_time": 1.0})
    ]
    mock_create_client.return_value = mock_client
    
    # Generate feedback
    feedback_service = FeedbackService(db_session)
    feedback = feedback_service.create_feedback(entry.id, "openai", "test-key")
    
    result = feedback_service.generate_feedback_sync(
        feedback.id,
        "openai",
        "test-key",
        max_retries=3
    )
    
    # Verify it eventually succeeded
    assert result.status == "completed"
    assert result.content == "Success!"


@patch('tracker.services.feedback_service.create_ai_client')
def test_generate_feedback_sync_failure(mock_create_client, db_session, test_user):
    """Test feedback generation failure after retries"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Mock AI client that always fails
    mock_client = MagicMock()
    mock_client.generate_feedback.side_effect = RuntimeError("API error")
    mock_create_client.return_value = mock_client
    
    # Generate feedback
    feedback_service = FeedbackService(db_session)
    feedback = feedback_service.create_feedback(entry.id, "anthropic", "test-key")
    
    with pytest.raises(RuntimeError, match="Failed to generate feedback"):
        feedback_service.generate_feedback_sync(
            feedback.id,
            "anthropic",
            "test-key",
            max_retries=2
        )
    
    # Verify feedback marked as failed
    feedback = feedback_service.get_feedback_by_id(feedback.id)
    assert feedback.status == "failed"
    assert "API error" in feedback.error_message


def test_get_feedback_by_entry(db_session, test_user):
    """Test retrieving feedback by entry"""
    
    # Create entry and feedback
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    feedback_service = FeedbackService(db_session)
    feedback = feedback_service.create_feedback(entry.id, "anthropic", "test-key")
    
    # Retrieve
    result = feedback_service.get_feedback_by_entry(entry.id)
    
    assert result is not None
    assert result.id == feedback.id


def test_regenerate_feedback(db_session, test_user):
    """Test regenerating feedback"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Mock successful generation
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.return_value = (
            "Regenerated feedback",
            {"model": "gpt-4", "tokens_used": 75, "generation_time": 1.5}
        )
        mock_create_client.return_value = mock_client
        
        feedback_service = FeedbackService(db_session)
        feedback = feedback_service.regenerate_feedback(
            entry.id,
            "openai",
            "test-key"
        )
        
        assert feedback.status == "completed"
        assert feedback.content == "Regenerated feedback"
