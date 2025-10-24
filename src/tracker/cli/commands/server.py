"""Server command - Run API server"""

import click
import uvicorn

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.config import settings


@click.command()
@click.option("--host", default=None, help=f"Host to bind (default: {settings.api_host})")
@click.option("--port", default=None, type=int, help=f"Port to bind (default: {settings.api_port})")
@click.option("--reload", is_flag=True, help="Enable auto-reload for development")
def server(host, port, reload):
    """Start the API server"""
    
    console = get_console()
    host = host or settings.api_host
    port = port or settings.api_port
    
    console.print(
        f"\n[bold green]{icon('🚀', 'Start')} Starting Tracker API Server[/bold green]\n"
    )
    console.print(f"Host: [cyan]{host}[/cyan]")
    console.print(f"Port: [cyan]{port}[/cyan]")
    console.print(f"API Docs: [cyan]http://{host}:{port}/docs[/cyan]")
    console.print(f"OpenAPI JSON: [cyan]http://{host}:{port}/openapi.json[/cyan]")
    console.print()
    
    if reload:
        console.print(
            emphasize(
                f"[yellow]{icon('⚠️', 'Warning')} Auto-reload enabled (development mode)[/yellow]\n",
                "auto reload enabled",
            )
        )
    
    try:
        uvicorn.run(
            "tracker.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        console.print(
            emphasize(
                f"\n[yellow]{icon('🛑', 'Stop')} Server stopped by user[/yellow]\n",
                "server stopped",
            )
        )
    except Exception as e:
        console.print(
            emphasize(
                f"\n[red]{icon('❌', 'Error')} Server error: {e}[/red]\n",
                "server error",
            )
        )
