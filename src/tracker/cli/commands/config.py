"""Configuration command"""

import click
import shutil
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from rich.console import Console
from rich.prompt import Confirm, Prompt

from tracker.config import settings, get_env_file_path, get_config_dir

console = Console()


def write_env_file(config_dict: dict, env_path: Path) -> None:
    """Write configuration to .env file, replacing provider-specific sections"""
    
    # Read existing .env if it exists
    existing_lines = []
    if env_path.exists():
        with open(env_path, 'r') as f:
            existing_lines = f.readlines()
    
    # Filter out AI provider lines (we'll add new ones)
    ai_section_markers = {
        '# AI Provider Configuration',
        '# AI Configuration',
        '# Local AI',
        'AI_PROVIDER=',
        'ANTHROPIC_API_KEY=',
        'ANTHROPIC_MODEL=',
        'OPENAI_API_KEY=',
        'OPENAI_MODEL=',
        'OPENROUTER_API_KEY=',
        'OPENROUTER_MODEL=',
        'LOCAL_API_URL=',
        'LOCAL_MODEL=',
    }
    
    filtered_lines = []
    skip_until_blank = False
    
    for line in existing_lines:
        stripped = line.strip()
        
        # Check if this is an AI config line
        is_ai_line = any(marker in stripped for marker in ai_section_markers)
        
        if is_ai_line:
            skip_until_blank = True
            continue
        
        # Stop skipping after blank line following AI section
        if skip_until_blank and not stripped:
            skip_until_blank = False
            continue
        
        if not skip_until_blank:
            filtered_lines.append(line)
    
    # Write file with filtered content + new AI config
    with open(env_path, 'w') as f:
        # Write existing non-AI config
        if filtered_lines:
            f.writelines(filtered_lines)
            # Ensure separation
            if filtered_lines and not filtered_lines[-1].endswith('\n'):
                f.write('\n')
        
        # Write new AI configuration
        f.write(f"\n# AI Provider Configuration\n")
        f.write(f"AI_PROVIDER={config_dict['provider']}\n")
        
        if config_dict.get('api_key'):
            f.write(f"{config_dict['api_key_var']}={config_dict['api_key']}\n")
        
        if config_dict['provider'] == 'local':
            f.write(f"LOCAL_API_URL={config_dict.get('local_url', 'http://localhost:11434/v1')}\n")
            if config_dict.get('model'):
                f.write(f"LOCAL_MODEL={config_dict['model']}\n")
        elif config_dict.get('model'):
            if config_dict['provider'] == 'anthropic':
                f.write(f"ANTHROPIC_MODEL={config_dict['model']}\n")
            elif config_dict['provider'] == 'openai':
                f.write(f"OPENAI_MODEL={config_dict['model']}\n")
            elif config_dict['provider'] == 'openrouter':
                f.write(f"OPENROUTER_MODEL={config_dict['model']}\n")
        
        # Add encryption key if new
        if config_dict.get('encryption_key'):
            # Check if ENCRYPTION_KEY already exists in filtered lines
            has_encryption = any('ENCRYPTION_KEY=' in line for line in filtered_lines)
            if not has_encryption:
                f.write(f"\n# Encryption\n")
                f.write(f"ENCRYPTION_KEY={config_dict['encryption_key']}\n")
        
        f.write('\n')


@click.group()
def config():
    """Manage configuration"""
    pass


@config.command()
def setup():
    """Interactive configuration setup"""
    
    console.print("\n[bold blue]🔧 Tracker Configuration Setup[/bold blue]\n")
    
    # Get the correct .env path
    env_path = get_env_file_path()
    console.print(f"[dim]Configuration file: {env_path}[/dim]\n")
    
    # Check if .env exists and offer backup
    backup_path = None
    
    if env_path.exists():
        console.print("[yellow]⚠️  Configuration file already exists[/yellow]")
        
        if Confirm.ask("Create backup before continuing?", default=True):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = env_path.parent / f".env.backup.{timestamp}"
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
        if provider == "anthropic":
            model = "claude-3-5-sonnet-20241022"
        elif provider == "openai":
            model = "gpt-4"
        elif provider == "openrouter":
            model = "anthropic/claude-3.5-sonnet"
        else:  # local
            model = "llama3.2:3b"
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
    console.print(f"Model: [cyan]{model}[/cyan]")
    
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
    
    # Prepare configuration dictionary
    config_dict = {
        'provider': provider,
        'model': model,
        'api_key': api_key,
        'api_key_var': env_var if api_key else None,
    }
    
    if provider == 'local':
        config_dict['local_url'] = 'http://localhost:11434/v1'
    
    if not settings.encryption_key:
        config_dict['encryption_key'] = Fernet.generate_key().decode()
    
    # Write to .env
    try:
        write_env_file(config_dict, env_path)
        
        console.print("\n[bold green]✅ Configuration saved![/bold green]")
        console.print(f"[dim]File: {env_path}[/dim]\n")
        
        if backup_path:
            console.print(f"[dim]💾 Backup available at: {backup_path}[/dim]")
            console.print(f"[dim]   To restore: cp {backup_path} {env_path}[/dim]\n")
        
        console.print("[cyan]✨ Ready to use! Try: tracker new[/cyan]\n")
        
        # Reload settings
        console.print("[dim]Note: Restart any running processes to pick up new config[/dim]\n")
    
    except Exception as e:
        console.print(f"\n[red]❌ Error writing configuration: {e}[/red]")
        if backup_path and backup_path.exists():
            console.print(f"[yellow]Backup preserved at: {backup_path}[/yellow]")
        raise
    
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
