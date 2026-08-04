from __future__ import annotations

import os
import shlex
import sys
from collections.abc import Sequence

import click
import typer

try:
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

from modeltoolbox_core.ui.rich_components import (
    create_command_table,
    create_help_panel,
    render_shell_ui,
)

EXIT_COMMANDS = {"exit", "quit", "q"}
HELP_COMMANDS = {"help", "?"}
CLEAR_COMMANDS = {"clear", "cls"}

# Command registry with descriptions
COMMAND_REGISTRY = {
    "/help": "Show this help message",
    "/doctor": "Check system health and dependencies",
    "/version": "Display ModelToolbox version",
    "/clear": "Clear the terminal screen",
    "/exit": "Exit the ModelToolbox shell",
}


def run_shell(app: typer.Typer) -> None:
    """Run the terminal-first ModelToolbox prompt."""
    ui_mode = os.getenv("MTB_UI_MODE", "rich" if RICH_AVAILABLE else "classic").lower()
    
    # Auto-launch TUI if available and in interactive terminal
    if ui_mode == "tui" and sys.stdout.isatty():
        try:
            from modeltoolbox_core.tui.app import run_tui
            run_tui()
            return
        except ImportError:
            typer.echo("Note: Textual TUI not available. Falling back to Rich shell.")
            typer.echo("Install with: pip install modeltoolbox-core[ui]")
            typer.echo()
            ui_mode = "rich" if RICH_AVAILABLE else "classic"
    
    use_rich = ui_mode == "rich" and RICH_AVAILABLE
    console = Console() if use_rich else None
    
    current_tab = 0
    tabs = ["Session", "Workspaces", "History", "Settings"]
    
    def render_ui():
        """Render the complete UI."""
        if use_rich and console:
            render_shell_ui(console, tabs, current_tab)
        else:
            _render_fallback_ui(tabs, current_tab)
    
    render_ui()
    
    # Main loop
    while True:
        try:
            # Use click.prompt for better input handling
            line = click.prompt("", prompt_suffix="❯ ", default="", show_default=False, err=True).lstrip("\ufeff").strip()
        except (EOFError, KeyboardInterrupt):
            typer.echo()
            return

        if not line:
            continue

        lowered = line.lower()
        
        # Handle slash commands with autocomplete
        if line.startswith("/") and len(line) > 1:
            if line == "/help" or lowered in HELP_COMMANDS:
                _show_help(app)
                continue
            elif line == "/clear" or lowered in CLEAR_COMMANDS:
                render_ui()
                continue
            elif line == "/exit" or lowered in EXIT_COMMANDS:
                return
            elif line == "/doctor":
                _invoke(app, ["doctor"])
                continue
            elif line == "/version":
                _invoke(app, ["version"])
                continue
        
        # Show command menu when just "/" is typed
        if line == "/":
            _show_command_menu(app)
            continue
        
        # Handle special navigation commands
        if line in ["<", "←", "left"]:
            current_tab = (current_tab - 1) % len(tabs)
            render_ui()
            continue
        elif line in [">", "→", "right"]:
            current_tab = (current_tab + 1) % len(tabs)
            render_ui()
            continue
        
        if lowered in EXIT_COMMANDS:
            return
        if lowered in HELP_COMMANDS:
            _show_help(app)
            continue
        if lowered in CLEAR_COMMANDS:
            typer.echo("\033c", nl=False)
            continue

        try:
            argv = shlex.split(line)
        except ValueError as exc:
            typer.secho(f"✗ parse error: {exc}", fg=typer.colors.RED)
            continue

        _invoke(app, argv)


def _show_command_menu(app: typer.Typer) -> None:
    """Show command autocomplete menu."""
    ui_mode = os.getenv("MTB_UI_MODE", "rich" if RICH_AVAILABLE else "classic").lower()
    use_rich = ui_mode == "rich" and RICH_AVAILABLE
    console = Console() if use_rich else None
    
    commands = []
    if hasattr(app, "registered_commands"):
        for cmd in app.registered_commands:
            if hasattr(cmd, "name") and cmd.name and hasattr(cmd, "help"):
                commands.append((f"/{cmd.name}", cmd.help or f"Run {cmd.name} command"))
    
    slash_commands = [
        ("/help", "Show this help message"),
        ("/doctor", "Check system health and dependencies"),
        ("/version", "Display ModelToolbox version"),
        ("/clear", "Clear the terminal screen"),
        ("/exit", "Exit the ModelToolbox shell"),
    ]
    
    all_commands = slash_commands + commands
    
    if use_rich and console:
        console.print()
        console.print(create_command_table(all_commands))
        console.print()
    else:
        typer.echo()
        for cmd, desc in all_commands:
            typer.echo(f"❯ {cmd:<20}{desc}")
        typer.echo()


