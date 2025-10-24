"""Search command - Full-text search across entries"""

import click
from rich.table import Table
from rich.text import Text

from tracker.cli.ui.console import (
    emphasize,
    get_console,
    icon,
    qualitative_scale,
)
from tracker.core.database import SessionLocal
from tracker.services.history_service import HistoryService


@click.command()
@click.argument("query", required=True)
@click.option("--limit", default=20, type=int, help="Maximum number of results", show_default=True)
def search(query: str, limit: int):
    """
    Search entries by journal or priority text
    
    QUERY: Search term to look for in journal and priority fields
    
    Examples:
    
      # Find entries mentioning "overtime"
      tracker search overtime
      
      # Search for "debt" with more results
      tracker search debt --limit 50
      
      # Find entries about bills
      tracker search "paid bills"
    """
    db = SessionLocal()
    service = HistoryService(db)
    
    try:
        # Search entries
        results = service.search_entries(1, query, limit=limit)  # TODO: Get actual user
        
        if not results:
            get_console().print(
                emphasize(
                    f"\n[yellow]{icon('🔎', 'Search')} No entries found matching '[cyan]{query}[/cyan]'[/yellow]\n",
                    "no search results",
                )
            )
            return
        
        # Display results
        console = get_console()
        console.print(
            f"\n[bold blue]{icon('🔎', 'Search')} Search Results[/bold blue] for '[cyan]{query}[/cyan]'"
        )
        console.print(
            f"[dim]Found {len(results)} {'entry' if len(results) == 1 else 'entries'}[/dim]\n"
        )
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Date", style="cyan", width=12)
        table.add_column("Stress", justify="center", width=8)
        table.add_column("Income", justify="right", width=10)
        table.add_column("Priority", width=20)
        table.add_column("Journal", width=50)
        
        for entry in results:
            # Highlight search term in text
            notes = highlight_text(entry.notes or "", query)
            priority = highlight_text(entry.priority or "", query)
            
            # Color-code stress level
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
            
            table.add_row(
                str(entry.date),
                stress_text,
                f"${entry.income_today:.2f}",
                priority,
                notes
            )
        
        console.print(table)
        console.print()
        
    except Exception as e:
        get_console().print(
            emphasize(f"[red]{icon('❌', 'Error')} Error: {e}[/red]", "search error")
        )
    finally:
        db.close()


def highlight_text(text: str, query: str) -> str:
    """
    Highlight search term in text
    
    Args:
        text: Original text
        query: Search term to highlight
        
    Returns:
        Text with search term highlighted
    """
    if not text or not query:
        return text or "[dim]none[/dim]"
    
    # Case-insensitive highlighting
    import re
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    
    # Find all matches
    matches = list(pattern.finditer(text))
    if not matches:
        return text
    
    # Build highlighted text
    result = ""
    last_end = 0
    
    for match in matches:
        # Add text before match
        result += text[last_end:match.start()]
        # Add highlighted match
        result += f"[bold yellow on black]{text[match.start():match.end()]}[/]"
        last_end = match.end()
    
    # Add remaining text
    result += text[last_end:]
    
    return result


def get_stress_color(stress_level: int) -> str:
    """Get color for stress level"""
    if stress_level <= 3:
        return "green"
    elif stress_level <= 6:
        return "yellow"
    else:
        return "red"
