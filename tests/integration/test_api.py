"""Integration tests for API endpoints"""

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from tracker.api.main import app
from tracker.core.models import User
from tracker.core.schemas import EntryCreate
from tracker.services.entry_service import EntryService

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user(db_session):
    """Test user login"""
    # Create user first
    from tracker.core.auth import get_password_hash
    
    user = User(
        username="logintest",
        email="login@test.com",
        password_hash=get_password_hash("password123")
    )
    db_session.add(user)
    db_session.commit()
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "logintest",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_create_entry_authenticated(db_session, test_user):
    """Test creating entry with authentication"""
    from tracker.core.auth import create_access_token
    
    # Get token
    token = create_access_token({"sub": test_user.username})
    
    # Create entry
    response = client.post(
        "/api/v1/entries/",
        json={
            "date": str(date.today()),
            "stress_level": 5,
            "income_today": 400.00,
            "bills_due_today": 200.00,
            "hours_worked": 8.0,
            "side_income": 0,
            "food_spent": 25.00,
            "gas_spent": 30.00,
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["stress_level"] == 5


def test_create_entry_unauthenticated():
    """Test that creating entry without auth fails"""
    response = client.post(
        "/api/v1/entries/",
        json={
            "date": str(date.today()),
            "stress_level": 5
        }
    )
    
    assert response.status_code == 403  # Forbidden without auth
