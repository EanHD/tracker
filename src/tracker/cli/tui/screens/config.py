"""Configuration screen"""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from tracker.config import settings


class ConfigScreen(Screen):
    """Screen for viewing configuration"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the configuration screen"""
        yield Header()
        yield Container(
            Static("[bold cyan]⚙️  Configuration[/bold cyan]\n[dim]Current settings[/dim]", id="config_title"),
            Static(id="config_content"),
            Static("\n[dim]To modify settings, use:[/dim]\n[cyan]tracker config set <key> <value>[/cyan]", id="config_help"),
            Button("⬅️  Back to Menu (Esc)", id="back_btn"),
            id="config_container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Load configuration when screen mounts"""
        self._load_config()
    
    def _load_config(self) -> None:
        """Load and display configuration"""
        content = f"""
[bold green]Current Configuration[/bold green]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[bold]AI Settings[/bold]
Provider:             {settings.ai_provider}
Model:                {settings.ai_model}
Temperature:          {settings.ai_temperature}
Max Tokens:           {settings.ai_max_tokens}

[bold]Database[/bold]
Path:                 {settings.get_database_path()}

[bold]API Server[/bold]
Host:                 {settings.api_host}
Port:                 {settings.api_port}
Debug Mode:           {settings.debug}

[bold]Security[/bold]
JWT Secret:           {'[SET]' if settings.jwt_secret_key else '[NOT SET]'}
API Key:              {'[SET]' if settings.get_ai_api_key() else '[NOT SET]'}
"""
        
        config_widget = self.query_one("#config_content", Static)
        config_widget.update(content)
    
    def action_cancel(self) -> None:
        """Return to main menu"""
        self.app.pop_screen()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back_btn":
            self.action_cancel()
