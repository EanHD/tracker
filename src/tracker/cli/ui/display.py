"""CLI UI components for display"""

from decimal import Decimal
from typing import Optional
import textwrap
import shutil

from rich.panel import Panel

from tracker.cli.ui.console import (
    emphasize,
    get_console,
    icon,
    qualitative_scale,
)


def get_stress_color(stress_level: int) -> str:
    """Get color for stress level"""
    if stress_level <= 3:
        return "green"
    if stress_level <= 6:
        return "yellow"
    return "red"


def format_currency(amount: Optional[Decimal]) -> str:
    """Format currency value"""
    if amount is None:
        return "N/A"
    return f"${amount:,.2f}"


def format_wrapped_text(text: str, indent: str = "  ") -> str:
    """
    Format text with proper word wrapping based on terminal width.
    
    Args:
        text: The text to wrap
        indent: String to indent each line with
        
    Returns:
        Formatted text with proper wrapping and indentation
    """
    if not text:
        return ""
    
    # Get terminal width, fallback to 80 if not available
    try:
        terminal_width = shutil.get_terminal_size().columns
    except (AttributeError, OSError):
        terminal_width = 80
    
    # Calculate wrap width accounting for indentation and some padding
    wrap_width = max(terminal_width - len(indent) - 4, 40)
    
    # Split into paragraphs first to preserve line breaks
    paragraphs = text.split('\n')
    formatted_paragraphs = []
    
    for paragraph in paragraphs:
        if not paragraph.strip():
            # Preserve empty lines
            formatted_paragraphs.append("")
            continue
            
        # Wrap each paragraph individually
        wrapped_lines = textwrap.wrap(
            paragraph,
            width=wrap_width,
            break_long_words=False,
            break_on_hyphens=False,
            replace_whitespace=False,
        )
        
        # Add indentation to each line
        if wrapped_lines:
            formatted_paragraphs.extend([f"{indent}{line}" for line in wrapped_lines])
        else:
            formatted_paragraphs.append("")
    
    # Join paragraphs back together
    return "\n".join(formatted_paragraphs)


def _format_wrapped_text(text: str, indent: str = "  ") -> str:
    """
    Format text with proper word wrapping based on terminal width.
    
    Args:
        text: The text to wrap
        indent: String to indent each line with
        
    Returns:
        Formatted text with proper wrapping and indentation
    """
    if not text:
        return ""
    
    # Get terminal width, fallback to 80 if not available
    try:
        terminal_width = shutil.get_terminal_size().columns
    except (AttributeError, OSError):
        terminal_width = 80
    
    # Calculate wrap width accounting for indentation and some padding
    wrap_width = max(terminal_width - len(indent) - 4, 40)
    
    # Wrap the text preserving word boundaries
    wrapped_lines = textwrap.wrap(
        text,
        width=wrap_width,
        break_long_words=False,
        break_on_hyphens=False,
        replace_whitespace=False,
    )
    
    # Add indentation to each line
    return "\n".join(f"{indent}{line}" for line in wrapped_lines)


def display_entry(entry, show_feedback: bool = False):
    """Display a daily entry with Rich formatting"""
    console = get_console()

    # Build the display text
    lines = []

    # Financial section
    lines.append(f"[bold cyan]{icon('💰', 'Finance')} Financial Snapshot[/bold cyan]")
    lines.append(f"  Cash on hand: {format_currency(entry.cash_on_hand)}")
    lines.append(f"  Bank balance: {format_currency(entry.bank_balance)}")
    lines.append(f"  Income today: {format_currency(entry.income_today)}")
    lines.append(f"  Bills due: {format_currency(entry.bills_due_today)}")
    lines.append(f"  Total debt: {format_currency(entry.debts_total)}")
    lines.append(f"  Side income: {format_currency(entry.side_income)}")
    lines.append("")

    # Spending section
    lines.append(f"[bold cyan]{icon('🛒', 'Spending')} Spending[/bold cyan]")
    lines.append(f"  Food: {format_currency(entry.food_spent)}")
    lines.append(f"  Gas: {format_currency(entry.gas_spent)}")
    lines.append(f"  Total: {format_currency(entry.food_spent + entry.gas_spent)}")
    lines.append("")

    # Work section
    lines.append(f"[bold cyan]{icon('💼', 'Work')} Work[/bold cyan]")
    lines.append(f"  Hours worked: {entry.hours_worked}")
    lines.append("")

    # Wellbeing section
    stress_color = get_stress_color(entry.stress_level)
    stress_descriptor = qualitative_scale(
        entry.stress_level,
        low=range(0, 4),
        medium=range(4, 7),
        high=range(7, 11),
    )
    stress_text = emphasize(
        f"[{stress_color}]{entry.stress_level}/10[/]",
        f"{stress_descriptor} stress" if stress_descriptor != "unknown" else None,
    )

    lines.append(f"[bold cyan]{icon('🧘', 'Wellbeing')} Wellbeing[/bold cyan]")
    lines.append(f"  Stress level: {stress_text}")
    lines.append(f"  Priority: {entry.priority or 'N/A'}")

    if entry.notes:
        lines.append("")
        lines.append(f"[bold cyan]{icon('📝', 'Journal')} Journal[/bold cyan]")
        # Use dynamic width based on console size with proper terminal detection
        wrapped_journal = format_wrapped_text(entry.notes, indent="  ")
        lines.append(wrapped_journal)

    # Create panel
    panel = Panel(
        "\n".join(lines),
        title=f"[bold]Entry for {entry.date}[/bold]",
        border_style="blue",
        padding=(1, 2),
    )

    console.print(panel)

    # Display feedback if requested and available
    if show_feedback and hasattr(entry, "feedback") and entry.feedback:
        display_feedback(entry.feedback)


