"""Test fixtures and utilities"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from tracker.core.database import Base
from tracker.core.models import User


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    # Create default user
    user = User(id=1, username="testuser", email="test@example.com")
    session.add(user)
    session.commit()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(db_session):
    """Get the test user"""
    return db_session.query(User).filter_by(username="testuser").first()
