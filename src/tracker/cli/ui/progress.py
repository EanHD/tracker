"""Progress indicators and spinners"""

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class FeedbackProgress:
    """Progress indicator for feedback generation"""

    def __init__(self, message: str = "Generating AI feedback..."):
        self.message = message
        self.progress = None
        self.task_id = None

    def __enter__(self):
        """Start progress indicator"""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            console=console,
            transient=True,
        )
        self.progress.start()
        self.task_id = self.progress.add_task(self.message, total=None)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop progress indicator"""
        if self.progress:
            self.progress.stop()
        return False

    def update(self, message: str):
        """Update progress message"""
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, description=message)
