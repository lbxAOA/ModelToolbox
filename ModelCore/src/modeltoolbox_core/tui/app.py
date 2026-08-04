"""Main Textual TUI application."""

from __future__ import annotations

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Horizontal
    from textual.widgets import Footer, Header, TabbedContent, TabPane
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


if TEXTUAL_AVAILABLE:
    from modeltoolbox_core.tui.screens.session import SessionTab
    from modeltoolbox_core.tui.screens.workspaces import WorkspacesTab
    from modeltoolbox_core.tui.screens.history import HistoryTab
    from modeltoolbox_core.tui.screens.settings import SettingsTab
    from modeltoolbox_core.tui.widgets.logo import LogoWidget
    
    
    class ModelToolboxApp(App):
        """ModelToolbox Textual TUI application."""
        
        CSS_PATH = "theme.tcss"
        TITLE = "ModelToolbox"
        SUB_TITLE = "v0.1.0 - Terminal UI"
        
        BINDINGS = [
            Binding("q", "quit", "Quit", priority=True),
            Binding("d", "toggle_dark", "Toggle Dark Mode"),
            Binding("ctrl+c", "quit", "Quit", show=False),
        ]
        
        def compose(self) -> ComposeResult:
            """Create child widgets for the app."""
            yield Header()
            
            with Container(id="app-grid"):
                yield LogoWidget()
                
                with TabbedContent(initial="session"):
                    with TabPane("Session", id="session"):
                        yield SessionTab()
                    
                    with TabPane("Workspaces", id="workspaces"):
                        yield WorkspacesTab()
                    
                    with TabPane("History", id="history"):
                        yield HistoryTab()
                    
                    with TabPane("Settings", id="settings"):
                        yield SettingsTab()
            
            yield Footer()
        
        def action_toggle_dark(self) -> None:
            """Toggle dark mode."""
            self.dark = not self.dark

else:
    class ModelToolboxApp:
        """Placeholder when Textual is not available."""
        pass


def run_tui() -> None:
    """Run the Textual TUI."""
    if not TEXTUAL_AVAILABLE:
        print("Error: Textual is not installed.")
        print("Install with: pip install modeltoolbox-core[ui]")
        return
    
    app = ModelToolboxApp()
    app.run()
