"""Profile screen"""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from tracker.core.database import SessionLocal
from tracker.core.models import User


class ProfileScreen(Screen):
    """Screen for viewing user profile"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the profile screen"""
        yield Header()
        yield Container(
            Static("[bold cyan]👤 User Profile[/bold cyan]\n[dim]Your account information[/dim]", id="profile_title"),
            Static(id="profile_content"),
            Button("⬅️  Back to Menu (Esc)", id="back_btn"),
            id="profile_container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Load profile when screen mounts"""
        self._load_profile()
    
    def _load_profile(self) -> None:
        """Load and display profile"""
        try:
            with SessionLocal() as db:
                user = db.query(User).filter_by(id=1).first()
                
                if user:
                    content = f"""
[bold green]Profile Information[/bold green]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Username:             {user.username}
Email:                {user.email or 'Not set'}
Created:              {user.created_at.strftime('%Y-%m-%d')}

[dim]To modify your profile, use the CLI commands:[/dim]
[cyan]tracker profile update --username newname[/cyan]
"""
                else:
                    content = "[yellow]No user profile found[/yellow]"
                
                profile_widget = self.query_one("#profile_content", Static)
                profile_widget.update(content)
                
        except Exception as e:
            self.notify(f"Error loading profile: {str(e)}", severity="error")
    
    def action_cancel(self) -> None:
        """Return to main menu"""
        self.app.pop_screen()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back_btn":
            self.action_cancel()
