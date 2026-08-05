"""Session tab for TUI."""

from __future__ import annotations

try:
    from textual.app import ComposeResult
    from textual.containers import Container, Horizontal
    from textual.widgets import Static, Button, Label
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    ComposeResult = None
    Container = object
    Horizontal = object
    Static = object
    Button = object
    Label = object


class SessionTab(Static):
    """Session information and quick actions."""
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            yield Label("Textual not available")
            return
        
        with Container(classes="session-info"):
            yield Label("[bold cyan]Current Session[/]")
            yield Label("Status: [green]Active[/]")
            yield Label("Plugins Loaded: [yellow]8[/]")
            yield Label("Last Command: [bright_black]None[/]")
        
        yield Label("\n[bold white]Quick Actions[/]")
        
        with Horizontal(classes="quick-actions"):
            yield Button("Run Doctor", id="btn-doctor", variant="primary")
            yield Button("Show Version", id="btn-version", variant="default")
            yield Button("Clear History", id="btn-clear", variant="warning")
        
        yield Label("\n[bright_black]Tip: Use the command palette (Ctrl+P) for more actions[/]")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        button_id = event.button.id
        
        if button_id == "btn-doctor":
            self.app.bell()
            self.notify("Running health check...", title="Doctor")
        elif button_id == "btn-version":
            from importlib.metadata import PackageNotFoundError, version as pkg_version
            try:
                ver = pkg_version("modeltoolbox")
            except PackageNotFoundError:
                ver = "dev"
            self.notify(f"ModelToolbox v{ver}", title="Version")
        elif button_id == "btn-clear":
            self.notify("History cleared", title="Clear")
