"""Integration tests for AI feedback generation workflow"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from tracker.core.models import DailyEntry
from tracker.core.schemas import EntryCreate
from tracker.services.entry_service import EntryService
from tracker.services.feedback_service import FeedbackService


def test_end_to_end_feedback_generation(db_session, test_user):
    """Test complete workflow: create entry → generate feedback → retrieve"""
    
    # Step 1: Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(
        date=date.today(),
        income_today=Decimal("500"),
        bills_due_today=Decimal("300"),
        hours_worked=Decimal("8"),
        side_income=Decimal("50"),
        food_spent=Decimal("30"),
        gas_spent=Decimal("25"),
        stress_level=6,
        priority="Pay rent tomorrow"
    )
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    assert entry.id is not None
    assert entry.stress_level == 6
    
    # Step 2: Generate AI feedback (mocked)
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.return_value = (
            "You've made excellent progress today! Working 8 hours while earning $500 shows dedication. "
            "Don't forget to prioritize that rent payment tomorrow - you've got the funds ready.",
            {
                "model": "gpt-4",
                "tokens_used": 125,
                "generation_time": 2.3
            }
        )
        mock_create_client.return_value = mock_client
        
        feedback_service = FeedbackService(db_session)
        feedback = feedback_service.regenerate_feedback(
            entry.id,
            "openai",
            "test-api-key"
        )
    
    # Verify feedback
    assert feedback.status == "completed"
    assert "excellent progress" in feedback.content
    assert feedback.model == "gpt-4"
    assert feedback.tokens_used == 125
    assert feedback.generation_time == 2.3
    assert feedback.error_message is None
    
    # Step 3: Retrieve feedback with entry
    retrieved_feedback = feedback_service.get_feedback_by_entry(entry.id)
    assert retrieved_feedback is not None
    assert retrieved_feedback.id == feedback.id
    assert retrieved_feedback.entry_id == entry.id


def test_multiple_providers_same_entry(db_session, test_user):
    """Test generating feedback from different AI providers for the same entry"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(
        date=date.today(),
        stress_level=7,
        income_today=Decimal("300")
    )
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    feedback_service = FeedbackService(db_session)
    
    # Test with Anthropic
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.return_value = (
            "Claude's supportive feedback",
            {"model": "claude-3-sonnet", "tokens_used": 100, "generation_time": 1.5}
        )
        mock_create_client.return_value = mock_client
        
        feedback1 = feedback_service.regenerate_feedback(
            entry.id,
            "anthropic",
            "anthropic-key"
        )
    
    assert feedback1.provider == "anthropic"
    assert feedback1.model == "claude-3-sonnet"
    
    # Test switching to OpenAI (should update existing feedback)
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.return_value = (
            "GPT's encouraging feedback",
            {"model": "gpt-4", "tokens_used": 120, "generation_time": 2.0}
        )
        mock_create_client.return_value = mock_client
        
        feedback2 = feedback_service.regenerate_feedback(
            entry.id,
            "openai",
            "openai-key"
        )
    
    # Should be same feedback record, updated
    assert feedback2.id == feedback1.id
    assert feedback2.provider == "openai"
    assert feedback2.model == "gpt-4"


def test_feedback_with_retry_recovery(db_session, test_user):
    """Test that feedback generation recovers from transient failures"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Mock client that fails once then succeeds (default has 3 retries)
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.side_effect = [
            RuntimeError("Rate limit exceeded"),
            (
                "Finally succeeded!",
                {"model": "gpt-4", "tokens_used": 80, "generation_time": 1.0}
            )
        ]
        mock_create_client.return_value = mock_client
        
        feedback_service = FeedbackService(db_session)
        feedback = feedback_service.regenerate_feedback(
            entry.id,
            "openai",
            "test-key"
        )
    
    # Should eventually succeed
    assert feedback.status == "completed"
    assert feedback.content == "Finally succeeded!"
    assert feedback.error_message is None


def test_feedback_failure_handling(db_session, test_user):
    """Test proper error handling when feedback generation fails"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Mock client that always fails
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.side_effect = RuntimeError("API key invalid")
        mock_create_client.return_value = mock_client
        
        feedback_service = FeedbackService(db_session)
        
        with pytest.raises(RuntimeError, match="Failed to generate feedback"):
            feedback_service.regenerate_feedback(
                entry.id,
                "openai",
                "bad-key"
            )
    
    # Verify feedback record shows failure
    feedback = feedback_service.get_feedback_by_entry(entry.id)
    assert feedback.status == "failed"
    assert "API key invalid" in feedback.error_message


def test_feedback_metadata_storage(db_session, test_user):
    """Test that all AI metadata is properly stored"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(
        date=date.today(),
        stress_level=4,
        income_today=Decimal("450")
    )
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Generate feedback with detailed metadata
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.return_value = (
            "Test feedback content",
            {
                "model": "claude-3-opus-20240229",
                "tokens_used": 234,
                "generation_time": 3.14159
            }
        )
        mock_create_client.return_value = mock_client
        
        feedback_service = FeedbackService(db_session)
        feedback = feedback_service.regenerate_feedback(
            entry.id,
            "anthropic",
            "test-key"
        )
    
    # Verify all metadata is stored
    assert feedback.provider == "anthropic"
    assert feedback.model == "claude-3-opus-20240229"
    assert feedback.tokens_used == 234
    assert feedback.generation_time == pytest.approx(3.14159, rel=1e-5)
    assert feedback.created_at is not None
    assert feedback.updated_at is not None


def test_feedback_with_local_provider(db_session, test_user):
    """Test feedback generation with local AI provider"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=5)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Mock local AI client
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.return_value = (
            "Local model feedback",
            {"model": "llama2", "tokens_used": 95, "generation_time": 0.8}
        )
        mock_create_client.return_value = mock_client
        
        feedback_service = FeedbackService(db_session)
        feedback = feedback_service.regenerate_feedback(
            entry.id,
            "local",
            "not-needed"  # Local doesn't need real API key
        )
    
    assert feedback.status == "completed"
    assert feedback.provider == "local"
    assert feedback.model == "llama2"


def test_feedback_with_openrouter(db_session, test_user):
    """Test feedback generation with OpenRouter provider"""
    
    # Create entry
    entry_service = EntryService(db_session)
    entry_data = EntryCreate(date=date.today(), stress_level=6)
    entry = entry_service.create_entry(test_user.id, entry_data)
    
    # Mock OpenRouter client
    with patch('tracker.services.feedback_service.create_ai_client') as mock_create_client:
        mock_client = MagicMock()
        mock_client.generate_feedback.return_value = (
            "OpenRouter feedback via Claude",
            {"model": "anthropic/claude-3.5-sonnet", "tokens_used": 140, "generation_time": 2.1}
        )
        mock_create_client.return_value = mock_client
        
        feedback_service = FeedbackService(db_session)
        feedback = feedback_service.regenerate_feedback(
            entry.id,
            "openrouter",
            "openrouter-key"
        )
    
    assert feedback.status == "completed"
    assert feedback.provider == "openrouter"
    assert feedback.model == "anthropic/claude-3.5-sonnet"
