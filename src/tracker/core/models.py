"""SQLAlchemy ORM models"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from tracker.core.database import Base
from tracker.core.encryption import encryption_service


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    api_key_hash = Column(String(255), nullable=True, index=True)
    settings = Column(Text, nullable=True)  # JSON string

    # Relationships
    entries = relationship("DailyEntry", back_populates="user", cascade="all, delete-orphan")


class DailyEntry(Base):
    """Daily entry model with financial and wellbeing data"""

    __tablename__ = "daily_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # Financial fields (some encrypted)
    cash_on_hand_encrypted = Column(Text, nullable=True)  # Encrypted
    bank_balance_encrypted = Column(Text, nullable=True)  # Encrypted
    income_today = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    bills_due_today = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    debts_total_encrypted = Column(Text, nullable=True)  # Encrypted
    hours_worked = Column(Numeric(4, 1), nullable=False, default=Decimal("0.0"))
    side_income = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    food_spent = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    gas_spent = Column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))

    # Wellbeing fields
    notes = Column(Text, nullable=True)
    stress_level = Column(Integer, nullable=False)
    priority = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="entries")
    feedback = relationship("AIFeedback", back_populates="entry", uselist=False)

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uix_user_date"),
        CheckConstraint("stress_level >= 1 AND stress_level <= 10", name="check_stress_level"),
        CheckConstraint("hours_worked >= 0 AND hours_worked <= 24", name="check_hours_worked"),
        Index("ix_daily_entries_user_date", "user_id", "date"),
    )

    @property
    def cash_on_hand(self) -> Optional[Decimal]:
        """Decrypt cash_on_hand"""
        if self.cash_on_hand_encrypted:
            return Decimal(encryption_service.decrypt(self.cash_on_hand_encrypted))
        return None

    @cash_on_hand.setter
    def cash_on_hand(self, value: Optional[Decimal]):
        """Encrypt cash_on_hand"""
        if value is not None:
            self.cash_on_hand_encrypted = encryption_service.encrypt(str(value))
        else:
            self.cash_on_hand_encrypted = None

    @property
    def bank_balance(self) -> Optional[Decimal]:
        """Decrypt bank_balance"""
        if self.bank_balance_encrypted:
            return Decimal(encryption_service.decrypt(self.bank_balance_encrypted))
        return None

    @bank_balance.setter
    def bank_balance(self, value: Optional[Decimal]):
        """Encrypt bank_balance"""
        if value is not None:
            self.bank_balance_encrypted = encryption_service.encrypt(str(value))
        else:
            self.bank_balance_encrypted = None

    @property
    def debts_total(self) -> Optional[Decimal]:
        """Decrypt debts_total"""
        if self.debts_total_encrypted:
            return Decimal(encryption_service.decrypt(self.debts_total_encrypted))
        return None

    @debts_total.setter
    def debts_total(self, value: Optional[Decimal]):
        """Encrypt debts_total"""
        if value is not None:
            self.debts_total_encrypted = encryption_service.encrypt(str(value))
        else:
            self.debts_total_encrypted = None


class AIFeedback(Base):
    """AI-generated feedback for entries"""

    __tablename__ = "ai_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(
        Integer, ForeignKey("daily_entries.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    content = Column(Text, nullable=False)
    status = Column(
        SQLEnum("pending", "completed", "failed", name="feedback_status"),
        default="pending",
        nullable=False,
        index=True,
    )
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    generation_time = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    entry = relationship("DailyEntry", back_populates="feedback")
    conversation_logs = relationship("ConversationLog", back_populates="feedback", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("tokens_used >= 0", name="check_tokens_used"),
        CheckConstraint("generation_time >= 0", name="check_generation_time"),
    )


class ConversationLog(Base):
    """Conversation history for AI interactions"""

    __tablename__ = "conversation_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    feedback_id = Column(
        Integer, ForeignKey("ai_feedback.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role = Column(
        SQLEnum("system", "user", "assistant", name="message_role"), nullable=False
    )
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    feedback = relationship("AIFeedback", back_populates="conversation_logs")

    # Indexes
    __table_args__ = (
        Index("ix_conversation_logs_feedback_timestamp", "feedback_id", "timestamp"),
    )


class UserProfile(Base):
    """User character sheet / profile for personalized AI context"""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Financial Character (JSON stored as Text)
    financial_personality = Column(String(500), nullable=True)
    typical_income_range = Column(String(100), nullable=True)
    debt_situation = Column(String(500), nullable=True)
    money_stressors = Column(Text, nullable=True)  # JSON array
    money_wins = Column(Text, nullable=True)  # JSON array
    
    # Work Character
    work_style = Column(String(500), nullable=True)
    side_hustle_status = Column(String(500), nullable=True)
    career_goals = Column(Text, nullable=True)  # JSON array
    work_challenges = Column(Text, nullable=True)  # JSON array
    
    # Wellbeing Character
    stress_pattern = Column(String(500), nullable=True)
    stress_triggers = Column(Text, nullable=True)  # JSON array
    coping_mechanisms = Column(Text, nullable=True)  # JSON array
    baseline_stress = Column(Float, default=5.0, nullable=False)
    
    # Life Patterns
    priorities = Column(Text, nullable=True)  # JSON array
    recurring_themes = Column(Text, nullable=True)  # JSON array
    celebration_moments = Column(Text, nullable=True)  # JSON array
    ongoing_challenges = Column(Text, nullable=True)  # JSON array
    
    # Growth & Goals
    short_term_goals = Column(Text, nullable=True)  # JSON array
    long_term_aspirations = Column(Text, nullable=True)  # JSON array
    recent_growth = Column(Text, nullable=True)  # JSON array
    
    # Preferences
    communication_style = Column(String(500), nullable=True)
    feedback_preferences = Column(String(500), nullable=True)
    
    # Meta
    total_entries = Column(Integer, default=0, nullable=False)
    entry_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_entry_date = Column(Date, nullable=True)
    
    # Version for tracking profile evolution
    profile_version = Column(Integer, default=1, nullable=False)
    
    # Relationship
    user = relationship("User")
