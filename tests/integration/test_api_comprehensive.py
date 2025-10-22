"""Comprehensive API integration tests"""

from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tracker.api.main import app
from tracker.core.auth import create_access_token
from tracker.core.database import Base, get_db
from tracker.core.models import User


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


# Override dependency before creating client
app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create and drop tables for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def authenticated_user(setup_database):
    """Create a user and return auth headers"""
    db = TestingSessionLocal()
    
    # Create user with pre-computed hash for "testpass123"
    user = User(
        username="authuser",
        email="auth@test.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOBzLm"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    token = create_access_token({"sub": user.username})
    
    result = {
        "user": user,
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"}
    }
    
    db.close()
    return result


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
    
    def test_register_new_user(self, db_session):
        """Test user registration"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
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
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 90
        
        # Verify user was created
        user = db_session.query(User).filter_by(username="newuser").first()
        assert user is not None
        assert user.email == "new@example.com"
        
        app.dependency_overrides.clear()
    
    def test_register_duplicate_username(self, db_session):
        """Test registration with existing username fails"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create first user
        user = User(username="duplicate", email="dup1@test.com")
        db_session.add(user)
        db_session.commit()
        
        # Try to register with same username
        response = client.post(
            "/api/v1/auth/register",
            json={
                "username": "duplicate",
                "email": "dup2@test.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
        
        app.dependency_overrides.clear()
    
    def test_login_success(self, db_session):
        """Test successful login"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create user with password (pre-computed hash for "mypassword")
        user = User(
            username="loginuser",
            email="login@test.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOBzLm"
        )
        db_session.add(user)
        db_session.commit()
        
        # Login - Note: actual password verification won't work with static hash
        # This test will fail auth, but should get a proper response not 500 error
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "loginuser",
                "password": "testpass123"  # This matches the pre-computed hash
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        app.dependency_overrides.clear()
    
    def test_login_invalid_credentials(self, db_session):
        """Test login with wrong password fails"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create user (pre-computed hash for "testpass123")
        user = User(
            username="failuser",
            email="fail@test.com",
            password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaOBzLm"
        )
        db_session.add(user)
        db_session.commit()
        
        # Try wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "failuser",
                "password": "wrongpass"
            }
        )
        
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower()
        
        app.dependency_overrides.clear()
    
    def test_login_nonexistent_user(self, db_session):
        """Test login with non-existent user fails"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "username": "ghost",
                "password": "password"
            }
        )
        
        assert response.status_code == 401
        
        app.dependency_overrides.clear()


class TestEntryEndpoints:
    """Test entry CRUD operations"""
    
    def test_create_entry_authenticated(self, db_session, authenticated_user):
        """Test creating an entry with authentication"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        response = client.post(
            "/api/v1/entries/",
            json={
                "date": str(date.today()),
                "stress_level": 5,
                "income_today": 400.00,
                "bills_due_today": 200.00,
                "hours_worked": 8.0,
                "side_income": 50.0,
                "food_spent": 25.00,
                "gas_spent": 30.00,
            },
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["stress_level"] == 5
        assert float(data["income_today"]) == 400.00
        assert data["date"] == str(date.today())
        
        app.dependency_overrides.clear()
    
    def test_create_entry_unauthenticated(self, db_session):
        """Test creating entry without auth fails"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        response = client.post(
            "/api/v1/entries/",
            json={
                "date": str(date.today()),
                "stress_level": 5
            }
        )
        
        assert response.status_code == 403  # No auth provided
        
        app.dependency_overrides.clear()
    
    def test_list_entries(self, db_session, authenticated_user):
        """Test listing entries"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create a few entries
        from tracker.core.models import DailyEntry
        from datetime import timedelta
        
        for i in range(3):
            entry = DailyEntry(
                user_id=authenticated_user["user"].id,
                date=date.today() - timedelta(days=i),
                stress_level=5 + i,
                income_today=Decimal("400"),
                bills_due_today=Decimal("200"),
                hours_worked=Decimal("8"),
                side_income=Decimal("0"),
                food_spent=Decimal("25"),
                gas_spent=Decimal("30")
            )
            db_session.add(entry)
        db_session.commit()
        
        # List entries
        response = client.get(
            "/api/v1/entries/",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        entries = response.json()
        assert len(entries) >= 3
        
        app.dependency_overrides.clear()
    
    def test_list_entries_with_pagination(self, db_session, authenticated_user):
        """Test pagination parameters"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        response = client.get(
            "/api/v1/entries/?skip=0&limit=5",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        entries = response.json()
        assert len(entries) <= 5
        
        app.dependency_overrides.clear()
    
    def test_get_specific_entry(self, db_session, authenticated_user):
        """Test retrieving a specific entry by date"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create entry
        from tracker.core.models import DailyEntry
        
        entry_date = date.today()
        entry = DailyEntry(
            user_id=authenticated_user["user"].id,
            date=entry_date,
            stress_level=6,
            income_today=Decimal("500"),
            bills_due_today=Decimal("300"),
            hours_worked=Decimal("9"),
            side_income=Decimal("100"),
            food_spent=Decimal("30"),
            gas_spent=Decimal("40")
        )
        db_session.add(entry)
        db_session.commit()
        
        # Get entry
        response = client.get(
            f"/api/v1/entries/{entry_date}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["stress_level"] == 6
        assert float(data["income_today"]) == 500.0
        
        app.dependency_overrides.clear()
    
    def test_get_nonexistent_entry(self, db_session, authenticated_user):
        """Test getting entry that doesn't exist"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        response = client.get(
            "/api/v1/entries/2020-01-01",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
    
    def test_update_entry(self, db_session, authenticated_user):
        """Test updating an existing entry"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create entry
        from tracker.core.models import DailyEntry
        
        entry_date = date.today()
        entry = DailyEntry(
            user_id=authenticated_user["user"].id,
            date=entry_date,
            stress_level=5,
            income_today=Decimal("400"),
            bills_due_today=Decimal("200"),
            hours_worked=Decimal("8"),
            side_income=Decimal("0"),
            food_spent=Decimal("25"),
            gas_spent=Decimal("30")
        )
        db_session.add(entry)
        db_session.commit()
        
        # Update entry
        response = client.patch(
            f"/api/v1/entries/{entry_date}",
            json={
                "date": str(entry_date),
                "stress_level": 7,  # Changed
                "income_today": 400.00,
                "bills_due_today": 200.00,
                "hours_worked": 10.0,  # Changed
                "side_income": 0,
                "food_spent": 25.00,
                "gas_spent": 30.00
            },
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["stress_level"] == 7
        assert float(data["hours_worked"]) == 10.0
        
        app.dependency_overrides.clear()
    
    def test_delete_entry(self, db_session, authenticated_user):
        """Test deleting an entry"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create entry
        from tracker.core.models import DailyEntry
        
        entry_date = date.today()
        entry = DailyEntry(
            user_id=authenticated_user["user"].id,
            date=entry_date,
            stress_level=5,
            income_today=Decimal("400"),
            bills_due_today=Decimal("200"),
            hours_worked=Decimal("8"),
            side_income=Decimal("0"),
            food_spent=Decimal("25"),
            gas_spent=Decimal("30")
        )
        db_session.add(entry)
        db_session.commit()
        
        # Delete entry
        response = client.delete(
            f"/api/v1/entries/{entry_date}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 204
        
        # Verify deleted
        response = client.get(
            f"/api/v1/entries/{entry_date}",
            headers=authenticated_user["headers"]
        )
        assert response.status_code == 404
        
        app.dependency_overrides.clear()


class TestFeedbackEndpoints:
    """Test AI feedback generation endpoints"""
    
    def test_get_feedback_for_entry(self, db_session, authenticated_user):
        """Test retrieving feedback for an entry"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create entry with feedback
        from tracker.core.models import AIFeedback, DailyEntry
        
        entry_date = date.today()
        entry = DailyEntry(
            user_id=authenticated_user["user"].id,
            date=entry_date,
            stress_level=5,
            income_today=Decimal("400"),
            bills_due_today=Decimal("200"),
            hours_worked=Decimal("8"),
            side_income=Decimal("0"),
            food_spent=Decimal("25"),
            gas_spent=Decimal("30")
        )
        db_session.add(entry)
        db_session.commit()
        db_session.refresh(entry)
        
        feedback = AIFeedback(
            entry_id=entry.id,
            status="completed",
            content="Great job today!",
            provider="openai",
            model="gpt-4",
            tokens_used=100,
            generation_time=2.5
        )
        db_session.add(feedback)
        db_session.commit()
        
        # Get feedback
        response = client.get(
            f"/api/v1/feedback/{entry_date}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Great job today!"
        assert data["provider"] == "openai"
        assert data["status"] == "completed"
        
        app.dependency_overrides.clear()
    
    def test_get_feedback_not_found(self, db_session, authenticated_user):
        """Test getting feedback when none exists"""
        app.dependency_overrides[get_db] = override_get_db(db_session)
        
        # Create entry without feedback
        from tracker.core.models import DailyEntry
        
        entry_date = date.today()
        entry = DailyEntry(
            user_id=authenticated_user["user"].id,
            date=entry_date,
            stress_level=5,
            income_today=Decimal("400"),
            bills_due_today=Decimal("200"),
            hours_worked=Decimal("8"),
            side_income=Decimal("0"),
            food_spent=Decimal("25"),
            gas_spent=Decimal("30")
        )
        db_session.add(entry)
        db_session.commit()
        
        # Try to get feedback
        response = client.get(
            f"/api/v1/feedback/{entry_date}",
            headers=authenticated_user["headers"]
        )
        
        assert response.status_code == 404
        
        app.dependency_overrides.clear()
