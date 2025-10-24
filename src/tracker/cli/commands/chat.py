"""Chat command for AI conversations"""

import click
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table

from tracker.cli.ui.console import get_console, icon, emphasize
from tracker.config import settings
from tracker.core.database import engine
from tracker.services.chat import ChatService
from sqlalchemy.orm import Session


@click.group()
def chat():
    """AI chat conversations"""
    pass


@chat.command()
@click.option("--entry-id", type=int, help="Link chat to a specific entry")
def new(entry_id):
    """Start a new chat conversation"""
    console = get_console()
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)  # Default user
        
        # Get or create chat
        if entry_id:
            try:
                chat_obj = chat_service.get_or_create_entry_chat(entry_id)
                console.print(f"\n[bold cyan]{icon('💬 ', '')}Chat for Entry #{entry_id}[/bold cyan]")
            except ValueError as e:
                console.print(f"\n[red]{icon('❌ ', '')}Error: {e}[/red]\n")
                return
        else:
            title = Prompt.ask("\n[cyan]Chat title[/cyan]", default="General Conversation")
            chat_obj = chat_service.create_chat(title=title)
            console.print(f"\n[bold cyan]{icon('💬 ', '')}New Chat: {title}[/bold cyan]")
        
        console.print(f"[dim]Chat ID: {chat_obj.id}[/dim]\n")
        
        # Start chat loop
        _chat_loop(console, chat_service, chat_obj.id)


@chat.command()
@click.argument("chat_id", type=int)
def open(chat_id):
    """Open an existing chat"""
    console = get_console()
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)
        
        chat_obj = chat_service.get_chat(chat_id)
        if not chat_obj:
            console.print(f"\n[red]{icon('❌ ', '')}Chat {chat_id} not found[/red]\n")
            return
        
        # Display chat header
        console.print(f"\n[bold cyan]{icon('💬 ', '')}{chat_obj.title}[/bold cyan]")
        if chat_obj.entry_id:
            console.print(f"[dim]Linked to Entry #{chat_obj.entry_id}[/dim]")
        console.print(f"[dim]Created: {chat_obj.created_at.strftime('%Y-%m-%d %H:%M')}[/dim]\n")
        
        # Display message history
        if chat_obj.messages:
            _display_messages(console, chat_obj.messages)
            console.print()
        
        # Continue conversation
        _chat_loop(console, chat_service, chat_id)


@chat.command()
@click.option("--standalone", is_flag=True, help="Show only standalone chats")
@click.option("--entry-linked", is_flag=True, help="Show only entry-linked chats")
def list(standalone, entry_linked):
    """List all chats"""
    console = get_console()
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)
        
        # Determine filter
        filter_value = None
        if standalone:
            filter_value = False
        elif entry_linked:
            filter_value = True
        
        chats = chat_service.list_chats(entry_linked=filter_value)
        
        if not chats:
            console.print(f"\n[yellow]{icon('📭 ', '')}No chats found[/yellow]\n")
            return
        
        # Display chats in a table
        table = Table(title=f"{icon('💬 ', '')}Your Chats")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Title", style="bold")
        table.add_column("Type", width=12)
        table.add_column("Messages", justify="right", width=10)
        table.add_column("Last Updated", width=18)
        
        for chat_obj in chats:
            chat_type = f"{icon('📝 ', '')}Entry #{chat_obj.entry_id}" if chat_obj.entry_id else f"{icon('💭 ', '')}Standalone"
            msg_count = len(chat_obj.messages) if hasattr(chat_obj, 'messages') else 0
            
            table.add_row(
                str(chat_obj.id),
                chat_obj.title,
                chat_type,
                str(msg_count),
                chat_obj.updated_at.strftime("%Y-%m-%d %H:%M")
            )
        
        console.print()
        console.print(table)
        console.print(f"\n[dim]Open a chat with: tracker chat open <ID>[/dim]\n")


@chat.command()
@click.argument("chat_id", type=int)
def delete(chat_id):
    """Delete a chat"""
    console = get_console()
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)
        
        chat_obj = chat_service.get_chat(chat_id)
        if not chat_obj:
            console.print(f"\n[red]{icon('❌ ', '')}Chat {chat_id} not found[/red]\n")
            return
        
        if Confirm.ask(f"Delete chat '{chat_obj.title}'?", default=False):
            if chat_service.delete_chat(chat_id):
                console.print(f"\n[green]{icon('✅ ', '')}Chat deleted[/green]\n")
            else:
                console.print(f"\n[red]{icon('❌ ', '')}Failed to delete chat[/red]\n")


@chat.command()
@click.argument("chat_id", type=int)
def rename(chat_id):
    """Rename a chat"""
    console = get_console()
    
    with Session(engine) as session:
        chat_service = ChatService(session, user_id=1)
        
        chat_obj = chat_service.get_chat(chat_id)
        if not chat_obj:
            console.print(f"\n[red]{icon('❌ ', '')}Chat {chat_id} not found[/red]\n")
            return
        
        console.print(f"\n[bold]Current title:[/bold] {chat_obj.title}")
        new_title = Prompt.ask("[cyan]New title[/cyan]")
        
        if new_title and chat_service.update_chat_title(chat_id, new_title):
            console.print(f"\n[green]{icon('✅ ', '')}Chat renamed[/green]\n")
        else:
            console.print(f"\n[red]{icon('❌ ', '')}Failed to rename chat[/red]\n")


def _display_messages(console: Console, messages: list):
    """Display chat messages"""
    for msg in messages:
        if msg.role == "user":
            console.print(Panel(
                msg.content,
                title=f"{icon('👤 ', '')}You",
                title_align="left",
                border_style="blue",
                padding=(0, 1)
            ))
        elif msg.role == "assistant":
            from rich.markdown import Markdown
            md = Markdown(msg.content)
            console.print(Panel(
                md,
                title=f"{icon('💭 ', '')}Tracker",
                title_align="left",
                border_style="green",
                padding=(0, 1)
            ))
        console.print()


def _chat_loop(console: Console, chat_service: ChatService, chat_id: int):
    """Interactive chat loop"""
    console.print("[dim]Type your message (or 'exit' to quit, 'clear' to clear screen)[/dim]\n")
    
    while True:
        try:
            user_input = Prompt.ask(f"{icon('💬 ', '')}You")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                console.print(f"\n[yellow]{icon('👋 ', '')}Chat saved. Goodbye![/yellow]\n")
                break
            
            if user_input.lower() == 'clear':
                console.clear()
                continue
            
            if not user_input.strip():
                continue
            
            # Send message and get response while keeping history visible
            console.print()
            
            try:
                with console.status(f"[dim]{icon('⏳ ', '')}Thinking...[/dim]", spinner="dots"):
                    response = chat_service.send_message(chat_id, user_input)
                
                from rich.markdown import Markdown
                md = Markdown(response)
                
                console.print()
                console.print(Panel(
                    md,
                    title=f"{icon('💭 ', '')}Tracker",
                    title_align="left",
                    border_style="green",
                    padding=(0, 1)
                ))
                console.print()
                
            except Exception as e:
                console.print(f"\n[red]{icon('❌ ', '')}Error: {e}[/red]\n")
                console.print("[dim]Check that your AI provider is configured and running[/dim]\n")
                if Confirm.ask("Try again?", default=True):
                    continue
                else:
                    break
        
        except KeyboardInterrupt:
            console.print(f"\n\n[yellow]{icon('👋 ', '')}Chat saved. Goodbye![/yellow]\n")
            break
        except EOFError:
            break
