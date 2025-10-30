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
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")


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
    chat = relationship("Chat", back_populates="entry", uselist=False, cascade="all, delete-orphan")

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
    
    # Basic Info
    nickname = Column(String(100), nullable=True)
    preferred_tone = Column(String(50), nullable=True)  # casual, professional, encouraging, stoic
    context_depth = Column(String(20), default="basic", nullable=False)  # basic, personal, deep
    
    # Work Setup (encrypted)
    work_info_encrypted = Column(Text, nullable=True)  # JSON: job title, hourly/salary, pay schedule, hours, commute
    
    # Financial Overview (encrypted)
    financial_info_encrypted = Column(Text, nullable=True)  # JSON: income sources, net pay, bills, debts
    
    # Goals (encrypted)
    goals_encrypted = Column(Text, nullable=True)  # JSON: short-term and long-term goals
    
    # Lifestyle (encrypted)
    lifestyle_encrypted = Column(Text, nullable=True)  # JSON: gym, gas usage, meals out, etc.
    
    # Emotional Context
    stress_triggers = Column(Text, nullable=True)  # JSON array
    calming_activities = Column(Text, nullable=True)  # JSON array
    baseline_energy = Column(Integer, default=5, nullable=False)  # 1-10 scale
    baseline_stress = Column(Float, default=5.0, nullable=False)
    
    # AI-Detected Patterns (not user-entered)
    detected_patterns_encrypted = Column(Text, nullable=True)  # JSON: themes AI notices over time
    
    # Preferences
    communication_style = Column(String(500), nullable=True)
    reminder_preferences = Column(Text, nullable=True)  # JSON: when to get reminders
    
    # Meta
    total_entries = Column(Integer, default=0, nullable=False)
    entry_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_entry_date = Column(Date, nullable=True)
    last_monthly_checkin = Column(Date, nullable=True)
    
    # Version for tracking profile evolution
    profile_version = Column(Integer, default=1, nullable=False)
    
    # Relationship
    user = relationship("User")
    
    @property
    def work_info(self) -> Optional[dict]:
        """Decrypt work_info"""
        if self.work_info_encrypted:
            import json
            return json.loads(encryption_service.decrypt(self.work_info_encrypted))
        return None
    
    @work_info.setter
    def work_info(self, value: Optional[dict]):
        """Encrypt work_info"""
        if value is not None:
            import json
            self.work_info_encrypted = encryption_service.encrypt(json.dumps(value))
        else:
            self.work_info_encrypted = None
    
    @property
    def financial_info(self) -> Optional[dict]:
        """Decrypt financial_info"""
        if self.financial_info_encrypted:
            import json
            return json.loads(encryption_service.decrypt(self.financial_info_encrypted))
        return None
    
    @financial_info.setter
    def financial_info(self, value: Optional[dict]):
        """Encrypt financial_info"""
        if value is not None:
            import json
            self.financial_info_encrypted = encryption_service.encrypt(json.dumps(value))
        else:
            self.financial_info_encrypted = None
    
    @property
    def goals(self) -> Optional[dict]:
        """Decrypt goals"""
        if self.goals_encrypted:
            import json
            return json.loads(encryption_service.decrypt(self.goals_encrypted))
        return None
    
    @goals.setter
    def goals(self, value: Optional[dict]):
        """Encrypt goals"""
        if value is not None:
            import json
            self.goals_encrypted = encryption_service.encrypt(json.dumps(value))
        else:
            self.goals_encrypted = None
    
    @property
    def lifestyle(self) -> Optional[dict]:
        """Decrypt lifestyle"""
        if self.lifestyle_encrypted:
            import json
            return json.loads(encryption_service.decrypt(self.lifestyle_encrypted))
        return None
    
    @lifestyle.setter
    def lifestyle(self, value: Optional[dict]):
        """Encrypt lifestyle"""
        if value is not None:
            import json
            self.lifestyle_encrypted = encryption_service.encrypt(json.dumps(value))
        else:
            self.lifestyle_encrypted = None
    
    @property
    def detected_patterns(self) -> Optional[dict]:
        """Decrypt detected_patterns"""
        if self.detected_patterns_encrypted:
            import json
            return json.loads(encryption_service.decrypt(self.detected_patterns_encrypted))
        return None
    
    @detected_patterns.setter
    def detected_patterns(self, value: Optional[dict]):
        """Encrypt detected_patterns"""
        if value is not None:
            import json
            self.detected_patterns_encrypted = encryption_service.encrypt(json.dumps(value))
        else:
            self.detected_patterns_encrypted = None


class Chat(Base):
    """Chat conversation model - can be linked to an entry or standalone"""
    
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_id = Column(Integer, ForeignKey("daily_entries.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Chat metadata
    title = Column(String(500), nullable=False)  # Human-readable title
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    entry = relationship("DailyEntry", back_populates="chat")
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan", order_by="ChatMessage.created_at")
    
    __table_args__ = (
        Index("ix_chats_user_created", "user_id", "created_at"),
    )


class ChatMessage(Base):
    """Individual messages in a chat conversation"""
    
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Message content
    role = Column(SQLEnum("user", "assistant", "system", name="message_role"), nullable=False)
    content = Column(Text, nullable=False)  # Encrypted if sensitive
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    chat = relationship("Chat", back_populates="messages")
    
    __table_args__ = (
        Index("ix_chat_messages_chat_created", "chat_id", "created_at"),
    )


class CashFlowEvent(Base):
    """Cash flow event for tracking generic money loops
    
    Sign convention: positive amount = outflow (expense), negative = inflow (income)
    This allows consistent handling across all event types.
    """
    
    __tablename__ = "cash_flow_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    event_date = Column(Date, nullable=False, index=True)
    
    # Event classification
    event_type = Column(
        String(50), 
        nullable=False, 
        index=True
    )  # 'income'|'bill'|'transfer'|'spend'|'advance'|'repayment'|'fee'
    provider = Column(String(100), nullable=True, index=True)  # User-defined: 'acorns_checking', 'tool_truck', 'advance_app'
    category = Column(String(100), nullable=True)  # 'gas', 'food', 'rent', 'subscription', 'tools', 'loan'
    
    # Amount stored in cents to avoid float precision issues
    # Positive = outflow (expense), Negative = inflow (income)
    amount_cents = Column(Integer, nullable=False)
    
    # Account tracking
    account = Column(String(100), nullable=True)  # 'chase', 'cash', 'wallet:x'
    
    # Additional context
    memo = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User")
    
    # Indexes for efficient queries
    __table_args__ = (
        Index("ix_cfe_user_date", "user_id", "event_date"),
        Index("ix_cfe_type_provider", "event_type", "provider"),
    )
    
    @property
    def amount(self) -> Decimal:
        """Get amount as Decimal (in dollars)"""
        return Decimal(self.amount_cents) / 100
    
    @amount.setter
    def amount(self, value: Decimal):
        """Set amount from Decimal (in dollars)"""
        self.amount_cents = int(value * 100)
