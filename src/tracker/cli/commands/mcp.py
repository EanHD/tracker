"""
MCP server CLI command

Provides commands to run the MCP server for AI agent integration.
"""

import click

from tracker.cli.ui.console import emphasize, get_console, icon


@click.group(name="mcp")
def mcp():
    """MCP server management commands."""
    pass


@mcp.command()
@click.option(
    "--http",
    is_flag=True,
    help="Use HTTP transport instead of stdio (for remote access)",
)
@click.option(
    "--host",
    default="localhost",
    help="Host to bind to (HTTP mode only)",
    show_default=True,
)
@click.option(
    "--port",
    default=8001,
    type=int,
    help="Port to bind to (HTTP mode only)",
    show_default=True,
)
def serve(http: bool, host: str, port: int):
    """
    Start the MCP server for AI agent integration.
    
    By default, uses stdio transport for local Claude Desktop integration.
    Use --http flag for remote HTTP access.
    
    Examples:
    
      # For Claude Desktop (stdio)
      tracker mcp serve
      
      # For remote access (HTTP)
      tracker mcp serve --http --host 0.0.0.0 --port 8001
    """
    console = get_console()

    if http:
        console.print(f"[yellow]Starting MCP server on HTTP transport at {host}:{port}...[/]")
        console.print(
            emphasize(
                "[red]HTTP transport not yet implemented. Use stdio mode for now.[/]",
                "http transport unavailable",
            )
        )
        console.print("\n[dim]To use with Claude Desktop, run without --http flag:[/]")
        console.print("[dim]  tracker mcp serve[/]")
        return
    
    # Stdio mode
    console.print(
        emphasize(
            f"[green]{icon('🚀', 'Start')} Starting MCP server with stdio transport...[/]",
            "starting mcp server",
        )
    )
    console.print(
        emphasize(
            "[dim]Waiting for MCP client connection (e.g., Claude Desktop)...[/]",
            "waiting for client",
        )
    )
    console.print()
    console.print(f"[yellow]{icon('🛠️', 'Setup')} To configure Claude Desktop:[/]")
    console.print("[dim]1. Open Claude Desktop settings[/]")
    console.print("[dim]2. Add this configuration to mcpServers:[/]")
    console.print()
    console.print('[cyan]  "tracker": {[/]')
    console.print('[cyan]    "command": "python",[/]')
    console.print('[cyan]    "args": ["-m", "tracker.mcp.server"][/]')
    console.print('[cyan]  }[/]')
    console.print()
    
    # Run the MCP server
    import asyncio
    from tracker.mcp.server import main
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print(
            emphasize(
                f"\n[yellow]{icon('🛑', 'Stop')} MCP server stopped.[/]", "mcp server stopped"
            )
        )
    except Exception as e:
        console.print(
            emphasize(
                f"[red]{icon('❌', 'Error')} Error running MCP server: {e}[/]",
                "mcp server error",
            )
        )
        raise
