"""Unit tests for AI client"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from tracker.core.models import DailyEntry
from tracker.services.ai_client import (
    AIClient,
    AnthropicClient,
    OpenAIClient,
    OpenRouterClient,
    LocalClient,
    create_ai_client,
)


def test_build_prompt():
    """Test that prompt is built correctly"""
    
    # Create a test entry
    entry = DailyEntry(
        id=1,
        user_id=1,
        date=date.today(),
        income_today=Decimal("400"),
        bills_due_today=Decimal("200"),
        hours_worked=Decimal("8"),
        side_income=Decimal("50"),
        food_spent=Decimal("25"),
        gas_spent=Decimal("30"),
        stress_level=5,
        priority="Pay bills",
        notes="Good day at work",
    )
    
    # Set encrypted fields
    entry.cash_on_hand = Decimal("100")
    entry.bank_balance = Decimal("-50")
    entry.debts_total = Decimal("15000")
    
    # Create mock client
    class MockClient(AIClient):
        def generate_feedback(self, entry):
            return "Mock feedback", {}
    
    client = MockClient()
    prompt = client._build_prompt(entry)
    
    # Verify prompt contains key information
    assert "Date:" in prompt
    assert "Cash on hand: $100" in prompt
    assert "Bank balance: $-50" in prompt
    assert "Income today: $400" in prompt
    assert "Stress level: 5/10" in prompt
    assert "Priority: Pay bills" in prompt
    assert "Notes: Good day at work" in prompt
    assert "Guidelines" in prompt


def test_create_ai_client_anthropic():
    """Test creating Anthropic client"""
    
    client = create_ai_client("anthropic", "test-key")
    
    assert isinstance(client, AnthropicClient)
    assert client.api_key == "test-key"
    assert client.model == "claude-3-sonnet-20240229"


def test_create_ai_client_openai():
    """Test creating OpenAI client"""
    
    client = create_ai_client("openai", "test-key")
    
    assert isinstance(client, OpenAIClient)
    assert client.api_key == "test-key"
    assert client.model == "gpt-4"


def test_create_ai_client_with_custom_model():
    """Test creating client with custom model"""
    
    client = create_ai_client("anthropic", "test-key", model="claude-3-opus")
    
    assert client.model == "claude-3-opus"


def test_create_ai_client_invalid_provider():
    """Test that invalid provider raises error"""
    
    with pytest.raises(ValueError, match="Unsupported AI provider"):
        create_ai_client("invalid", "test-key")


def test_create_ai_client_openrouter():
    """Test creating OpenRouter client"""
    
    client = create_ai_client("openrouter", "test-key")
    
    assert isinstance(client, OpenRouterClient)
    assert client.api_key == "test-key"
    assert client.model == "anthropic/claude-3.5-sonnet"


def test_create_ai_client_local():
    """Test creating Local client"""
    
    client = create_ai_client("local", local_api_url="http://localhost:1234/v1")
    
    assert isinstance(client, LocalClient)
    assert client.base_url == "http://localhost:1234/v1"
    assert client.model == "local-model"


def test_create_ai_client_local_custom_model():
    """Test creating Local client with custom model"""
    
    client = create_ai_client("local", model="llama2", local_api_url="http://localhost:8080/v1")
    
    assert client.model == "llama2"
    assert client.base_url == "http://localhost:8080/v1"


def test_create_ai_client_missing_api_key():
    """Test that missing API key raises error for providers that need it"""
    
    with pytest.raises(ValueError, match="API key is required"):
        create_ai_client("openai")
    
    with pytest.raises(ValueError, match="API key is required"):
        create_ai_client("anthropic")
    
    with pytest.raises(ValueError, match="API key is required"):
        create_ai_client("openrouter")


@patch('anthropic.Anthropic')
def test_anthropic_client_generate_feedback(mock_anthropic_class, db_session):
    """Test AnthropicClient.generate_feedback with mocked Anthropic"""
    
    # Mock the Anthropic client and response
    mock_anthropic = mock_anthropic_class.return_value
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Great job managing your finances today!")]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 50
    mock_anthropic.messages.create.return_value = mock_response
    
    # Create client and generate feedback
    client = AnthropicClient(api_key="test-key", model="claude-3-sonnet-20240229")
    entry = DailyEntry(
        id=1,
        user_id=1,
        date=date.today(),
        income_today=Decimal("400"),
        bills_due_today=Decimal("200"),
        hours_worked=Decimal("8"),
        side_income=Decimal("0"),
        food_spent=Decimal("25"),
        gas_spent=Decimal("30"),
        stress_level=5,
    )
    
    content, metadata = client.generate_feedback(entry)
    
    # Verify response
    assert content == "Great job managing your finances today!"
    assert metadata["model"] == "claude-3-sonnet-20240229"
    assert metadata["tokens_used"] == 150
    assert "generation_time" in metadata


@patch('openai.OpenAI')
def test_openai_client_generate_feedback(mock_openai_class, db_session):
    """Test OpenAIClient.generate_feedback with mocked OpenAI"""
    
    # Mock the OpenAI client and response
    mock_openai = mock_openai_class.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="You're doing great!"))]
    mock_response.usage.total_tokens = 120
    mock_openai.chat.completions.create.return_value = mock_response
    
    # Create client and generate feedback
    client = OpenAIClient(api_key="test-key", model="gpt-4")
    entry = DailyEntry(
        id=1,
        user_id=1,
        date=date.today(),
        income_today=Decimal("400"),
        bills_due_today=Decimal("200"),
        hours_worked=Decimal("8"),
        side_income=Decimal("0"),
        food_spent=Decimal("25"),
        gas_spent=Decimal("30"),
        stress_level=5,
    )
    
    content, metadata = client.generate_feedback(entry)
    
    # Verify response
    assert content == "You're doing great!"
    assert metadata["model"] == "gpt-4"
    assert metadata["tokens_used"] == 120
    assert "generation_time" in metadata


@patch('openai.OpenAI')
def test_openrouter_client_generate_feedback(mock_openai_class, db_session):
    """Test OpenRouterClient.generate_feedback with mocked OpenAI"""
    
    # Mock the OpenAI client and response
    mock_openai = mock_openai_class.return_value
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Excellent progress!"))]
    mock_response.usage.total_tokens = 135
    mock_openai.chat.completions.create.return_value = mock_response
    
    # Create client and generate feedback
    client = OpenRouterClient(api_key="test-key", model="anthropic/claude-3.5-sonnet")
    entry = DailyEntry(
        id=1,
        user_id=1,
        date=date.today(),
        income_today=Decimal("400"),
        bills_due_today=Decimal("200"),
        hours_worked=Decimal("8"),
        side_income=Decimal("0"),
        food_spent=Decimal("25"),
        gas_spent=Decimal("30"),
        stress_level=5,
    )
    
    content, metadata = client.generate_feedback(entry)
    
    # Verify response
    assert content == "Excellent progress!"
    assert metadata["model"] == "anthropic/claude-3.5-sonnet"
    assert metadata["tokens_used"] == 135
    assert "generation_time" in metadata


@patch('openai.OpenAI')
def test_local_client_generate_feedback(mock_openai_class, db_session):
    """Test Local client feedback generation"""
    
    # Create test entry
    entry = DailyEntry(
        id=1,
        user_id=1,
        date=date.today(),
        income_today=Decimal("400"),
        bills_due_today=Decimal("200"),
        hours_worked=Decimal("8"),
        side_income=Decimal("0"),
        food_spent=Decimal("25"),
        gas_spent=Decimal("30"),
        stress_level=5,
    )
    
    # Mock Local AI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="You're making good progress!"))]
    mock_response.usage.total_tokens = 95
    
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai_class.return_value = mock_client
    
    # Generate feedback
    client = LocalClient(base_url="http://localhost:1234/v1")
    content, metadata = client.generate_feedback(entry)
    
    # Verify
    assert content == "You're making good progress!"
    assert metadata["model"] == "local-model"
    assert metadata["tokens_used"] == 95
    assert "generation_time" in metadata