def display_feedback(feedback):
    """Display AI feedback with Markdown rendering"""
    from rich.markdown import Markdown
    
    console = get_console()

    if feedback.status == "pending":
        console.print(
            emphasize(
                f"\n[yellow]{icon('⏳', 'Pending')} AI feedback is being generated...[/yellow]",
                "feedback pending",
            )
        )
        return

    if feedback.status == "failed":
        console.print(
            emphasize(
                f"\n[red]{icon('❌', 'Error')} AI feedback generation failed: {feedback.error_message}[/red]",
                "feedback error",
            )
        )
        return

    # Render feedback as Markdown for proper formatting
    # This preserves **bold**, line breaks, lists, etc.
    md = Markdown(feedback.content)
    
    panel = Panel(
        md,
        title=f"[bold green]{icon('💬', 'Feedback')} Tracker[/bold green]",
        border_style="green",
        padding=(1, 2),
    )
    console.print("\n")
    console.print(panel)

    # Show metadata
    if feedback.provider:
        metadata = f"[dim]Generated by {feedback.provider}"
        if feedback.model:
            metadata += f" ({feedback.model})"
        if feedback.generation_time:
            metadata += f" in {feedback.generation_time:.1f}s"
        metadata += "[/dim]"
        console.print(metadata)


def display_entry_preview(entry_data: dict):
    """Display entry preview before saving"""
    console = get_console()

    lines = []
    lines.append(f"Date: {entry_data['date']}")
    lines.append(f"Cash on hand: {format_currency(entry_data.get('cash_on_hand'))}")
    lines.append(f"Bank balance: {format_currency(entry_data.get('bank_balance'))}")
    lines.append(f"Income: {format_currency(entry_data.get('income_today'))}")
    lines.append(f"Bills: {format_currency(entry_data.get('bills_due_today'))}")
    lines.append(f"Debt: {format_currency(entry_data.get('debts_total'))}")
    lines.append(f"Hours worked: {entry_data.get('hours_worked')}")
    lines.append(f"Side income: {format_currency(entry_data.get('side_income'))}")
    lines.append(f"Food: {format_currency(entry_data.get('food_spent'))}")
    lines.append(f"Gas: {format_currency(entry_data.get('gas_spent'))}")

    stress_value = entry_data.get("stress_level")
    stress_color = get_stress_color(stress_value or 0)
    stress_descriptor = qualitative_scale(
        stress_value if stress_value is not None else 0,
        low=range(0, 4),
        medium=range(4, 7),
        high=range(7, 11),
    )
    stress_text = emphasize(
        f"[{stress_color}]{stress_value}/10[/{stress_color}]"
        if stress_value is not None
        else "N/A",
        f"{stress_descriptor} stress" if stress_value is not None else None,
    )
    lines.append(f"Stress: {stress_text}")
    lines.append(f"Priority: {entry_data.get('priority') or 'N/A'}")

    if entry_data.get("notes"):
        lines.append("")
        wrapped_lines = textwrap.wrap(
            entry_data["notes"],
            width=70,
            break_long_words=False,
            break_on_hyphens=False,
        )
        lines.append("Journal:")
        for line in wrapped_lines:
            lines.append(f"  {line}")

    panel = Panel(
        "\n".join(lines),
        title="[bold]Entry Preview[/bold]",
        border_style="cyan",
        padding=(1, 2),
    )

    console.print("\n")
    console.print(panel)


def display_success(message: str):
    """Display success message"""
    console = get_console()
    console.print(
        emphasize(f"\n[bold green]{icon('✅', 'Success')} {message}[/bold green]\n", "success")
    )


def display_error(message: str):
    """Display error message"""
    console = get_console()
    console.print(
        emphasize(f"\n[bold red]{icon('❌', 'Error')} {message}[/bold red]\n", "error")
    )


def display_info(message: str):
    """Display info message"""
    console = get_console()
    console.print(
        emphasize(f"\n[cyan]{icon('ℹ️', 'Info')}  {message}[/cyan]\n", "info")
    )
