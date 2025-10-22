"""Achievements screen"""

from textual.app import ComposeResult
from textual.containers import Container
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual.binding import Binding

from tracker.core.database import SessionLocal
from tracker.services.gamification_service import GamificationService


class AchievementsScreen(Screen):
    """Screen for viewing achievements"""
    
    BINDINGS = [
        Binding("escape", "cancel", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Compose the achievements screen"""
        yield Header()
        yield Container(
            Static("[bold cyan]🏆 Achievements[/bold cyan]\n[dim]Your tracking milestones[/dim]", id="achievements_title"),
            Static(id="achievements_content"),
            Button("⬅️  Back to Menu (Esc)", id="back_btn"),
            id="achievements_container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Load achievements when screen mounts"""
        self._load_achievements()
    
    def _load_achievements(self) -> None:
        """Load and display achievements"""
        try:
            with SessionLocal() as db:
                service = GamificationService(db)
                achievements = service.get_achievements(user_id=1)
                
                content = "[bold green]Your Achievements[/bold green]\n"
                content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                
                unlocked = [a for a in achievements if a.is_unlocked]
                locked = [a for a in achievements if not a.is_unlocked]
                
                if unlocked:
                    content += "[bold]✅ Unlocked:[/bold]\n"
                    for achievement in unlocked:
                        content += f"{achievement.icon} [green]{achievement.name}[/green]\n"
                        content += f"   {achievement.description}\n\n"
                
                if locked:
                    content += "\n[bold]🔒 Locked:[/bold]\n"
                    for achievement in locked:
                        content += f"⬜ [dim]{achievement.name}[/dim]\n"
                        content += f"   {achievement.description}\n\n"
                
                stats = service.get_user_stats(user_id=1)
                content += f"\n[bold cyan]📊 Your Stats[/bold cyan]\n"
                content += f"Current Streak: {stats.current_streak} days\n"
                content += f"Longest Streak: {stats.longest_streak} days\n"
                content += f"Total Points: {stats.total_points}\n"
                
                achievements_widget = self.query_one("#achievements_content", Static)
                achievements_widget.update(content)
                
        except Exception as e:
            self.notify(f"Error loading achievements: {str(e)}", severity="error")
    
    def action_cancel(self) -> None:
        """Return to main menu"""
        self.app.pop_screen()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "back_btn":
            self.action_cancel()
