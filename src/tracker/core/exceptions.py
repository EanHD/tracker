"""Custom exceptions for the Tracker application."""

from typing import Optional, Any, Dict


class TrackerError(Exception):
    """Base exception for all Tracker errors."""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}


class ConfigurationError(TrackerError):
    """Raised when there's a configuration issue."""
    pass


class DatabaseError(TrackerError):
    """Raised when database operations fail."""
    pass


class ValidationError(TrackerError):
    """Raised when input validation fails."""
    pass


class AuthenticationError(TrackerError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(TrackerError):
    """Raised when authorization fails."""
    pass


class EntryNotFoundError(TrackerError):
    """Raised when an entry is not found."""
    
    def __init__(self, date_or_id: Any):
        super().__init__(
            f"Entry not found: {date_or_id}",
            details={"identifier": str(date_or_id)}
        )


class DuplicateEntryError(TrackerError):
    """Raised when trying to create a duplicate entry."""
    
    def __init__(self, date: Any):
        super().__init__(
            f"Entry already exists for {date}",
            details={"date": str(date)}
        )


class AIServiceError(TrackerError):
    """Raised when AI service operations fail."""
    pass


class ExportError(TrackerError):
    """Raised when export operations fail."""
    pass


class NetworkError(TrackerError):
    """Raised when network operations fail."""
    pass


class FileSystemError(TrackerError):
    """Raised when file system operations fail."""
    pass


class EncryptionError(TrackerError):
    """Raised when encryption/decryption fails."""
    pass
from typing import Optional, Any, Dict


class TrackerError(Exception):
    """Base exception for all Tracker errors."""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}


class ConfigurationError(TrackerError):
    """Raised when there's a configuration issue."""
    pass


class DatabaseError(TrackerError):
    """Raised when database operations fail."""
    pass


class ValidationError(TrackerError):
    """Raised when input validation fails."""
    pass


class AuthenticationError(TrackerError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(TrackerError):
    """Raised when authorization fails."""
    pass


class EntryNotFoundError(TrackerError):
    """Raised when an entry is not found."""
    
    def __init__(self, date_or_id: Any):
        super().__init__(
            f"Entry not found: {date_or_id}",
            details={"identifier": str(date_or_id)}
        )


class DuplicateEntryError(TrackerError):
    """Raised when trying to create a duplicate entry."""
    
    def __init__(self, date: Any):
        super().__init__(
            f"Entry already exists for {date}",
            details={"date": str(date)}
        )


class AIServiceError(TrackerError):
    """Raised when AI service operations fail."""
    pass


class ExportError(TrackerError):
    """Raised when export operations fail."""
    pass


class NetworkError(TrackerError):
    """Raised when network operations fail."""
    pass


class FileSystemError(TrackerError):
    """Raised when file system operations fail."""
    pass


class EncryptionError(TrackerError):
    """Raised when encryption/decryption fails."""
    pass
