"""Settings tab for TUI."""

from __future__ import annotations

try:
    from textual.app import ComposeResult
    from textual.containers import Container, Vertical
    from textual.widgets import Static, Label, Switch, Input
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    ComposeResult = None
    Container = object
    Vertical = object
    Static = object
    Label = object
    Switch = object
    Input = object


class SettingsTab(Static):
    """Application settings."""
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            yield Label("Textual not available")
            return
        
        yield Label("[bold cyan]Settings[/]\n")
        
        with Container(classes="settings-panel"):
            with Vertical(classes="setting-item"):
                yield Label("[white]Dark Mode[/]")
                yield Switch(value=True, id="switch-dark")
            
            with Vertical(classes="setting-item"):
                yield Label("[white]Auto-save History[/]")
                yield Switch(value=True, id="switch-history")
            
            with Vertical(classes="setting-item"):
                yield Label("[white]Default Workspace[/]")
                yield Input(placeholder="Enter workspace name", id="input-workspace")
            
            with Vertical(classes="setting-item"):
                yield Label("[white]Plugin Auto-load[/]")
                yield Switch(value=True, id="switch-plugins")
        
        yield Label("\n[bright_black]Settings are saved automatically[/]")
