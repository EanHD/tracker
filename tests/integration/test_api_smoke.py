"""Smoke tests for API critical paths

These tests validate that the API server, authentication, and core endpoints work correctly.
Uses the conftest.py db_session fixture for proper test isolation.
"""

import pytest
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient

from tracker.api.main import app
from tracker.core.auth import create_access_token
from tracker.core.database import get_db
from tracker.core.models import User, DailyEntry, AIFeedback


def override_get_db(session):
    """Override database dependency for testing"""
    def _override():
        try:
            yield session
        finally:
            pass
    return _override


@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    app.dependency_overrides[get_db] = override_get_db(db_session)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_user(db_session):
    """Create test user with known password hash"""
    # Pre-computed bcrypt hash for "testpass123"
    user = User(
        username="apitest",
        email="apitest@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOBzLm"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(auth_user):
    """Get authorization headers for test user"""
    token = create_access_token({"sub": auth_user.username})
    return {"Authorization": f"Bearer {token}"}


class TestAPIHealth:
    """Test API health and basic connectivity"""
    
    def test_root_endpoint(self, client):
        """Verify root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tracker API"
        assert data["status"] == "running"
    
    def test_health_check(self, client):
        """Verify health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAPIAuthentication:
    """Test authentication flows"""
    
    def test_register_new_user(self, client):
        """Verify user registration works"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@test.com",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert "id" in data
    
    def test_login_success(self, client, auth_user):
        """Verify login with correct credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "apitest",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_protected_endpoint_requires_auth(self, client):
        """Verify protected endpoints reject unauthenticated requests"""
        response = client.get("/api/v1/entries/")
        assert response.status_code == 401


class TestAPIEntries:
    """Test entry CRUD operations"""
    
    def test_create_entry(self, client, auth_headers, auth_user):
        """Verify entry creation"""
        response = client.post(
            "/api/v1/entries/",
            json={
                "date": "2024-01-15",
                "cash_on_hand": 150.00,
                "bank_balance": 1250.50,
                "income_today": 0,
                "bills_due_today": 0,
                "debts_total": 5000.00,
                "hours_worked": 0,
                "side_income": 0,
                "food_spent": 0,
                "gas_spent": 0,
                "stress_level": 5,
                "notes": "Test entry"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["notes"] == "Test entry"
        assert data["stress_level"] == 5
    
    def test_list_entries(self, client, auth_headers, auth_user, db_session):
        """Verify entry listing"""
        # Create test entry
        entry = DailyEntry(
            user_id=auth_user.id,
            date=date(2024, 1, 15),
            income_today=Decimal("0"),
            bills_due_today=Decimal("0"),
            hours_worked=Decimal("0"),
            side_income=Decimal("0"),
            food_spent=Decimal("0"),
            gas_spent=Decimal("0"),
            stress_level=5,
            notes="Test"
        )
        db_session.add(entry)
        db_session.commit()
        
        response = client.get("/api/v1/entries/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_entry_by_date(self, client, auth_headers, auth_user, db_session):
        """Verify getting specific entry"""
        # Create test entry
        entry = DailyEntry(
            user_id=auth_user.id,
            date=date(2024, 1, 20),
            income_today=Decimal("100"),
            bills_due_today=Decimal("0"),
            hours_worked=Decimal("8"),
            side_income=Decimal("0"),
            food_spent=Decimal("25"),
            gas_spent=Decimal("0"),
            stress_level=6,
            notes="Specific test"
        )
        db_session.add(entry)
        db_session.commit()
        
        response = client.get("/api/v1/entries/2024-01-20", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Specific test"
        assert data["stress_level"] == 6


class TestAPIFeedback:
    """Test AI feedback operations"""
    
    def test_get_feedback(self, client, auth_headers, auth_user, db_session):
        """Verify feedback retrieval"""
        # Create entry and feedback
        entry = DailyEntry(
            user_id=auth_user.id,
            date=date(2024, 1, 25),
            income_today=Decimal("0"),
            bills_due_today=Decimal("0"),
            hours_worked=Decimal("0"),
            side_income=Decimal("0"),
            food_spent=Decimal("0"),
            gas_spent=Decimal("0"),
            stress_level=5
        )
        db_session.add(entry)
        db_session.commit()
        
        feedback = AIFeedback(
            entry_id=entry.id,
            content="Great work!",
            status="completed",
            provider="openai",
            model="gpt-4"
        )
        db_session.add(feedback)
        db_session.commit()
        
        response = client.get(f"/api/v1/feedback/2024-01-25", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Great work!"
        assert data["provider"] == "openai"
