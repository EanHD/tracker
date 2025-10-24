"""Configuration command"""

import click
import shutil
from datetime import datetime
from pathlib import Path
from cryptography.fernet import Fernet
from rich.prompt import Confirm, Prompt

from tracker.cli.ui.console import emphasize, get_console, icon
from tracker.config import settings, get_env_file_path, get_config_dir


def save_provider_backup(env_path: Path, provider: str, config_dict: dict) -> None:
    """Save provider-specific backup of .env file"""
    backup_path = env_path.parent / f".env.backup.{provider}"
    
    # Build provider-specific config
    lines = []
    lines.append(f"# Tracker Configuration - {provider.upper()}\n")
    lines.append(f"# Last saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append("\n")
    
    # AI Provider config
    lines.append("# AI Provider Configuration\n")
    lines.append(f"AI_PROVIDER={provider}\n")
    
    if config_dict.get('api_key'):
        lines.append(f"{config_dict['api_key_var']}={config_dict['api_key']}\n")
    
    if provider == 'anthropic':
        lines.append(f"ANTHROPIC_MODEL={config_dict['model']}\n")
    elif provider == 'openai':
        lines.append(f"OPENAI_MODEL={config_dict['model']}\n")
    elif provider == 'openrouter':
        lines.append(f"OPENROUTER_MODEL={config_dict['model']}\n")
    elif provider == 'local':
        lines.append(f"LOCAL_API_URL={config_dict.get('local_url', 'http://localhost:11434/v1')}\n")
        lines.append(f"LOCAL_MODEL={config_dict['model']}\n")
    
    lines.append("\n")
    
    # Encryption key (from current .env)
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith('ENCRYPTION_KEY='):
                    lines.append(line)
                    break
    elif config_dict.get('encryption_key'):
        lines.append(f"ENCRYPTION_KEY={config_dict['encryption_key']}\n")
    
    # Write backup
    with open(backup_path, 'w') as f:
        f.writelines(lines)
    
    get_console().print(
        emphasize(
            f"[dim]{icon('💾', 'Saved')} Saved {provider} config to {backup_path.name}[/dim]",
            "configuration backup saved",
        )
    )


def load_provider_backup(env_path: Path, provider: str) -> dict:
    """Load provider-specific backup and return config dict"""
    backup_path = env_path.parent / f".env.backup.{provider}"
    
    if not backup_path.exists():
        return None
    
    config = {}
    with open(backup_path, 'r') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                if key == 'ANTHROPIC_API_KEY':
                    config['api_key'] = value
                    config['api_key_var'] = 'ANTHROPIC_API_KEY'
                elif key == 'OPENAI_API_KEY':
                    config['api_key'] = value
                    config['api_key_var'] = 'OPENAI_API_KEY'
                elif key == 'OPENROUTER_API_KEY':
                    config['api_key'] = value
                    config['api_key_var'] = 'OPENROUTER_API_KEY'
                elif key == 'ANTHROPIC_MODEL':
                    config['model'] = value
                elif key == 'OPENAI_MODEL':
                    config['model'] = value
                elif key == 'OPENROUTER_MODEL':
                    config['model'] = value
                elif key == 'LOCAL_MODEL':
                    config['model'] = value
                elif key == 'LOCAL_API_URL':
                    config['local_url'] = value
    
    return config if config else None


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
    
    console = get_console()
    console.print(
        f"\n[bold blue]{icon('🔧', 'Setup')} Tracker Configuration Setup[/bold blue]\n"
    )
    
    # Get the correct .env path
    env_path = get_env_file_path()
    console.print(f"[dim]Configuration file: {env_path}[/dim]\n")
    
    # AI Provider
    console.print(
        f"[bold cyan]{icon('🤖', 'AI')} AI Provider Configuration[/bold cyan]"
    )
    
    # Check for existing backups
    backup_dir = env_path.parent
    available_backups = []
    for provider in ["anthropic", "openai", "openrouter", "local"]:
        backup_path = backup_dir / f".env.backup.{provider}"
        if backup_path.exists():
            available_backups.append(provider)
    
    if available_backups:
        console.print(f"[dim]Found saved configs for: {', '.join(available_backups)}[/dim]\n")
    
    provider = Prompt.ask(
        "Choose AI provider",
        choices=["anthropic", "openai", "openrouter", "local"],
        default="local"
    )
    
    console.print(f"\nSelected provider: [green]{provider}[/green]")
    
    # Try to load existing backup for this provider
    saved_config = load_provider_backup(env_path, provider)
    
    if saved_config:
        console.print(
            emphasize(
                f"\n[yellow]{icon('📋', 'Saved config')} Found saved {provider} configuration[/yellow]",
                "saved configuration detected",
            )
        )
        if saved_config.get('model'):
            console.print(f"[dim]Last used model: {saved_config['model']}[/dim]")
        
        use_saved = Confirm.ask("Use saved configuration?", default=True)
        
        if use_saved:
            # Use saved config but allow model change
            api_key = saved_config.get('api_key')
            env_var = saved_config.get('api_key_var')
            
            if saved_config.get('model'):
                use_saved_model = Confirm.ask(
                    f"Use saved model ({saved_config['model']})?",
                    default=True
                )
                
                if use_saved_model:
                    model = saved_config['model']
                else:
                    model = Prompt.ask("Enter model name", default=saved_config['model'])
            else:
                model = None
            
            # Skip to encryption step
            console.print(
                emphasize(
                    f"\n[green]{icon('✅', 'Ready')} Using saved configuration[/green]",
                    "using saved configuration",
                )
            )
        else:
            saved_config = None  # Fall through to new config
    
    if not saved_config:
        # New configuration
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
                model = "gpt-4o-mini"
            elif provider == "openrouter":
                model = "anthropic/claude-3.5-sonnet"
            else:  # local
                model = "llama3.2:3b"
        else:
            if provider == "anthropic":
                console.print("\n[dim]Available models: claude-3-opus, claude-3-sonnet, claude-3-haiku[/dim]")
                model = Prompt.ask("Model name", default="claude-3-5-sonnet-20241022")
            elif provider == "openai":
                console.print("\n[dim]Recommended: gpt-4o-mini (best for creative tasks)[/dim]")
                console.print("[dim]Also available: gpt-4o, gpt-4-turbo[/dim]")
                console.print("[yellow]Note: GPT-5 models require Responses API (not yet supported)[/yellow]")
                model = Prompt.ask("Model name", default="gpt-4o-mini")
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
        console.print(
            emphasize(
                f"{icon('✅', 'Enabled')} Encryption key already configured",
                "encryption ready",
            )
        )
    else:
        console.print("Generating new encryption key...")
        encryption_key = Fernet.generate_key().decode()
    
    # Show configuration summary with confirmation
    console.print(
        f"\n[bold green]{icon('✅', 'Summary')} Configuration Summary[/bold green]\n"
    )
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
        console.print(
            emphasize(
                f"\n[yellow]{icon('❌', 'Cancelled')} Configuration cancelled. No changes made.[/yellow]\n",
                "configuration cancelled",
            )
        )
        return
    
    # Prepare configuration dictionary
    config_dict = {
        'provider': provider,
        'model': model,
        'api_key': api_key,
        'api_key_var': env_var if api_key else None,
    }
    
    if provider == 'local':
        config_dict['local_url'] = saved_config.get('local_url') if saved_config else 'http://localhost:11434/v1'
    
    if not settings.encryption_key:
        config_dict['encryption_key'] = Fernet.generate_key().decode()
    
    # Save provider-specific backup
    save_provider_backup(env_path, provider, config_dict)
    
    # Write to .env
    try:
        write_env_file(config_dict, env_path)
        
        console.print(
            emphasize(
                f"\n[bold green]{icon('✅', 'Saved')} Configuration saved![/bold green]",
                "configuration saved",
            )
        )
        console.print(f"[dim]Active config: {env_path}[/dim]")
        console.print(f"[dim]Backup: .env.backup.{provider}[/dim]\n")
        
        console.print(f"[cyan]{icon('✨', 'Ready')} Ready to use! Try: tracker new[/cyan]\n")
        
        # Show quick switch tip
        console.print(
            f"[dim]{icon('💡', 'Tip')} Run 'tracker config setup' again to quickly switch providers[/dim]\n"
        )
        
        # Reload settings
        console.print("[dim]Note: Restart any running processes to pick up new config[/dim]\n")
    
    except Exception as e:
        console.print(
            emphasize(
                f"\n[red]{icon('❌', 'Error')} Error writing configuration: {e}[/red]",
                "configuration write error",
            )
        )
        if backup_path and backup_path.exists():
            console.print(f"[yellow]Backup preserved at: {backup_path}[/yellow]")
        raise
    
    except Exception as e:
        console.print(
            emphasize(
                f"\n[red]{icon('❌', 'Error')} Failed to write .env: {e}[/red]",
                "env write error",
            )
        )
        
        # Offer to restore backup
        if backup_path and backup_path.exists():
            if Confirm.ask("Restore from backup?", default=True):
                shutil.copy2(backup_path, env_path)
                console.print(
                    emphasize(
                        f"[green]{icon('✅', 'Restored')} Restored from {backup_path}[/green]",
                        "configuration restored from backup",
                    )
                )
            else:
                console.print(f"[yellow]Backup preserved at: {backup_path}[/yellow]")
        
        console.print("[yellow]Please add the configuration manually or try again[/yellow]\n")


@config.command()
def show():
    """Show current configuration"""
    
    console = get_console()
    console.print(f"\n[bold blue]{icon('🛠️', 'Config')} Current Configuration[/bold blue]\n")
    
    # Database
    console.print("[bold cyan]Database[/bold cyan]")
    console.print(f"  URL: {settings.database_url}")
    console.print(f"  Path: {settings.get_database_path()}")
    encryption_icon = icon('✅', '') if settings.encryption_key else icon('❌', '')
    encryption_label = "Enabled" if settings.encryption_key else "Not configured"
    console.print(f"  Encryption: {(encryption_icon + ' ') if encryption_icon else ''}{encryption_label}")
    
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
    api_key_icon = icon('✅', '') if has_key else icon('❌', '')
    api_key_label = "Configured" if has_key else "Not configured"
    console.print(f"  API Key: {(api_key_icon + ' ') if api_key_icon else ''}{api_key_label}")
    
    if not has_key:
        console.print(
            emphasize(
                f"\n[yellow]{icon('⚠️', 'Warning')} No API key configured. Run: tracker config setup[/yellow]",
                "api key missing",
            )
        )
    
    # API Server
    console.print("\n[bold cyan]API Server[/bold cyan]")
    console.print(f"  Host: {settings.api_host}")
    console.print(f"  Port: {settings.api_port}")
    
    console.print()


@config.command()
@click.option("--scopes", default="entries:read,entries:write,feedback:generate", help="Token scopes")
def generate_token(scopes):
    """Generate API token for external access"""
    
    console.print(
        f"\n[bold blue]{icon('🔑', 'Token')} Generate API Token[/bold blue]\n"
    )
    
    # This is a placeholder - actual JWT generation will be in Phase 5
    console.print("[yellow]API token generation will be available in Phase 5[/yellow]")
    console.print(f"Requested scopes: {scopes}")
    console.print()
