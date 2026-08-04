"""Rich components for terminal UI."""

from __future__ import annotations

from typing import Any

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None
    Layout = None
    Panel = None
    Table = None
    Text = None
    Markdown = None


def create_logo_panel() -> Panel | str:
    """Create the 3D ModelToolbox logo panel."""
    if not RICH_AVAILABLE:
        return _create_fallback_logo()
    
    logo_text = """
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
"""
    
    text = Text(logo_text, style="bold cyan")
    text.append("\n  ModelToolbox v0.1.0 ", style="bold bright_white")
    text.append("uses AI.", style="white")
    text.append("\n  Check for mistakes.", style="bright_black")
    
    return Panel(text, border_style="cyan", padding=(0, 1))


def create_tabs(tabs: list[str], current_tab: int) -> Text | str:
    """Create tab navigation bar."""
    if not RICH_AVAILABLE:
        return _create_fallback_tabs(tabs, current_tab)
    
    text = Text()
    for i, name in enumerate(tabs):
        if i == current_tab:
            text.append(f" {name} ", style="bold white on blue")
        else:
            text.append(f" {name} ", style="bright_black")
        text.append(" ")
    
    return text


def create_command_table(commands: list[tuple[str, str]]) -> Table | str:
    """Create command menu table."""
    if not RICH_AVAILABLE:
        return _create_fallback_command_table(commands)
    
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Command", style="cyan", width=20)
    table.add_column("Description", style="bright_black")
    
    for cmd, desc in commands:
        table.add_row(f"❯ {cmd}", desc)
    
    return table


def create_help_panel(slash_commands: list[tuple[str, str]], module_commands: list[tuple[str, str]] | None = None) -> Panel | str:
    """Create help panel with command documentation."""
    if not RICH_AVAILABLE:
        return _create_fallback_help(slash_commands, module_commands)
    
    text = Text()
    
    text.append("Slash Commands\n", style="bold cyan")
    text.append("\n")
    
    for cmd, desc in slash_commands:
        text.append(f"  {cmd:<15}", style="green")
        text.append(f"{desc}\n", style="white")
    
    if module_commands:
        text.append("\n")
        text.append("Module Commands\n", style="bold cyan")
        text.append("\n")
        
        for cmd, desc in module_commands:
            text.append(f"  {cmd:<15}", style="yellow")
            text.append(f"{desc}\n", style="white")
    
    text.append("\n")
    text.append("Tip: ", style="bold blue")
    text.append("Type ", style="bright_black")
    text.append("/", style="cyan")
    text.append(" to see command suggestions", style="bright_black")
    
    return Panel(text, title="[bold bright_white]ModelToolbox Commands[/]", border_style="bright_black", padding=(1, 2))


def render_shell_ui(console: Console, tabs: list[str], current_tab: int) -> None:
    """Render the complete shell UI."""
    if not RICH_AVAILABLE:
        _render_fallback_ui(tabs, current_tab)
        return
    
    console.clear()
    
    # Tabs
    console.print(create_tabs(tabs, current_tab))
    console.print()
    
    # Logo
    console.print(create_logo_panel())
    console.print()
    
    # Tip
    tip = Text()
    tip.append("● ", style="blue")
    tip.append("Tip: ", style="bold white")
    tip.append("/help", style="cyan")
    tip.append(" - Show all available commands and usage\n", style="white")
    tip.append("  └─ ", style="bright_black")
    tip.append("Type ", style="bright_black")
    tip.append("/", style="cyan")
    tip.append(" to see command menu, use ", style="bright_black")
    tip.append("← →", style="cyan")
    tip.append(" to switch tabs", style="bright_black")
    
    console.print(tip)
    console.print()


def _create_fallback_logo() -> str:
    """Fallback logo when Rich is not available."""
    return """
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

  ModelToolbox v0.1.0 uses AI.
  Check for mistakes.
"""


def _create_fallback_tabs(tabs: list[str], current_tab: int) -> str:
    """Fallback tabs when Rich is not available."""
    result = ""
    for i, name in enumerate(tabs):
        if i == current_tab:
            result += f"[{name}] "
        else:
            result += f" {name}  "
    return result


def _create_fallback_command_table(commands: list[tuple[str, str]]) -> str:
    """Fallback command table when Rich is not available."""
    result = "\n"
    for cmd, desc in commands:
        result += f"❯ {cmd:<20}{desc}\n"
    return result


def _create_fallback_help(slash_commands: list[tuple[str, str]], module_commands: list[tuple[str, str]] | None = None) -> str:
    """Fallback help when Rich is not available."""
    result = "\nModelToolbox Commands\n"
    result += "=" * 60 + "\n\n"
    result += "Slash Commands\n\n"
    
    for cmd, desc in slash_commands:
        result += f"  {cmd:<15}{desc}\n"
    
    if module_commands:
        result += "\nModule Commands\n\n"
        for cmd, desc in module_commands:
            result += f"  {cmd:<15}{desc}\n"
    
    result += "\nTip: Type / to see command suggestions\n"
    return result


def _render_fallback_ui(tabs: list[str], current_tab: int) -> None:
    """Fallback UI rendering when Rich is not available."""
    import sys
    
    sys.stdout.write("\033c")
    sys.stdout.flush()
    
    print(_create_fallback_tabs(tabs, current_tab))
    print()
    print(_create_fallback_logo())
    print()
    print("● Tip: /help - Show all available commands and usage")
    print("  └─ Type / to see command menu, use ← → to switch tabs")
    print()
