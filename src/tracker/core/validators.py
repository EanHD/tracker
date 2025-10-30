"""Input validation utilities for the Tracker application."""

import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional, Union, List, Dict
from tracker.core.exceptions import ValidationError


class Validators:
    """Collection of validation methods for various input types."""
    
    @staticmethod
    def validate_decimal(
        value: Any,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        allow_negative: bool = False,
        allow_zero: bool = True,
        max_decimal_places: int = 2
    ) -> Decimal:
        """
        Validate and convert a value to Decimal.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_negative: Whether negative values are allowed
            allow_zero: Whether zero is allowed
            max_decimal_places: Maximum number of decimal places
            
        Returns:
            Validated Decimal value
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            if isinstance(value, str):
                value = value.strip().replace(',', '')
            
            decimal_value = Decimal(str(value))
            
            # Check for NaN or Infinity
            if not decimal_value.is_finite():
                raise ValidationError("Value must be a finite number")
            
            # Check negative constraint
            if not allow_negative and decimal_value < 0:
                raise ValidationError("Value cannot be negative")
            
            # Check zero constraint
            if not allow_zero and decimal_value == 0:
                raise ValidationError("Value cannot be zero")
            
            # Check min/max constraints
            if min_value is not None and decimal_value < min_value:
                raise ValidationError(f"Value must be at least {min_value}")
            
            if max_value is not None and decimal_value > max_value:
                raise ValidationError(f"Value must be at most {max_value}")
            
            # Check decimal places
            if decimal_value.as_tuple().exponent < -max_decimal_places:
                raise ValidationError(f"Value can have at most {max_decimal_places} decimal places")
            
            return decimal_value
            
        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Invalid decimal value: {value}")
    
    @staticmethod
    def validate_integer(
        value: Any,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> int:
        """
        Validate and convert a value to integer.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated integer value
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            int_value = int(value)
            
            if min_value is not None and int_value < min_value:
                raise ValidationError(f"Value must be at least {min_value}")
            
            if max_value is not None and int_value > max_value:
                raise ValidationError(f"Value must be at most {max_value}")
            
            return int_value
            
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer value: {value}")
    
    @staticmethod
    def validate_date(
        value: Any,
        allow_future: bool = False,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ) -> date:
        """
        Validate and convert a value to date.
        
        Args:
            value: Value to validate (string, date, or datetime)
            allow_future: Whether future dates are allowed
            min_date: Minimum allowed date
            max_date: Maximum allowed date
            
        Returns:
            Validated date
            
        Raises:
            ValidationError: If validation fails
        """
        if isinstance(value, datetime):
            date_value = value.date()
        elif isinstance(value, date):
            date_value = value
        elif isinstance(value, str):
            # Try multiple date formats
            formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%m/%d/%Y",
                "%m-%d-%Y",
                "%d/%m/%Y",
                "%d-%m-%Y",
            ]
            
            date_value = None
            for fmt in formats:
                try:
                    date_value = datetime.strptime(value.strip(), fmt).date()
                    break
                except ValueError:
                    continue
            
            if date_value is None:
                raise ValidationError(f"Invalid date format: {value}")
        else:
            raise ValidationError(f"Invalid date type: {type(value)}")
        
        # Check future constraint
        if not allow_future and date_value > date.today():
            raise ValidationError("Date cannot be in the future")
        
        # Check min/max constraints
        if min_date and date_value < min_date:
            raise ValidationError(f"Date must be on or after {min_date}")
        
        if max_date and date_value > max_date:
            raise ValidationError(f"Date must be on or before {max_date}")
        
        return date_value
    
    @staticmethod
    def validate_string(
        value: Any,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_chars: Optional[str] = None,
        strip: bool = True
    ) -> str:
        """
        Validate and clean a string value.
        
        Args:
            value: Value to validate
            min_length: Minimum string length
            max_length: Maximum string length
            pattern: Regex pattern the string must match
            allowed_chars: String of allowed characters
            strip: Whether to strip whitespace
            
        Returns:
            Validated string
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError("Value cannot be None")
        
        str_value = str(value)
        
        if strip:
            str_value = str_value.strip()
        
        # Check length constraints
        if min_length is not None and len(str_value) < min_length:
            raise ValidationError(f"String must be at least {min_length} characters")
        
        if max_length is not None and len(str_value) > max_length:
            raise ValidationError(f"String must be at most {max_length} characters")
        
        # Check pattern
        if pattern and not re.match(pattern, str_value):
            raise ValidationError(f"String does not match required pattern")
        
        # Check allowed characters
        if allowed_chars:
            for char in str_value:
                if char not in allowed_chars:
                    raise ValidationError(f"Character '{char}' is not allowed")
        
        return str_value
    
    @staticmethod
    def validate_email(value: str) -> str:
        """
        Validate an email address.
        
        Args:
            value: Email address to validate
            
        Returns:
            Validated email address (lowercase)
            
        Raises:
            ValidationError: If email is invalid
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        email = value.strip().lower()
        
        if not re.match(email_pattern, email):
            raise ValidationError(f"Invalid email address: {value}")
        
        return email
    
    @staticmethod
    def validate_username(value: str) -> str:
        """
        Validate a username.
        
        Args:
            value: Username to validate
            
        Returns:
            Validated username
            
        Raises:
            ValidationError: If username is invalid
        """
        username = value.strip()
        
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters")
        
        if len(username) > 50:
            raise ValidationError("Username must be at most 50 characters")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError("Username can only contain letters, numbers, hyphens, and underscores")
        
        return username
    
    @staticmethod
    def validate_path(
        value: Union[str, Path],
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        create_parents: bool = False
    ) -> Path:
        """
        Validate a file system path.
        
        Args:
            value: Path to validate
            must_exist: Whether the path must exist
            must_be_file: Whether the path must be a file
            must_be_dir: Whether the path must be a directory
            create_parents: Whether to create parent directories
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If path is invalid
        """
        try:
            path = Path(value).resolve()
            
            if must_exist and not path.exists():
                raise ValidationError(f"Path does not exist: {path}")
            
            if must_be_file and path.exists() and not path.is_file():
                raise ValidationError(f"Path is not a file: {path}")
            
            if must_be_dir and path.exists() and not path.is_dir():
                raise ValidationError(f"Path is not a directory: {path}")
            
            if create_parents and not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            return path
            
        except Exception as e:
            raise ValidationError(f"Invalid path: {value} - {e}")
    
    @staticmethod
    def validate_stress_level(value: Any) -> int:
        """
        Validate stress level (1-10).
        
        Args:
            value: Stress level to validate
            
        Returns:
            Validated stress level
            
        Raises:
            ValidationError: If stress level is invalid
        """
        return Validators.validate_integer(value, min_value=1, max_value=10)
    
    @staticmethod
    def validate_hours_worked(value: Any) -> Decimal:
        """
        Validate hours worked (0-24).
        
        Args:
            value: Hours to validate
            
        Returns:
            Validated hours as Decimal
            
        Raises:
            ValidationError: If hours are invalid
        """
        return Validators.validate_decimal(
            value,
            min_value=Decimal("0"),
            max_value=Decimal("24"),
            max_decimal_places=1
        )
    
    @staticmethod
    def validate_currency(value: Any) -> Decimal:
        """
        Validate currency amount.
        
        Args:
            value: Amount to validate
            
        Returns:
            Validated amount as Decimal
            
        Raises:
            ValidationError: If amount is invalid
        """
        return Validators.validate_decimal(
            value,
            allow_negative=True,  # Allow negative for debts
            max_decimal_places=2
        )
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 5000) -> str:
        """
        Sanitize text input for storage.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        sanitized = re.sub(r'[ \t]+', ' ', sanitized)
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length-3] + "..."
        
        return sanitized.strip()


# Convenience functions
def validate_entry_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate all fields for a daily entry.
    
    Args:
        data: Entry data dictionary
        
    Returns:
        Validated data dictionary
        
    Raises:
        ValidationError: If any field is invalid
    """
    validated = {}
    
    # Date
    if 'date' in data:
        validated['date'] = Validators.validate_date(data['date'])
    
    # Financial fields
    currency_fields = [
        'cash_on_hand', 'bank_balance', 'income_today',
        'bills_due_today', 'debts_total', 'side_income',
        'food_spent', 'gas_spent'
    ]
    
    for field in currency_fields:
        if field in data and data[field] is not None:
            validated[field] = Validators.validate_currency(data[field])
    
    # Hours worked
    if 'hours_worked' in data and data['hours_worked'] is not None:
        validated['hours_worked'] = Validators.validate_hours_worked(data['hours_worked'])
    
    # Stress level
    if 'stress_level' in data:
        validated['stress_level'] = Validators.validate_stress_level(data['stress_level'])
    
    # Text fields
    if 'priority' in data and data['priority']:
        validated['priority'] = Validators.sanitize_text(data['priority'], max_length=255)
    
    if 'notes' in data and data['notes']:
        validated['notes'] = Validators.sanitize_text(data['notes'], max_length=5000)
    
    return validated
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Optional, Union, List, Dict
from tracker.core.exceptions import ValidationError


