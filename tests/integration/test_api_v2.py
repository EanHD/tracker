"""Simplified comprehensive API integration tests"""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tracker.api.main import app
from tracker.core.auth import create_access_token
from tracker.core.database import Base, get_db
from tracker.core.models import User, DailyEntry, AIFeedback


# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db dependency"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override dependency and create client
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create and drop tables for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Get test database session"""
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db):
    """Create test user with known password hash"""
    # Hash for "testpass123"
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOBzLm"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get auth headers for test user"""
    token = create_access_token({"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}


class TestHealthEndpoints:
    """Test health and info endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tracker API"
        assert "version" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self):
        """Test health check"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAuthenticationEndpoints:
    """Test authentication flows"""
    
    def test_register_new_user(self):
        """Test user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert "id" in data
    
    def test_register_duplicate_username(self, test_user):
        """Test registering duplicate username fails"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": test_user.username,
                "email": "different@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_login_success(self, test_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, test_user):
        """Test login with wrong password fails"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user fails"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "ghost",
                "password": "password"
            }
        )
        
        assert response.status_code == 401


class TestEntryEndpoints:
    """Test entry CRUD operations"""
    
    def test_create_entry_authenticated(self, auth_headers):
        """Test creating entry as authenticated user"""
        response = client.post(
            "/api/v1/entries/",
            json={
                "entry_date": "2024-01-15",
                "content": "Today was productive",
                "mood_score": 8,
                "energy_level": 7
            },
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Today was productive"
        assert data["mood_score"] == 8
    
    def test_create_entry_unauthenticated(self):
        """Test creating entry without auth fails"""
        response = client.post(
            "/api/v1/entries/",
            json={
                "entry_date": "2024-01-15",
                "content": "Test",
                "mood_score": 5
            }
        )
        
        assert response.status_code == 401
    
    def test_list_entries(self, test_user, auth_headers, db):
        """Test listing user entries"""
        # Create some entries
        entry1 = DailyEntry(
            user_id=test_user.id,
            entry_date=date(2024, 1, 15),
            content="Entry 1",
            mood_score=7
        )
        entry2 = DailyEntry(
            user_id=test_user.id,
            entry_date=date(2024, 1, 16),
            content="Entry 2",
            mood_score=8
        )
        db.add_all([entry1, entry2])
        db.commit()
        
        response = client.get("/api/v1/entries/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
    
    def test_list_entries_with_pagination(self, test_user, auth_headers, db):
        """Test listing entries with pagination"""
        # Create multiple entries
        for i in range(5):
            entry = DailyEntry(
                user_id=test_user.id,
                entry_date=date(2024, 1, i + 1),
                content=f"Entry {i}",
                mood_score=5
            )
            db.add(entry)
        db.commit()
        
        response = client.get("/api/v1/entries/?limit=2", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_get_specific_entry(self, test_user, auth_headers, db):
        """Test getting a specific entry by date"""
        entry = DailyEntry(
            user_id=test_user.id,
            entry_date=date(2024, 1, 15),
            content="Specific entry",
            mood_score=6
        )
        db.add(entry)
        db.commit()
        
        response = client.get("/api/v1/entries/2024-01-15", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Specific entry"
        assert data["entry_date"] == "2024-01-15"
    
    def test_get_nonexistent_entry(self, auth_headers):
        """Test getting non-existent entry returns 404"""
        response = client.get("/api/v1/entries/2099-12-31", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_entry(self, test_user, auth_headers, db):
        """Test updating an existing entry"""
        entry = DailyEntry(
            user_id=test_user.id,
            entry_date=date(2024, 1, 15),
            content="Original content",
            mood_score=5
        )
        db.add(entry)
        db.commit()
        
        response = client.patch(
            "/api/v1/entries/2024-01-15",
            json={
                "content": "Updated content",
                "mood_score": 8
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"
        assert data["mood_score"] == 8
    
    def test_delete_entry(self, test_user, auth_headers, db):
        """Test deleting an entry"""
        entry = DailyEntry(
            user_id=test_user.id,
            entry_date=date(2024, 1, 15),
            content="To be deleted",
            mood_score=5
        )
        db.add(entry)
        db.commit()
        
        response = client.delete("/api/v1/entries/2024-01-15", headers=auth_headers)
        
        assert response.status_code == 204


class TestFeedbackEndpoints:
    """Test AI feedback operations"""
    
    def test_get_feedback_for_entry(self, test_user, auth_headers, db):
        """Test getting feedback for an entry"""
        # Create entry
        entry = DailyEntry(
            user_id=test_user.id,
            entry_date=date(2024, 1, 15),
            content="Test entry",
            mood_score=7
        )
        db.add(entry)
        db.commit()
        
        # Create feedback
        feedback = AIFeedback(
            entry_id=entry.id,
            provider="openai",
            feedback_text="Great progress!",
            sentiment_score=0.8
        )
        db.add(feedback)
        db.commit()
        
        response = client.get("/api/v1/feedback/2024-01-15", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["feedback_text"] == "Great progress!"
        assert data["provider"] == "openai"
    
    def test_get_feedback_not_found(self, auth_headers):
        """Test getting feedback for non-existent entry"""
        response = client.get("/api/v1/feedback/2099-12-31", headers=auth_headers)
        
        assert response.status_code == 404
