"""CLI UI components for prompts"""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

from prompt_toolkit import prompt
from prompt_toolkit.validation import ValidationError, Validator

from tracker.cli.ui.console import get_console


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
    """Prompt for decimal input with retry on error"""
    
    while True:
        try:
            validator = DecimalValidator(allow_negative=allow_negative) if required else None
            
            result = prompt(
                message,
                default=default or "",
                validator=validator,
            )
            
            result = result.strip()
            if not result:
                return Decimal("0") if default == "" else None
            
            return Decimal(result)
        
        except (ValidationError, InvalidOperation) as e:
            get_console().print(f"[red]Invalid input: {e}[/red]")
            get_console().print("[yellow]Please try again (or press Ctrl+C to cancel)[/yellow]")
        except KeyboardInterrupt:
            raise  # Allow cancellation
        except Exception as e:
            get_console().print(f"[red]Error: {e}[/red]")
            get_console().print("[yellow]Please try again (or press Ctrl+C to cancel)[/yellow]")


def prompt_integer_range(
    message: str,
    min_val: int,
    max_val: int,
    default: Optional[str] = None
) -> int:
    """Prompt for integer within range with retry on error"""
    
    while True:
        try:
            result = prompt(
                message,
                default=default or "",
                validator=IntegerRangeValidator(min_val, max_val),
            )
            
            return int(result.strip())
        
        except (ValidationError, ValueError) as e:
            get_console().print(f"[red]Invalid input: {e}[/red]")
            get_console().print(f"[yellow]Please enter a number between {min_val} and {max_val}[/yellow]")
        except KeyboardInterrupt:
            raise  # Allow cancellation
        except Exception as e:
            get_console().print(f"[red]Error: {e}[/red]")
            get_console().print("[yellow]Please try again (or press Ctrl+C to cancel)[/yellow]")


def prompt_text(
    message: str,
    default: Optional[str] = None,
    multiline: bool = False
) -> Optional[str]:
    """Prompt for text input with error handling"""
    
    while True:
        try:
            if multiline:
                # Custom multiline input that handles "Enter twice to finish"
                return _prompt_multiline_text(message, default)
            else:
                # Single line input using prompt_toolkit
                result = prompt(
                    message,
                    default=default or "",
                    multiline=False,
                )
                
                result = result.strip()
                return result if result else None
        
        except KeyboardInterrupt:
            raise  # Allow cancellation
        except Exception as e:
            get_console().print(f"[red]Error: {e}[/red]")
            get_console().print("[yellow]Please try again (or press Ctrl+C to cancel)[/yellow]")


def _prompt_multiline_text(message: str, default: Optional[str] = None) -> Optional[str]:
    """
    Custom multiline text input that handles "Enter twice to finish" behavior.
    
    Args:
        message: The prompt message
        default: Default text to show
        
    Returns:
        The multiline text input, or None if empty
    """
    console = get_console()
    
    # Show the prompt message
    console.print(f"[green]{message}[/green]")
    
    lines = []
    empty_line_count = 0
    
    while True:
        try:
            # Get user input
            line = input()
            
            # Check for empty line (Enter twice to finish)
            if line.strip() == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    # Two consecutive empty lines - end input
                    break
                else:
                    # First empty line - add it to the text but continue
                    lines.append("")
            else:
                # Reset empty line counter when we get non-empty input
                empty_line_count = 0
                lines.append(line)
                
        except KeyboardInterrupt:
            raise  # Allow cancellation
        except EOFError:
            break  # End of input (Ctrl+D)
    
    # Join lines and clean up
    result = "\n".join(lines).strip()
    return result if result else None


def prompt_date(
    message: str,
    default: Optional[date] = None
) -> date:
    """Prompt for date input with retry on error"""
    
    default_str = default.strftime("%Y-%m-%d") if default else date.today().strftime("%Y-%m-%d")
    
    while True:
        try:
            result = prompt(
                message,
                default=default_str,
                validator=DateValidator(),
            )
            
            return datetime.strptime(result.strip(), "%Y-%m-%d").date()
        
        except (ValidationError, ValueError) as e:
            get_console().print(f"[red]Invalid date: {e}[/red]")
            get_console().print("[yellow]Please use YYYY-MM-DD format (e.g., 2025-10-21)[/yellow]")
        except KeyboardInterrupt:
            raise  # Allow cancellation
        except Exception as e:
            get_console().print(f"[red]Error: {e}[/red]")
            get_console().print("[yellow]Please try again (or press Ctrl+C to cancel)[/yellow]")


def prompt_yes_no(message: str, default: bool = True) -> bool:
    """
    Prompt for yes/no confirmation with error handling
    
    Args:
        message: Prompt message
        default: Default value (True for yes, False for no)
        
    Returns:
        True if yes, False if no
    """
    
    while True:
        try:
            default_str = "Y/n" if default else "y/N"
            result = prompt(f"{message} [{default_str}]: ").strip().lower()
            
            if not result:
                return default
            
            if result in ('y', 'yes', 'true', '1'):
                return True
            elif result in ('n', 'no', 'false', '0'):
                return False
            else:
                get_console().print("[yellow]Please answer 'y' or 'n'[/yellow]")
                continue
        
        except KeyboardInterrupt:
            raise  # Allow cancellation
        except Exception as e:
            get_console().print(f"[red]Error: {e}[/red]")
            get_console().print("[yellow]Please try again (or press Ctrl+C to cancel)[/yellow]")
