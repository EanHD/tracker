"""Pydantic schemas for validation"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class EntryCreate(BaseModel):
    """Schema for creating an entry"""

    date: date
    cash_on_hand: Optional[Decimal] = None
    bank_balance: Optional[Decimal] = None
    income_today: Decimal = Field(default=Decimal("0.00"), ge=0)
    bills_due_today: Decimal = Field(default=Decimal("0.00"), ge=0)
    debts_total: Optional[Decimal] = None
    hours_worked: Decimal = Field(default=Decimal("0.0"), ge=0, le=24)
    side_income: Decimal = Field(default=Decimal("0.00"), ge=0)
    food_spent: Decimal = Field(default=Decimal("0.00"), ge=0)
    gas_spent: Decimal = Field(default=Decimal("0.00"), ge=0)
    notes: Optional[str] = None
    stress_level: int = Field(..., ge=1, le=10)
    priority: Optional[str] = Field(None, max_length=255)

    @field_validator("date")
    @classmethod
    def validate_date(cls, v: date) -> date:
        """Validate date is not in future"""
        from datetime import date as dt_date
        if v > dt_date.today():
            raise ValueError("Date cannot be in the future")
        return v


class EntryUpdate(BaseModel):
    """Schema for updating an entry (all fields optional for partial updates)"""

    cash_on_hand: Optional[Decimal] = None
    bank_balance: Optional[Decimal] = None
    income_today: Optional[Decimal] = Field(None, ge=0)
    bills_due_today: Optional[Decimal] = Field(None, ge=0)
    debts_total: Optional[Decimal] = None
    hours_worked: Optional[Decimal] = Field(None, ge=0, le=24)
    side_income: Optional[Decimal] = Field(None, ge=0)
    food_spent: Optional[Decimal] = Field(None, ge=0)
    gas_spent: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    priority: Optional[str] = Field(None, max_length=255)

    class Config:
        # Allow arbitrary types for Decimal handling
        arbitrary_types_allowed = True


class EntryResponse(BaseModel):
    """Schema for entry response"""

    id: int
    date: date
    cash_on_hand: Optional[Decimal]
    bank_balance: Optional[Decimal]
    income_today: Decimal
    bills_due_today: Decimal
    debts_total: Optional[Decimal]
    hours_worked: Decimal
    side_income: Decimal
    food_spent: Decimal
    gas_spent: Decimal
    notes: Optional[str]
    stress_level: int
    priority: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""

    id: int
    entry_id: int
    content: str
    status: str
    provider: Optional[str]
    model: Optional[str]
    tokens_used: Optional[int]
    generation_time: Optional[float]
    created_at: str

    class Config:
        from_attributes = True
