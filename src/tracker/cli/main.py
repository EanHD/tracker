"""Main CLI entry point"""

import click

from tracker.cli.ui.console import configure_accessibility, get_console, emphasize, icon


@click.group(invoke_without_command=True)
@click.option("--plain", is_flag=True, help="Simplify output for screen readers (disables color and emoji).")
@click.option("--no-color", is_flag=True, help="Disable color output.")
@click.option("--no-emoji", is_flag=True, help="Disable emoji characters.")
@click.pass_context
@click.version_option(version="0.1.0")
def cli(ctx, plain, no_color, no_emoji):
    """Tracker - Daily logging app with feedback
    
    Running 'tracker' without arguments launches the interactive TUI.
    Use 'tracker --help' to see all available commands.
    """
    configure_accessibility(plain=plain, no_color=no_color, no_emoji=no_emoji)

    if ctx.invoked_subcommand is None:
        # No command provided, launch TUI
        from tracker.cli.commands.tui import tui
        ctx.invoke(tui)


@cli.command()
def init():
    """Initialize database"""
    console = get_console()
    from tracker.core.database import Base, engine, init_db
    from tracker.core.models import User
    from tracker.config import settings

    console.print(
        f"[bold blue]{icon('🚀', 'Init')} Initializing Tracker...[/bold blue]"
    )

    # Create database directory
    db_path = settings.get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create tables
    init_db()
    console.print(
        emphasize(
            f"{icon('✅', 'Ready')} Database initialized at {db_path}",
            "database initialized",
        )
    )

    # Create default user
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        existing_user = session.query(User).filter_by(username="default").first()
        if not existing_user:
            user = User(username="default", email=None)
            session.add(user)
            session.commit()
            console.print(
                emphasize(
                    f"{icon('✅', 'Ready')} Default user created",
                    "default user created",
                )
            )
        else:
            console.print(
                emphasize(
                    f"{icon('ℹ️', 'Info')}  Default user already exists",
                    "default user exists",
                )
            )

    console.print(
        f"[bold green]{icon('🎉', 'Ready')} Tracker initialized successfully![/bold green]"
    )
    console.print("\nNext steps:")
    console.print("  1. Create your first entry: [cyan]tracker new[/cyan]")
    console.print("  2. View your entry: [cyan]tracker show today[/cyan]")


@cli.command()
def version():
    """Show version"""
    console = get_console()
    from tracker import __version__
    console.print(f"Tracker v{__version__}")


# Register commands
from tracker.cli.commands.achievements import achievements
from tracker.cli.commands.chat import chat
from tracker.cli.commands.config import config
from tracker.cli.commands.edit import edit
from tracker.cli.commands.export import export
from tracker.cli.commands.list import list
from tracker.cli.commands.mcp import mcp
from tracker.cli.commands.new import new
from tracker.cli.commands.onboard import onboard
from tracker.cli.commands.profile import profile
from tracker.cli.commands.retry import retry
from tracker.cli.commands.search import search
from tracker.cli.commands.server import server
from tracker.cli.commands.show import show
from tracker.cli.commands.stats import stats
from tracker.cli.commands.tui import tui

cli.add_command(new)
cli.add_command(edit)
cli.add_command(show)
cli.add_command(list, name="list")
cli.add_command(search)
cli.add_command(export)
cli.add_command(stats)
cli.add_command(achievements)
cli.add_command(chat)
cli.add_command(config)
cli.add_command(onboard)
cli.add_command(server)
cli.add_command(mcp)
cli.add_command(retry)
cli.add_command(profile)
cli.add_command(tui)


if __name__ == "__main__":
    cli()
