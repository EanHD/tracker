"""Configuration command"""

import click
import shutil
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from rich.console import Console
from rich.prompt import Confirm, Prompt

from tracker.config import settings

console = Console()


@click.group()
def config():
    """Manage configuration"""
    pass


@config.command()
def setup():
    """Interactive configuration setup"""
    
    console.print("\n[bold blue]🔧 Tracker Configuration Setup[/bold blue]\n")
    
    # Check if .env exists and offer backup
    env_path = Path(".env")
    backup_path = None
    
    if env_path.exists():
        console.print("[yellow]⚠️  .env file already exists[/yellow]")
        
        if Confirm.ask("Create backup before continuing?", default=True):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = Path(f".env.backup.{timestamp}")
            shutil.copy2(env_path, backup_path)
            console.print(f"[green]✅ Backup created: {backup_path}[/green]\n")
    
    # AI Provider
    console.print("[bold cyan]AI Provider Configuration[/bold cyan]")
    
    provider = Prompt.ask(
        "Choose AI provider",
        choices=["anthropic", "openai", "openrouter", "local"],
        default="local"
    )
    
    console.print(f"\nSelected provider: [green]{provider}[/green]")
    
    # API Key
    if provider == "anthropic":
        console.print("\n[dim]Get your API key from: https://console.anthropic.com/[/dim]")
        api_key = Prompt.ask("Anthropic API key", password=True)
        env_var = "ANTHROPIC_API_KEY"
    elif provider == "openai":
        console.print("\n[dim]Get your API key from: https://platform.openai.com/api-keys[/dim]")
        api_key = Prompt.ask("OpenAI API key", password=True)
        env_var = "OPENAI_API_KEY"
    elif provider == "openrouter":
        console.print("\n[dim]Get your API key from: https://openrouter.ai/keys[/dim]")
        api_key = Prompt.ask("OpenRouter API key", password=True)
        env_var = "OPENROUTER_API_KEY"
    else:  # local
        console.print("\n[dim]Using local AI (Ollama). No API key needed.[/dim]")
        console.print("[dim]Make sure Ollama is running: http://localhost:11434[/dim]")
        api_key = None
        env_var = None
    
    # Model configuration
    use_default_model = Confirm.ask("Use default model?", default=True)
    
    if use_default_model:
        model = None
        if provider == "anthropic":
            model_name = "claude-3-5-sonnet-20241022"
        elif provider == "openai":
            model_name = "gpt-4"
        elif provider == "openrouter":
            model_name = "anthropic/claude-3.5-sonnet"
        else:  # local
            model_name = "llama3.2:3b"
    else:
        if provider == "anthropic":
            console.print("\n[dim]Available models: claude-3-opus, claude-3-sonnet, claude-3-haiku[/dim]")
            model = Prompt.ask("Model name", default="claude-3-5-sonnet-20241022")
        elif provider == "openai":
            console.print("\n[dim]Available models: gpt-4, gpt-4-turbo, gpt-3.5-turbo[/dim]")
            model = Prompt.ask("Model name", default="gpt-4")
        elif provider == "openrouter":
            console.print("\n[dim]Available models: anthropic/claude-3.5-sonnet, openai/gpt-4, etc.[/dim]")
            model = Prompt.ask("Model name", default="anthropic/claude-3.5-sonnet")
        else:  # local
            console.print("\n[dim]Available models depend on your Ollama installation[/dim]")
            console.print("[dim]Common: llama3.2:3b, llama3.2:1b, gemma2:2b[/dim]")
            model = Prompt.ask("Model name", default="llama3.2:3b")
        model_name = model
    
    # Encryption key
    console.print("\n[bold cyan]Encryption Configuration[/bold cyan]")
    
    if settings.encryption_key:
        console.print("✅ Encryption key already configured")
    else:
        console.print("Generating new encryption key...")
        encryption_key = Fernet.generate_key().decode()
    
    # Show configuration summary with confirmation
    console.print("\n[bold green]✅ Configuration Summary[/bold green]\n")
    console.print(f"AI Provider: [cyan]{provider}[/cyan]")
    console.print(f"Model: [cyan]{model_name}[/cyan]")
    
    if api_key:
        # Show first/last few chars of API key for verification
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        console.print(f"API Key: [dim]{masked_key}[/dim]")
    else:
        console.print(f"API Key: [dim]Not required (local)[/dim]")
    
    if not settings.encryption_key:
        console.print(f"New Encryption Key: [dim]Will be generated[/dim]")
    
    # Allow user to cancel before writing
    console.print()
    if not Confirm.ask("[bold]Does this look correct?[/bold]", default=True):
        console.print("\n[yellow]❌ Configuration cancelled. No changes made.[/yellow]")
        if backup_path and backup_path.exists():
            backup_path.unlink()  # Remove backup if we're not making changes
            console.print(f"[dim]Backup {backup_path} removed[/dim]")
        console.print("\n[dim]Run 'tracker config setup' again to restart.[/dim]\n")
        return
    
    # Instructions
    console.print("\n[bold yellow]📝 Next Steps:[/bold yellow]\n")
    console.print("Add these to your .env file:")
    console.print()
    console.print(f"[cyan]AI_PROVIDER={provider}[/cyan]")
    
    if api_key:
        console.print(f"[cyan]{env_var}={api_key}[/cyan]")
    
    if provider == "local":
        console.print(f"[cyan]LOCAL_API_URL=http://localhost:11434/v1[/cyan]")
        console.print(f"[cyan]LOCAL_MODEL={model or model_name}[/cyan]")
    elif model:
        if provider == "anthropic":
            console.print(f"[cyan]ANTHROPIC_MODEL={model}[/cyan]")
        elif provider == "openai":
            console.print(f"[cyan]OPENAI_MODEL={model}[/cyan]")
        elif provider == "openrouter":
            console.print(f"[cyan]OPENROUTER_MODEL={model}[/cyan]")
    
    if not settings.encryption_key:
        console.print(f"[cyan]ENCRYPTION_KEY={encryption_key}[/cyan]")
    
    console.print()
    console.print(f"[dim]Or run: echo 'AI_PROVIDER={provider}' >> .env[/dim]")
    console.print()
    
    # Offer to write to .env
    console.print()
    if not Confirm.ask("💾 Write configuration to .env file?", default=True):
        console.print("\n[yellow]❌ Configuration not saved.[/yellow]")
        if backup_path and backup_path.exists():
            backup_path.unlink()
            console.print(f"[dim]Backup {backup_path} removed[/dim]")
        console.print("\n[dim]You can copy the configuration above manually, or run 'tracker config setup' again.[/dim]\n")
        return
    
    # Write to .env
    try:
        with open(".env", "a") as f:
            f.write(f"\n# AI Configuration (added {datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write(f"AI_PROVIDER={provider}\n")
            
            if api_key:
                f.write(f"{env_var}={api_key}\n")
            
            if provider == "local":
                f.write(f"LOCAL_API_URL=http://localhost:11434/v1\n")
                f.write(f"LOCAL_MODEL={model or model_name}\n")
            elif model:
                if provider == "anthropic":
                    f.write(f"ANTHROPIC_MODEL={model}\n")
                elif provider == "openai":
                    f.write(f"OPENAI_MODEL={model}\n")
                elif provider == "openrouter":
                    f.write(f"OPENROUTER_MODEL={model}\n")
            
            if not settings.encryption_key:
                f.write(f"ENCRYPTION_KEY={encryption_key}\n")
        
        console.print("\n[bold green]✅ Configuration saved to .env[/bold green]")
        
        if backup_path:
            console.print(f"[dim]💾 Backup available at: {backup_path}[/dim]")
            console.print(f"[dim]   To restore: mv {backup_path} .env[/dim]")
        
        console.print("\n[cyan]✨ Ready to use! Try: tracker new[/cyan]\n")
    
    except Exception as e:
        console.print(f"\n[red]❌ Failed to write .env: {e}[/red]")
        
        # Offer to restore backup
        if backup_path and backup_path.exists():
            if Confirm.ask("Restore from backup?", default=True):
                shutil.copy2(backup_path, env_path)
                console.print(f"[green]✅ Restored from {backup_path}[/green]")
            else:
                console.print(f"[yellow]Backup preserved at: {backup_path}[/yellow]")
        
        console.print("[yellow]Please add the configuration manually or try again[/yellow]\n")


@config.command()
def show():
    """Show current configuration"""
    
    console.print("\n[bold blue]Current Configuration[/bold blue]\n")
    
    # Database
    console.print("[bold cyan]Database[/bold cyan]")
    console.print(f"  URL: {settings.database_url}")
    console.print(f"  Path: {settings.get_database_path()}")
    console.print(f"  Encryption: {'✅ Enabled' if settings.encryption_key else '❌ Not configured'}")
    
    # AI
    console.print("\n[bold cyan]AI Provider[/bold cyan]")
    console.print(f"  Provider: {settings.ai_provider}")
    
    # Show provider-specific model
    model_display = settings.ai_model or "default"
    if settings.ai_provider == "local":
        model_display = settings.local_model or model_display
    elif settings.ai_provider == "anthropic":
        model_display = settings.anthropic_model or model_display
    elif settings.ai_provider == "openai":
        model_display = settings.openai_model or model_display
    elif settings.ai_provider == "openrouter":
        model_display = settings.openrouter_model or model_display
    
    console.print(f"  Model: {model_display}")
    
    has_key = bool(settings.get_ai_api_key())
    console.print(f"  API Key: {'✅ Configured' if has_key else '❌ Not configured'}")
    
    if not has_key:
        console.print("\n[yellow]⚠️  No API key configured. Run: tracker config setup[/yellow]")
    
    # API Server
    console.print("\n[bold cyan]API Server[/bold cyan]")
    console.print(f"  Host: {settings.api_host}")
    console.print(f"  Port: {settings.api_port}")
    
    console.print()


@config.command()
@click.option("--scopes", default="entries:read,entries:write,feedback:generate", help="Token scopes")
def generate_token(scopes):
    """Generate API token for external access"""
    
    console.print("\n[bold blue]🔑 Generate API Token[/bold blue]\n")
    
    # This is a placeholder - actual JWT generation will be in Phase 5
    console.print("[yellow]API token generation will be available in Phase 5[/yellow]")
    console.print(f"Requested scopes: {scopes}")
    console.print()