def _show_help(app: typer.Typer) -> None:
    """Show help panel."""
    ui_mode = os.getenv("MTB_UI_MODE", "rich" if RICH_AVAILABLE else "classic").lower()
    use_rich = ui_mode == "rich" and RICH_AVAILABLE
    console = Console() if use_rich else None
    
    slash_commands = [
        ("/help", "Show this help message"),
        ("/doctor", "Check system health and dependencies"),
        ("/version", "Display ModelToolbox version"),
        ("/clear", "Clear the terminal screen"),
        ("/exit", "Exit the ModelToolbox shell"),
    ]
    
    module_commands = []
    if hasattr(app, "registered_commands"):
        for cmd in app.registered_commands:
            if hasattr(cmd, "name") and cmd.name:
                help_text = getattr(cmd, "help", f"Run {cmd.name} command")
                module_commands.append((cmd.name, help_text))
    
    if use_rich and console:
        console.print()
        console.print(create_help_panel(slash_commands, module_commands if module_commands else None))
        console.print()
    else:
        _show_fallback_help(slash_commands, module_commands if module_commands else None)


def _show_commands(app: typer.Typer) -> None:
    """Show available commands in a nice box."""
    _show_command_menu(app)


def _render_fallback_ui(tabs: list[str], current_tab: int) -> None:
    """Fallback UI rendering when Rich is not available."""
    typer.echo("\033c", nl=False)
    
    tab_line = ""
    for i, name in enumerate(tabs):
        if i == current_tab:
            tab_line += typer.style(f" {name} ", fg=typer.colors.WHITE, bg=typer.colors.BLUE, bold=True)
        else:
            tab_line += typer.style(f" {name} ", fg=typer.colors.BRIGHT_BLACK)
        tab_line += " "
    
    typer.echo(tab_line)
    typer.echo()
    
    logo_3d = """
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
    
    typer.echo(typer.style(logo_3d, fg=typer.colors.CYAN, bold=True))
    typer.echo(typer.style("  ModelToolbox v0.1.0 ", fg=typer.colors.BRIGHT_WHITE, bold=True) +
               typer.style("uses AI.", fg=typer.colors.WHITE))
    typer.echo(typer.style("  Check for mistakes.", fg=typer.colors.BRIGHT_BLACK))
    typer.echo()
    typer.echo()
    typer.echo(typer.style("● ", fg=typer.colors.BLUE) +
               typer.style("Tip: ", fg=typer.colors.WHITE, bold=True) +
               typer.style("/help", fg=typer.colors.CYAN) +
               typer.style(" - Show all available commands and usage", fg=typer.colors.WHITE))
    typer.echo(typer.style("  └─ ", fg=typer.colors.BRIGHT_BLACK) +
               typer.style("Type ", fg=typer.colors.BRIGHT_BLACK) +
               typer.style("/", fg=typer.colors.CYAN) +
               typer.style(" to see command menu, use ", fg=typer.colors.BRIGHT_BLACK) +
               typer.style("← →", fg=typer.colors.CYAN) +
               typer.style(" to switch tabs", fg=typer.colors.BRIGHT_BLACK))
    typer.echo()


def _show_fallback_help(slash_commands: list[tuple[str, str]], module_commands: list[tuple[str, str]] | None = None) -> None:
    """Fallback help when Rich is not available."""
    typer.echo()
    typer.echo(typer.style("ModelToolbox Commands", fg=typer.colors.BRIGHT_WHITE, bold=True))
    typer.echo(typer.style("=" * 60, fg=typer.colors.BRIGHT_BLACK))
    typer.echo()
    typer.echo(typer.style("Slash Commands", fg=typer.colors.CYAN, bold=True))
    typer.echo()
    
    for cmd, desc in slash_commands:
        typer.echo(typer.style(f"  {cmd:<15}", fg=typer.colors.GREEN) +
                   typer.style(desc, fg=typer.colors.WHITE))
    
    if module_commands:
        typer.echo()
        typer.echo(typer.style("Module Commands", fg=typer.colors.CYAN, bold=True))
        typer.echo()
        for cmd, desc in module_commands:
            typer.echo(typer.style(f"  {cmd:<15}", fg=typer.colors.YELLOW) +
                       typer.style(desc, fg=typer.colors.WHITE))
    
    typer.echo()
    typer.echo(typer.style("Tip: ", fg=typer.colors.BLUE, bold=True) +
               typer.style("Type ", fg=typer.colors.BRIGHT_BLACK) +
               typer.style("/", fg=typer.colors.CYAN) +
               typer.style(" to see command suggestions", fg=typer.colors.BRIGHT_BLACK))
    typer.echo()


def _invoke(app: typer.Typer, argv: Sequence[str]) -> None:
    try:
        app(args=list(argv), standalone_mode=False)
    except click.exceptions.Exit as exc:
        if exc.exit_code not in (0, None):
            typer.secho(f"exit code: {exc.exit_code}", fg=typer.colors.RED)
    except click.ClickException as exc:
        exc.show()
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 1
        if code:
            typer.secho(f"exit code: {code}", fg=typer.colors.RED)
