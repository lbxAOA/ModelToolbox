"""History tab for TUI."""

from __future__ import annotations

try:
    from textual.app import ComposeResult
    from textual.containers import Container
    from textual.widgets import Static, Label, DataTable
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    ComposeResult = None
    Container = object
    Static = object
    Label = object
    DataTable = object


class HistoryTab(Static):
    """Command history viewer."""
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        if not TEXTUAL_AVAILABLE:
            yield Label("Textual not available")
            return
        
        yield Label("[bold cyan]Command History[/]\n")
        
        table = DataTable(classes="history-list")
        table.add_columns("Time", "Command", "Status")
        table.add_row("10:30:45", "/doctor", "[green]✓[/]")
        table.add_row("10:28:12", "/version", "[green]✓[/]")
        table.add_row("10:25:03", "ingest fetch --url example.com", "[green]✓[/]")
        table.add_row("10:20:15", "/help", "[green]✓[/]")
        
        yield table
        
        yield Label("\n[bright_black]Tip: Press Enter to re-run a command[/]")
