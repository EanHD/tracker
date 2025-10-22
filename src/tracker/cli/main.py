"""Main CLI entry point"""

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Tracker - Daily logging app with AI feedback"""
    pass


@cli.command()
def init():
    """Initialize database"""
    from tracker.core.database import Base, engine, init_db
    from tracker.core.models import User
    from tracker.config import settings

    console.print("[bold blue]Initializing Tracker...[/bold blue]")

    # Create database directory
    db_path = settings.get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Create tables
    init_db()
    console.print(f"✅ Database initialized at {db_path}")

    # Create default user
    from sqlalchemy.orm import Session
    with Session(engine) as session:
        existing_user = session.query(User).filter_by(username="default").first()
        if not existing_user:
            user = User(username="default", email=None)
            session.add(user)
            session.commit()
            console.print("✅ Default user created")
        else:
            console.print("ℹ️  Default user already exists")

    console.print("[bold green]🎉 Tracker initialized successfully![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Create your first entry: [cyan]tracker new[/cyan]")
    console.print("  2. View your entry: [cyan]tracker show today[/cyan]")


@cli.command()
def version():
    """Show version"""
    from tracker import __version__
    console.print(f"Tracker v{__version__}")


# Register commands
from tracker.cli.commands.achievements import achievements
from tracker.cli.commands.config import config
from tracker.cli.commands.edit import edit
from tracker.cli.commands.export import export
from tracker.cli.commands.list import list
from tracker.cli.commands.mcp import mcp
from tracker.cli.commands.new import new
from tracker.cli.commands.onboard import onboard
from tracker.cli.commands.retry import retry
from tracker.cli.commands.search import search
from tracker.cli.commands.server import server
from tracker.cli.commands.show import show
from tracker.cli.commands.stats import stats

cli.add_command(new)
cli.add_command(edit)
cli.add_command(show)
cli.add_command(list, name="list")
cli.add_command(search)
cli.add_command(export)
cli.add_command(stats)
cli.add_command(achievements)
cli.add_command(config)
cli.add_command(onboard)
cli.add_command(server)
cli.add_command(mcp)
cli.add_command(retry)


if __name__ == "__main__":
    cli()
