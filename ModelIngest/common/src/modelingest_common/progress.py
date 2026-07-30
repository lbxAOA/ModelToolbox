"""进度追踪和显示。

支持 Rich 终端显示和简单文本显示（Rich 未安装时降级）。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable

try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeElapsedColumn,
    )
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class ProgressStage(Enum):
    """处理阶段枚举"""
    RENDER = "render"
    FETCH = "fetch"
    PARSE = "parse"
    CLEAN = "clean"
    DISTILL = "distill"
    ORGANIZE = "organize"
    COMPLETE = "complete"


@dataclass
class ProgressInfo:
    """进度信息"""
    stage: ProgressStage
    current: int
    total: int
    message: str


class ProgressTracker:
    """进度追踪器。
    
    支持两种显示模式：
    - Rich 模式：带进度条、时间、彩色显示（需安装 rich）
    - 简单模式：纯文本显示（rich 未安装时自动降级）
    """
    
    def __init__(self, use_rich: bool = True):
        """初始化进度追踪器。
        
        Args:
            use_rich: 是否使用 Rich 显示（默认 True，未安装会自动降级）
        """
        self.use_rich = use_rich and RICH_AVAILABLE
        self._progress = None
        self._task_ids: dict[str, int] = {}
        
        if self.use_rich:
            self._console = Console()
            self._progress = Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
                console=self._console,
            )
    
    def start(self):
        """开始进度显示"""
        if self._progress:
            self._progress.start()
    
    def update(
        self,
        stage: ProgressStage,
        current: int,
        total: int,
        message: str = "",
    ):
        """更新进度。
        
        Args:
            stage: 当前阶段
            current: 当前进度
            total: 总数
            message: 进度消息
        """
        stage_name = stage.value
        
        if self.use_rich and self._progress:
            # Rich 模式
            if stage_name not in self._task_ids:
                self._task_ids[stage_name] = self._progress.add_task(
                    f"[cyan]{stage_name}[/cyan]",
                    total=total,
                )
            
            task_id = self._task_ids[stage_name]
            desc = f"[cyan]{stage_name}[/cyan]"
            if message:
                desc += f": {message}"
            
            self._progress.update(
                task_id,
                completed=current,
                total=total,
                description=desc,
            )
        else:
            # 简单文本模式
            if total > 0:
                percentage = (current / total) * 100
                print(f"[{stage_name}] {percentage:.1f}% ({current}/{total}) - {message}")
            else:
                print(f"[{stage_name}] {message}")
    
    def complete(self, message: str = "完成"):
        """标记为完成。
        
        Args:
            message: 完成消息
        """
        if self.use_rich and self._progress:
            self._progress.stop()
        else:
            print(f"✓ {message}")
    
    def error(self, message: str):
        """显示错误。
        
        Args:
            message: 错误消息
        """
        if self.use_rich:
            self._console.print(f"[red]✗ {message}[/red]")
        else:
            print(f"✗ {message}")
    
    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.complete()
        else:
            self.error(f"处理失败: {exc_val}")
