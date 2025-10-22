"""CLI UI components for prompts"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from prompt_toolkit import prompt
from prompt_toolkit.validation import ValidationError, Validator


class DecimalValidator(Validator):
    """Validator for decimal input"""

    def __init__(self, allow_negative: bool = False):
        self.allow_negative = allow_negative

    def validate(self, document):
        text = document.text.strip()
        if not text:
            return  # Allow empty for optional fields

        try:
            value = Decimal(text)
            if not self.allow_negative and value < 0:
                raise ValidationError(
                    message="Value cannot be negative"
                )
        except InvalidOperation:
            raise ValidationError(
                message="Please enter a valid number"
            )


class IntegerRangeValidator(Validator):
    """Validator for integer range"""

    def __init__(self, min_val: int, max_val: int):
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, document):
        text = document.text.strip()
        if not text:
            raise ValidationError(message="This field is required")

        try:
            value = int(text)
            if value < self.min_val or value > self.max_val:
                raise ValidationError(
                    message=f"Value must be between {self.min_val} and {self.max_val}"
                )
        except ValueError:
            raise ValidationError(
                message="Please enter a valid number"
            )


class DateValidator(Validator):
    """Validator for date input"""

    def validate(self, document):
        text = document.text.strip()
        if not text:
            return  # Will use default

        try:
            parsed_date = datetime.strptime(text, "%Y-%m-%d").date()
            if parsed_date > date.today():
                raise ValidationError(
                    message="Date cannot be in the future"
                )
        except ValueError:
            raise ValidationError(
                message="Please enter date in YYYY-MM-DD format"
            )


def prompt_decimal(
    message: str,
    default: Optional[str] = None,
    allow_negative: bool = False,
    required: bool = True
) -> Optional[Decimal]:
    """Prompt for decimal input"""
    validator = DecimalValidator(allow_negative=allow_negative) if required else None
    
    result = prompt(
        message,
        default=default or "",
        validator=validator,
    )
    
    result = result.strip()
    if not result:
        return None
    
    return Decimal(result)


def prompt_integer_range(
    message: str,
    min_val: int,
    max_val: int,
    default: Optional[str] = None
) -> int:
    """Prompt for integer within range"""
    result = prompt(
        message,
        default=default or "",
        validator=IntegerRangeValidator(min_val, max_val),
    )
    
    return int(result.strip())


def prompt_text(
    message: str,
    default: Optional[str] = None,
    multiline: bool = False
) -> Optional[str]:
    """Prompt for text input"""
    result = prompt(
        message,
        default=default or "",
        multiline=multiline,
    )
    
    result = result.strip()
    return result if result else None


def prompt_date(
    message: str,
    default: Optional[date] = None
) -> date:
    """Prompt for date input"""
    default_str = default.strftime("%Y-%m-%d") if default else date.today().strftime("%Y-%m-%d")
    
    result = prompt(
        message,
        default=default_str,
        validator=DateValidator(),
    )
    
    return datetime.strptime(result.strip(), "%Y-%m-%d").date()


def prompt_yes_no(message: str, default: bool = True) -> bool:
    """
    Prompt for yes/no confirmation
    
    Args:
        message: Prompt message
        default: Default value (True for yes, False for no)
        
    Returns:
        True if yes, False if no
    """
    default_str = "Y/n" if default else "y/N"
    result = prompt(f"{message} [{default_str}]: ").strip().lower()
    
    if not result:
        return default
    
    return result in ('y', 'yes', 'true', '1')
