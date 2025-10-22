"""Server command - Run API server"""

import click
import uvicorn
from rich.console import Console

from tracker.config import settings

console = Console()


@click.command()
@click.option("--host", default=None, help=f"Host to bind (default: {settings.api_host})")
@click.option("--port", default=None, type=int, help=f"Port to bind (default: {settings.api_port})")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def server(host, port, reload):
    """Start the API server"""
    
    host = host or settings.api_host
    port = port or settings.api_port
    
    console.print(f"\n[bold green]🚀 Starting Tracker API Server[/bold green]\n")
    console.print(f"Host: [cyan]{host}[/cyan]")
    console.print(f"Port: [cyan]{port}[/cyan]")
    console.print(f"API Docs: [cyan]http://{host}:{port}/docs[/cyan]")
    console.print(f"OpenAPI JSON: [cyan]http://{host}:{port}/openapi.json[/cyan]")
    console.print()
    
    if reload:
        console.print("[yellow]⚠️  Auto-reload enabled (development mode)[/yellow]\n")
    
    try:
        uvicorn.run(
            "tracker.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped by user[/yellow]\n")
    except Exception as e:
        console.print(f"\n[red]❌ Server error: {e}[/red]\n")
