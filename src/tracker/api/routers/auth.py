"""Authentication endpoints"""

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from tracker.core.auth import (
    create_access_token,
    create_api_key,
    get_password_hash,
    verify_password,
)
from tracker.core.database import get_db
from tracker.core.models import User

router = APIRouter()


class UserCreate(BaseModel):
    """User registration schema"""
    username: str
    email: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    """User login schema"""
    username: str
    password: str


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 90


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Creates a user account and returns an access token
    """
    # Check if user already exists
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 90
    }


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with username and password
    
    Returns JWT access token
    """
    # Find user
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not user.password_hash or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 90
    }


@router.post("/api-key", response_model=Token)
def generate_api_key(
    username: str,
    password: str,
    db: Session = Depends(get_db)
):
    """
    Generate long-lived API key
    
    Useful for integrations and automation
    """
    # Authenticate user
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate API key
    api_key = create_api_key(username)
    
    # Store hash in database
    user.api_key_hash = get_password_hash(api_key)
    db.commit()
    
    return {
        "access_token": api_key,
        "token_type": "bearer",
        "expires_in": 90 * 24 * 60  # 90 days in minutes
    }
