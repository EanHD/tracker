"""Logging configuration for the Tracker application."""

import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
import platform

from tracker.config import settings


def get_log_dir() -> Path:
    """Get the log directory path, creating it if necessary."""
    if platform.system() == "Windows":
        log_dir = Path.home() / "AppData" / "Local" / "tracker" / "logs"
    else:
        log_dir = Path.home() / ".local" / "share" / "tracker" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    level: Optional[str] = None,
    log_file: bool = True,
    console: bool = True,
    verbose: bool = False
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Whether to log to file
        console: Whether to log to console
        verbose: Enable verbose output (sets DEBUG level)
    """
    # Determine log level
    if verbose:
        log_level = logging.DEBUG
    elif level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("tracker")
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter if not verbose else detailed_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_path = get_log_dir() / "tracker.log"
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Log startup information
    logger.info(f"Tracker v{__import__('tracker').__version__} starting")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version}")
    logger.debug(f"Log level: {logging.getLevelName(log_level)}")
    logger.debug(f"Log directory: {get_log_dir()}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"tracker.{name}")


class LogContext:
    """Context manager for temporary log level changes."""
    
    def __init__(self, level: str):
        self.new_level = getattr(logging, level.upper())
        self.logger = logging.getLogger("tracker")
        self.old_level = None
    
    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)


def log_exception(logger: logging.Logger, exc: Exception, context: str = "") -> None:
    """
    Log an exception with full traceback.
    
    Args:
        logger: Logger instance
        exc: Exception to log
        context: Additional context about where the error occurred
    """
    import traceback
    
    error_msg = f"Exception in {context}: {exc}" if context else f"Exception: {exc}"
    logger.error(error_msg)
    logger.debug(f"Traceback:\n{traceback.format_exc()}")


def sanitize_log_data(data: dict) -> dict:
    """
    Remove sensitive information from data before logging.
    
    Args:
        data: Dictionary containing data to log
        
    Returns:
        Sanitized dictionary
    """
    sensitive_keys = {
        'password', 'api_key', 'secret', 'token', 
        'cash_on_hand', 'bank_balance', 'debts_total',
        'encryption_key', 'jwt_secret'
    }
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        else:
            sanitized[key] = value
    
    return sanitized
import logging
import sys
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler
import platform

from tracker.config import settings


def get_log_dir() -> Path:
    """Get the log directory path, creating it if necessary."""
    if platform.system() == "Windows":
        log_dir = Path.home() / "AppData" / "Local" / "tracker" / "logs"
    else:
        log_dir = Path.home() / ".local" / "share" / "tracker" / "logs"
    
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def setup_logging(
    level: Optional[str] = None,
    log_file: bool = True,
    console: bool = True,
    verbose: bool = False
) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Whether to log to file
        console: Whether to log to console
        verbose: Enable verbose output (sets DEBUG level)
    """
    # Determine log level
    if verbose:
        log_level = logging.DEBUG
    elif level:
        log_level = getattr(logging, level.upper(), logging.INFO)
    else:
        log_level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("tracker")
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(simple_formatter if not verbose else detailed_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if log_file:
        log_path = get_log_dir() / "tracker.log"
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    
    # Log startup information
    logger.info(f"Tracker v{__import__('tracker').__version__} starting")
    logger.info(f"Platform: {platform.system()} {platform.release()}")
    logger.info(f"Python: {sys.version}")
    logger.debug(f"Log level: {logging.getLevelName(log_level)}")
    logger.debug(f"Log directory: {get_log_dir()}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"tracker.{name}")


class LogContext:
    """Context manager for temporary log level changes."""
    
    def __init__(self, level: str):
        self.new_level = getattr(logging, level.upper())
        self.logger = logging.getLogger("tracker")
        self.old_level = None
    
    def __enter__(self):
        self.old_level = self.logger.level
        self.logger.setLevel(self.new_level)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.old_level)


def log_exception(logger: logging.Logger, exc: Exception, context: str = "") -> None:
    """
    Log an exception with full traceback.
    
    Args:
        logger: Logger instance
        exc: Exception to log
        context: Additional context about where the error occurred
    """
    import traceback
    
    error_msg = f"Exception in {context}: {exc}" if context else f"Exception: {exc}"
    logger.error(error_msg)
    logger.debug(f"Traceback:\n{traceback.format_exc()}")


def sanitize_log_data(data: dict) -> dict:
    """
    Remove sensitive information from data before logging.
    
    Args:
        data: Dictionary containing data to log
        
    Returns:
        Sanitized dictionary
    """
    sensitive_keys = {
        'password', 'api_key', 'secret', 'token', 
        'cash_on_hand', 'bank_balance', 'debts_total',
        'encryption_key', 'jwt_secret'
    }
    
    sanitized = {}
    for key, value in data.items():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
        else:
            sanitized[key] = value
    
    return sanitized
