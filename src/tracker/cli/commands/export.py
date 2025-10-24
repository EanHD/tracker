"""Export command - Export entries to CSV or JSON"""

from datetime import datetime
from pathlib import Path

import click
from rich.panel import Panel

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.core.database import SessionLocal
from tracker.services.export_service import ExportService


@click.command()
@click.option(
    "--format",
    "export_format",
    type=click.Choice(["csv", "json"], case_sensitive=False),
    default="json",
    help="Export format",
    show_default=True
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path (default: tracker_export_YYYYMMDD.{format})"
)
@click.option(
    "--start-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Export entries from this date (YYYY-MM-DD)"
)
@click.option(
    "--end-date",
    type=click.DateTime(formats=["%Y-%m-%d"]),
    help="Export entries until this date (YYYY-MM-DD)"
)
@click.option(
    "--compact",
    is_flag=True,
    help="Compact JSON output (no pretty-printing)"
)
def export(export_format: str, output: str, start_date, end_date, compact: bool):
    """
    Export entries to CSV or JSON format
    
    Examples:
    
      # Export all entries to JSON
      tracker export
      
      # Export to CSV
      tracker export --format csv
      
      # Export to specific file
      tracker export -o my_data.json
      
      # Export date range
      tracker export --start-date 2025-10-01 --end-date 2025-10-31
      
      # Compact JSON (smaller file size)
      tracker export --format json --compact
    """
    db = SessionLocal()
    service = ExportService(db)
    
    try:
        console = get_console()
        # Parse dates
        start = start_date.date() if start_date else None
        end = end_date.date() if end_date else None
        
        # Get export stats
        stats = service.get_export_stats(1, start_date=start, end_date=end)  # TODO: Get actual user
        
        if stats["entry_count"] == 0:
            console.print("[yellow]No entries found to export.[/yellow]")
            return
        
        # Determine output path
        if output:
            output_path = Path(output)
        else:
            # Create human-readable filename
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Add date range if specified
            if start and end:
                date_range = f"{start.strftime('%Y-%m-%d')}_to_{end.strftime('%Y-%m-%d')}"
                output_path = Path(f"tracker_export_{date_range}.{export_format}")
            elif start:
                date_range = f"from_{start.strftime('%Y-%m-%d')}"
                output_path = Path(f"tracker_export_{date_range}.{export_format}")
            elif end:
                date_range = f"until_{end.strftime('%Y-%m-%d')}"
                output_path = Path(f"tracker_export_{date_range}.{export_format}")
            else:
                # All time export with today's date
                output_path = Path(f"tracker_export_all_{today}.{export_format}")
        
        # Show export info
        console.print(
            f"\n[bold blue]{icon('📤', 'Export')} Exporting Data[/bold blue]\n"
        )
        console.print(f"  Format: [cyan]{export_format.upper()}[/cyan]")
        console.print(f"  Entries: [cyan]{stats['entry_count']}[/cyan]")
        console.print(f"  Date range: [cyan]{stats['earliest_date']} to {stats['latest_date']}[/cyan]")
        console.print(f"  Output: [cyan]{output_path}[/cyan]")
        
        # Estimate file size
        size_key = f"estimated_{export_format}_size_kb"
        if size_key in stats:
            console.print(f"  Estimated size: [cyan]{stats[size_key]:.1f} KB[/cyan]")
        
        console.print()
        
        # Perform export
        with console.status("[cyan]Exporting...[/cyan]"):
            if export_format == "csv":
                content = service.export_to_csv(
                    1,  # TODO: Get actual user
                    filepath=output_path,
                    start_date=start,
                    end_date=end
                )
            else:  # json
                content = service.export_to_json(
                    1,  # TODO: Get actual user
                    filepath=output_path,
                    start_date=start,
                    end_date=end,
                    pretty=not compact
                )
        
        # Show success
        actual_size = len(content.encode('utf-8')) / 1024
        console.print(
            emphasize(
                f"[green]{icon('✅', 'Done')} Export complete![/green]",
                "export complete",
            )
        )
        console.print(f"  File: [cyan]{output_path.absolute()}[/cyan]")
        console.print(f"  Size: [cyan]{actual_size:.1f} KB[/cyan]\n")
        
        # Show sample for JSON
        if export_format == "json" and stats["entry_count"] > 0:
            console.print("[dim]Preview (first few lines):[/dim]")
            lines = content.split('\n')[:10]
            preview = '\n'.join(lines)
            console.print(Panel(preview, border_style="dim"))
        
    except Exception as e:
        get_console().print(
            emphasize(f"[red]{icon('❌', 'Error')} Error: {e}[/red]", "export error")
        )
        raise
    finally:
        db.close()