class Validators:
    """Collection of validation methods for various input types."""
    
    @staticmethod
    def validate_decimal(
        value: Any,
        min_value: Optional[Decimal] = None,
        max_value: Optional[Decimal] = None,
        allow_negative: bool = False,
        allow_zero: bool = True,
        max_decimal_places: int = 2
    ) -> Decimal:
        """
        Validate and convert a value to Decimal.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_negative: Whether negative values are allowed
            allow_zero: Whether zero is allowed
            max_decimal_places: Maximum number of decimal places
            
        Returns:
            Validated Decimal value
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            if isinstance(value, str):
                value = value.strip().replace(',', '')
            
            decimal_value = Decimal(str(value))
            
            # Check for NaN or Infinity
            if not decimal_value.is_finite():
                raise ValidationError("Value must be a finite number")
            
            # Check negative constraint
            if not allow_negative and decimal_value < 0:
                raise ValidationError("Value cannot be negative")
            
            # Check zero constraint
            if not allow_zero and decimal_value == 0:
                raise ValidationError("Value cannot be zero")
            
            # Check min/max constraints
            if min_value is not None and decimal_value < min_value:
                raise ValidationError(f"Value must be at least {min_value}")
            
            if max_value is not None and decimal_value > max_value:
                raise ValidationError(f"Value must be at most {max_value}")
            
            # Check decimal places
            if decimal_value.as_tuple().exponent < -max_decimal_places:
                raise ValidationError(f"Value can have at most {max_decimal_places} decimal places")
            
            return decimal_value
            
        except (InvalidOperation, ValueError) as e:
            raise ValidationError(f"Invalid decimal value: {value}")
    
    @staticmethod
    def validate_integer(
        value: Any,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ) -> int:
        """
        Validate and convert a value to integer.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            
        Returns:
            Validated integer value
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            int_value = int(value)
            
            if min_value is not None and int_value < min_value:
                raise ValidationError(f"Value must be at least {min_value}")
            
            if max_value is not None and int_value > max_value:
                raise ValidationError(f"Value must be at most {max_value}")
            
            return int_value
            
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer value: {value}")
    
    @staticmethod
    def validate_date(
        value: Any,
        allow_future: bool = False,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None
    ) -> date:
        """
        Validate and convert a value to date.
        
        Args:
            value: Value to validate (string, date, or datetime)
            allow_future: Whether future dates are allowed
            min_date: Minimum allowed date
            max_date: Maximum allowed date
            
        Returns:
            Validated date
            
        Raises:
            ValidationError: If validation fails
        """
        if isinstance(value, datetime):
            date_value = value.date()
        elif isinstance(value, date):
            date_value = value
        elif isinstance(value, str):
            # Try multiple date formats
            formats = [
                "%Y-%m-%d",
                "%Y/%m/%d",
                "%m/%d/%Y",
                "%m-%d-%Y",
                "%d/%m/%Y",
                "%d-%m-%Y",
            ]
            
            date_value = None
            for fmt in formats:
                try:
                    date_value = datetime.strptime(value.strip(), fmt).date()
                    break
                except ValueError:
                    continue
            
            if date_value is None:
                raise ValidationError(f"Invalid date format: {value}")
        else:
            raise ValidationError(f"Invalid date type: {type(value)}")
        
        # Check future constraint
        if not allow_future and date_value > date.today():
            raise ValidationError("Date cannot be in the future")
        
        # Check min/max constraints
        if min_date and date_value < min_date:
            raise ValidationError(f"Date must be on or after {min_date}")
        
        if max_date and date_value > max_date:
            raise ValidationError(f"Date must be on or before {max_date}")
        
        return date_value
    
    @staticmethod
    def validate_string(
        value: Any,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        allowed_chars: Optional[str] = None,
        strip: bool = True
    ) -> str:
        """
        Validate and clean a string value.
        
        Args:
            value: Value to validate
            min_length: Minimum string length
            max_length: Maximum string length
            pattern: Regex pattern the string must match
            allowed_chars: String of allowed characters
            strip: Whether to strip whitespace
            
        Returns:
            Validated string
            
        Raises:
            ValidationError: If validation fails
        """
        if value is None:
            raise ValidationError("Value cannot be None")
        
        str_value = str(value)
        
        if strip:
            str_value = str_value.strip()
        
        # Check length constraints
        if min_length is not None and len(str_value) < min_length:
            raise ValidationError(f"String must be at least {min_length} characters")
        
        if max_length is not None and len(str_value) > max_length:
            raise ValidationError(f"String must be at most {max_length} characters")
        
        # Check pattern
        if pattern and not re.match(pattern, str_value):
            raise ValidationError(f"String does not match required pattern")
        
        # Check allowed characters
        if allowed_chars:
            for char in str_value:
                if char not in allowed_chars:
                    raise ValidationError(f"Character '{char}' is not allowed")
        
        return str_value
    
    @staticmethod
    def validate_email(value: str) -> str:
        """
        Validate an email address.
        
        Args:
            value: Email address to validate
            
        Returns:
            Validated email address (lowercase)
            
        Raises:
            ValidationError: If email is invalid
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        email = value.strip().lower()
        
        if not re.match(email_pattern, email):
            raise ValidationError(f"Invalid email address: {value}")
        
        return email
    
    @staticmethod
    def validate_username(value: str) -> str:
        """
        Validate a username.
        
        Args:
            value: Username to validate
            
        Returns:
            Validated username
            
        Raises:
            ValidationError: If username is invalid
        """
        username = value.strip()
        
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters")
        
        if len(username) > 50:
            raise ValidationError("Username must be at most 50 characters")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise ValidationError("Username can only contain letters, numbers, hyphens, and underscores")
        
        return username
    
    @staticmethod
    def validate_path(
        value: Union[str, Path],
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        create_parents: bool = False
    ) -> Path:
        """
        Validate a file system path.
        
        Args:
            value: Path to validate
            must_exist: Whether the path must exist
            must_be_file: Whether the path must be a file
            must_be_dir: Whether the path must be a directory
            create_parents: Whether to create parent directories
            
        Returns:
            Validated Path object
            
        Raises:
            ValidationError: If path is invalid
        """
        try:
            path = Path(value).resolve()
            
            if must_exist and not path.exists():
                raise ValidationError(f"Path does not exist: {path}")
            
            if must_be_file and path.exists() and not path.is_file():
                raise ValidationError(f"Path is not a file: {path}")
            
            if must_be_dir and path.exists() and not path.is_dir():
                raise ValidationError(f"Path is not a directory: {path}")
            
            if create_parents and not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
            
            return path
            
        except Exception as e:
            raise ValidationError(f"Invalid path: {value} - {e}")
    
    @staticmethod
    def validate_stress_level(value: Any) -> int:
        """
        Validate stress level (1-10).
        
        Args:
            value: Stress level to validate
            
        Returns:
            Validated stress level
            
        Raises:
            ValidationError: If stress level is invalid
        """
        return Validators.validate_integer(value, min_value=1, max_value=10)
    
    @staticmethod
    def validate_hours_worked(value: Any) -> Decimal:
        """
        Validate hours worked (0-24).
        
        Args:
            value: Hours to validate
            
        Returns:
            Validated hours as Decimal
            
        Raises:
            ValidationError: If hours are invalid
        """
        return Validators.validate_decimal(
            value,
            min_value=Decimal("0"),
            max_value=Decimal("24"),
            max_decimal_places=1
        )
    
    @staticmethod
    def validate_currency(value: Any) -> Decimal:
        """
        Validate currency amount.
        
        Args:
            value: Amount to validate
            
        Returns:
            Validated amount as Decimal
            
        Raises:
            ValidationError: If amount is invalid
        """
        return Validators.validate_decimal(
            value,
            allow_negative=True,  # Allow negative for debts
            max_decimal_places=2
        )
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 5000) -> str:
        """
        Sanitize text input for storage.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        sanitized = re.sub(r'[ \t]+', ' ', sanitized)
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length-3] + "..."
        
        return sanitized.strip()


