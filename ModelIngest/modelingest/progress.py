"""Rich 终端实时进度显示模块。"""

from __future__ import annotations

from typing import Callable

try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeRemainingColumn,
        TimeElapsedColumn,
    )
    from rich.table import Table
    from rich.live import Live
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def create_rich_progress_callback() -> Callable:
    """创建 Rich 进度回调函数"""

    if not RICH_AVAILABLE:
        # Rich 未安装，使用简单的文本进度
        return _simple_progress_callback

    console = Console()

    # 创建进度条
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    )

    task_ids = {}

    def callback(progress_info):
        """进度回调"""
        from .builder import BuildStage

        stage_name = progress_info.stage.value

        # 为每个阶段创建或更新任务
        if stage_name not in task_ids:
            task_ids[stage_name] = progress.add_task(
                f"[cyan]{stage_name}[/cyan]",
                total=100
            )

        task_id = task_ids[stage_name]

        # 更新进度
        if progress_info.total > 0:
            percentage = (progress_info.current / progress_info.total) * 100
            progress.update(
                task_id,
                completed=percentage,
                description=f"[cyan]{stage_name}[/cyan]: {progress_info.message}"
            )
        else:
            progress.update(
                task_id,
                description=f"[cyan]{stage_name}[/cyan]: {progress_info.message}"
            )

        # 如果是第一次调用，启动进度显示
        if not progress.live.is_started:
            progress.start()

        # 完成阶段时标记为完成
        if progress_info.stage == BuildStage.COMPLETE:
            progress.stop()

    return callback


def _simple_progress_callback(progress_info):
    """简单的文本进度回调（Rich 未安装时使用）"""
    stage_name = progress_info.stage.value
    message = progress_info.message

    if progress_info.total > 0:
        percentage = (progress_info.current / progress_info.total) * 100
        print(f"[{stage_name}] {percentage:.1f}% - {message}")
    else:
        print(f"[{stage_name}] {message}")


class ProgressDisplay:
    """进度显示管理器"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.current_stage = None

    def show_header(self, title: str):
        """显示标题"""
        if self.console:
            self.console.print(f"\n[bold green]{title}[/bold green]\n")
        else:
            print(f"\n{'='*60}")
            print(f"  {title}")
            print(f"{'='*60}\n")

    def show_stage(self, stage_name: str, message: str = ""):
        """显示当前阶段"""
        if self.console:
            self.console.print(f"[bold cyan]▶ {stage_name}[/bold cyan] {message}")
        else:
            print(f"▶ {stage_name} {message}")

    def show_progress(self, current: int, total: int, message: str = ""):
        """显示进度"""
        if total > 0:
            percentage = (current / total) * 100
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = "█" * filled + "░" * (bar_length - filled)

            if self.console:
                self.console.print(f"  {bar} {percentage:.1f}% {message}", end="\r")
            else:
                print(f"  {bar} {percentage:.1f}% {message}", end="\r")
        else:
            if self.console:
                self.console.print(f"  {message}")
            else:
                print(f"  {message}")

    def show_success(self, message: str):
        """显示成功消息"""
        if self.console:
            self.console.print(f"[bold green]✓[/bold green] {message}")
        else:
            print(f"✓ {message}")

    def show_error(self, message: str):
        """显示错误消息"""
        if self.console:
            self.console.print(f"[bold red]✗[/bold red] {message}")
        else:
            print(f"✗ {message}")

    def show_warning(self, message: str):
        """显示警告消息"""
        if self.console:
            self.console.print(f"[bold yellow]⚠[/bold yellow] {message}")
        else:
            print(f"⚠ {message}")

    def show_stats(self, stats: dict):
        """显示统计信息"""
        if self.console:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("指标", style="cyan")
            table.add_column("数量", justify="right", style="green")

            for key, value in stats.items():
                table.add_row(key, str(value))

            self.console.print(table)
        else:
            print("\n统计信息:")
            for key, value in stats.items():
                print(f"  {key}: {value}")
