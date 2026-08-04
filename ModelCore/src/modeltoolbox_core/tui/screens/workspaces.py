"""Workspaces tab for TUI."""

from __future__ import annotations

try:
    from textual.app import ComposeResult
    from textual.containers import Container
    from textual.widgets import Static, Label, ListView, ListItem
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    ComposeResult = None
    Container = object
    Static = object
    Label = object
    ListView = object
    ListItem = object


class WorkspacesTab(Static):
    """Manage workspaces."""
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            yield Label("Textual not available")
            return
        
        yield Label("[bold cyan]Available Workspaces[/]\n")
        
        with Container(classes="workspace-list"):
            yield ListView(
                ListItem(Label("[green]●[/] Default Workspace")),
                ListItem(Label("[yellow]●[/] Project A")),
                ListItem(Label("[yellow]●[/] Project B")),
                ListItem(Label("[bright_black]○[/] Archived Project")),
            )
        
        yield Label("\n[bright_black]Tip: Select a workspace to switch context[/]")