# Convenience functions
def validate_entry_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate all fields for a daily entry.
    
    Args:
        data: Entry data dictionary
        
    Returns:
        Validated data dictionary
        
    Raises:
        ValidationError: If any field is invalid
    """
    validated = {}
    
    # Date
    if 'date' in data:
        validated['date'] = Validators.validate_date(data['date'])
    
    # Financial fields
    currency_fields = [
        'cash_on_hand', 'bank_balance', 'income_today',
        'bills_due_today', 'debts_total', 'side_income',
        'food_spent', 'gas_spent'
    ]
    
    for field in currency_fields:
        if field in data and data[field] is not None:
            validated[field] = Validators.validate_currency(data[field])
    
    # Hours worked
    if 'hours_worked' in data and data['hours_worked'] is not None:
        validated['hours_worked'] = Validators.validate_hours_worked(data['hours_worked'])
    
    # Stress level
    if 'stress_level' in data:
        validated['stress_level'] = Validators.validate_stress_level(data['stress_level'])
    
    # Text fields
    if 'priority' in data and data['priority']:
        validated['priority'] = Validators.sanitize_text(data['priority'], max_length=255)
    
    if 'notes' in data and data['notes']:
        validated['notes'] = Validators.sanitize_text(data['notes'], max_length=5000)
    
    return validated
