"""Logo widget for ModelToolbox TUI."""

from __future__ import annotations

try:
    from textual.widget import Widget
    from textual.widgets import Static
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False
    Widget = object
    Static = object


LOGO_TEXT = """
 ███╗   ███╗ ██████╗ ██████╗ ███████╗██╗     
 ████╗ ████║██╔═══██╗██╔══██╗██╔════╝██║     
 ██╔████╔██║██║   ██║██║  ██║█████╗  ██║     
 ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  ██║     
 ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗███████╗
 ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚══════╝
                                              
 ████████╗ ██████╗  ██████╗ ██╗     ██████╗  ██████╗ ██╗  ██╗
 ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔══██╗██╔═══██╗╚██╗██╔╝
    ██║   ██║   ██║██║   ██║██║     ██████╔╝██║   ██║ ╚███╔╝ 
    ██║   ██║   ██║██║   ██║██║     ██╔══██╗██║   ██║ ██╔██╗ 
    ██║   ╚██████╔╝╚██████╔╝███████╗██████╔╝╚██████╔╝██╔╝ ██╗
    ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝

  [bold bright_white]ModelToolbox v0.1.0[/] [white]uses AI.[/]
  [bright_black]Check for mistakes.[/]
"""


class LogoWidget(Static):
    """Display the ModelToolbox 3D logo."""
    
    def __init__(self) -> None:
        """Initialize the logo widget."""
        super().__init__(LOGO_TEXT)
